import flet as ft
import threading
import keyboard
import sys
from pathlib import Path
import asyncio

from Backend.tradutor_functions import obter_atalho, atualizar_atalho, cancel_selection, clear_cancel_selection, inserir_atalho

sys.path.append(str(Path(__file__).resolve().parents[1])) 

COR_FUNDO = "#0D1117"
COR_PAINEL = "#161B22"
COR_TEXTO = "#E6EDF3"
COR_BORDA = "#30363D"
COR_BOTAO_ROXO = "#7E57C2"
COR_BOTAO_AZUL = "#0078FF"
COR_BOTAO_VERDE = "#00B87C" 
COR_CAIXA_TEXTO = "#22272E"
COR_PINK = "#E91E63"
COR_SECUNDARIA = COR_BOTAO_AZUL


PLACEHOLDER_TEXT = "Pressione as teclas para o atalho..." 
capturing = False
atalho_temp = ""

# ------------------------------
# FUNÇÃO SNACKBAR (REUTILIZADA)
# ------------------------------
# Mensagem de snackbar principalmente usada para erros e validações
def mostrar_snackbar(page, msg, cor="red"):
    page.snack_bar = ft.SnackBar(
        content=ft.Container(
            ft.Text(msg, color="white"),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=8,
            bgcolor=cor,
        ),
        open=True,
        duration=2000,
    )
    if page.snack_bar not in page.overlay:
        page.overlay.append(page.snack_bar)
    page.snack_bar.open = True
    page.update()

# ------------------------------
# ATALHO GLOBAL ESPECÍFICO PARA O TRADUTOR
# ------------------------------

GLOBAL_HOTKEY_REF = None 

def registrar_hotkey_tradutor(atalho_nome: str, callback_fn):
    global GLOBAL_HOTKEY_REF

    # Remove o hotkey anterior se houver
    if GLOBAL_HOTKEY_REF is not None:
        try:
            keyboard.remove_hotkey(GLOBAL_HOTKEY_REF)
        except Exception as ex:
            print(f"Aviso: Não foi possível remover o hotkey anterior: {ex}")
    GLOBAL_HOTKEY_REF = None
    
    # verifica se o atalho é válido
    if not atalho_nome or atalho_nome.strip() == "" or atalho_nome == PLACEHOLDER_TEXT:
        print("Atalho global de tradução desativado ou inválido.")
        return
    
    # Registra o novo hotkey
    hotkey_str = atalho_nome.lower().replace("meta", "cmd")
    try:
        GLOBAL_HOTKEY_REF = keyboard.add_hotkey(hotkey_str, callback_fn)
        print(f"Hotkey de tradução registrado: {hotkey_str}")
    except ValueError:
        print(f"Erro: Atalho '{hotkey_str}' inválido ou reservado pelo OS.")
        GLOBAL_HOTKEY_REF = None
    except Exception as ex:
        print(f"Erro inesperado ao registrar hotkey: {ex}")
        GLOBAL_HOTKEY_REF = None


def criar_aba_tradutor(page, ID_usuario):
    try:
        from Backend.tradutor_functions import selecionar_area_e_extrair_texto, traduzir_texto_gemini 
    except ImportError:
        def selecionar_area_e_extrair_texto():
            return "Erro: Backend (Tesseract/Seleção) indisponível."
        def traduzir_texto_gemini(texto, de_lang, para_lang):
            return f"Erro: Backend (Gemini) indisponível. Tentativa de tradução de {de_lang} para {para_lang} com o texto: '{texto[:30]}...'"
        print("Aviso: Não foi possível importar o backend. Usando funções dummy.")

    # Declarações antecipadas para referências circulares
    btn_selecionar_area_ref = None 
    btn_alterar_atalho = None 
    btn_traduzir_texto = None
    botoes_topo = None 


    inserir_atalho(ID_usuario, "ctrl+alt+t")
    ATALHO_INICIAL = obter_atalho(ID_usuario)
    if ATALHO_INICIAL is None:
        ATALHO_INICIAL = 'ctrl+alt+t'


    # --------------------------------------
    # Dicionário de Idiomas e Dropdowns (UI) 
    # --------------------------------------
    IDIOMAS = {
        "Japonês": "japonês", "Português": "português", "Inglês": "inglês",
        "Francês": "francês", "Espanhol": "espanhol", "Alemão": "alemão",
        "Russo": "russo", "Coreano": "coreano",
    }
    IDIOMA_OPTIONS = [ft.dropdown.Option(k) for k in IDIOMAS.keys()]
    
    dd_idioma_origem = ft.Dropdown(
        options=IDIOMA_OPTIONS,
        value="Inglês", width=150,
        border_color=COR_BORDA,
        text_style=ft.TextStyle(color=COR_TEXTO), 
        color=COR_TEXTO, 
    )
    
    dd_idioma_destino = ft.Dropdown(
        options=IDIOMA_OPTIONS, 
        value="Português",
        width=150, 
        border_color=COR_BORDA,
        text_style=ft.TextStyle(color=COR_TEXTO), 
        color=COR_TEXTO, 
    )
    
    campo_texto_original = ft.TextField(
        multiline=True,
        min_lines=12,
        max_lines=12,
        hint_text="Cole ou digite o texto aqui...",
        bgcolor=COR_CAIXA_TEXTO, border_radius=8,
        border_color="transparent", hint_style=ft.TextStyle(color="#CCCCCC"),
        text_style=ft.TextStyle(color="white", size=14),
        expand=True,
    )
    

    campo_texto_traduzido = ft.TextField(
        multiline=True,
        min_lines=12,
        max_lines=12,
        hint_text="A tradução aparecerá aqui...",
        bgcolor=COR_CAIXA_TEXTO,
        border_radius=8,
        border_color="transparent",
        hint_style=ft.TextStyle(color="#CCCCCC"),
        text_style=ft.TextStyle(color="white", size=14),
        expand=True,
    )

    # ------------------------------
    # FUNÇÕES DE CAPTURA DE ATALHO
    # ------------------------------
    async def ativar_captura(page, text_field):
        global capturing, atalho_temp
        desativar_captura(page) 
        capturing = True
        atalho_temp = ""
        text_field.value = PLACEHOLDER_TEXT
        text_field.update()
        
        def on_keyboard(e):
            global atalho_temp
            if not capturing:
                return
            
            modifiers = []
            if e.ctrl: modifiers.append("Ctrl")
            if e.shift: modifiers.append("Shift")
            if e.alt: modifiers.append("Alt")
            if e.meta: modifiers.append("Meta")
            
            if e.key in ["Control", "Shift", "Alt", "Meta"]:
                return

            atalho_str = "+".join(modifiers)
            if atalho_str:
                atalho_str += "+"
            # Corrige a formatação da tecla. Ex: 'a' -> 'A'
            key_name = e.key.upper() if len(e.key) == 1 else e.key
            
            # Corrige caso a tecla principal seja um modificador (ex: pressiona só Ctrl, espera a próxima tecla)
            if not modifiers and key_name in ["CONTROL", "SHIFT", "ALT", "META"]:
                return
            
            atalho_temp = atalho_str + key_name
            text_field.value = atalho_temp
            text_field.update()
            
            # Desativa e salva automaticamente
            desativar_captura(page)

            novo_atalho = atalho_temp.strip()
            if not novo_atalho or novo_atalho == PLACEHOLDER_TEXT:
                mostrar_snackbar(page, "Defina um atalho válido!", cor=COR_PINK)
                return
            
            registrar_hotkey_tradutor(novo_atalho, atalho_global_callback_sync)
            
            # Verifica se o registro foi bem-sucedido
            if GLOBAL_HOTKEY_REF is None:
                mostrar_snackbar(page, f"Erro: O atalho '{novo_atalho}' não pôde ser registrado. Tente outro.", cor=COR_PINK)
                # Volta o valor do campo para o atalho anterior
                text_field.value = btn_alterar_atalho.content.replace("Atalho OCR: ", "")
                text_field.update()  
            else:
                mostrar_snackbar(page, f"Atalho global atualizado para '{novo_atalho}'!", cor=COR_BOTAO_VERDE)
            
            btn_alterar_atalho.content = f"Atalho OCR: {novo_atalho if GLOBAL_HOTKEY_REF is not None else ATALHO_INICIAL}"
            btn_alterar_atalho.update()
            
            # Volta ao layout normal
            botoes_topo.content = ft.Row([
                btn_selecionar_area_ref,
                btn_traduzir_texto,
                btn_alterar_atalho,
                ft.Container(expand=True),
            ], alignment=ft.MainAxisAlignment.START, spacing=10)
            botoes_topo.update()
            page.update() 
            
        page.on_keyboard_event = on_keyboard
        page.update()
        
    def desativar_captura(page):
        global capturing
        if capturing:
            capturing = False
            page.on_keyboard_event = None
            page.update()

    # -----------------------------------------
    # FUNÇÕES DE CALLBACK DA TRADUÇÃO E SELEÇÃO
    # -----------------------------------------

    # Função para executar a tradução normal (clique no botão 'Traduzir Texto')
    def on_traduzir_click(e, texto_original_ref, dd_origem_ref, dd_destino_ref, campo_traduzido_ref):
        texto_a_traduzir = texto_original_ref.value
        idioma_origem = IDIOMAS[dd_origem_ref.value]
        idioma_destino = IDIOMAS[dd_destino_ref.value]

        if not texto_a_traduzir or texto_a_traduzir.strip() == "":
            campo_traduzido_ref.value = "Nenhum texto para traduzir."
            campo_traduzido_ref.update()
            return
            
        campo_traduzido_ref.value = f"Traduzindo de {idioma_origem.capitalize()} para {idioma_destino.capitalize()} com Gemini, aguarde..."
        campo_traduzido_ref.update()

        def run_translation_task():
            traducao = traduzir_texto_gemini(texto_a_traduzir, de_lang=idioma_origem, para_lang=idioma_destino)
            async def update_translation_field():
                campo_traduzido_ref.value = traducao
                campo_traduzido_ref.update()
            
            page.run_task(update_translation_field) 
        
        threading.Thread(target=run_translation_task, name="Thread-Traduzir").start()
    
    # Função principal de Seleção de Área (chamada pelo clique ou hotkey)
    def on_selecionar_area(e, dd_origem_ref, dd_destino_ref, campo_original_ref, campo_traduzido_ref, btn_selecionar_area_ref):
        btn = btn_selecionar_area_ref
        
        if btn.disabled:
            return
            
        btn.disabled = True
        btn.text = "Aguardando seleção..."
        btn.update()
        page.update() # Garante que o estado 'disabled' seja refletido imediatamente
        # limpa qualquer sinal de cancelamento vindo de tentativa anterior
        try:
            clear_cancel_selection()
        except Exception:
            pass
        
        # Referência para remover hotkey ESC globalmente durante a seleção
        escape_ref = {"id": None}
        
        def run_selection_and_translation():
            texto_extraido = ""

            # Função auxiliar para reabilitar o botão na thread principal do Flet
            async def restore_button_and_update_text(text_for_original_field, re_enable=True):
                btn.text = "Selecionar Área de Tela"
                btn.update()
                
                if re_enable:
                    btn.disabled = False 
                    campo_original_ref.value = text_for_original_field
                    campo_original_ref.update()
                    btn.update()
                
                # limpa handler de teclado ao finalizar
                page.on_keyboard_event = None
                page.update()
                
                # remove hotkey ESC global se registrado
                try:
                    if escape_ref.get("id") is not None:
                        keyboard.remove_hotkey(escape_ref["id"])
                except Exception:
                    pass

            try:
                # Operação Bloqueante na Thread Secundária
                texto_extraido = selecionar_area_e_extrair_texto()
                
                # Verifica Erros/Cancelamento após a seleção
                if "Nenhuma área válida selecionada" in texto_extraido or "Erro: Tesseract" in texto_extraido or "Cancelado" in texto_extraido:
                    async def _call_restore():
                        await restore_button_and_update_text(texto_extraido, re_enable=True)
                    page.run_task(_call_restore)
                    return

                idioma_origem_popup = IDIOMAS[dd_origem_ref.value]
                idioma_destino_popup = IDIOMAS[dd_destino_ref.value]
                
                texto_traduzido_temp = traduzir_texto_gemini(
                    texto_extraido, 
                    de_lang=idioma_origem_popup, 
                    para_lang=idioma_destino_popup
                )
                
                # Chama o Diálogo (que assumirá o controle da reabilitação do botão)
                async def show_dialog_async():
                    show_edit_dialog(
                        page, 
                        btn,
                        campo_original_ref, 
                        campo_traduzido_ref, 
                        dd_origem_ref, 
                        dd_destino_ref, 
                        texto_extraido, 
                        texto_traduzido_temp
                    )
                
                page.run_task(show_dialog_async)
                
            except Exception as e:
                print(f"Erro na thread de OCR/Tradução: {e}")
                async def _call_restore_err():
                    await restore_button_and_update_text(f"Erro inesperado durante a captura ou OCR: {e}", re_enable=True)
                page.run_task(_call_restore_err)
        
        # handler para ESC que solicita cancelamento no backend (quando page tem foco)
        def _on_keyboard_local(ev):
            try:
                if ev.key == "Escape":
                    cancel_selection()
                    mostrar_snackbar(page, "Seleção cancelada", cor=COR_PINK)
                    btn.disabled = False
            except Exception:
                pass

        page.on_keyboard_event = _on_keyboard_local
        
        # registra hotkey global ESC temporária para garantir cancelamento mesmo
        # quando a janela Tkinter estiver em foco (outras threads)
        try:
            escape_ref["id"] = keyboard.add_hotkey('esc', cancel_selection)
        except Exception:
            escape_ref["id"] = None
        
        threading.Thread(target=run_selection_and_translation, name="Thread-SelecaoOCR").start()


    # ------------------------------------
    # Diálogo de Edição de Texto Selecionado
    # ------------------------------------

    def show_edit_dialog(page, btn_selecionar_area_ref, campo_original_ref, campo_traduzido_ref, dd_origem_ref, dd_destino_ref, texto_extraido, texto_traduzido_temp):
        
        dd_dialog_origem = ft.Dropdown(
            options=IDIOMA_OPTIONS,
            value=dd_origem_ref.value,
            width=120,
            border_color=COR_BORDA,
            text_style=ft.TextStyle(color=COR_TEXTO),
            color=COR_TEXTO, 
            dense=True,
        )
        dd_dialog_destino = ft.Dropdown(
            options=IDIOMA_OPTIONS,
            value=dd_destino_ref.value,
            width=120,
            border_color=COR_BORDA,
            text_style=ft.TextStyle(color=COR_TEXTO),
            color=COR_TEXTO,
            dense=True,
        )

        text_field_original = ft.TextField(
            value=texto_extraido,
            multiline=True,
            min_lines=4,
            max_lines=4,
            hint_text="Edite o texto extraído se necessário...",
            bgcolor=COR_CAIXA_TEXTO,
            border_radius=8,
            border_color="transparent",
            text_style=ft.TextStyle(color="white",
            size=14),
            expand=True,
        )

        text_field_traduzido_dialog = ft.TextField(
            value=texto_traduzido_temp,
            multiline=True,
            min_lines=4,
            max_lines=4,
            disabled=True,
            hint_text="A tradução instantânea aparecerá aqui.",
            bgcolor="#30363D",
            border_radius=8,
            border_color="transparent",
            text_style=ft.TextStyle(color="#CCCCCC", size=14),
            expand=True,
        )

        def on_idioma_change(e):
            novo_origem = IDIOMAS[dd_dialog_origem.value]
            novo_destino = IDIOMAS[dd_dialog_destino.value]
            texto_para_traduzir = text_field_original.value
            
            text_field_traduzido_dialog.value = "Recalculando tradução..."
            dialog.update()
            
            def run_retranslation():
                retraducao = traduzir_texto_gemini(texto_para_traduzir, de_lang=novo_origem, para_lang=novo_destino)
                async def update_dialog():
                    text_field_traduzido_dialog.value = retraducao
                    dialog.update()
                page.run_task(update_dialog)

            threading.Thread(target=run_retranslation, name="Thread-Retraducao").start()


        dd_dialog_origem.on_change = on_idioma_change
        dd_dialog_destino.on_change = on_idioma_change
        
        def on_finish(e_dialog):
            dialog.open = False
            page.dialog = None 
            btn_selecionar_area_ref.disabled = False
            btn_selecionar_area_ref.text = "Selecionar Área de Tela"
            btn_selecionar_area_ref.update()
            page.update()

        def on_confirm(e_dialog):
            dd_origem_ref.value = dd_dialog_origem.value
            dd_destino_ref.value = dd_dialog_destino.value
            campo_original_ref.value = text_field_original.value 
            campo_traduzido_ref.value = text_field_traduzido_dialog.value             
            campo_original_ref.update()
            campo_traduzido_ref.update()
            dd_origem_ref.update()
            dd_destino_ref.update()
            on_finish(e_dialog)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Text("Revisão e Tradução Rápida", weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=COR_TEXTO, tooltip="Cancelar (Esc)", on_click=on_finish)
                ], spacing=0
            ),
            content=ft.Column(
                [
                    ft.Divider(height=10, color="#30363D"),
                    ft.Row( [dd_dialog_origem, ft.Icon(ft.Icons.ARROW_RIGHT_ALT, color=COR_TEXTO, size=20), dd_dialog_destino, ft.Container(expand=True),], alignment=ft.MainAxisAlignment.START, spacing=10,), 
                    ft.Container(height=10),
                    ft.Text("Texto Extraído (Edite)", size=12, color="#AAAAAA"),
                    text_field_original,
                    ft.Container(height=5),
                    ft.Text("Tradução (Automática)", size=12, color="#AAAAAA"), 
                    text_field_traduzido_dialog,
                ], spacing=0, width=500, height=480
            ),
            actions=[ft.Button(content="Usar e Fechar", on_click=on_confirm, bgcolor=COR_BOTAO_ROXO, color="white"),],
            bgcolor=COR_PAINEL, content_padding=ft.padding.only(top=0, bottom=10, left=24, right=24), actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.dialog = dialog
        page.overlay.append(dialog)
        dialog.open = True
        page.update()


    # -----------------------------------------------
    # ATALHO GLOBAL: Função de Callback para o Hotkey
    # -----------------------------------------------
    def atalho_global_callback_sync():
        
        async def notify_and_run():
            if btn_alterar_atalho is not None:
                current_shortcut = btn_alterar_atalho.content.replace("Atalho OCR: ", "")
                mostrar_snackbar(page, f"Atalho global '{current_shortcut}' ativado!", cor=COR_BOTAO_VERDE)
            
                on_selecionar_area(
                    e=None, 
                    dd_origem_ref=dd_idioma_origem, 
                    dd_destino_ref=dd_idioma_destino, 
                    campo_original_ref=campo_texto_original, 
                    campo_traduzido_ref=campo_texto_traduzido, 
                    btn_selecionar_area_ref=btn_selecionar_area_ref
                )
        
        page.run_task(notify_and_run)

    # --------------------------------------------
    # FUNÇÃO PARA ABRIR DIALOG DE EDIÇÃO DE ATALHO
    # --------------------------------------------
    def abrir_dialog_atalho(e):
        campo_atalho = ft.TextField(
            label="Pressione as teclas para o novo atalho (ex: Ctrl+A)",
            value=btn_alterar_atalho.content.replace("Atalho OCR: ", "") if "Atalho OCR:" in btn_alterar_atalho.content else PLACEHOLDER_TEXT,
            read_only=True,
            width=400,
            border_radius=8,
            bgcolor=COR_CAIXA_TEXTO,
            color=COR_TEXTO,
        )

        def fechar_dialog(e_close):
            modal.open = False
            page.dialog = None
            desativar_captura(page)
            page.update()

        def salvar_atalho(e_save):
            novo_atalho = campo_atalho.value.strip()
            if not novo_atalho or novo_atalho == PLACEHOLDER_TEXT:
                mostrar_snackbar(page, "Defina um atalho válido!", cor=COR_PINK)
                return
            
            registrar_hotkey_tradutor(novo_atalho, atalho_global_callback_sync)
            
            if GLOBAL_HOTKEY_REF is None:
                mostrar_snackbar(page, f"Erro: O atalho '{novo_atalho}' não pôde ser registrado. Tente outro.", cor=COR_PINK)
            else:
                mostrar_snackbar(page, f"Atalho global atualizado para '{novo_atalho}'!", cor=COR_BOTAO_VERDE)
                btn_alterar_atalho.content = f"Atalho OCR: {novo_atalho}"
                atualizar_atalho(ID_usuario, novo_atalho)
                btn_alterar_atalho.update()
            fechar_dialog(e_save)

        modal = ft.AlertDialog(
            bgcolor=COR_PAINEL,
            title=ft.Text("Editar Atalho de OCR", color=COR_TEXTO, weight=ft.FontWeight.BOLD),
            content=campo_atalho,
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialog),
                ft.Button(content="Salvar", bgcolor=COR_BOTAO_ROXO, color="white", on_click=salvar_atalho),
            ],
        )

        page.overlay.append(modal)
        modal.open = True
        page.dialog = modal
        page.update()
        
        # Ativa a captura de atalho quando o dialog abre
        async def ativar_captura_no_dialog():
            await ativar_captura(page, campo_atalho)
        
        page.run_task(ativar_captura_no_dialog)

    # -------------------
    #  CRIAÇÃO DOS BOTÕES 
    # -------------------

    btn_selecionar_area_ref = ft.Button(
        content="Selecionar Área de Tela",
        icon=ft.Icons.CAMERA_ALT,
        bgcolor=COR_BOTAO_ROXO,
        color="white",
        on_click=lambda e: on_selecionar_area(
            e, dd_idioma_origem, dd_idioma_destino, campo_texto_original, 
            campo_texto_traduzido, btn_selecionar_area_ref
        ),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=20, vertical=10))
    )
    

    btn_traduzir_texto = ft.Button(
        content="Traduzir Texto",
        icon=ft.Icons.TRANSLATE,
        bgcolor=COR_BOTAO_AZUL,
        color="white",
        on_click=lambda e: on_traduzir_click(e, campo_texto_original, dd_idioma_origem, dd_idioma_destino, campo_texto_traduzido),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=20, vertical=10))
    )


    btn_alterar_atalho = ft.Button(
        content=f"Atalho OCR: {ATALHO_INICIAL}", 
        icon=ft.Icons.KEYBOARD,
        bgcolor=COR_SECUNDARIA,
        color="white",
        on_click=abrir_dialog_atalho,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=20, vertical=10))
    )
    
    # Tentativa de registro do atalho inicial
    registrar_hotkey_tradutor(ATALHO_INICIAL, atalho_global_callback_sync)
    if GLOBAL_HOTKEY_REF is None:
        btn_alterar_atalho.content = "Atalho OCR: Não Definido"


    # ----------
    #  Layout UI 
    # ----------

    botoes_topo = ft.Container(
        content=ft.Row([
            btn_selecionar_area_ref,
            btn_traduzir_texto,
            btn_alterar_atalho,
            ft.Container(expand=True),
        ], alignment=ft.MainAxisAlignment.START, spacing=10)
    )
    
    selecao_idiomas_principal = ft.Row(
        [
            ft.Text("De:", color=COR_TEXTO, size=14),
            dd_idioma_origem,
            ft.Text("Para:", color=COR_TEXTO, size=14),
            dd_idioma_destino,
            ft.Container(expand=True)
        ], alignment=ft.MainAxisAlignment.START, spacing=10,
    )

    texto_original = ft.Container(
        bgcolor=COR_PAINEL, border=ft.border.all(1, COR_BORDA), border_radius=10, padding=15, expand=True,
        content=ft.Column([ft.Text("Texto Original", color=COR_TEXTO, size=16, weight=ft.FontWeight.BOLD), campo_texto_original,], spacing=10,),)

    texto_traduzido = ft.Container(
        bgcolor=COR_PAINEL, border=ft.border.all(1, COR_BORDA), border_radius=10, padding=15, expand=True,
        content=ft.Column([ft.Text("Texto Traduzido", color=COR_TEXTO, size=16, weight=ft.FontWeight.BOLD), campo_texto_traduzido,], spacing=10,),)


    layout = ft.Container(
        bgcolor=COR_FUNDO,
        padding=25,
        expand=True,
        content=ft.Column(
            [
                ft.Text("Tradutor Inteligente", color=COR_TEXTO, size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Cole ou capture texto para traduzir automaticamente", color="#B0B0B0", size=14),
                ft.Container(height=20),
                botoes_topo,
                ft.Container(height=15),
                selecao_idiomas_principal, 
                ft.Container(height=10),
                ft.Row([texto_original, texto_traduzido], spacing=20, expand=True,),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    return layout

# Exemplo teste
# if __name__ == "__main__":
#     def main(page: ft.Page):
#         page.title = "Tradutor Flet"
#         page.vertical_alignment = ft.CrossAxisAlignment.START
#         page.theme_mode = ft.ThemeMode.DARK
#         page.add(criar_aba_tradutor(page))
#     ft.app(target=main)