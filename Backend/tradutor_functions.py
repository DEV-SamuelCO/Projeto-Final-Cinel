# Backend/tradutor_functions.py
import sqlite3
from pathlib import Path
import tkinter as tk
from PIL import Image
import pyautogui
import os
import pytesseract
import time
from google import genai 
from google.genai import types

pytesseract.pytesseract.tesseract_cmd = r'C:\Pytesseract\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = r'C:\programacao\tesseract\tesseract.exe'

# -----------------------------------
# Conexão Global + WAL (super rápido)
# -----------------------------------
DB_PATH = Path(__file__).resolve().parents[1] / "users.db"
CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
CONN.execute("PRAGMA journal_mode=WAL;")
CONN.execute("PRAGMA synchronous=NORMAL;")
CURSOR = CONN.cursor()

# Flag global para cancelar seleção de tela
CANCEL_SELECTION = False

def cancel_selection():
    """Sinaliza para cancelar qualquer seleção em andamento."""
    global CANCEL_SELECTION
    CANCEL_SELECTION = True

def clear_cancel_selection():
    """Limpa o sinal de cancelamento antes de iniciar nova seleção."""
    global CANCEL_SELECTION
    CANCEL_SELECTION = False


# -----------------------------
# Criar Tabelas
# -----------------------------
def criar_tabela_macros():
    CURSOR.execute('''
        CREATE TABLE IF NOT EXISTS Atalho_Translator(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            atalho_nome TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usuarios(id)
        );
    ''')

    CONN.commit()

# -----------------------------
# Inserir Atalho de Tradutor Padrao
# -----------------------------
def inserir_atalho(user_id, atalho_nome):
    CURSOR.execute(
        "INSERT INTO Atalho_Translator (user_id, atalho_nome) VALUES (?, ?)",
        (user_id, atalho_nome)
    )
    CONN.commit()
    return CURSOR.lastrowid


# -----------------------------
# Atualizar Atalho de Tradutor
# -----------------------------

def atualizar_atalho(user_id, atalho_nome):
    CURSOR.execute(
        "UPDATE Atalho_Translator SET atalho_nome = ? WHERE user_id = ?",
        (atalho_nome, user_id)
    )
    CONN.commit()

# -----------------------------
# Obter Atalho de Tradutor
# -----------------------------
def obter_atalho(user_id):
    CURSOR.execute(
        "SELECT atalho_nome FROM Atalho_Translator WHERE user_id = ?",
        (user_id,)
    )
    resultado = CURSOR.fetchone()
    return resultado[0] if resultado else None




GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def traduzir_texto_gemini(texto_original: str, de_lang: str = 'inglês', para_lang: str = 'português') -> str:
    """Traduz um texto usando o modelo Gemini, mantendo o contexto."""
    if not texto_original or texto_original.strip() == "":
        return "Nenhum texto válido fornecido para o Gemini."


    prompt = f"""
    Você é um tradutor profissional, especializado em tradução de mangás e quadrinhos, onde o contexto é crucial.
    Traduza o texto a seguir de {de_lang} para {para_lang}.
    Se o texto for curto (como uma onomatopeia ou uma única palavra), traduza de forma apropriada e contextualizada.
    Sua resposta deve conter APENAS a tradução.

    TEXTO ORIGINAL ({de_lang.upper()}):
    ---
    {texto_original}
    ---
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        traducao = response.text.strip()
        return traducao
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "Erro: Limite de requisições da API Gemini excedido (quota gratuita: 20/dia). Tente novamente amanhã ou verifique seu plano em https://ai.google.dev/aistudio."
        else:
            return f"Erro ao acessar o Gemini: {error_msg}"

class ScreenSelector:
    #Uma classe para permitir ao usuário selecionar uma área da tela e retornar a imagem recortada.

    def __init__(self):
        self.root = None
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 0, 0
        self.rect_id = None
        self.canvas = None
        self.screen_shot = None
        self.selection_done = False
        
    def start_selection(self):
        # Inicia o processo de seleção de área na tela e retorna o texto extraído via OCR
        # Optei por utilizar o Tkinter para a seleção de área devido à sua simplicidade e por estar mais familiarizado com ele.
        
        #Inicializa a interface de seleção de área.
        self.root = tk.Tk()
        self.root.withdraw()

        # Cria janela de seleção em tela cheia
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-fullscreen', True)
        # autera transparência e mantém a janela no topo
        self.selection_window.attributes('-alpha', 0.3)
        self.selection_window.attributes('-topmost', True)
        
        # Bindings para eventos
        self.selection_window.bind('<Escape>', self._on_cancel)
        self.selection_window.protocol("WM_DELETE_WINDOW", self._on_cancel) 

        # Cria canvas para desenhar a seleção
        self.canvas = tk.Canvas(self.selection_window, cursor="cross", bg='grey')
        self.canvas.pack(fill="both", expand=True)

        # Bindings do mouse
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)
        
        
        try:
            clear_cancel_selection()
        except Exception:
            pass

        # checa periodicamente se houve pedido de cancelamento vindo de outra thread
        def _check_cancel():
            global CANCEL_SELECTION
            try:
                if CANCEL_SELECTION and not self.selection_done:
                    self._on_cancel()
                elif not self.selection_done and self.selection_window.winfo_exists():
                    # agenda nova checagem
                    self.selection_window.after(100, _check_cancel)
            except Exception:
                pass

        self.selection_window.focus_force()
        try:
            self.selection_window.after(100, _check_cancel)
            self.root.mainloop()
        except Exception as e:
            print(f"Erro durante mainloop: {e}")
        finally:
            # Cleanup agressivo no finally
            self._force_cleanup()
        
        return self._capture_and_ocr()
    
    def _force_cleanup(self):
        #Força limpeza segura de todas as janelas Tkinter.
        self.selection_done = True
        
        try:
            if self.canvas:
                self.canvas = None
        except Exception:
            pass
        
        try:
            if self.selection_window:
                self.selection_window.withdraw()
                self.selection_window.update()
                self.selection_window.destroy()
        except Exception:
            pass
        finally:
            self.selection_window = None
        
        try:
            if self.root:
                self.root.withdraw()
                self.root.update()
                self.root.destroy()
        except Exception:
            pass
        finally:
            self.root = None

    def _on_cancel(self, event=None):
        #Função chamada ao tentar fechar/cancelar a seleção.
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 0, 0
        self.selection_done = True
        
        try:
            if self.selection_window and self.selection_window.winfo_exists():
                self.selection_window.after_idle(self.selection_window.quit)
        except Exception:
            pass
        
        try:
            if self.root and self.root.winfo_exists():
                self.root.after_idle(self.root.quit)
        except Exception:
            pass
        
    def _on_button_press(self, event):
        #Salva a posição inicial do clique e remove o retângulo anterior.
        self.x1, self.y1 = event.x_root, event.y_root
        
        if self.rect_id:
            try:
                self.canvas.delete(self.rect_id)
            except Exception:
                pass
            self.rect_id = None

    def _on_mouse_drag(self, event):
        #Atualiza a posição do retângulo de seleção enquanto arrasta.
        self.x2, self.y2 = event.x_root, event.y_root
        
        if self.rect_id:
            try:
                self.canvas.delete(self.rect_id)
            except Exception:
                pass
            
        try:
            self.rect_id = self.canvas.create_rectangle(
                self.x1 - self.selection_window.winfo_x(),
                self.y1 - self.selection_window.winfo_y(),
                self.x2 - self.selection_window.winfo_x(),
                self.y2 - self.selection_window.winfo_y(),
                outline="red", width=2, dash=(3, 3)
            )
            self.canvas.update()
        except Exception:
            pass

    def _on_button_release(self, event):
        #Termina a seleção e fecha a janela.
        self.x2, self.y2 = event.x_root, event.y_root
        self.selection_done = True
        
        try:
            if self.selection_window and self.selection_window.winfo_exists():
                self.selection_window.after_idle(self.selection_window.quit)
        except Exception:
            pass
        
        try:
            if self.root and self.root.winfo_exists():
                self.root.after_idle(self.root.quit)
        except Exception:
            pass

    def _capture_and_ocr(self):
        #Captura a área selecionada e usa OCR para extrair o texto.
        
        x_min = min(self.x1, self.x2)
        y_min = min(self.y1, self.y2)
        x_max = max(self.x1, self.x2)
        y_max = max(self.y1, self.y2)
        
        # Cleanup seguro das janelas Tkinter
        try:
            if self.selection_window and self.selection_window.winfo_exists():
                self.selection_window.destroy()
        except Exception:
            pass
        
        try:
            if self.root:
                self.root.destroy()
        except Exception:
            pass
        finally:
            self.root = None
            self.selection_window = None
            
        if x_max - x_min < 10 or y_max - y_min < 10:
            return "Nenhuma área válida selecionada."

        try:
            time.sleep(0.1) 
            cropped_img = pyautogui.screenshot(region=(x_min, y_min, x_max - x_min, y_max - y_min))
            texto = pytesseract.image_to_string(cropped_img, lang='eng')
            
            return texto.strip()

        except pytesseract.TesseractNotFoundError:
            return "Erro: Tesseract não encontrado. Certifique-se de que está instalado e o caminho configurado corretamente."
        except Exception as e:
            return f"Erro ao capturar ou processar imagem: {e}"


def selecionar_area_e_extrair_texto():
    selector = ScreenSelector()
    texto_extraido = selector.start_selection()
    return texto_extraido