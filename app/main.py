from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth_router, assinaturas_router

# Cria as tabelas no banco ao iniciar (SQLAlchemy ORM)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gestor de Assinaturas API",
    description="""
## API para gerenciamento de assinaturas e serviços recorrentes.

### Funcionalidades
- **Autenticação**: cadastro, login e recuperação de senha
- **Assinaturas**: CRUD completo (criar, listar, editar, excluir)
- **Dashboard**: resumo financeiro com gastos e vencimentos

### Como usar
1. Cadastre um usuário em `POST /auth/cadastro`
2. Faça login em `POST /auth/login` e copie o `token`
3. Use o token como query param `?token=...` nas demais rotas
    """,
    version="1.0.0",
    contact={
        "name": "Luiz Henrique Neres Santos",
        "email": "luiz@email.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os routers
app.include_router(auth_router.router)
app.include_router(assinaturas_router.router)


@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
