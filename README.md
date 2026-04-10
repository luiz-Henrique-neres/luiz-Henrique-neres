# 📊 Gestor de Assinaturas — API

API REST para gerenciamento de assinaturas e serviços recorrentes, desenvolvida com **FastAPI** e **SQLAlchemy ORM**.

> Projeto P2 — Engenharia de Software  
> FATEC Ribeirão Preto — Análise e Desenvolvimento de Sistemas  
> Desenvolvedor: Luiz Henrique Neres Santos

---

## 🚀 Tecnologias

| Tecnologia | Uso |
|---|---|
| **FastAPI** | Framework web principal |
| **SQLAlchemy** | ORM para acesso ao banco de dados |
| **SQLite** | Banco de dados (desenvolvimento) |
| **Pydantic v2** | Validação de dados e schemas |
| **Passlib + bcrypt** | Hash seguro de senhas |
| **Pytest + HTTPX** | Testes unitários |

---

## 📁 Estrutura do Projeto

```
gestor_api_p2/
├── app/
│   ├── main.py               ← Inicialização da API e routers
│   ├── database.py           ← Conexão e sessão SQLAlchemy
│   ├── auth.py               ← Hash de senha e gerenciamento de tokens
│   ├── models/
│   │   └── models.py         ← Models ORM (Usuario, Assinatura)
│   ├── schemas/
│   │   └── schemas.py        ← Schemas Pydantic (request/response)
│   └── routers/
│       ├── auth_router.py    ← Rotas de autenticação
│       └── assinaturas_router.py ← Rotas de assinaturas + dashboard
├── tests/
│   ├── conftest.py           ← Fixtures e banco de teste
│   ├── test_auth.py          ← Testes de autenticação
│   └── test_assinaturas.py   ← Testes de assinaturas e dashboard
├── requirements.txt
└── README.md
```

---

## ⚙️ Como Rodar

### 1. Clonar e instalar dependências

```bash
git clone https://github.com/seu-usuario/gestor-assinaturas-api.git
cd gestor-assinaturas-api
pip install -r requirements.txt
```

### 2. Iniciar a API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Acessar a documentação

| URL | Descrição |
|---|---|
| http://localhost:8000/docs | Swagger UI interativo |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | Schema OpenAPI (importar no APIdog) |

---

## 🧪 Testes Unitários

```bash
# Rodar todos os testes
pytest tests/ -v

# Ver cobertura resumida
pytest tests/ -v --tb=short
```

**Total de testes:** 23 casos cobrindo todos os endpoints.

| Arquivo | O que testa |
|---|---|
| `test_auth.py` | Cadastro, login e recuperação de senha |
| `test_assinaturas.py` | CRUD completo de assinaturas + dashboard |

---

## 📡 Endpoints

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/cadastro` | Criar nova conta |
| `POST` | `/auth/login` | Autenticar e obter token |
| `POST` | `/auth/recuperar-senha` | Solicitar recuperação de senha |

### Assinaturas *(requer `?token=` em todas)*

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/dashboard` | Resumo financeiro |
| `GET` | `/assinaturas` | Listar assinaturas |
| `GET` | `/assinaturas/{id}` | Detalhar assinatura |
| `POST` | `/assinaturas` | Criar assinatura |
| `PUT` | `/assinaturas/{id}` | Editar assinatura |
| `DELETE` | `/assinaturas/{id}` | Excluir assinatura |

---

## 📘 Importar no APIdog

1. Com a API rodando, acesse: `http://localhost:8000/openapi.json`
2. Copie o conteúdo JSON
3. No APIdog: **Import → OpenAPI/Swagger → Cole o JSON**
4. Todos os endpoints serão importados automaticamente com exemplos

---

## 🗄️ Modelo de Dados (ORM)

```
Usuario
  ├── id (PK, UUID)
  ├── nome
  ├── email (único)
  ├── telefone
  ├── senha_hash
  └── assinaturas → [Assinatura]

Assinatura
  ├── id (PK, UUID)
  ├── nome
  ├── categoria
  ├── valor
  ├── vencimento (Date)
  ├── ativa (Boolean)
  └── usuario_id (FK → Usuario)
```

---

## 🔒 Segurança

- Senhas armazenadas com **bcrypt** (hash irreversível)
- Tokens UUID únicos por sessão
- Cada usuário acessa apenas suas próprias assinaturas
- Validação de dados com Pydantic em todas as rotas

---

## 📄 Licença

MIT © 2025 — Luiz Henrique Neres Santos
