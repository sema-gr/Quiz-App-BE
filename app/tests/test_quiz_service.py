import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.models.user import User
from app.models.company import Company
from app.models.company_association import CompanyAssociation
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.enum import RoleEnum
from app.schemas.quiz_submission import QuizResultRead, QuizSubmit, UserAnswerSubmit
from app.uow.unit_of_work import UnitOfWork
from app.services.quiz import QuizService
from app.core.exceptions import MaxAttemptsReached


@pytest_asyncio.fixture(scope="function")
async def uow(db_engine):
    session_factory = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def _session_factory():
        async with session_factory() as session:
            yield session

    yield UnitOfWork(session_factory=_session_factory)


@pytest_asyncio.fixture(scope="function")
async def test_data(db_engine):
    session_factory = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async with session_factory() as session:
        uow_instance = UnitOfWork(session_factory=lambda: session)

        if hasattr(uow_instance, "_initialize_repositories"):
            uow_instance._initialize_repositories()
        else:
            from app.repository.user import UserRepository
            from app.repository.company import CompanyRepository
            from app.repository.company_association import CompanyAssociationRepository
            from app.repository.quiz import (
                QuizRepository,
                QuestionRepository,
                AnswerRepository,
            )

            uow_instance.users = UserRepository(session)
            uow_instance.companies = CompanyRepository(session)
            uow_instance.company_associations = CompanyAssociationRepository(session)
            uow_instance.quizzes = QuizRepository(session)
            uow_instance.questions = QuestionRepository(session)
            uow_instance.answers = AnswerRepository(session)

        owner_user = User(email="owner@test.com", hashed_password="hash_password")
        member_user = User(email="member@test.com", hashed_password="hash_password")
        await uow_instance.users.create(owner_user)
        await uow_instance.users.create(member_user)

        company = Company(name="Test Company", owner_id=owner_user.id)
        await uow_instance.companies.create(company)

        owner_assoc = CompanyAssociation(
            user_id=owner_user.id, company_id=company.id, role=RoleEnum.OWNER.value
        )
        member_assoc = CompanyAssociation(
            user_id=member_user.id, company_id=company.id, role=RoleEnum.MEMBER.value
        )
        await uow_instance.company_associations.create(owner_assoc)
        await uow_instance.company_associations.create(member_assoc)

        quiz = Quiz(
            company_id=company.id,
            name="Sample Quiz",
            description="A test quiz",
            max_attempts_per_user=1,
        )
        await uow_instance.quizzes.create(quiz)

        q1 = Question(quiz_id=quiz.id, text="What is 2+2?")
        await uow_instance.questions.create(q1)
        a1_1 = Answer(question_id=q1.id, text="3", is_correct=False)
        a1_2 = Answer(question_id=q1.id, text="4", is_correct=True)
        await uow_instance.answers.create(a1_1)
        await uow_instance.answers.create(a1_2)

        q2 = Question(quiz_id=quiz.id, text="Capital of France?")
        await uow_instance.questions.create(q2)
        a2_1 = Answer(question_id=q2.id, text="Paris", is_correct=True)
        a2_2 = Answer(question_id=q2.id, text="London", is_correct=False)
        await uow_instance.answers.create(a2_1)
        await uow_instance.answers.create(a2_2)

        await session.commit()

        class TestData:
            def __init__(self):
                self.owner = owner_user
                self.member = member_user
                self.company = company
                self.quiz = quiz
                self.questions = [q1, q2]
                self.q1_answers = {a1_1.id: a1_1.is_correct, a1_2.id: a1_2.is_correct}
                self.q2_answers = {a2_1.id: a2_1.is_correct, a2_2.id: a2_2.is_correct}

            def get_answer_id(self, answers_dict, is_correct: bool):
                for answer_id, correct_status in answers_dict.items():
                    if correct_status == is_correct:
                        return answer_id
                return None

        return TestData()


@pytest.mark.asyncio
class TestQuizWorkflow:
    async def test_submit_quiz_correctly(self, uow: UnitOfWork, test_data):
        service = QuizService(uow)

        submit_data = QuizSubmit(
            answers=[
                UserAnswerSubmit(
                    question_id=test_data.questions[0].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q1_answers, True)
                    ],
                ),
                UserAnswerSubmit(
                    question_id=test_data.questions[1].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q2_answers, True)
                    ],
                ),
            ]
        )

        result = await service.submit_quiz(
            user_id=test_data.member.id,
            company_id=test_data.company.id,
            quiz_id=test_data.quiz.id,
            submission=submit_data,
        )

        assert isinstance(result, QuizResultRead)
        assert result.score == 2
        assert result.total_questions == 2
        assert result.percentage == 100.0

        attempt = await uow.quiz_attempts.get_by_field("id", result.attempt_id)
        assert attempt is not None
        assert attempt.score == 2

        correct_count = await uow.user_answer.get_total_correct_for_user(
            test_data.member.id
        )
        assert correct_count == 2

    async def test_submit_quiz_partially_correct(self, uow: UnitOfWork, test_data):
        service = QuizService(uow)

        submit_data = QuizSubmit(
            answers=[
                UserAnswerSubmit(
                    question_id=test_data.questions[0].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q1_answers, True)
                    ],
                ),
                UserAnswerSubmit(
                    question_id=test_data.questions[1].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q2_answers, False)
                    ],
                ),
            ]
        )

        result = await service.submit_quiz(
            user_id=test_data.member.id,
            company_id=test_data.company.id,
            quiz_id=test_data.quiz.id,
            submission=submit_data,
        )

        assert result.score == 1
        assert result.total_questions == 2
        assert result.percentage == 50.0

    async def test_submit_quiz_max_attempts_fails(self, uow: UnitOfWork, test_data):
        service = QuizService(uow)

        submit_data = QuizSubmit(
            answers=[
                UserAnswerSubmit(
                    question_id=test_data.questions[0].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q1_answers, True)
                    ],
                ),
                UserAnswerSubmit(
                    question_id=test_data.questions[1].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q2_answers, True)
                    ],
                ),
            ]
        )

        await service.submit_quiz(
            user_id=test_data.member.id,
            company_id=test_data.company.id,
            quiz_id=test_data.quiz.id,
            submission=submit_data,
        )

        with pytest.raises(MaxAttemptsReached):
            await service.submit_quiz(
                user_id=test_data.member.id,
                company_id=test_data.company.id,
                quiz_id=test_data.quiz.id,
                submission=submit_data,
            )

    async def test_get_user_stats(self, uow: UnitOfWork, test_data):
        service = QuizService(uow)

        stats_before = await service.get_user_stats(test_data.member.id)
        assert stats_before.total_answered_questions == 0
        assert stats_before.average_score_percentage == 0

        submit_data = QuizSubmit(
            answers=[
                UserAnswerSubmit(
                    question_id=test_data.questions[0].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q1_answers, True)
                    ],
                ),
                UserAnswerSubmit(
                    question_id=test_data.questions[1].id,
                    selected_answer_ids=[
                        test_data.get_answer_id(test_data.q2_answers, False)
                    ],
                ),
            ]
        )

        await service.submit_quiz(
            user_id=test_data.member.id,
            company_id=test_data.company.id,
            quiz_id=test_data.quiz.id,
            submission=submit_data,
        )

        stats_after = await service.get_user_stats(test_data.member.id)

        assert stats_after.total_correct_answers == 1
        assert stats_after.total_answered_questions == 2
        assert stats_after.average_score_percentage == 50.0

        stats_company = await service.get_user_stats(
            test_data.member.id, test_data.company.id
        )
        stats_other_company = await service.get_user_stats(test_data.member.id, uuid4())

        assert stats_company.average_score_percentage == 50.0
        assert stats_other_company.average_score_percentage == 0.0
