import sqlite3
from pathlib import Path
import os
import webbrowser
import pyautogui as ag

# -----------------------------------
# Conexão Global + WAL (super rápido)
# -----------------------------------
DB_PATH = Path(__file__).resolve().parents[1] / "users.db"
CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
CONN.execute("PRAGMA journal_mode=WAL;")
CONN.execute("PRAGMA synchronous=NORMAL;")
CURSOR = CONN.cursor()

executando_atalho = False


# -----------------------------
# Criar Tabelas
# -----------------------------
def criar_tabela_atalhos():

    CURSOR.execute('''
        CREATE TABLE IF NOT EXISTS atalhos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            atalho_nome TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );
    ''')

    CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS destinos_atalho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atalho_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            destino TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (atalho_id) REFERENCES atalhos(id)
        );
    """)

    CONN.commit()


# -----------------------------
# Inserir Atalho
# -----------------------------
def inserir_atalho(user_id, nome, atalho_nome):
    CURSOR.execute(
        "INSERT INTO atalhos (user_id, nome, atalho_nome) VALUES (?, ?, ?)",
        (user_id, nome, atalho_nome)
    )
    CONN.commit()
    return CURSOR.lastrowid


# -----------------------------
# Inserir Destino
# -----------------------------
def inserir_destino(atalho_id, tipo, destino, quantidade):
    CURSOR.execute(
        "INSERT INTO destinos_atalho (atalho_id, tipo, destino, quantidade) VALUES (?, ?, ?, ?)",
        (atalho_id, tipo, destino, quantidade)
    )
    CONN.commit()


# -----------------------------
# Excluir Atalho
# -----------------------------
def excluir_atalho(atalho_id):

    CURSOR.execute("DELETE FROM destinos_atalho WHERE atalho_id = ?", (atalho_id,))
    CURSOR.execute("DELETE FROM atalhos WHERE id = ?", (atalho_id,))
    CONN.commit()


# -----------------------------
# Obter atalhos e destinos
# -----------------------------
def obter_atalhos_por_usuario(user_id):

    CURSOR.execute(
        "SELECT id, nome, atalho_nome FROM atalhos WHERE user_id = ?",
        (user_id,)
    )
    atalhos = CURSOR.fetchall()

    resultado = []

    for atalho_id, nome, atalho_nome in atalhos:

        CURSOR.execute(
            "SELECT tipo, destino, quantidade FROM destinos_atalho WHERE atalho_id = ?",
            (atalho_id,)
        )
        destinos = CURSOR.fetchall()

        resultado.append({
            "id": atalho_id,
            "nome": nome,
            "atalho_nome": atalho_nome,
            "destinos": [
                {"tipo": tipo, "destino": destino, "quantidade": quantidade}
                for (tipo, destino, quantidade) in destinos
            ]
        })

    return resultado


# -----------------------------
# Atualizar atalho
# -----------------------------
def atualizar_atalho(atalho_id, nome, atalho_nome):

    CURSOR.execute(
        "UPDATE atalhos SET nome = ?, atalho_nome = ? WHERE id = ?",
        (nome, atalho_nome, atalho_id)
    )
    CONN.commit()


# -----------------------------
# Deletar destinos por atalho
# -----------------------------
def deletar_destinos_por_atalho(atalho_id):
    CURSOR.execute("DELETE FROM destinos_atalho WHERE atalho_id = ?", (atalho_id,))
    CONN.commit()


# -----------------------------
# Executar Atalho
# -----------------------------
def executar_atalho(atalho_id):
    global executando_atalho

    if executando_atalho:
        return

    executando_atalho = True

    CURSOR.execute(
        "SELECT tipo, destino, quantidade FROM destinos_atalho WHERE atalho_id = ?",
        (atalho_id,)
    )
    destinos = CURSOR.fetchall()

    try:
        for tipo, destino, quantidade in destinos:
            for _ in range(quantidade):
                if tipo == "Caminho":
                    os.startfile(destino)
                    ag.sleep(0.5)

                elif tipo == "Site":
                    webbrowser.open(destino, new=2)
                    ag.sleep(0.5)

        print("Atalho executado com sucesso.")

    except Exception as ex:
        print(f"Erro em executar_atalho: {ex}")

    finally:
        executando_atalho = False
        print("Listener reativado após execução.")


# -----------------------------
# Teste
# -----------------------------
if __name__ == "__main__":
    criar_tabela_atalhos()
