from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import (
    LoginRequest, LoginResponse, CadastroRequest,
    RecuperarSenhaRequest, UsuarioResponse,
)
from app.auth import hash_senha, verificar_senha, criar_token
import uuid

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autenticar usuário",
    description="Recebe e-mail e senha, retorna token de acesso e dados do usuário.",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == body.email).first()
    if not usuario or not verificar_senha(body.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )
    token = criar_token(usuario.id)
    return {"token": token, "usuario": usuario}


@router.post(
    "/cadastro",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    description="Cria uma nova conta. E-mail deve ser único. Retorna token de acesso.",
)
def cadastro(body: CadastroRequest, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado.",
        )
    novo = Usuario(
        id=str(uuid.uuid4()),
        nome=body.nome,
        email=body.email,
        telefone=body.telefone,
        senha_hash=hash_senha(body.senha),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    token = criar_token(novo.id)
    return {"token": token, "usuario": novo}


@router.post(
    "/recuperar-senha",
    summary="Solicitar recuperação de senha",
    description="Verifica se o e-mail está cadastrado e simula o envio do link de recuperação.",
)
def recuperar_senha(body: RecuperarSenhaRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == body.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="E-mail não encontrado.",
        )
    # Em produção: disparar e-mail com link JWT de redefinição
    return {"mensagem": f"Link de recuperação enviado para {body.email}."}
