import sqlite3
from hashlib import sha256
from pathlib import Path

# Caminho do banco de dados
DB_PATH = Path(__file__).resolve().parents[1] / "users.db"

# -----------------------------
# Conexão global otimizada
# -----------------------------
CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
CONN.execute("PRAGMA journal_mode=WAL;")     # aumenta desempenho
CONN.execute("PRAGMA synchronous=NORMAL;")   # menos bloqueios
CURSOR = CONN.cursor()


# -----------------------------
# Criar tabela
# -----------------------------
def criar_tabela():
    CURSOR.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    CONN.commit()


# -----------------------------
# Criar usuário
# -----------------------------
def criar_usuario(nome, email, senha, confirmar_senha):
    # Validar campos obrigatórios
    if not nome or not nome.strip():
        print("Nome é obrigatório!")
        return False

    if not email or not email.strip():
        print("Email é obrigatório!")
        return False
    
    if not senha or not senha.strip():
        print("Senha é obrigatória!")
        return False
    
    if not confirmar_senha or not confirmar_senha.strip():
        print("Confirmação de senha é obrigatória!")
        return False
    
    if len(senha) < 3:
        print("Senha deve ter no mínimo 3 caracteres!")
        return False
    
    if senha != confirmar_senha:
        print("Senhas não coincidem!")
        return False

    senha_hash = sha256(senha.encode()).hexdigest()

    try:
        CURSOR.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
            (nome, email, senha_hash)
        )
        CONN.commit()
        return True
    except sqlite3.IntegrityError:
        print("Email já existe!")
        return False


# -----------------------------
# Atualizar usuário
# -----------------------------
def atualizar_usuario(novo_nome, novo_email, senha, email_original):

    if senha:
        senha_hash = sha256(senha.encode()).hexdigest()
        CURSOR.execute("""
            UPDATE usuarios SET nome=?, email=?, senha=?
            WHERE email=?
        """, (novo_nome, novo_email, senha_hash, email_original))
    else:
        CURSOR.execute("""
            UPDATE usuarios SET nome=?, email=?
            WHERE email=?
        """, (novo_nome, novo_email, email_original))

    CONN.commit()


# -----------------------------
# Deletar usuário
# -----------------------------
def deletar_usuario(email):
    CURSOR.execute('DELETE FROM usuarios WHERE email=?', (email,))
    CONN.commit()


# -----------------------------
# Login
# -----------------------------
def login(email, senha):
    senha_hash = sha256(senha.encode()).hexdigest()

    CURSOR.execute(
        'SELECT * FROM usuarios WHERE email=? AND senha=?',
        (email, senha_hash)
    )
    return CURSOR.fetchone() is not None


# -----------------------------
# Obter informações
# -----------------------------
def obter_informacoes(email):
    CURSOR.execute("SELECT nome, email, senha FROM usuarios WHERE email=?", (email,))
    return CURSOR.fetchone()  # (nome, email, senha_hash)


# -----------------------------
# Obter ID
# -----------------------------
def obter_id_usuario(email):
    CURSOR.execute("SELECT id FROM usuarios WHERE email=?", (email,))
    r = CURSOR.fetchone()
    return r[0] if r else None


# -----------------------------
# Testes
# -----------------------------
if __name__ == "__main__":
    criar_tabela()
    print("Criando usuário...")
    criar_usuario("samuel", "samuel@example.com", "123", "123")
    print("Login correto:", login("samuel@example.com", "123"))
    print("Login errado:", login("samuel@example.com", "999"))
