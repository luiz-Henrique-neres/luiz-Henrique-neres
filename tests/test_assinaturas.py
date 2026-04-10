"""
Testes unitários — Assinaturas (RF005, RF007) e Dashboard
"""

ASSINATURA_VALIDA = {
    "nome": "Netflix",
    "categoria": "Streaming",
    "valor": 55.90,
    "vencimento": "2025-11-15",
}


def _criar(client, token, dados=None):
    """Helper: cria uma assinatura e retorna o JSON."""
    resp = client.post(
        f"/assinaturas?token={token}",
        json=dados or ASSINATURA_VALIDA,
    )
    assert resp.status_code == 201
    return resp.json()


class TestCriarAssinatura:
    def test_criar_sucesso(self, client, token):
        """RF005 — Criação com dados válidos retorna 201."""
        resp = client.post(f"/assinaturas?token={token}", json=ASSINATURA_VALIDA)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nome"] == "Netflix"
        assert data["valor"] == 55.90
        assert data["ativa"] is True

    def test_criar_sem_token(self, client):
        """RF005 — Requisição sem token deve retornar 401."""
        resp = client.post("/assinaturas?token=invalido", json=ASSINATURA_VALIDA)
        assert resp.status_code == 401

    def test_criar_valor_zero(self, client, token):
        """RF005 — Valor igual a zero deve retornar 422."""
        resp = client.post(f"/assinaturas?token={token}", json={
            **ASSINATURA_VALIDA, "valor": 0
        })
        assert resp.status_code == 422

    def test_criar_valor_negativo(self, client, token):
        """RF005 — Valor negativo deve retornar 422."""
        resp = client.post(f"/assinaturas?token={token}", json={
            **ASSINATURA_VALIDA, "valor": -10
        })
        assert resp.status_code == 422

    def test_criar_sem_nome(self, client, token):
        """RF005 — Nome ausente deve retornar 422."""
        dados = {k: v for k, v in ASSINATURA_VALIDA.items() if k != "nome"}
        resp = client.post(f"/assinaturas?token={token}", json=dados)
        assert resp.status_code == 422


class TestListarAssinaturas:
    def test_listar_vazia(self, client, token):
        """RF007 — Lista vazia para usuário sem assinaturas."""
        resp = client.get(f"/assinaturas?token={token}")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_com_itens(self, client, token):
        """RF007 — Lista retorna assinaturas criadas."""
        _criar(client, token)
        _criar(client, token, {**ASSINATURA_VALIDA, "nome": "Spotify", "valor": 21.90})
        resp = client.get(f"/assinaturas?token={token}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_listar_isolamento_entre_usuarios(self, client, token):
        """RF005 — Usuário só vê suas próprias assinaturas."""
        _criar(client, token)

        # Cria segundo usuário
        resp2 = client.post("/auth/cadastro", json={
            "nome": "Outro",
            "email": "outro@email.com",
            "telefone": "(11) 91111-1111",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        })
        token2 = resp2.json()["token"]

        resp = client.get(f"/assinaturas?token={token2}")
        assert resp.status_code == 200
        assert resp.json() == []


class TestDetalharAssinatura:
    def test_detalhar_sucesso(self, client, token):
        """RF005 — Detalha assinatura existente."""
        criada = _criar(client, token)
        resp = client.get(f"/assinaturas/{criada['id']}?token={token}")
        assert resp.status_code == 200
        assert resp.json()["id"] == criada["id"]

    def test_detalhar_nao_encontrado(self, client, token):
        """RF005 — ID inexistente deve retornar 404."""
        resp = client.get(f"/assinaturas/id-falso?token={token}")
        assert resp.status_code == 404


class TestEditarAssinatura:
    def test_editar_sucesso(self, client, token):
        """RF005 — Editar campos válidos retorna dados atualizados."""
        criada = _criar(client, token)
        resp = client.put(
            f"/assinaturas/{criada['id']}?token={token}",
            json={"valor": 75.90, "ativa": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["valor"] == 75.90
        assert data["ativa"] is False
        assert data["nome"] == "Netflix"   # não alterado

    def test_editar_nao_encontrado(self, client, token):
        """RF005 — Editar ID inexistente deve retornar 404."""
        resp = client.put(
            f"/assinaturas/id-falso?token={token}",
            json={"valor": 10.0},
        )
        assert resp.status_code == 404

    def test_editar_sem_token(self, client, token):
        """RF005 — Editar sem token válido deve retornar 401."""
        criada = _criar(client, token)
        resp = client.put(
            f"/assinaturas/{criada['id']}?token=invalido",
            json={"valor": 10.0},
        )
        assert resp.status_code == 401


class TestDeletarAssinatura:
    def test_deletar_sucesso(self, client, token):
        """RF005 — Deletar assinatura existente retorna 204."""
        criada = _criar(client, token)
        resp = client.delete(f"/assinaturas/{criada['id']}?token={token}")
        assert resp.status_code == 204

        # Confirma que sumiu
        resp2 = client.get(f"/assinaturas/{criada['id']}?token={token}")
        assert resp2.status_code == 404

    def test_deletar_nao_encontrado(self, client, token):
        """RF005 — Deletar ID inexistente deve retornar 404."""
        resp = client.delete(f"/assinaturas/id-falso?token={token}")
        assert resp.status_code == 404


class TestDashboard:
    def test_dashboard_vazio(self, client, token):
        """Dashboard sem assinaturas retorna zeros."""
        resp = client.get(f"/dashboard?token={token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["gasto_mensal"] == 0.0
        assert data["gasto_anual"] == 0.0
        assert data["total_ativas"] == 0

    def test_dashboard_com_assinaturas(self, client, token):
        """Dashboard calcula gasto mensal e anual corretamente."""
        _criar(client, token, {**ASSINATURA_VALIDA, "valor": 55.90})
        _criar(client, token, {**ASSINATURA_VALIDA, "nome": "Spotify", "valor": 21.90})

        resp = client.get(f"/dashboard?token={token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["gasto_mensal"] == round(55.90 + 21.90, 2)
        assert data["gasto_anual"] == round((55.90 + 21.90) * 12, 2)
        assert data["total_ativas"] == 2
        assert len(data["proximos_vencimentos"]) <= 3

    def test_dashboard_token_invalido(self, client):
        """Dashboard com token inválido deve retornar 401."""
        resp = client.get("/dashboard?token=token-falso")
        assert resp.status_code == 401
