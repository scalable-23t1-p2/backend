from databases import Database
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Table,
    create_engine,
    func,
)


from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

database = Database(DATABASE_URL, force_rollback=settings.ENVIRONMENT.is_testing)


auth_user = Table(
    "auth_user",
    metadata,
    Column("uuid", Integer, Identity(), primary_key=True),
    Column("email", String, nullable=False),
    Column("password", LargeBinary, nullable=False),
    Column("is_admin", Boolean, server_default="false", nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

#CASCADE means that when a row in the parent table is deleted, 
# all rows in the child table that reference it will also be deleted

refresh_tokens = Table(
    "auth_refresh_token",
    metadata,
    Column("uuid", UUID, primary_key=True),
    Column("user_id", ForeignKey("auth_user.uuid", ondelete="CASCADE"), nullable=False),
    Column("refresh_token", String, nullable=False),
    Column("expires_at", DateTime, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("user_id", ForeignKey("auth_user.uuid", ondelete="CASCADE"), nullable=False),
    Column("message", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

task_data = Table(
    'task_data',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', String, nullable=False),
    Column('task_type', String, nullable=False),
    Column('user', String , nullable=False),
    Column('filename_noext', String, nullable=False),
)

metadata.create_all(engine)
