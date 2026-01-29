# Backend/macros_functions.py

import sqlite3
from pathlib import Path
import time
import pyautogui
import subprocess
import os
import keyboard

# ---------------------
# Conexão Global + WAL 
# ---------------------
DB_PATH = Path(__file__).resolve().parents[1] / "users.db"
CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
CONN.execute("PRAGMA journal_mode=WAL;")
CONN.execute("PRAGMA synchronous=NORMAL;")
CURSOR = CONN.cursor()

# -----------------------------
# Criar Tabelas
# -----------------------------
def criar_tabela_macros():
    CURSOR.execute('''
        CREATE TABLE IF NOT EXISTS macros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            atalho_nome TEXT,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );
    ''')

    CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS acoes_macro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            macro_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            valor TEXT NOT NULL,
            ordem INTEGER NOT NULL,
            FOREIGN KEY (macro_id) REFERENCES macros(id)
        );
    """)
    
    # Migração: Adiciona coluna atalho_nome se ela não existir
    try:
        CURSOR.execute("SELECT atalho_nome FROM     macros LIMIT 1")
    except sqlite3.OperationalError:
        # Coluna não existe, adiciona
        print("Adicionando coluna atalho_nome à tabela macros...")
        CURSOR.execute("ALTER TABLE macros ADD COLUMN atalho_nome TEXT DEFAULT ''")
        print("Coluna atalho_nome adicionada com sucesso!")

    CONN.commit()

# -----------------------------
# Inserir Macro
# -----------------------------
def inserir_macro(user_id, nome, acoes, atalho_nome=""):
    CURSOR.execute(
        "INSERT INTO macros (user_id, nome, atalho_nome) VALUES (?, ?, ?)",
        (user_id, nome, atalho_nome)
    )
    macro_id = CURSOR.lastrowid
    for idx, acao in enumerate(acoes):
        CURSOR.execute(
            "INSERT INTO acoes_macro (macro_id, tipo, valor, ordem) VALUES (?, ?, ?, ?)",
            (macro_id, acao["tipo"], acao["valor"], idx)
        )
    CONN.commit()
    return macro_id

# -----------------------------
# Obter macros e ações
# -----------------------------
def obter_macros_por_usuario(user_id):
    criar_tabela_macros()
    CURSOR.execute(
        "SELECT id, nome, atalho_nome FROM macros WHERE user_id = ?",
        (user_id,)
    )
    macros = CURSOR.fetchall()
    resultado = []
    for macro_id, nome, atalho_nome in macros:
        CURSOR.execute(
            "SELECT tipo, valor FROM acoes_macro WHERE macro_id = ? ORDER BY ordem",
            (macro_id,)
        )
        acoes = CURSOR.fetchall()
        resultado.append({
            "id": macro_id,
            "nome": nome,
            "atalho_nome": atalho_nome or "",
            "acoes": [{"tipo": tipo, "valor": valor} for tipo, valor in acoes]
        })
    return resultado

# -----------------------------
# Atualizar Macro
# -----------------------------
def atualizar_macro(macro_id, nome, acoes, atalho_nome=""):
    CURSOR.execute(
        "UPDATE macros SET nome = ?, atalho_nome = ? WHERE id = ?",
        (nome, atalho_nome, macro_id)
    )
    CURSOR.execute("DELETE FROM acoes_macro WHERE macro_id = ?", (macro_id,))
    for idx, acao in enumerate(acoes):
        CURSOR.execute(
            "INSERT INTO acoes_macro (macro_id, tipo, valor, ordem) VALUES (?, ?, ?, ?)",
            (macro_id, acao["tipo"], acao["valor"], idx)
        )
    CONN.commit()

# -----------------------------
# Excluir Macro
# -----------------------------
def excluir_macro(macro_id):
    CURSOR.execute("DELETE FROM acoes_macro WHERE macro_id = ?", (macro_id,))
    CURSOR.execute("DELETE FROM macros WHERE id = ?", (macro_id,))
    CONN.commit()

# --- Configurações de Repetição de Teclado ---
REPETITION_DELAY = 0
REPETITION_INTERVAL = 0

def execute_macro(acoes, macros_salvos=None, loop_count=1):
    pressed_keys = {}
    i = 0
    while i < len(acoes):
        acao = acoes[i]
        tipo = acao["tipo"]
        valor = acao["valor"]

        
        if tipo == "DELAY":
            try:
                delay_seconds = float(valor.rstrip('s'))
                start_time = time.time()
                end_time = start_time + delay_seconds
                keys_to_repeat = list(pressed_keys.keys())
                time_spent = 0.0
                if keys_to_repeat:
                    sleep_until_repeat = min(REPETITION_DELAY, delay_seconds)
                    time.sleep(sleep_until_repeat)
                    time_spent += sleep_until_repeat
                    while time.time() < end_time:
                        for key in keys_to_repeat:
                            pyautogui.press(key)
                        remaining_time = end_time - time.time()
                        if remaining_time > 0:
                            wait_time = min(REPETITION_INTERVAL, remaining_time)
                            time.sleep(wait_time)
                            time_spent += wait_time
                else:
                    time.sleep(delay_seconds)
                    time_spent = delay_seconds
                for key in pressed_keys:
                    pressed_keys[key] += time_spent
            except ValueError:
                print(f"Erro: Valor de delay inválido: {valor}")

        elif tipo == "KEYBOARD FUNCTION":
            if "PRESS:" in valor:
                tecla = valor.split(": ")[1]
                pyautogui.keyDown(tecla)
                pressed_keys[tecla] = 0.0
            elif "RELEASE:" in valor:
                tecla = valor.split(": ")[1]
                if tecla in pressed_keys:
                    pyautogui.keyUp(tecla)
                    del pressed_keys[tecla]
                else:
                    print(f"Aviso: Tentativa de RELEASE da tecla '{tecla}' que não está pressionada.")

        elif tipo == "MOUSE FUNCTION":
            if valor == "Clique esquerdo":
                pyautogui.click(button='left')
            elif valor == "Clique direito":
                pyautogui.click(button='right')
            elif valor == "Clique do meio":
                pyautogui.click(button='middle')
            elif valor == "Botão lateral 1":
                pyautogui.click(button='x')
            elif valor == "Botão lateral 2":
                pyautogui.click(button='x2')
            else:
                print(f"Botão do mouse desconhecido: {valor}")

        elif tipo == "MACRO":
            if macros_salvos:
                for macro in macros_salvos:
                    if macro["nome"] == valor:
                        execute_macro(macro["acoes"], macros_salvos)
                        break
                else:
                    print(f"Macro não encontrada: {valor}")

        elif tipo == "SAVE POSITION":
            try:
                pos_str = valor.split("Posição ")[1]
                x, y = eval(pos_str)
                pyautogui.moveTo(x, y)
            except Exception as e:
                print(f"Erro ao mover para posição: {e}")

        elif tipo == "TEXT FUNCTION":
            pyautogui.write(valor)

        elif tipo == "LOOP":
            if valor == "END":
                pass
            else:
                try:
                    ciclos = int(valor.split()[0])
                    end_idx = None
                    loop_depth = 0
                    for j in range(i + 1, len(acoes)):
                        if acoes[j]["tipo"] == "LOOP":
                            if acoes[j]["valor"] == "END":
                                if loop_depth == 0:
                                    end_idx = j
                                    break
                                else:
                                    loop_depth -= 1
                            else:
                                loop_depth += 1
                    if end_idx:
                        loop_acoes = acoes[i+1:end_idx]
                        for _ in range(ciclos):
                            execute_macro(loop_acoes, macros_salvos)
                        i = end_idx
                    else:
                        print("Erro: LOOP sem END correspondente")
                except ValueError:
                    print(f"Erro: Valor de loop inválido: {valor}")

        elif tipo == "ATALHO":
            from Backend.atalhos_functions import executar_atalho
            executar_atalho(int(valor))

        else:
            print(f"Tipo de ação desconhecido: {tipo}")

        i += 1


# ---------------------------
# HOTKEYS GLOBAIS PARA MACROS
# ---------------------------

PLACEHOLDER_TEXT_MACRO = "Pressione as teclas para o hotkey..."

def registrar_hotkeys_macros(macros_globais):
    #Registra hotkeys globais para todas as macros
    try:
        if hasattr(keyboard, 'unhook_all_hotkeys'):
            keyboard.unhook_all_hotkeys()
        else:
            keyboard.unhook_all()
    except (AttributeError, Exception):
        print("Aviso: Falha ao limpar hotkeys existentes de macros.")
    
    for macro in macros_globais:
        atalho_nome = macro.get("atalho_nome", "")
        macro_id = macro["id"]
        
        # Pula hotkeys inválidas (vazias ou placeholder)
        if not atalho_nome or atalho_nome.strip() == "" or atalho_nome == PLACEHOLDER_TEXT_MACRO:
            print(f"Aviso: Macro ID {macro_id} ('{atalho_nome}') ignorada, pois o hotkey é inválido ou não foi definido.")
            continue
        
        # Converte Meta para cmd (para a biblioteca keyboard)
        hotkey_str = atalho_nome.lower().replace("meta", "cmd")
        
        try:
            keyboard.add_hotkey(hotkey_str, lambda id=macro_id: executar_macro_callback(id))
            print(f"Hotkey de macro registrado: {hotkey_str} -> Macro ID {macro_id}")
        except ValueError:
            print(f"Erro: Hotkey '{hotkey_str}' inválido ou reservado pelo OS para Macro ID {macro_id}.")
        except Exception as ex:
            print(f"Erro inesperado ao registrar hotkey de macro: {ex}")


def executar_macro_callback(macro_id):
    #Callback executado quando um hotkey global de macro é pressionado
    try:
        # Busca as ações da macro em acoes_macro
        CURSOR.execute(
            "SELECT tipo, valor FROM acoes_macro WHERE macro_id = ? ORDER BY ordem",
            (macro_id,)
        )
        acoes_list = CURSOR.fetchall()
        acoes = [{"tipo": tipo, "valor": valor} for tipo, valor in acoes_list]
        
        if acoes:
            execute_macro(acoes, None)
            print(f"Macro ID {macro_id} executada via hotkey global com sucesso!")
        else:
            print(f"Aviso: Macro ID {macro_id} não tem ações associadas.")
    except Exception as ex:
        print(f"Erro ao executar macro {macro_id} via hotkey: {ex}")


def carregar_macros_globais(ID_usuario):
    #Carrega macros do usuário e registra seus hotkeys globais
    macros_db = obter_macros_por_usuario(ID_usuario)
    macros_globais = [{"atalho_nome": m.get("atalho_nome", ""), "id": m["id"]} for m in macros_db]
    registrar_hotkeys_macros(macros_globais)
    print(f"Macros globais carregadas e hotkeys registrados: {[m['id'] for m in macros_globais if m['atalho_nome']]}")