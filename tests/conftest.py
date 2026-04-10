import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Banco de dados separado só para testes (em memória)
TEST_DATABASE_URL = "sqlite:///./test_gestor.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


# Substitui a dependência real pelo banco de teste
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Cria as tabelas antes de cada teste e apaga depois."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_cadastrado(client):
    """Cria um usuário e retorna os dados + token."""
    resp = client.post("/auth/cadastro", json={
        "nome": "João Teste",
        "email": "joao@teste.com",
        "telefone": "(11) 99999-0000",
        "senha": "123456",
        "confirmar_senha": "123456",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def token(usuario_cadastrado):
    """Retorna apenas o token do usuário de teste."""
    return usuario_cadastrado["token"]
