from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

from app.core.settings import settings
from app.core.database import Base
from app.models import user
from app.models import company
from app.models import company_association
from app.models import company_action
from app.models import quiz
from app.models import question
from app.models import answer
from app.models import quiz_attempt
from app.models import user_answer
import app.models

target_metadata = Base.metadata

config = context.config
fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url", settings.database_url.replace("asyncpg", "psycopg2")
)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.database_url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


main()
