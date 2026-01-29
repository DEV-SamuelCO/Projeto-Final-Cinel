# Frontend/macros.py

import flet as ft
import keyboard
import threading
import mouse
import pyautogui
from Backend.macros_functions import obter_macros_por_usuario, inserir_macro, atualizar_macro, excluir_macro, execute_macro, carregar_macros_globais


PLACEHOLDER_TEXT_HOTKEY = "Pressione as teclas para o hotkey..."
capturing_hotkey = False
hotkey_temp = ""


def criar_aba_macros(page, ID_usuario):
    COR_FUNDO = "#0D1117"
    COR_PAINEL = "#161B22"
    COR_BORDA = "#30363D"
    COR_TEXTO = "#E6EDF3"
    COR_AZUL = "#0078FF"
    COR_BOTAO = "#00B87C"
    COR_PINK = "#E91E63"

    
    campo_hotkey_ref = None

    # Funções para captura de hotkey
    def ativar_captura_hotkey(page, text_field):
        global capturing_hotkey, hotkey_temp
        desativar_captura_hotkey(page)
        capturing_hotkey = True
        hotkey_temp = ""
        text_field.value = PLACEHOLDER_TEXT_HOTKEY
        text_field.update()
        
        def on_keyboard(e):
            global hotkey_temp
            if not capturing_hotkey:
                return
            
            modifiers = []
            if e.ctrl: modifiers.append("Ctrl")
            if e.shift: modifiers.append("Shift")
            if e.alt: modifiers.append("Alt")
            if e.meta: modifiers.append("Meta")
            
            if e.key in ["Control", "Shift", "Alt", "Meta"]:
                return
            
            hotkey_str = "+".join(modifiers)
            if hotkey_str:
                hotkey_str += "+"
            key_name = e.key.upper() if len(e.key) == 1 else e.key
            
            if not modifiers and key_name in ["CONTROL", "SHIFT", "ALT", "META"]:
                return
            
            hotkey_temp = hotkey_str + key_name
            text_field.value = hotkey_temp
            text_field.update()
            
            desativar_captura_hotkey(page)

        page.on_keyboard_event = on_keyboard
        page.update()

    def desativar_captura_hotkey(page):
        global capturing_hotkey
        if capturing_hotkey:
            capturing_hotkey = False
            page.on_keyboard_event = None
            page.update()

    def mostrar_erro(page, mensagem):
        conteudo = ft.Container(
            content=ft.Text(mensagem, size=16, color=COR_TEXTO),
            padding=ft.padding.all(8),
        )
        
        dialog = ft.AlertDialog(
            bgcolor=COR_FUNDO,
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(icon=ft.Icons.ERROR, color="red", size=28),
                    ft.Text("Erro", color="red", size=20, weight="bold"),
                ],
                spacing=10,
            ),
            content=conteudo,
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: fechar()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def fechar():
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Carregar macros do DB
    macros_salvos = obter_macros_por_usuario(ID_usuario)

    # Índice da macro sendo editada (None se for nova)
    macro_editando_idx = None

    # ---------- Painel esquerdo ----------
    def adicionar_acao(tipo):
        if tipo == "DELAY":
            acoes_macro.append({"tipo": "DELAY", "valor": "0s"})
        elif tipo == "KEYBOARD FUNCTION":
            acoes_macro.append({"tipo": "KEYBOARD FUNCTION", "valor": "PRESS: None"})
            acoes_macro.append({"tipo": "KEYBOARD FUNCTION", "valor": "RELEASE: None"})
        elif tipo == "MOUSE FUNCTION":
            acoes_macro.append({"tipo": "MOUSE FUNCTION", "valor": "Clique esquerdo"})
        elif tipo == "MACRO":
            acoes_macro.append({"tipo": "MACRO", "valor": "Sub-macro"})
        elif tipo == "SAVE POSITION":
            x, y = pyautogui.position()
            acoes_macro.append({"tipo": "SAVE POSITION", "valor": f"Posição ({x}, {y})"})
        elif tipo == "TEXT FUNCTION":
            acoes_macro.append({"tipo": "TEXT FUNCTION", "valor": "Texto"})
        elif tipo == "LOOP":
            acoes_macro.append({"tipo": "LOOP", "valor": "1 ciclo"})
            acoes_macro.append({"tipo": "LOOP", "valor": "END"})
        elif tipo == "ATALHO":
            acoes_macro.append({"tipo": "ATALHO", "valor": "Selecione um atalho"})
        atualizar_painel_central()

    # TextFields para nome e hotkey
    campo_nome_macro = ft.TextField(
        label="Nome Macro", 
        label_style=ft.TextStyle(color=COR_TEXTO),
        width=200,
        text_style=ft.TextStyle(color=COR_TEXTO),
    )
    
    campo_hotkey_macro = ft.TextField(
        label="(Clique e pressione)",
        label_style=ft.TextStyle(color=COR_TEXTO),
        width=200,
        text_style=ft.TextStyle(color=COR_TEXTO),
        read_only=True,
        on_focus=lambda e: ativar_captura_hotkey(e.page, e.control),
        on_blur=lambda e: desativar_captura_hotkey(e.page),
    )

    painel_esquerdo = ft.Container(
        bgcolor=COR_PAINEL,
        border_radius=10,
        border=ft.border.all(1, COR_BORDA),
        padding=15,
        expand=1,
        content=ft.Column(
            [
                campo_nome_macro,
                campo_hotkey_macro,
                ft.Divider(height=5, color="transparent"),
                ft.Button(
                    content="SAVE",
                    bgcolor="#00C853",
                    color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=6),
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    ),
                    on_click=lambda e: salvar_macro(),
                ),
                ft.Divider(height=15, color="transparent"),
                ft.Container(
                    content=ft.Text("DELAY", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("DELAY"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("KEYBOARD FUNCTION", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("KEYBOARD FUNCTION"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("MOUSE FUNCTION", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("MOUSE FUNCTION"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("SAVE POSITION", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("SAVE POSITION"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("TEXT FUNCTION", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("TEXT FUNCTION"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("LOOP", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("LOOP"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("MACRO", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("MACRO"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("ATALHO", color=COR_TEXTO, size=14),
                    on_click=lambda e: adicionar_acao("ATALHO"),
                    ink=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
    )

    # Lista para rastrear ações da macro atual
    acoes_macro = []

    # ---------- Painel central ----------
    painel_central_area = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[]
    )
    # Funções para manipular posições das ações
    def mover_acao_cima(idx):
        if idx > 0:
            if acoes_macro[idx]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[idx]["valor"]:
                if idx > 1 and acoes_macro[idx-1]["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acoes_macro[idx-1]["valor"]:
                    acoes_macro[idx-2], acoes_macro[idx-1], acoes_macro[idx] = acoes_macro[idx-1], acoes_macro[idx], acoes_macro[idx-2]
                else:
                    return
            elif acoes_macro[idx]["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acoes_macro[idx]["valor"]:
                if idx < len(acoes_macro) - 1 and acoes_macro[idx+1]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[idx+1]["valor"]:
                    acoes_macro[idx-1], acoes_macro[idx], acoes_macro[idx+1] = acoes_macro[idx], acoes_macro[idx+1], acoes_macro[idx-1]
                else:
                    return
            elif acoes_macro[idx]["tipo"] == "LOOP" and acoes_macro[idx]["valor"] == "END":
                return
            else:
                acoes_macro[idx], acoes_macro[idx-1] = acoes_macro[idx-1], acoes_macro[idx]
            atualizar_painel_central()

    def mover_acao_baixo(idx):
        if idx < len(acoes_macro) - 1:
            if acoes_macro[idx]["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acoes_macro[idx]["valor"]:
                if idx < len(acoes_macro) - 2 and acoes_macro[idx+1]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[idx+1]["valor"]:
                    acoes_macro[idx+1], acoes_macro[idx+2], acoes_macro[idx] = acoes_macro[idx], acoes_macro[idx+1], acoes_macro[idx+2]
                else:
                    return
            elif acoes_macro[idx]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[idx]["valor"]:
                if idx > 0 and acoes_macro[idx-1]["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acoes_macro[idx-1]["valor"]:
                    acoes_macro[idx], acoes_macro[idx+1], acoes_macro[idx-1] = acoes_macro[idx+1], acoes_macro[idx-1], acoes_macro[idx]
                else:
                    return
            elif acoes_macro[idx]["tipo"] == "LOOP" and acoes_macro[idx]["valor"] == "END":
                return
            else:
                acoes_macro[idx], acoes_macro[idx+1] = acoes_macro[idx+1], acoes_macro[idx]
            atualizar_painel_central()

    def atualizar_painel_central():
        painel_central_area.controls.clear()
        for i, acao in enumerate(acoes_macro):
            if (acao["tipo"] == "LOOP" and acao["valor"] == "END") or (acao["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acao["valor"]):
                container_acao = ft.Container(
                    bgcolor=COR_BORDA,
                    border_radius=6,
                    padding=10,
                    content=ft.Row(
                        [
                            ft.Text(f"{acao['tipo']}: {acao['valor']}", color=COR_TEXTO, expand=True),
                            ft.IconButton(
                                ft.Icons.ARROW_DROP_UP,
                                icon_color=COR_AZUL,
                                on_click=lambda e, idx=i: mover_acao_cima(idx),
                            ),
                            ft.IconButton(
                                ft.Icons.ARROW_DROP_DOWN,
                                icon_color=COR_AZUL,
                                on_click=lambda e, idx=i: mover_acao_baixo(idx),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                )
                painel_central_area.controls.append(container_acao)
                continue
            # botões de editar e remover e alterar posição
            container_acao = ft.Container(
                bgcolor=COR_BORDA,
                border_radius=6,
                padding=10,
                content=ft.Row(
                    [
                        ft.Text(f"{acao['tipo']}: {acao['valor']}", color=COR_TEXTO, expand=True),
                        ft.IconButton(
                            ft.Icons.EDIT,
                            icon_color=COR_AZUL,
                            on_click=lambda e, idx=i: editar_acao(e, idx),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            icon_color=COR_PINK,
                            on_click=lambda e, idx=i: remover_acao(idx),
                        ),
                        ft.IconButton(
                            ft.Icons.ARROW_DROP_UP,
                            icon_color=COR_AZUL,
                            on_click=lambda e, idx=i: mover_acao_cima(idx),
                        ),
                        ft.IconButton(
                            ft.Icons.ARROW_DROP_DOWN,
                            icon_color=COR_AZUL,
                            on_click=lambda e, idx=i: mover_acao_baixo(idx),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
            painel_central_area.controls.append(container_acao)
        painel_central_area.update()

    def editar_acao(e, idx):
        acao = acoes_macro[idx]
        if acao["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acao["valor"]:
            # Usar key listener para capturar a tecla
            def capture_key():
                try:
                    key = keyboard.read_key()
                    # utilização do async def para atualizar na thread principal de forma segura
                    async def update_ui():
                        acoes_macro[idx]["valor"] = f"PRESS: {key}"
                        # Encontrar o RELEASE correspondente e atualizar
                        for j in range(idx + 1, len(acoes_macro)):
                            if acoes_macro[j]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[j]["valor"]:
                                acoes_macro[j]["valor"] = f"RELEASE: {key}"
                                break
                        atualizar_painel_central()
                        modal.open = False
                        e.page.update()
                    e.page.run_task(update_ui)
                except Exception as ex:
                    # Para erro, também na thread principal
                    async def show_error():
                        mostrar_erro(e.page, f"Erro ao capturar tecla: {str(ex)}")
                    e.page.run_task(show_error)

            thread = threading.Thread(target=capture_key)
            thread.start()

            modal = ft.AlertDialog(
                bgcolor=COR_FUNDO,
                title=ft.Text("Pressione a tecla desejada", color=COR_TEXTO),
                content=ft.Text("Ouvindo a próxima tecla pressionada...", color=COR_TEXTO),
                actions=[],  # Fecha automaticamente após captura
            )
        elif acao["tipo"] == "MOUSE FUNCTION":
            # Usar mouse listener para capturar o clique
            captured_button = [None]  # Usar lista para modificar dentro do callback

            def on_click(event):
                if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down':
                    button_names = {
                        'left': 'Clique esquerdo',
                        'right': 'Clique direito',
                        'middle': 'Clique do meio',
                        'x': 'Botão lateral 1',
                        'x2': 'Botão lateral 2'
                    }
                    captured_button[0] = button_names.get(event.button, f'Botão {event.button}')
                    mouse.unhook(on_click)
                    # Atualizar na thread principal
                    async def update_ui():
                        acoes_macro[idx]["valor"] = captured_button[0]
                        atualizar_painel_central()
                        modal.open = False
                        e.page.update()
                    e.page.run_task(update_ui)

            mouse.hook(on_click)

            modal = ft.AlertDialog(
                bgcolor=COR_FUNDO,
                title=ft.Text("Clique no botão do mouse desejado", color=COR_TEXTO),
                content=ft.Text("Ouvindo o próximo clique do mouse...", color=COR_TEXTO),
                actions=[],  # Fecha automaticamente após captura
            )
        elif acao["tipo"] == "SAVE POSITION":
            def on_click(event):
                if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down' and event.button == 'left':
                    x, y = pyautogui.position()
                    acoes_macro[idx]["valor"] = f"Posição ({x}, {y})"
                    mouse.unhook(on_click)
                    async def update_ui():
                        atualizar_painel_central()
                        modal.open = False
                        e.page.update()
                    e.page.run_task(update_ui)

            mouse.hook(on_click)

            modal = ft.AlertDialog(
                bgcolor=COR_FUNDO,
                title=ft.Text("Posicione o mouse e clique com o botão esquerdo", color=COR_TEXTO),
                content=ft.Text("Ouvindo o clique esquerdo do mouse...", color=COR_TEXTO),
                actions=[], 
            )
        elif acao["tipo"] == "ATALHO":
            from Backend.atalhos_functions import obter_atalhos_por_usuario
            atalhos = obter_atalhos_por_usuario(ID_usuario)
            options = [ft.dropdown.Option(key=str(a["id"]), text=a["nome"]) for a in atalhos]
            dropdown = ft.Dropdown(
                label="Selecione um atalho",
                color=COR_TEXTO,
                options=options,
                value=acao["valor"] if acao["valor"].isdigit() else None,
                width=400,
            )

            def salvar_edicao(e):
                selected_id = dropdown.value
                if selected_id:
                    acoes_macro[idx]["valor"] = selected_id
                    atualizar_painel_central()
                modal.open = False
                e.page.dialog = None
                e.page.update()

            modal = ft.AlertDialog(
                bgcolor=COR_FUNDO,
                title=ft.Text(f"Editar {acao['tipo']}", color=COR_TEXTO),
                content=dropdown,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: (setattr(modal, 'open', False), e.page.update())),
                    ft.Button(content="Salvar", on_click=lambda e: salvar_edicao(e)),
                ],
            )

        else:
            campo = ft.TextField(
                label=f"Editar {acao['tipo']}", color=COR_TEXTO,
                value=acao["valor"],  # Preenche com o valor atual
                width=400,
            )

            def salvar_edicao(e):
                novo_valor = campo.value.strip()
                if novo_valor:
                    acoes_macro[idx]["valor"] = novo_valor
                    atualizar_painel_central()
                modal.open = False
                e.page.dialog = None
                e.page.update()

            modal = ft.AlertDialog(
                bgcolor=COR_FUNDO,
                title=ft.Text(f"Editar {acao['tipo']}", color=COR_TEXTO),
                content=campo,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: (setattr(modal, 'open', False), e.page.update())),
                    ft.Button(content="Salvar", on_click=lambda e: salvar_edicao(e)),
                ],
            )

        e.page.overlay.append(modal)
        modal.open = True
        e.page.dialog = modal
        e.page.update()

    def remover_acao(idx):
        if acoes_macro[idx]["tipo"] == "LOOP":
            # Remover o LOOP e seu END correspondente
            end_idx = None
            for j in range(idx + 1, len(acoes_macro)):
                if acoes_macro[j]["tipo"] == "LOOP" and acoes_macro[j]["valor"] == "END":
                    end_idx = j
                    break
            if end_idx is not None:
                del acoes_macro[end_idx]
        elif acoes_macro[idx]["tipo"] == "KEYBOARD FUNCTION":
            # Remover o par PRESS/RELEASE
            if "PRESS" in acoes_macro[idx]["valor"]:
                # Procurar o RELEASE seguinte correspondente
                tecla_press = acoes_macro[idx]["valor"].split(": ")[1] if ": " in acoes_macro[idx]["valor"] else None
                for j in range(idx + 1, len(acoes_macro)):
                    if acoes_macro[j]["tipo"] == "KEYBOARD FUNCTION" and "RELEASE" in acoes_macro[j]["valor"]:
                        tecla_release = acoes_macro[j]["valor"].split(": ")[1] if ": " in acoes_macro[j]["valor"] else None
                        if tecla_press == tecla_release or tecla_press == "None":
                            del acoes_macro[j]
                            break
            elif "RELEASE" in acoes_macro[idx]["valor"]:
                # Procurar o PRESS anterior correspondente
                tecla_release = acoes_macro[idx]["valor"].split(": ")[1] if ": " in acoes_macro[idx]["valor"] else None
                for j in range(idx - 1, -1, -1):
                    if acoes_macro[j]["tipo"] == "KEYBOARD FUNCTION" and "PRESS" in acoes_macro[j]["valor"]:
                        tecla_press = acoes_macro[j]["valor"].split(": ")[1] if ": " in acoes_macro[j]["valor"] else None
                        if tecla_press == tecla_release or tecla_release == "None":
                            del acoes_macro[j]
                            break
        del acoes_macro[idx]
        atualizar_painel_central()


    def salvar_macro():
        nonlocal macro_editando_idx
        nome_macro = campo_nome_macro.value.strip()
        hotkey_macro = campo_hotkey_macro.value.strip()
        
        if nome_macro == "":
            mostrar_erro(page, "O nome da macro não pode estar vazio.")  
            return
        if acoes_macro == []:
            mostrar_erro(page, "A macro deve conter pelo menos uma ação.")  
            return
        
        # Validação do hotkey se foi definido
        if hotkey_macro and hotkey_macro != PLACEHOLDER_TEXT_HOTKEY:
            # Hotkey válido
            pass
        else:
            hotkey_macro = ""  # Limpa se for placeholder ou vazio
        
        try:
            if macro_editando_idx is not None:
                # Atualizar macro existente na DB
                macro_id = macros_salvos[macro_editando_idx]["id"]
                atualizar_macro(macro_id, nome_macro, acoes_macro, hotkey_macro)
                macros_salvos[macro_editando_idx]["nome"] = nome_macro
                macros_salvos[macro_editando_idx]["atalho_nome"] = hotkey_macro
                macros_salvos[macro_editando_idx]["acoes"] = acoes_macro.copy()
            else:
                # Inserir nova macro na DB
                macro_id = inserir_macro(ID_usuario, nome_macro, acoes_macro, hotkey_macro)
                macros_salvos.append({"id": macro_id, "nome": nome_macro, "atalho_nome": hotkey_macro, "acoes": acoes_macro.copy()})
        except Exception as ex:
            mostrar_erro(page, f"Erro ao salvar macro: {ex}")
            return
        
        # Recarrega os hotkeys globais após salvar
        try:
            carregar_macros_globais(ID_usuario)
        except Exception as ex:
            print(f"Aviso: Não foi possível registrar os hotkeys globais: {ex}")
        
        # Limpar após salvar
        acoes_macro.clear()
        painel_central_area.controls.clear()
        campo_nome_macro.value = ""
        campo_hotkey_macro.value = ""
        campo_nome_macro.update()
        campo_hotkey_macro.update()
        macro_editando_idx = None
        atualizar_painel_central()
        atualizar_painel_direito()

    painel_central = ft.Container(
        expand=3,  # Maior parte da tela
        padding=15,
        content=ft.Column(
            [
                ft.Container(height=15),
                ft.Container(
                    bgcolor=COR_PAINEL,
                    border=ft.border.all(1, COR_BORDA),
                    border_radius=10,
                    expand=True,
                    content=painel_central_area,
                ),
            ],
            expand=True,
        ),
    )

    # ---------- Painel direito (macros salvos) ----------
    painel_direito_area = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[]
    )

    def remover_macro(idx):
        try:
            macro_id = macros_salvos[idx]["id"]
            excluir_macro(macro_id)
            del macros_salvos[idx]
            atualizar_painel_direito()
        except Exception as ex:
            mostrar_erro(page, f"Erro ao remover macro: {ex}")

    def editar_macro(idx):
        nonlocal macro_editando_idx
        acoes_macro.clear()
        acoes_macro.extend(macros_salvos[idx]["acoes"].copy())
        campo_nome_macro.value = macros_salvos[idx]["nome"]
        campo_hotkey_macro.value = macros_salvos[idx].get("atalho_nome", "")
        campo_nome_macro.update()
        campo_hotkey_macro.update()
        macro_editando_idx = idx
        atualizar_painel_central()
        page.update()

    # Cria a macros de atalhos para a interface principal (callback)
    def atualizar_painel_direito():
        painel_direito_area.controls.clear()
        for i, macro in enumerate(macros_salvos):
            hotkey_display = ""
            if macro.get("atalho_nome"):
                hotkey_display = f" ({macro['atalho_nome']})"
            
            container_macro = ft.Container(
                bgcolor=COR_BORDA,
                border_radius=6,
                padding=3,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(macro["nome"], color=COR_TEXTO, weight=ft.FontWeight.BOLD),
                                ft.Text(hotkey_display, color="#AAAAAA", size=11) if hotkey_display else ft.Container(),
                            ],
                            spacing=2,
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    ft.Icons.PLAY_ARROW,
                                    icon_color=COR_AZUL,
                                    on_click=lambda e, idx=i: execute_macro(macros_salvos[idx]["acoes"], macros_salvos),
                                    tooltip="Executar",
                                ),
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    icon_color=COR_AZUL,
                                    on_click=lambda e, idx=i: editar_macro(idx),
                                    tooltip="Editar",
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    icon_color=COR_PINK,
                                    on_click=lambda e, idx=i: remover_macro(idx),
                                    tooltip="Deletar",
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            painel_direito_area.controls.append(container_macro)
        painel_direito_area.update()


    painel_direito = ft.Container(
        bgcolor=COR_PAINEL,
        border_radius=10,
        border=ft.border.all(1, COR_BORDA),
        padding=15,
        expand=1,
        content=ft.Column(
            [
                ft.Text("Macros Salvos", color=COR_TEXTO, size=16, weight=ft.FontWeight.BOLD),
                painel_direito_area,
            ],
            expand=True,
        ),
    )


    # ---------- Layout geral ----------
    layout = ft.Container(
        bgcolor=COR_FUNDO,
        padding=20,
        expand=True,
        content=ft.Row(
            [
                painel_esquerdo,
                ft.Container(width=20),
                painel_central,
                ft.Container(width=20),
                painel_direito,
            ],
            expand=True,
        ),
    )

    def carregar_hotkeys_e_atualizar():
        """Carrega os hotkeys globais e atualiza o painel direito"""
        try:
            carregar_macros_globais(ID_usuario)
        except Exception as ex:
            print(f"Aviso: Não foi possível registrar os hotkeys globais: {ex}")
        atualizar_painel_direito()

    return layout, carregar_hotkeys_e_atualizar
