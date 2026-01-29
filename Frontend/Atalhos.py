import flet as ft
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import keyboard

# Cores
COR_SECUNDARIA = "#0078FF"
COR_TEXTO = "#E6EDF3"      
COR_BOTAO = "#00B87C"     
COR_FUNDO = "#0D1117"      
COR_CAMPO = "#161B22"      
COR_PAINEL = COR_CAMPO   
COR_BORDA = "#30363D"    
COR_PINK = "#E91E63"       

#------------------------------
#key capture (mantém para modais)
#------------------------------
capturing = False
atalho_temp = ""
# Variável global para o texto placeholder (para validação)
PLACEHOLDER_TEXT = "Pressione as teclas para o atalho..." 

def ativar_captura(page, text_field):
    global capturing, atalho_temp
    capturing = True
    atalho_temp = ""
    text_field.value = PLACEHOLDER_TEXT
    text_field.update()
    
    # Função para capturar eventos de teclado
    def on_keyboard(e):
        global atalho_temp
        if not capturing:
            return
        modifiers = []
        if e.ctrl:
            modifiers.append("Ctrl")
        if e.shift:
            modifiers.append("Shift")
        if e.alt:
            modifiers.append("Alt")
        if e.meta:
            modifiers.append("Meta")
        
        if e.key in ["Control", "Shift", "Alt", "Meta"]:
            return
        
        atalho_str = "+".join(modifiers)
        if atalho_str:
            atalho_str += "+"
        atalho_str += e.key.upper() if len(e.key) == 1 else e.key
        
        atalho_temp = atalho_str
        text_field.value = atalho_temp
        text_field.update()
        
        desativar_captura(page)
    
    page.on_keyboard_event = on_keyboard
    page.update()

def desativar_captura(page):
    global capturing
    capturing = False
    page.on_keyboard_event = None
    page.update()

#------------------------------
# Funções para hotkeys globais com keyboard
#------------------------------
def registrar_hotkeys_globais(atalhos_globais):
    # Tenta limpar hotkeys existentes para evitar duplicatas e conflitos de versões
    try:
        # Tenta o método mais recente primeiro
        if hasattr(keyboard, 'unhook_all_hotkeys'):
            keyboard.unhook_all_hotkeys()
        # Se não existir, tenta o método antigo
        else:
            keyboard.unhook_all()
    # Se mesmo unhook_all falhar ou der AttributeError no listener
    except AttributeError: 
        print("Aviso: Falha ao limpar hotkeys existentes. O listener interno da biblioteca keyboard pode estar desativado ou a versão é incompatível.")
    except Exception as ex:
        # Captura outras exceções durante a limpeza
        print(f"Aviso: Erro inesperado ao limpar hotkeys: {ex}")
    
    # Registra os hotkeys globais
    for atalho in atalhos_globais:
        atalho_nome = atalho["atalho_nome"]
        atalho_id = atalho["id"]
        
        if not atalho_nome or atalho_nome.strip() == "" or atalho_nome == PLACEHOLDER_TEXT:
            print(f"Aviso: Atalho ID {atalho_id} ('{atalho_nome}') ignorado, pois o atalho é inválido ou não foi definido.")
            continue
            
        # Converte o nome do atalho para o formato esperado pela biblioteca keyboard
        hotkey_str = atalho_nome.lower().replace("meta", "cmd")
        
        # Registra o hotkey
        # O uso de lambda com argumento padrão (id=atalho_id) garante que o ID correto seja capturado para cada hotkey
        keyboard.add_hotkey(hotkey_str, lambda id=atalho_id: executar_atalho_callback(id))
        print(f"Hotkey registrado: {hotkey_str} -> Atalho ID {atalho_id}")

# Callback para executar o atalho
def executar_atalho_callback(atalho_id):
    from Backend.atalhos_functions import executar_atalho
    try:
        executar_atalho(atalho_id)
        print(f"Atalho ID {atalho_id} executado via hotkey!")
    except Exception as ex:
        print(f"Erro ao executar atalho {atalho_id}: {ex}")

def carregar_atalhos_globais(ID_usuario):
    from Backend.atalhos_functions import obter_atalhos_por_usuario
    atalhos_db = obter_atalhos_por_usuario(ID_usuario)
    atalhos_globais = [{"atalho_nome": a["atalho_nome"], "id": a["id"]} for a in atalhos_db]
    registrar_hotkeys_globais(atalhos_globais)
    print(f"Atalhos globais carregados e hotkeys registrados: {atalhos_globais}")

# ------------------------------
# FUNÇÃO SNACKBAR
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
    page.overlay.append(page.snack_bar)
    page.update()

# ------------------------------
# CARD DOS ATALHOS
# ------------------------------
def criar_card_atalho(id: int, nome: str, atalho_nome: str, destinos: list, ID_usuario: int):
    def executar(e):
        mostrar_snackbar(e.page, f"Executando atalho '{nome}'...", cor=COR_BOTAO)
        from Backend.atalhos_functions import executar_atalho
        executar_atalho(id)

    def editar(e):
        card_container = e.control.parent.parent.parent
        atalho_id = card_container.data
        criar_formulario_editar_atalho(e.page, card_container.parent, ID_usuario, atalho_id, nome, atalho_nome, destinos)

    def remover(e):
        card_container = e.control.parent.parent.parent 
        atalho_id = card_container.data
        nome_atalho_v = "Atalho Desconhecido"
        try:
            nome_atalho_v = card_container.content.controls[0].controls[0].value
        except AttributeError:
            try:
                nome_atalho_v = card_container.content.controls[0].controls[0].value
            except (AttributeError, IndexError):
                nome_atalho_v = nome
        grid = card_container.parent
        
        # Tenta garantir que estamos removendo do GridView correto
        if not isinstance(grid, ft.GridView):
            grid = card_container.parent.parent
        if isinstance(grid, ft.GridView) and card_container in grid.controls:
            from Backend.atalhos_functions import excluir_atalho
            try:
                excluir_atalho(atalho_id)
                carregar_atalhos_globais(ID_usuario)  # Recarrega hotkeys após remoção
            except Exception as ex:
                mostrar_snackbar(e.page, f"Erro DB: Não foi possível excluir o atalho. {ex}", cor=COR_PINK)
                return
            grid.controls.remove(card_container)
            grid.update()
            mostrar_snackbar(e.page, f"Atalho '{nome_atalho_v}' (ID: {atalho_id}) removido!", cor=COR_PINK)
        else:
            mostrar_snackbar(e.page, f"Erro: Não foi possível localizar o GridView para remover o atalho.", cor=COR_PINK)
    
    # Estrutura do cards
    return ft.Container(
        bgcolor=COR_PAINEL,
        border_radius=15,
        padding=20,
        height=300,
        data=id,
        content=ft.Column(
            [
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [
                            ft.Text(nome, size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                            ft.Text(f"Atalho: {atalho_nome}", size=14, color=COR_TEXTO),
                            ft.Divider(color=COR_BORDA), 
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{item['tipo']} ({item['quantidade']}x): {item['destino']}",
                                        size=14,
                                        weight=ft.FontWeight.W_500 if item['quantidade'] > 1 else ft.FontWeight.NORMAL,
                                        color=COR_TEXTO,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=2,
                                    ) for item in destinos
                                ],
                                spacing=5,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                            ),
                            ft.Divider(color=COR_BORDA), 
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.PLAY_ARROW, icon_color=COR_BOTAO, tooltip="Executar", on_click=executar),
                        ft.IconButton(ft.Icons.EDIT, icon_color=COR_SECUNDARIA, tooltip="Editar", on_click=editar),
                        ft.IconButton(ft.Icons.DELETE, icon_color=COR_PINK, tooltip="Remover", on_click=remover),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

# ------------------------------
# FORMULÁRIO MODAL DE EDIÇÃO
# ------------------------------
def criar_formulario_editar_atalho(page, grid: ft.GridView, ID_usuario, atalho_id, nome_atual, atalho_nome_atual, destinos_atuais):
    nome = ft.TextField(
        label="Nome do Atalho",
        value=nome_atual,
        width=450,
        autofocus=True,
        border_radius=8,
        bgcolor=COR_CAMPO,
        color=COR_TEXTO,
    )
    atalho = ft.TextField(
        label="Atalho (Clique e pressione as teclas)",
        value=atalho_nome_atual,
        width=450,
        border_radius=8,
        bgcolor=COR_CAMPO,
        color=COR_TEXTO,
        read_only=True,
        on_focus=lambda e: ativar_captura(e.page, e.control),
        on_blur=lambda e: desativar_captura(e.page),
    )
    
    lista_destinos = ft.Column(tight=True, spacing=10)
    
    def criar_par_destino_input(tipo_val="", destino_val="", qtd_val="1"):
        dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("Site"), ft.dropdown.Option("Caminho")],
            value=tipo_val,
            width=120,
            color=COR_TEXTO,
        )
        caminho = ft.TextField(
            hint_text="https://exemplo.com ou /caminho/do/exe",
            value=destino_val,
            expand=True,
            border_radius=8,
            bgcolor=COR_CAMPO,
            color=COR_TEXTO,
        )
        quantidade_destino = ft.TextField(
            label="Qtd",
            value=qtd_val,
            width=60,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            bgcolor=COR_CAMPO,
            color=COR_TEXTO,
            dense=True,
        )
        # Função para remover o par de destino
        def remover_par(e):
            row_pai = e.control.parent.parent
            lista_destinos.controls.remove(row_pai)
            lista_destinos.update()
        botao_remover = ft.IconButton(ft.Icons.DELETE, icon_color=COR_PINK, tooltip="Remover Destino", on_click=remover_par)
        return ft.Container(
            ft.Row([quantidade_destino, dropdown, caminho, botao_remover], alignment=ft.MainAxisAlignment.START, spacing=10),
            padding=ft.padding.only(top=5),
            data={"dropdown": dropdown, "caminho": caminho, "quantidade": quantidade_destino}
        )
    
    for dest in destinos_atuais:
        lista_destinos.controls.append(criar_par_destino_input(dest["tipo"], dest["destino"], str(dest["quantidade"])))
    
    # Adiciona botão para novo destino
    def adicionar_destino(e, initial_load=False ):
        # se for chamado na inicialização, não atualiza a interface
        lista_destinos.controls.append(criar_par_destino_input())
        # atualiza só quando o utilizador clica em “Adicionar Destino”
        if not initial_load:
            lista_destinos.update()
    
    destino_btn = ft.Button(
        content="Adicionar Destino",
        icon=ft.Icons.ADD,
        width=450,
        bgcolor=COR_BOTAO,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=adicionar_destino,
    )
    
    def salvar_edicao(e):        
        nome_v = (nome.value or "").strip()
        atalho_v = (atalho.value or "").strip()
        
        if not nome_v or not atalho_v:
            mostrar_snackbar(page, "Erro: Preencha nome e atalho.", cor=COR_PINK)
            return
            
        if atalho_v == PLACEHOLDER_TEXT:
            mostrar_snackbar(page, "Erro: Defina um atalho de teclado válido.", cor=COR_PINK)
            return
        
        destinos_coletados = []
        for par in lista_destinos.controls:
            dropdown_ctrl = par.data.get("dropdown")
            caminho_ctrl = par.data.get("caminho")
            quantidade_ctrl = par.data.get("quantidade")
            tipo_v = dropdown_ctrl.value
            caminho_v = (caminho_ctrl.value or "").strip()
            qtd_v = (quantidade_ctrl.value or "1").strip()
            if not tipo_v or not caminho_v or not qtd_v:
                mostrar_snackbar(page, "Erro: Destino incompleto.", cor=COR_PINK)
                return
            try:
                qtd = int(qtd_v)
                if qtd <= 0:
                    raise ValueError()
            except:
                mostrar_snackbar(page, f"Erro: Quantidade inválida para '{caminho_v}'.", cor=COR_PINK)
                return
            destinos_coletados.append({"tipo": tipo_v, "destino": caminho_v, "quantidade": qtd})
        
        from Backend.atalhos_functions import atualizar_atalho, deletar_destinos_por_atalho, inserir_destino
        try:
            atualizar_atalho(atalho_id, nome_v, atalho_v)
            deletar_destinos_por_atalho(atalho_id)
            for item in destinos_coletados:
                inserir_destino(atalho_id, item["tipo"], item["destino"], item["quantidade"])
            carregar_atalhos_globais(ID_usuario)  # Recarrega após atualização
        except Exception as ex:
            mostrar_snackbar(page, f"Erro DB: {ex}", cor=COR_PINK)
            return
        
        novo_card = criar_card_atalho(atalho_id, nome_v, atalho_v, destinos_coletados, ID_usuario)
        for i, ctrl in enumerate(grid.controls):
            if ctrl.data == atalho_id:
                grid.controls[i] = novo_card
                break
        grid.update()
        modal.open = False
        page.dialog = None
        page.update()
        mostrar_snackbar(page, "Atalho editado com sucesso!", cor=COR_BOTAO)
    
    def cancelar(e):
        modal.open = False
        page.dialog = None
        page.update()
    
    modal = ft.AlertDialog(
        modal=True,
        bgcolor=COR_FUNDO,
        title=ft.Text("Editar Atalho", size=20, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
        content=ft.Column([nome, atalho, ft.Divider(height=15), ft.Text("Destinos", weight=ft.FontWeight.BOLD, color=COR_TEXTO), lista_destinos, destino_btn], tight=True, spacing=15),
        actions=[ft.TextButton("Cancelar", on_click=cancelar), ft.Button(content="Salvar", bgcolor=COR_BOTAO, color="white", width=200, height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), on_click=salvar_edicao)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(modal)
    modal.open = True
    page.dialog = modal
    page.update()

# ------------------------------
# FORMULÁRIO MODAL
# ------------------------------
def criar_formulario_adicionar_atalho(page, grid: ft.GridView, ID_usuario):
    nome = ft.TextField(
        label="Nome do Atalho",
        width=450,
        autofocus=True,
        border_radius=8,
        bgcolor=COR_CAMPO,
        color=COR_TEXTO,
    )
    atalho = ft.TextField(
        label="Atalho (Clique e pressione as teclas)",
        width=450,
        border_radius=8,
        bgcolor=COR_CAMPO,
        color=COR_TEXTO,
        read_only=True,
        on_focus=lambda e: ativar_captura(e.page, e.control),
        on_blur=lambda e: desativar_captura(e.page),
    )
    
    lista_destinos = ft.Column(tight=True, spacing=10)
    
    def criar_par_destino_input():
        dropdown = ft.Dropdown(
            options=[ft.dropdown.Option("Site"),
            ft.dropdown.Option("Caminho")],
            value="Site",
            width=120,
            color=COR_TEXTO,
        )
        caminho = ft.TextField(
            hint_text="https://exemplo.com ou /caminho/do/exe",
            expand=True,
            border_radius=8,
            bgcolor=COR_CAMPO,
            color=COR_TEXTO,
        )
        quantidade_destino = ft.TextField(
            label="Qtd",
            value="1",
            width=60,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            bgcolor=COR_CAMPO,
            color=COR_TEXTO,
            dense=True,
        )
        def remover_par(e):
            row_pai = e.control.parent.parent
            lista_destinos.controls.remove(row_pai)
            lista_destinos.update()

        botao_remover = ft.IconButton(
            ft.Icons.DELETE,
            icon_color=COR_PINK,
            tooltip="Remover Destino",
            on_click=remover_par
        )

        return ft.Container(
            ft.Row([
                    quantidade_destino,
                    dropdown,
                    caminho,
                    botao_remover
                ],
                alignment=ft.MainAxisAlignment.START, spacing=10
            ),
            padding=ft.padding.only(top=5),
            data={"dropdown": dropdown, "caminho": caminho, "quantidade": quantidade_destino}
        )
    
    def adicionar_destino(e, initial_load=False):
        lista_destinos.controls.append(criar_par_destino_input())
        if not initial_load:
            lista_destinos.update()
    
    adicionar_destino(None, initial_load=True)
    
    destino_btn = ft.Button(
        content="Adicionar Destino",
        icon=ft.Icons.ADD,
        width=450,
        bgcolor=COR_BOTAO,
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=adicionar_destino,
    )
    
    def adicionar(e):
        nome_v = (nome.value or "").strip()
        atalho_v = (atalho.value or "").strip()
        
        if not nome_v or not atalho_v:
            mostrar_snackbar(page, "Erro: Preencha nome e atalho.", cor=COR_PINK)
            return
            

        if atalho_v == PLACEHOLDER_TEXT:
            mostrar_snackbar(page, "Erro: Defina um atalho de teclado válido.", cor=COR_PINK)
            return
        
        destinos_coletados = []
        if not lista_destinos.controls:
            mostrar_snackbar(page, "Erro: Adicione pelo menos um destino!", cor=COR_PINK)
            return
        
        carregar_atalhos_globais(ID_usuario)

        for par_destino_container in lista_destinos.controls:
            
            # Recupera as referências
            dropdown_ctrl = par_destino_container.data.get("dropdown")
            caminho_ctrl = par_destino_container.data.get("caminho")
            quantidade_ctrl = par_destino_container.data.get("quantidade")

            tipo_v = dropdown_ctrl.value
            caminho_v = (caminho_ctrl.value or "").strip()
            qtd_v = (quantidade_ctrl.value or "1").strip()

            # Validação
            if not tipo_v or not caminho_v or not qtd_v:
                mostrar_snackbar(page, "Erro: Um dos destinos está incompleto. Preencha o tipo, destino e quantidade.", cor=COR_PINK)
                return
                
            try:
                qtd = int(qtd_v)
                if qtd <= 0:
                    raise ValueError()
            except Exception:
                mostrar_snackbar(page, f"Erro: Quantidade inválida para o destino '{caminho_v}' (use um número inteiro > 0).", cor=COR_PINK)
                return
                
            # Adiciona o dicionário com a quantidade individual
            destinos_coletados.append({"tipo": tipo_v, "destino": caminho_v, "quantidade": qtd})
            
      
        from Backend.atalhos_functions import inserir_atalho, inserir_destino 

        try:
            atalho_id = inserir_atalho(ID_usuario, nome_v, atalho_v)
            
            for item in destinos_coletados:
                inserir_destino( 
                    atalho_id, item["tipo"],
                    item["destino"],
                    item["quantidade"] )
                    
            carregar_atalhos_globais(ID_usuario) 

        except Exception as ex:
            mostrar_snackbar(page, f"Erro DB: Falha ao inserir atalho ou destino: {ex}", cor=COR_PINK) 
            return
        
        novo_card = criar_card_atalho(
            id=atalho_id,
            nome=nome_v,
            atalho_nome=atalho_v,
            destinos=destinos_coletados,
            ID_usuario=ID_usuario 
        )

        grid.controls.append(novo_card)
        grid.update()

        modal.open = False
        page.dialog = None 
        page.update()

        mostrar_snackbar(page, "Atalho criado com sucesso!", cor=COR_BOTAO)

    def cancelar(e):
        modal.open = False
        page.dialog = None  
        page.update()

    
    modal = ft.AlertDialog(
        modal=True,
        bgcolor=COR_FUNDO,
        title=ft.Text("Novo Atalho", size=20, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
        content=ft.Column(
            [
                nome,
                atalho,
                ft.Divider(height=15),
                ft.Text("Lista de Destinos (com quantidade de instâncias)", weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                lista_destinos, 
                destino_btn,
            ],
            tight=True,
            spacing=15
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar),
            ft.Button(
                content="Adicionar",
                bgcolor=COR_BOTAO,
                color="white",
                width=200,
                height=45,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=adicionar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(modal)
    modal.open = True
    page.dialog = modal
    page.update()

# ------------------------------
# ABA DE ATALHOS
# ------------------------------
# Cria a aba de atalhos para a interface principal (callback)
def criar_aba_atalhos(page, ID_usuario):

    carregar_atalhos_globais(ID_usuario)
    grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=280,
        spacing=20,
        run_spacing=20,
        controls=[],
    )
    
    # Carregar cards (código existente)
    from Backend.atalhos_functions import obter_atalhos_por_usuario
    atalhos = obter_atalhos_por_usuario(ID_usuario)
    for atalho in atalhos:
        card = criar_card_atalho(
            id=atalho["id"],
            nome=atalho["nome"],
            atalho_nome=atalho["atalho_nome"],
            destinos=atalho["destinos"],
            ID_usuario=ID_usuario
        )
        grid.controls.append(card)
    
    botao_adicionar = ft.Container(
        padding=ft.padding.symmetric(horizontal=0, vertical=10),
        content=ft.Row(
            [
                ft.Button(
                    content="Adicionar Atalho",
                    icon=ft.Icons.ADD,
                    bgcolor=COR_SECUNDARIA,
                    color="white",
                    on_click=lambda e: criar_formulario_adicionar_atalho(page, grid, ID_usuario),
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
    )
    
    return ft.Container(
        bgcolor=COR_FUNDO, 
        padding=ft.padding.symmetric(horizontal=25, vertical=10),
        content=ft.Column([botao_adicionar, grid], expand=True),
        expand=True,
    )

# exemplo de main para testar
def main(page: ft.Page):
    page.title = "Exemplo Atalhos Múltiplos por Destino"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = "dark" 
    page.bgcolor = COR_FUNDO 
    page.update()
    
    aba = criar_aba_atalhos(page, 1)
    page.add(aba)


if __name__ == "__main__":
    ft.app(target=main)