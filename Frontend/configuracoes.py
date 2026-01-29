import flet as ft
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from Backend.Base_Dados import obter_informacoes, atualizar_usuario

def criar_aba_configuracoes(email_usuario, on_delete):

    dados = obter_informacoes(email_usuario)

    if dados is None:
        nome_usuario = "Desconhecido"
        email_usuario_real = email_usuario
        senha_usuario = ""
    else:
        nome_usuario, email_usuario_real, senha_hash = dados
        senha_usuario = ""

    COR_FUNDO = "#0D1117"
    COR_PAINEL = "#161B22"
    COR_TEXTO = "#E6EDF3"
    COR_AZUL = "#0078FF"
    COR_BORDA = "#30363D"

    # Campos de perfil
    nome_input = ft.TextField(
        label="Nome",
        value=nome_usuario,
        bgcolor="#21262D",
        border_radius=8,
        color=COR_TEXTO,
        border_color="#30363D",
        read_only=True,
    )

    email_input = ft.TextField(
        label="Email",
        value=email_usuario_real,
        bgcolor="#21262D",
        border_radius=8,
        color=COR_TEXTO,
        border_color="#30363D",
        read_only=True,
    )

    password_input = ft.TextField(
        label="Password",
        value=senha_usuario,
        password=True,
        can_reveal_password=True,
        bgcolor="#21262D",
        border_radius=8,
        color=COR_TEXTO,
        border_color="#30363D",
        read_only=True,
        visible=False,
    )

    # Botões
    btn_excluir = ft.Button(
        content="Excluir conta",
        bgcolor="#E74C3C",
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        ),
    )

    btn_editar = ft.Button(
        content="Editar",
        bgcolor=COR_AZUL,
        color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        ),
    )

    btn_cancelar = ft.Button(
        content="Cancelar",
        bgcolor="#8B949E",
        color="white",
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        ),
    )

    editando = False

    # valores originais
    valor_nome_original = nome_input.value
    valor_email_original = email_input.value
    valor_senha_original = password_input.value

    def alternar_modo_edicao(e):
        nonlocal editando, valor_nome_original, valor_email_original, valor_senha_original

        if not editando:
            editando = True
            valor_nome_original = nome_input.value
            valor_email_original = email_input.value

            password_input.visible = True
            btn_editar.text = "Guardar"
            btn_editar.bgcolor = "#00B87C"
            btn_cancelar.visible = True

        else:
            editando = False

            novo_nome = nome_input.value
            novo_email = email_input.value
            nova_senha = password_input.value

            atualizar_usuario(novo_nome, novo_email, nova_senha, valor_email_original)

            password_input.visible = False
            btn_editar.text = "Editar"
            btn_editar.bgcolor = COR_AZUL
            btn_cancelar.visible = False

        nome_input.read_only = not editando
        email_input.read_only = not editando
        password_input.read_only = not editando

        nome_input.update()
        email_input.update()
        password_input.update()
        btn_editar.update()
        btn_cancelar.update()



    def cancelar_edicao(e):
        nonlocal editando
        editando = False

        nome_input.value = valor_nome_original
        email_input.value = valor_email_original
        password_input.value = valor_senha_original
        password_input.visible = False

        nome_input.read_only = True
        email_input.read_only = True
        password_input.read_only = True

        btn_editar.text = "Editar"
        btn_editar.bgcolor = COR_AZUL
        btn_cancelar.visible = False

        nome_input.update()
        email_input.update()
        password_input.update()
        btn_editar.update()
        btn_cancelar.update()




    btn_editar.on_click = alternar_modo_edicao
    btn_cancelar.on_click = cancelar_edicao
    btn_excluir.on_click = lambda e: on_delete(email_usuario)





    # Avatar + título
    avatar = ft.CircleAvatar(
        radius=40,
        bgcolor=COR_AZUL,
        content=ft.Text("S", size=30, weight=ft.FontWeight.BOLD, color="white"),
    )

    return ft.Container(
        bgcolor=COR_FUNDO,
        expand=True,
        padding=25,
        content=ft.Column(
            [
                ft.Text("Perfil do Utilizador", size=22, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                ft.Container(height=15),

                ft.Container(
                    bgcolor=COR_PAINEL,
                    border=ft.border.all(1, COR_BORDA),
                    border_radius=10,
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    avatar,
                                    ft.Column(
                                        [
                                            ft.Text("Informações do Perfil", size=16, color=COR_AZUL, weight=ft.FontWeight.BOLD),
                                            ft.Text("Gerencie as suas informações pessoais", size=13, color="#8B949E"),
                                        ],
                                        spacing=3,
                                    ),
                                ],
                                spacing=15,
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Divider(height=20, color="transparent"),

                            nome_input,
                            email_input,
                            password_input,

                            ft.Container(height=10),

                            ft.Row(
                                [
                                    btn_excluir,
                                    btn_cancelar,   
                                    btn_editar,     
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=10,
                            )
                        ],
                        spacing=10,
                    ),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

