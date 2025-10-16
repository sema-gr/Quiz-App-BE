from app.db.postgres import async_session
from app.uow.unit_of_work import UnitOfWork


def get_uow():
    return UnitOfWork(async_session)
