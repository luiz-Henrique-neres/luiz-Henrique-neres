"""
Testes unitários — Autenticação (RF001, RF002, RF003)
"""


class TestCadastro:
    def test_cadastro_sucesso(self, client):
        """RF002 — Cadastro com dados válidos retorna 201 e token."""
        resp = client.post("/auth/cadastro", json={
            "nome": "Maria Silva",
            "email": "maria@email.com",
            "telefone": "(11) 98888-0000",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "token" in data
        assert data["usuario"]["email"] == "maria@email.com"
        assert data["usuario"]["nome"] == "Maria Silva"

    def test_cadastro_email_duplicado(self, client, usuario_cadastrado):
        """RF002 — E-mail já cadastrado deve retornar 400."""
        resp = client.post("/auth/cadastro", json={
            "nome": "Outro",
            "email": "joao@teste.com",   # mesmo e-mail do fixture
            "telefone": "(11) 90000-0000",
            "senha": "outrasenha",
            "confirmar_senha": "outrasenha",
        })
        assert resp.status_code == 400
        assert "já cadastrado" in resp.json()["detail"]

    def test_cadastro_senhas_diferentes(self, client):
        """RF002 — Senhas divergentes devem retornar 422."""
        resp = client.post("/auth/cadastro", json={
            "nome": "Pedro",
            "email": "pedro@email.com",
            "telefone": "(11) 97777-0000",
            "senha": "abc123",
            "confirmar_senha": "xyz789",
        })
        assert resp.status_code == 422

    def test_cadastro_senha_curta(self, client):
        """RF002 — Senha com menos de 6 caracteres deve retornar 422."""
        resp = client.post("/auth/cadastro", json={
            "nome": "Ana",
            "email": "ana@email.com",
            "telefone": "(11) 96666-0000",
            "senha": "123",
            "confirmar_senha": "123",
        })
        assert resp.status_code == 422

    def test_cadastro_email_invalido(self, client):
        """RF002 — E-mail com formato inválido deve retornar 422."""
        resp = client.post("/auth/cadastro", json={
            "nome": "Carlos",
            "email": "nao-é-um-email",
            "telefone": "(11) 95555-0000",
            "senha": "senha123",
            "confirmar_senha": "senha123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_sucesso(self, client, usuario_cadastrado):
        """RF001 — Login com credenciais válidas retorna token."""
        resp = client.post("/auth/login", json={
            "email": "joao@teste.com",
            "senha": "123456",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["usuario"]["email"] == "joao@teste.com"

    def test_login_senha_errada(self, client, usuario_cadastrado):
        """RF001 — Senha incorreta deve retornar 401."""
        resp = client.post("/auth/login", json={
            "email": "joao@teste.com",
            "senha": "senhaerrada",
        })
        assert resp.status_code == 401
        assert "inválidos" in resp.json()["detail"]

    def test_login_email_inexistente(self, client):
        """RF001 — E-mail não cadastrado deve retornar 401."""
        resp = client.post("/auth/login", json={
            "email": "naoexiste@email.com",
            "senha": "qualquer",
        })
        assert resp.status_code == 401

    def test_login_campos_vazios(self, client):
        """RF001 — Campos obrigatórios ausentes devem retornar 422."""
        resp = client.post("/auth/login", json={})
        assert resp.status_code == 422


class TestRecuperarSenha:
    def test_recuperar_senha_email_valido(self, client, usuario_cadastrado):
        """RF003 — E-mail cadastrado deve retornar mensagem de sucesso."""
        resp = client.post("/auth/recuperar-senha", json={
            "email": "joao@teste.com"
        })
        assert resp.status_code == 200
        assert "enviado" in resp.json()["mensagem"].lower()

    def test_recuperar_senha_email_nao_cadastrado(self, client):
        """RF003 — E-mail não cadastrado deve retornar 404."""
        resp = client.post("/auth/recuperar-senha", json={
            "email": "fantasma@email.com"
        })
        assert resp.status_code == 404

    def test_recuperar_senha_email_invalido(self, client):
        """RF003 — E-mail com formato inválido deve retornar 422."""
        resp = client.post("/auth/recuperar-senha", json={
            "email": "isso-nao-e-email"
        })
        assert resp.status_code == 422
