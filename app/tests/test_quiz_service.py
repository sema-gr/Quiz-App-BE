from contextlib import asynccontextmanager
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from uuid import uuid4
from main import app
from app.core.database import Base
from app.core.dependencies import get_current_user, get_uow
from app.uow.unit_of_work import UnitOfWork
from app.models.user import User
from app.models.company import Company
from app.models.company_association import CompanyAssociation
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.enum import RoleEnum
from app.models.quiz_attempt import QuizAttempt


@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine(
        "postgresql+asyncpg://admin:admin@db/quiz_app_test",
        future=True,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session_factory(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="function")
def uow_factory(session_factory):
    @asynccontextmanager
    async def _uow():
        session = session_factory()
        uow = UnitOfWork(lambda: session)
        await uow.__aenter__()
        try:
            yield uow
        finally:
            await uow.__aexit__(None, None, None)

    return _uow


async def _override_get_uow():
    async with uow_factory() as uow:
        yield uow


app.dependency_overrides[get_uow] = _override_get_uow


@pytest_asyncio.fixture(scope="function")
async def test_data_without_attempt(uow_factory):
    async with uow_factory() as uow:
        owner_user = User(id=uuid4(), email="owner@test.com", hashed_password="hash")
        member_user = User(id=uuid4(), email="member@test.com", hashed_password="hash")
        await uow.users.create(owner_user)
        await uow.users.create(member_user)
        await uow.session.flush()

        company = Company(id=uuid4(), name="Test Company", owner_id=owner_user.id)
        await uow.companies.create(company)
        await uow.session.flush()

        owner_assoc = CompanyAssociation(
            user_id=owner_user.id, company_id=company.id, role=RoleEnum.OWNER.value
        )
        member_assoc = CompanyAssociation(
            user_id=member_user.id, company_id=company.id, role=RoleEnum.MEMBER.value
        )
        await uow.company_associations.create(owner_assoc)
        await uow.company_associations.create(member_assoc)

        quiz = Quiz(
            id=uuid4(),
            company_id=company.id,
            name="Sample Quiz",
            description="A test quiz",
            max_attempts_per_user=1,
        )
        await uow.quizzes.create(quiz)

        q1 = Question(quiz_id=quiz.id, text="2+2?")
        q2 = Question(quiz_id=quiz.id, text="Capital of France?")
        await uow.questions.create(q1)
        await uow.questions.create(q2)

        a1_1 = Answer(question_id=q1.id, text="3", is_correct=False)
        a1_2 = Answer(question_id=q1.id, text="4", is_correct=True)
        a2_1 = Answer(question_id=q2.id, text="Paris", is_correct=True)
        a2_2 = Answer(question_id=q2.id, text="London", is_correct=False)
        assoc_list = await uow.company_associations.list()
        await uow.answers.create(a1_1)
        await uow.answers.create(a1_2)
        await uow.answers.create(a2_1)
        await uow.answers.create(a2_2)

        await uow.commit()

        class TD:
            def __init__(self):
                self.owner = owner_user
                self.member = member_user
                self.company = company
                self.quiz = quiz
                self.questions = [q1, q2]
                self.q1_answers = {a1_1.id: a1_1.is_correct, a1_2.id: a1_2.is_correct}
                self.q2_answers = {a2_1.id: a2_1.is_correct, a2_2.id: a2_2.is_correct}
                self.company_associations = assoc_list

            def get_answer_id(self, answers_dict, is_correct: bool):
                for aid, correct in answers_dict.items():
                    if correct == is_correct:
                        return aid
                return None

        return TD()


@pytest_asyncio.fixture(scope="function")
async def test_data_with_attempt(test_data_without_attempt, uow_factory):
    async with uow_factory() as uow:
        attempt = QuizAttempt(
            user_id=test_data_without_attempt.member.id,
            quiz_id=test_data_without_attempt.quiz.id,
            company_id=test_data_without_attempt.company.id,
            total_questions=2,
            score=2,
        )
        await uow.quiz_attempts.create(attempt)
        await uow.commit()
    return test_data_without_attempt


@pytest_asyncio.fixture()
async def client(test_data_without_attempt, uow_factory):
    td = test_data_without_attempt

    async def _get_current_user():
        return td.member

    async def _get_uow():
        async with uow_factory() as uow:
            yield uow

    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_uow] = _get_uow

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submit_quiz(client, test_data_without_attempt):
    td = test_data_without_attempt

    payload = {
        "answers": [
            {
                "question_id": str(td.questions[0].id),
                "selected_answer_ids": [str(td.get_answer_id(td.q1_answers, True))],
            }
        ]
    }

    response = await client.post(
        f"/companies/{td.company.id}/quizzes/{td.quiz.id}/submit", json=payload
    )

    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_get_my_overall_stats(client, test_data_with_attempt, uow_factory):
    td = test_data_with_attempt

    async def _get_current_user():
        return td.member

    async def _get_uow():
        async with uow_factory() as uow:
            yield uow

    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_uow] = _get_uow

    response = await client.get("/profile/me/stats")
    assert response.status_code == 200

    data = response.json()
    assert "user_id" in data
    assert "company_id" in data
    assert "total_correct_answers" in data
    assert "total_answered_questions" in data
    assert "average_score_percentage" in data


@pytest.mark.asyncio
async def test_get_my_company_stats(client, test_data_with_attempt, uow_factory):
    td = test_data_with_attempt
    company_id = str(td.company.id)

    async def _get_current_user():
        return td.member

    async def _get_uow():
        async with uow_factory() as uow:
            yield uow

    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_uow] = _get_uow

    response = await client.get(f"/profile/me/stats/companies/{company_id}")
    assert response.status_code == 200

    data = response.json()
    assert "user_id" in data
    assert "company_id" in data
    assert "total_correct_answers" in data
    assert "total_answered_questions" in data
    assert "average_score_percentage" in data
