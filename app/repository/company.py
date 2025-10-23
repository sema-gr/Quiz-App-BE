from app.models.company import Company
from app.repository.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, sessions):
        super().__init__(Company, sessions)
