from app.models.company import Company
from app.repository.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db):
        super().__init__(Company, db)
