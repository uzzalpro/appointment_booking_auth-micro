
from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config, pool, text

from alembic import context
from app.config import config as _config
from app.db.models.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    config.set_main_option("sqlalchemy.url", _config.DATABASE_URL)
    
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url= _config.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema='public',  # Ensure alembic_version is in correct schema
        version_table="alembic_version",
        include_schemas=False, 
        default_schema_name="public",
        include_object=lambda obj, name, type_, reflected, compare_to: (
            obj.schema == "public" if hasattr(obj, "schema") else False
        )
    )

    with context.begin_transaction():
        context.run_migrations()


# def create_alembic_version_table(connection):
#     connection.execute(text("""
#         CREATE TABLE IF NOT EXISTS api_testing.alembic_version (
#             version_num VARCHAR(32) NOT NULL PRIMARY KEY
#         );
#     """))
#     connection.commit()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = create_engine(_config.DATABASE_URL, poolclass=pool.NullPool)



    with connectable.connect() as connection:
        connection.execute(text(f"SET search_path TO public;"))
        connection.commit()
        # create_alembic_version_table(connection)


        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema='public',  # Ensure alembic_version is in correct schema
            version_table="alembic_version",
            include_schemas=False,  
            default_schema_name="public"
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
