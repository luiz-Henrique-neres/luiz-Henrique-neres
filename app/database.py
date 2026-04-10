from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator

# SQLite local — troque pela URL do seu banco em produção
# Ex PostgreSQL: "postgresql://user:senha@localhost/gestor_db"
DATABASE_URL = "sqlite:///./gestor_assinaturas.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # necessário para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency que fornece uma sessão do banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
