import flet as ft

def criar_tela_login(ao_login, ao_ir_registro, page):

    COR_FUNDO = "#0D1117"
    COR_CARD = "#161B22"
    COR_BOTAO = "#0078FF"
    COR_TEXTO = "#E6EDF3"
    COR_INPUT = "#21262D"

    # campos e guarda referências
    usuario_field = ft.TextField(
        label="Utilizador",
        hint_text="Digite seu Email ou Username",
        bgcolor=COR_INPUT,
        border_radius=8,
        border_color="#30363D",
        color=COR_TEXTO,
        prefix_icon=ft.Icons.PERSON,
    )
    senha_field = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        bgcolor=COR_INPUT,
        border_radius=8,
        border_color="#30363D",
        color=COR_TEXTO,
        prefix_icon=ft.Icons.LOCK,
    )

    return ft.Container(
        bgcolor=COR_FUNDO,
        expand=True,
        alignment=ft.alignment.Alignment.CENTER,
        content=ft.Container(
            width=400,
            padding=40,
            border_radius=15,
            bgcolor=COR_CARD,
            content=ft.Column(
                [
                    ft.Icon(icon=ft.Icons.FLASH_ON, color=COR_BOTAO, size=50),
                    ft.Text("SmartDesk Tools", size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                    ft.Text("Faça login para continuar", size=14, color="#9E8B8B"),
                    ft.Divider(height=30, color="transparent"),

                    usuario_field,
                    senha_field,
                    ft.Divider(height=20, color="transparent"),

                    ft.Button(
                        content="Entrar",
                        bgcolor=COR_BOTAO,
                        color="white",
                        width=300,
                        height=45,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        # envia os valores ao callback
                        on_click=lambda e: ao_login(e, usuario_field.value, senha_field.value),
                    ),

                    ft.Row(
                        [
                            ft.Text("Ainda não tem conta?", size=12, color="#8B949E"),
                            ft.TextButton(
                                "Criar conta",
                                style=ft.ButtonStyle(color=COR_BOTAO),
                                on_click=ao_ir_registro, 
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),

                    ft.Divider(height=20, color="transparent"),
                    ft.Text("SmartDesk Tools v1.0", size=11, color="#555"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        ),
    )
