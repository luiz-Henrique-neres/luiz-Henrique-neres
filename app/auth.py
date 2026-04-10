from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Armazena tokens em memória: token → usuario_id
# Em produção, use JWT ou Redis
_tokens: dict[str, str] = {}


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha."""
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    """Verifica se a senha bate com o hash armazenado."""
    return pwd_context.verify(senha, hash_)


def criar_token(usuario_id: str) -> str:
    """Gera um token único e armazena o vínculo com o usuário."""
    token = str(uuid.uuid4())
    _tokens[token] = usuario_id
    return token


def resolver_token(token: str) -> str | None:
    """Retorna o usuario_id associado ao token, ou None se inválido."""
    return _tokens.get(token)


def revogar_token(token: str) -> None:
    """Remove o token (logout)."""
    _tokens.pop(token, None)
