import os

import dotenv
from flask_caching import Cache
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

dotenv.load_dotenv()


class DatabaseConfig:
    DATABASE_NAME = os.getenv("DATABASE_NAME", "messanger_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    ROOT_DB_USER = os.getenv("DB_PASSWORD")
    ROOT_DB_PASSWORD = os.getenv("DB_USER", "postgres")

    SECRET_KEY = os.getenv("SECRET_KEY", "dsklfj")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MAX_FORM_MEMORY_SIZE = 1024 * 1024  # 1MB
    MAX_FORM_PARTS = 500  # Ліміт 500 полів

    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 30
    CACHE_KEY_PREFIX = "messnger_"

    def uri_postgres(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DATABASE_NAME}"

    def uri_sqlite(self):
        return f"sqlite:///{self.DATABASE_NAME}.db"


config = DatabaseConfig()


# ===========
cache = Cache()
 #=============

# Налаштування бази даних Postgres
# engine = create_engine(config.uri_postgres(), echo=True)
engine = create_engine(config.uri_sqlite(), echo=False)
Session = sessionmaker(bind=engine)


# Декларація базового класу для моделей, Необхідно для реалізації відношень у ORM
class Base(DeclarativeBase):
    def create_db(self):
        """
        Ініціалізація метаданих,
        створює базу даних, якщо відсутня,
        створює таблиці на основі моделей(що спадкуються від Base),
        якщо жодної немає
        """
        self.metadata.create_all(engine)

    def drop_db(self):
        """
        Деструкція метаданих,
        видаляє базу даних, якщо така наявна,
        видаляє усі таблиці
        """
        self.metadata.drop_all(engine)
