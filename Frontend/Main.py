#MACRO GESTOR DE ATALHOS - MAIN FRONTEND


import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import flet as ft

#importar abas
from Atalhos import criar_aba_atalhos
from macros import criar_aba_macros
from tradutor import criar_aba_tradutor
from configuracoes import criar_aba_configuracoes
from login import criar_tela_login

#importar funcoes do backend
from Backend.Base_Dados import login, criar_usuario, deletar_usuario, obter_id_usuario
from Registrar import criar_tela_registro
from Backend.atalhos_functions import criar_tabela_atalhos
from Backend.macros_functions import criar_tabela_macros
from Backend.tradutor_functions import criar_tabela_macros


async def main(page: ft.Page):

    # Configurações iniciais da janela
    page.window.resizable = False
    page.window.full_screen = False
    page.window.width = 1400
    page.window.height = 800
    await page.window.center() 
    page.update()

    # Mensagem de snackbar principalmente usada para erros e validações
    def mostrar_snackbar(msg, cor="red"):
        sb = ft.SnackBar(
            content=ft.Container(
                ft.Text(msg, color="white"),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=8,
                bgcolor=cor,
            ),
            open=True,
            duration=2000, 
        )
        page.overlay.append(sb)
        page.update()

    # Callback de login e registro
    def ao_login(e, usuario, senha):
        if not usuario or not senha:
            mostrar_snackbar("Erro: preencha todos os campos!")
            return

        if login(usuario, senha):
            global usuario_logado
            usuario_logado = usuario
            page.clean()
            id_user = obter_id_usuario(usuario)
            criar_tabela_atalhos()
            criar_tabela_macros()
            criar_tabela_macros()
            carregar_interface_principal(id_user)
        else:
            page.snack_bar.content = ft.Text("Erro: usuário ou senha inválidos")
            page.snack_bar.bgcolor = "red"
            page.snack_bar.open = True
            page.update()

    def ir_para_registro(e):
        def registrar_e_voltar(usuario, email, senha, confirmar):
            isregistrado = criar_usuario(usuario, email, senha, confirmar)
            if isregistrado:
                print("Usuário criado com sucesso!")
                ir_para_login(e)
            else:
                print("Erro ao criar usuário!")

        page.clean()
        page.add(
            criar_tela_registro(
                ao_registrar=registrar_e_voltar,
                ao_ir_login=ir_para_login
            )
        )

    def ir_para_login(e=None):
        page.clean()
        page.add(criar_tela_login(ao_login, ir_para_registro, page))

    def deletar_usuario_e_voltar(email):
        deletar_usuario(email)   
        page.clean()             
        ir_para_login(None)

    # Carregar interface principal após login bem-sucedido
    def carregar_interface_principal(ID_usuario):
        page.title = "Gestor de Atalhos"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        # Carregar hotkeys globais de macros na inicialização
        try:
            from Backend.macros_functions import carregar_macros_globais
            carregar_macros_globais(ID_usuario)
            print("Hotkeys de macros carregados na inicialização")
        except Exception as ex:
            print(f"Aviso: Não foi possível carregar hotkeys de macros: {ex}")

        COR_PRINCIPAL = "#2C3E50"
        COR_SECUNDARIA = "#3498DB"
        COR_FUNDO = "#121A27"
        COR_TEXTO = "#E6EDF3"

        menu_aberto = False
        # Função para abrir/fechar menu
        def abrir_menu(e):
            nonlocal menu_aberto
            menu_aberto = not menu_aberto
            sidebar.width = 250 if menu_aberto else 80
            sidebar.content = ft.Column(
                [
                    criar_item_menu(ft.Icons.HOME, "Atalhos", lambda e: trocar_aba("Atalhos")),
                    criar_item_menu(ft.Icons.STAR, "Macros", lambda e: trocar_aba("macros")),
                    criar_item_menu(ft.Icons.LANGUAGE, "Tradutor", lambda e: trocar_aba("Tradutor")),
                    criar_item_menu(ft.Icons.SETTINGS, "Configurações", lambda e: trocar_aba("Configurações")),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER if not menu_aberto else ft.CrossAxisAlignment.START,
                spacing=25,
            )
            page.update()
        # Função para criar item de menu
        def criar_item_menu(icone, texto, ao_clicar):
            return ft.Container(
                animate=ft.Animation(300, "easeInOut"),
                content=ft.Row(
                    [
                        ft.IconButton(icone, icon_color="white", icon_size=30, on_click=ao_clicar),
                        ft.GestureDetector(
                            content=ft.Text(texto, color="white", size=16) if menu_aberto else ft.Container(width=0),
                            on_tap=ao_clicar),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER if not menu_aberto else ft.CrossAxisAlignment.START,
                    spacing=10,
                ),
            )

        # Header
        header_titulo = ft.Text("Gestor de Atalhos", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO)
        header = ft.Container(
            bgcolor=COR_FUNDO,
            padding=ft.padding.symmetric(horizontal=25, vertical=15),
            content=ft.Row(
                [
                    ft.IconButton(ft.Icons.MENU, icon_color=COR_PRINCIPAL, data="menu", on_click=abrir_menu),
                    header_titulo,
                    ft.Container(expand=True),
                    ft.CircleAvatar(bgcolor=COR_SECUNDARIA, radius=18, content=ft.Text("S", color="white")),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # Conteúdo principal
        conteudo_principal = ft.Container(expand=True, padding=0)

        # Função para trocar aba
        def trocar_aba(nome_aba):
            header_titulo.value = nome_aba 
            if nome_aba == "Atalhos":
                conteudo_principal.content = criar_aba_atalhos(page, ID_usuario)
            elif nome_aba == "macros":
                layout, update_macros = criar_aba_macros(page, ID_usuario)
                conteudo_principal.content = layout
                page.update()  
                print("layout sincronizado")
                update_macros()  
                print("painel direito atualizado")
            elif nome_aba == "Tradutor":
                conteudo_principal.content = criar_aba_tradutor(page, ID_usuario)
            elif nome_aba == "Configurações":
                conteudo_principal.content = criar_aba_configuracoes(usuario_logado, deletar_usuario_e_voltar)
            else:
                conteudo_principal.content = ft.Text("Aba não implementada")
            page.update()

        # Sidebar
        sidebar = ft.Container(
            width=80,
            bgcolor=COR_PRINCIPAL,
            animate=ft.Animation(300, "easeInOut"),
            padding=ft.padding.symmetric(vertical=30),
            content=ft.Column(
                [
                    ft.IconButton(ft.Icons.HOME, icon_color="white", icon_size=30, on_click=lambda e: trocar_aba("Atalhos")),
                    ft.IconButton(ft.Icons.STAR, icon_color="white", icon_size=30, on_click=lambda e: trocar_aba("macros")),
                    ft.IconButton(ft.Icons.LANGUAGE, icon_color="white", icon_size=30, on_click=lambda e: trocar_aba("Tradutor")),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", icon_size=30, on_click=lambda e: trocar_aba("Configurações")),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=40,
            ),
        )

        # Layout principal
        page.add(
            ft.Row(
                [
                    sidebar,
                    ft.Container(
                        expand=True,
                        bgcolor=COR_FUNDO,
                        content=ft.Column(
                            [
                                header,              # Header completo
                                ft.Container(content=conteudo_principal, padding=0, expand=True)  # Conteúdo da aba
                            ],
                            expand=True,
                            spacing=0,
                        ),
                    ),
                ],
                expand=True,
                spacing=0,
            )
        )
        trocar_aba("Atalhos")   

    page.add(criar_tela_login(ao_login, ir_para_registro, page))
    

ft.run(main)