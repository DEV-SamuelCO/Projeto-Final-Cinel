import flet as ft

def criar_tela_registro(ao_registrar, ao_ir_login):
    COR_FUNDO = "#0D1117"
    COR_CARD = "#161B22"
    COR_BOTAO = "#0078FF"
    COR_TEXTO = "#E6EDF3"
    COR_INPUT = "#21262D"

    usuario_field = ft.TextField(
        label="Utilizador *",
        hint_text="Escolha um utilizador",
        bgcolor=COR_INPUT,
        border_radius=8,
        border_color="#30363D",
        color=COR_TEXTO,
        prefix_icon=ft.Icons.PERSON,
    )

    email_field = ft.TextField(
        label="Email *",
        hint_text="seu@email.com",
        bgcolor=COR_INPUT,
        border_radius=8,
        border_color="#30363D",
        color=COR_TEXTO,
        prefix_icon=ft.Icons.EMAIL,
    )

    senha_field = ft.TextField(
        label="Senha *",
        hint_text="Minimo 3 caracteres",
        password=True,
        can_reveal_password=True,
        bgcolor=COR_INPUT,
        border_radius=8,
        border_color="#30363D",
        color=COR_TEXTO,
        prefix_icon=ft.Icons.LOCK,
    )

    confirmar_field = ft.TextField(
        label="Confirmar Senha *",
        hint_text="Digite a senha novamente",
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
            width=420,
            padding=40,
            border_radius=15,
            bgcolor=COR_CARD,
            content=ft.Column(
                [
                    ft.Icon(icon=ft.Icons.FLASH_ON, color=COR_BOTAO, size=50),
                    ft.Text("SmartDesk Tools", size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                    ft.Text("Crie sua conta", size=14, color="#9E8B8B"),

                    ft.Divider(height=30, color="transparent"),

                    usuario_field,
                    email_field,
                    senha_field,
                    confirmar_field,

                    ft.Divider(height=20, color="transparent"),

                    ft.Button(
                        content="Criar Conta",
                        bgcolor=COR_BOTAO,
                        color="white",
                        width=300,
                        height=45,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda e: ao_registrar(
                            usuario_field.value,
                            email_field.value,
                            senha_field.value,
                            confirmar_field.value,
                        ),
                    ),                
                    ft.Divider(height=20, color="transparent"),

                    ft.Row(
                        [
                            ft.Text("Já tem uma conta?", size=12, color="#8B949E"),
                            ft.TextButton(
                                "Fazer login",
                                style=ft.ButtonStyle(color=COR_BOTAO),
                                on_click=ao_ir_login,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),

                    ft.Text("SmartDesk Tools v1.0", size=11, color="#555"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        ),
    )
