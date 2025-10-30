from app.repository.quiz import AnswerRepository, QuestionRepository, QuizRepository
from app.repository.quiz_attempt import QuizAttemptRepository
from app.repository.user import UserRepository
from app.repository.company import CompanyRepository
from app.repository.company_action import CompanyActionRepository
from app.repository.company_association import CompanyAssociationRepository
from app.repository.user_answer import UserAnswerRepository
from app.uow.base import BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory):
        super().__init__(session_factory)
        self.users: UserRepository
        self.companies: CompanyRepository
        self.company_actions: CompanyActionRepository
        self.company_associations: CompanyAssociationRepository
        self.quizzes: QuizRepository
        self.questions: QuestionRepository
        self.answers: AnswerRepository
        self.quiz_attempts: QuizAttemptRepository
        self.user_answer: UserAnswerRepository

    async def __aenter__(self):
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_actions = CompanyActionRepository(self.session)
        self.company_associations = CompanyAssociationRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answers = AnswerRepository(self.session)
        self.quiz_attempts = QuizAttemptRepository(self.session)
        self.user_answer = UserAnswerRepository(self.session)
        return self
