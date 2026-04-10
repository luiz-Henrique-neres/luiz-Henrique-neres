from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import date


def gerar_uuid() -> str:
    return str(uuid.uuid4())


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=gerar_uuid)
    nome = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    senha_hash = Column(String(200), nullable=False)

    # Relacionamento: um usuário tem muitas assinaturas
    assinaturas = relationship(
        "Assinatura", back_populates="usuario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email}>"


class Assinatura(Base):
    __tablename__ = "assinaturas"

    id = Column(String, primary_key=True, default=gerar_uuid)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(60), nullable=False)
    valor = Column(Float, nullable=False)
    vencimento = Column(Date, nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)

    # Chave estrangeira para Usuario
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False, index=True)
    usuario = relationship("Usuario", back_populates="assinaturas")

    def __repr__(self) -> str:
        return f"<Assinatura id={self.id} nome={self.nome} valor={self.valor}>"
