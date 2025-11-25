from uuid import UUID
from typing import List, Optional
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.quiz_attempt import QuizAttempt
from app.models.user_answer import UserAnswer
from app.schemas.quiz import QuizCreate, QuizRead, QuizUpdate
from app.schemas.quiz_submission import QuizResultRead, QuizSubmit, UserStatsRead
from app.uow.unit_of_work import UnitOfWork
from app.core.exceptions import (
    MaxAttemptsReached,
    QuizNotFound,
    PermissionDenied,
    NotCompanyMember,
)
from app.models.enum import RoleEnum


class QuizService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _check_admin_or_owner_permissions(
        self, user_id: UUID, company_id: UUID
    ) -> None:
        assoc = await self.uow.company_associations.get_by_user_and_company(
            user_id, company_id
        )
        if not assoc or assoc.role not in [RoleEnum.OWNER.value, RoleEnum.ADMIN.value]:
            raise PermissionDenied("You must be an owner or admin to manage quizzes")

    async def create_quiz(
        self, user_id: UUID, company_id: UUID, quiz_data: QuizCreate
    ) -> QuizRead:
        await self._check_admin_or_owner_permissions(user_id, company_id)

        async with self.uow:
            new_quiz = Quiz(
                company_id=company_id,
                name=quiz_data.name,
                description=quiz_data.description,
                max_attempts_per_user=quiz_data.max_attempts_per_user,
            )

            for question_data in quiz_data.questions:
                new_question = Question(text=question_data.text, quiz=new_quiz)
                for answer_data in question_data.answers:
                    Answer(
                        text=answer_data.text,
                        is_correct=answer_data.is_correct,
                        question=new_question,
                    )

            await self.uow.quizzes.create(new_quiz)

            created_quiz = await self.uow.quizzes.get_by_id_with_details(new_quiz.id)
            if not created_quiz:
                raise QuizNotFound

            return QuizRead.model_validate(created_quiz)

    async def update_quiz(
        self, user_id: UUID, company_id: UUID, quiz_id: UUID, quiz_data: QuizUpdate
    ) -> QuizRead:
        await self._check_admin_or_owner_permissions(user_id, company_id)

        async with self.uow:
            quiz = await self.uow.quizzes.get_by_id_with_details(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise QuizNotFound

            update_data = quiz_data.model_dump(exclude_unset=True)

            for field in ["name", "description", "max_attempts_per_user"]:
                if field in update_data:
                    setattr(quiz, field, update_data[field])

            if "questions" in update_data:
                for old_question in list(quiz.questions):
                    await self.uow.questions.delete(old_question)

                quiz.questions.clear()

                for question_data in quiz_data.questions:
                    new_question = Question(text=question_data.text, quiz_id=quiz.id)

                    for answer_data in question_data.answers:
                        new_answer = Answer(
                            text=answer_data.text,
                            is_correct=answer_data.is_correct,
                            question=new_question,
                        )
                        new_question.answers.append(new_answer)

                    quiz.questions.append(new_question)

            await self.uow.quizzes.create(quiz)

            updated_quiz = await self.uow.quizzes.get_by_id_with_details(quiz_id)
            if not updated_quiz:
                raise QuizNotFound

            return QuizRead.model_validate(updated_quiz)

    async def delete_quiz(self, user_id: UUID, company_id: UUID, quiz_id: UUID) -> None:
        await self._check_admin_or_owner_permissions(user_id, company_id)

        async with self.uow:
            quiz = await self.uow.quizzes.get_by_field("id", quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise QuizNotFound
            await self.uow.quizzes.delete(quiz)

    async def get_quiz(
        self, user_id: UUID, company_id: UUID, quiz_id: UUID
    ) -> QuizRead:
        async with self.uow:
            assoc = await self.uow.company_associations.get_by_user_and_company(
                user_id, company_id
            )
            if not assoc:
                raise NotCompanyMember

            quiz = await self.uow.quizzes.get_by_id_with_details(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise QuizNotFound

            return QuizRead.model_validate(quiz)

    async def list_quizzes_for_company(
        self, user_id: UUID, company_id: UUID, skip: int = 0, limit: int = 10
    ) -> List[QuizRead]:
        async with self.uow:
            assoc = await self.uow.company_associations.get_by_user_and_company(
                user_id, company_id
            )
            if not assoc:
                raise NotCompanyMember

            quizzes = await self.uow.quizzes.get_all_for_company(
                company_id, skip, limit
            )
            return [QuizRead.model_validate(q) for q in quizzes]

    async def submit_quiz(
        self, user_id: UUID, company_id: UUID, quiz_id: UUID, submission: QuizSubmit
    ) -> QuizResultRead:
        async with self.uow:
            assoc = await self.uow.company_associations.get_by_user_and_company(
                user_id, company_id
            )
            if not assoc:
                raise NotCompanyMember

            quiz = await self.uow.quizzes.get_by_id_with_details(quiz_id)
            if not quiz or quiz.company_id != company_id:
                raise QuizNotFound()

            if quiz.max_attempts_per_user is not None:
                attempt_count = await self.uow.quiz_attempts.count_attempts_for_quiz(
                    user_id, quiz_id
                )
                if attempt_count >= quiz.max_attempts_per_user:
                    raise MaxAttemptsReached

            correct_answers_map = {
                q.id: {a.id for a in q.answers if a.is_correct} for q in quiz.questions
            }

            new_attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                company_id=company_id,
                total_questions=len(submission.answers),
            )
            await self.uow.quiz_attempts.create(new_attempt)

            score = 0
            for answer_data in submission.answers:
                question_id = answer_data.question_id
                selected_ids = set(answer_data.selected_answer_ids)

                if question_id not in correct_answers_map:
                    continue

                actual_correct_ids = correct_answers_map[question_id]
                is_correct = selected_ids == actual_correct_ids

                if is_correct:
                    score += 1

                await self.uow.user_answer.create(
                    UserAnswer(
                        attempt_id=new_attempt.id,
                        question_id=question_id,
                        is_correct=is_correct,
                    )
                )

            new_attempt.score = score

            return QuizResultRead(
                attempt_id=new_attempt.id,
                quiz_id=new_attempt.quiz_id,
                company_id=new_attempt.company_id,
                score=new_attempt.score,
                total_questions=new_attempt.total_questions,
                percentage=(
                    (new_attempt.score / new_attempt.total_questions) * 100
                    if new_attempt.total_questions > 0
                    else 0
                ),
                submitted_at=new_attempt.created_at,
            )

    async def get_user_stats(
        self, user_id: UUID, company_id: Optional[UUID] = None
    ) -> UserStatsRead:
        total_correct = await self.uow.user_answer.get_total_correct_for_user(
            user_id, company_id
        )
        total_answered = await self.uow.user_answer.get_total_answered_for_user(
            user_id, company_id
        )

        average_percentage = 0
        if total_answered > 0:
            average_percentage = (total_correct / total_answered) * 100

        return UserStatsRead(
            user_id=user_id,
            company_id=company_id,
            total_correct_answers=total_correct,
            total_answered_questions=total_answered,
            average_score_percentage=average_percentage,
        )
