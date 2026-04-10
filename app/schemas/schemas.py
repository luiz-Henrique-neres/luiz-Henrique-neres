from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

    model_config = {"json_schema_extra": {
        "example": {"email": "joao@email.com", "senha": "123456"}
    }}


class CadastroRequest(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    senha: str
    confirmar_senha: str

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("A senha deve ter ao menos 6 caracteres.")
        return v

    @field_validator("confirmar_senha")
    @classmethod
    def senhas_coincidem(cls, v: str, info) -> str:
        if "senha" in info.data and v != info.data["senha"]:
            raise ValueError("As senhas não coincidem.")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "nome": "João Silva",
            "email": "joao@email.com",
            "telefone": "(11) 99999-0000",
            "senha": "123456",
            "confirmar_senha": "123456",
        }
    }}


class RecuperarSenhaRequest(BaseModel):
    email: EmailStr


class UsuarioResponse(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    usuario: UsuarioResponse


# ─── Assinaturas ──────────────────────────────────────────────────────────────

class AssinaturaCreate(BaseModel):
    nome: str
    categoria: str
    valor: float
    vencimento: date

    @field_validator("valor")
    @classmethod
    def valor_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "nome": "Netflix",
            "categoria": "Streaming",
            "valor": 55.90,
            "vencimento": "2025-11-15",
        }
    }}


class AssinaturaUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    valor: Optional[float] = None
    vencimento: Optional[date] = None
    ativa: Optional[bool] = None

    @field_validator("valor")
    @classmethod
    def valor_positivo(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        return v


class AssinaturaResponse(BaseModel):
    id: str
    nome: str
    categoria: str
    valor: float
    vencimento: date
    ativa: bool
    usuario_id: str

    model_config = {"from_attributes": True}


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    gasto_mensal: float
    gasto_anual: float
    total_ativas: int
    proximos_vencimentos: list[AssinaturaResponse]
