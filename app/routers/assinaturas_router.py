from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Assinatura, Usuario
from app.schemas.schemas import (
    AssinaturaCreate, AssinaturaUpdate, AssinaturaResponse, DashboardResponse,
)
from app.auth import resolver_token
import uuid

router = APIRouter(tags=["Assinaturas"])


def _get_usuario(token: str, db: Session) -> Usuario:
    """Valida o token e retorna o usuário autenticado."""
    usuario_id = resolver_token(token)
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    return usuario


def _get_assinatura(assinatura_id: str, usuario: Usuario, db: Session) -> Assinatura:
    """Busca assinatura garantindo que pertence ao usuário autenticado."""
    a = db.query(Assinatura).filter(
        Assinatura.id == assinatura_id,
        Assinatura.usuario_id == usuario.id,
    ).first()
    if not a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinatura não encontrada.",
        )
    return a


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Resumo financeiro",
    description="Retorna gasto mensal, anual, total de assinaturas ativas e próximos vencimentos.",
)
def dashboard(token: str, db: Session = Depends(get_db)):
    usuario = _get_usuario(token, db)
    ativas = db.query(Assinatura).filter(
        Assinatura.usuario_id == usuario.id,
        Assinatura.ativa == True,
    ).all()

    gasto_mensal = sum(a.valor for a in ativas)
    proximas = sorted(ativas, key=lambda a: a.vencimento)[:3]

    return {
        "gasto_mensal": round(gasto_mensal, 2),
        "gasto_anual": round(gasto_mensal * 12, 2),
        "total_ativas": len(ativas),
        "proximos_vencimentos": proximas,
    }


# ─── CRUD Assinaturas ─────────────────────────────────────────────────────────

@router.get(
    "/assinaturas",
    response_model=List[AssinaturaResponse],
    summary="Listar assinaturas",
    description="Retorna todas as assinaturas do usuário autenticado.",
)
def listar(token: str, db: Session = Depends(get_db)):
    usuario = _get_usuario(token, db)
    return db.query(Assinatura).filter(
        Assinatura.usuario_id == usuario.id
    ).all()


@router.get(
    "/assinaturas/{assinatura_id}",
    response_model=AssinaturaResponse,
    summary="Detalhar assinatura",
)
def detalhar(assinatura_id: str, token: str, db: Session = Depends(get_db)):
    usuario = _get_usuario(token, db)
    return _get_assinatura(assinatura_id, usuario, db)


@router.post(
    "/assinaturas",
    response_model=AssinaturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar assinatura",
    description="Adiciona uma nova assinatura para o usuário autenticado.",
)
def criar(body: AssinaturaCreate, token: str, db: Session = Depends(get_db)):
    usuario = _get_usuario(token, db)
    nova = Assinatura(
        id=str(uuid.uuid4()),
        nome=body.nome,
        categoria=body.categoria,
        valor=body.valor,
        vencimento=body.vencimento,
        ativa=True,
        usuario_id=usuario.id,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.put(
    "/assinaturas/{assinatura_id}",
    response_model=AssinaturaResponse,
    summary="Editar assinatura",
    description="Atualiza os campos informados da assinatura.",
)
def editar(
    assinatura_id: str,
    body: AssinaturaUpdate,
    token: str,
    db: Session = Depends(get_db),
):
    usuario = _get_usuario(token, db)
    a = _get_assinatura(assinatura_id, usuario, db)

    # Atualiza apenas os campos enviados (PATCH semântico via PUT)
    dados = body.model_dump(exclude_unset=True)
    for campo, valor in dados.items():
        setattr(a, campo, valor)

    db.commit()
    db.refresh(a)
    return a


@router.delete(
    "/assinaturas/{assinatura_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir assinatura",
    description="Remove permanentemente a assinatura do banco de dados.",
)
def deletar(assinatura_id: str, token: str, db: Session = Depends(get_db)):
    usuario = _get_usuario(token, db)
    a = _get_assinatura(assinatura_id, usuario, db)
    db.delete(a)
    db.commit()
