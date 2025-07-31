#!/usr/bin/env python3
"""
Test the enhanced config interface
"""

import flet as ft
from settings_manager import SettingsManager

def main(page: ft.Page):
    page.title = "Enhanced Config Test"
    page.window_width = 800
    page.window_height = 600
    
    settings = SettingsManager()
    settings.load()
    
    def show_enhanced_settings(e):
        print("Enhanced config opened!")
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
            
        def validate_api_key(api_key):
            """Validate OpenAI API key format"""
            if not api_key:
                return True, ""  # Empty is allowed
            if not api_key.startswith('sk-'):
                return False, "Chave da API deve começar com 'sk-'"
            if len(api_key) < 40:
                return False, "Chave da API parece muito curta"
            return True, ""
        
        def on_api_key_change(e):
            """Validate API key as user types"""
            api_key = api_key_field.value.strip()
            is_valid, error_msg = validate_api_key(api_key)
            
            if not is_valid:
                api_key_field.error_text = error_msg
                save_button.disabled = True
            else:
                api_key_field.error_text = None
                save_button.disabled = False
            
            page.update()
        
        def save_settings(e):
            print("Settings saved!")
            close_dialog(e)
            
            # Show success
            def close_success(e):
                page.dialog.open = False
                page.update()
                
            success_dialog = ft.AlertDialog(
                title=ft.Text("Sucesso"),
                content=ft.Text("Configurações salvas com sucesso!"),
                actions=[ft.TextButton("OK", on_click=close_success)]
            )
            
            page.dialog = success_dialog
            success_dialog.open = True
            page.update()
        
        # API key field with validation
        api_key_field = ft.TextField(
            label="Chave da API OpenAI",
            value=settings.get('openai_api_key', ''),
            password=True,
            hint_text="sk-...",
            helper_text="Obtenha gratuitamente em: https://platform.openai.com/api-keys",
            on_change=on_api_key_change,
            border_radius=8,
            filled=True
        )
        
        # Auto-scroll checkbox
        auto_scroll_checkbox = ft.Checkbox(
            label="Rolar automaticamente para o topo ao trocar páginas",
            value=settings.get('auto_scroll_on_page_change', True),
            check_color=ft.Colors.WHITE,
            active_color=ft.Colors.BLUE
        )
        
        # Font size dropdown
        font_size_dropdown = ft.Dropdown(
            label="Tamanho da fonte",
            value=str(settings.get('font_size', 14)),
            options=[
                ft.dropdown.Option("10", "Muito pequeno (10px)"),
                ft.dropdown.Option("12", "Pequeno (12px)"),
                ft.dropdown.Option("14", "Normal (14px)"),
                ft.dropdown.Option("16", "Grande (16px)"),
                ft.dropdown.Option("18", "Muito grande (18px)"),
                ft.dropdown.Option("20", "Extra grande (20px)")
            ],
            border_radius=8,
            filled=True
        )
        
        # Create save button reference for validation
        save_button = ft.ElevatedButton(
            "Salvar",
            on_click=save_settings,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        )
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE),
                ft.Text("Configurações do Epubizon", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    # OpenAI API Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.GREEN),
                                ft.Text("Inteligência Artificial", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            api_key_field,
                            ft.Container(
                                content=ft.Text(
                                    "• Necessário para gerar resumos inteligentes\n• Sua chave é armazenada localmente com segurança\n• Nunca compartilhamos seus dados",
                                    size=11,
                                    color=ft.Colors.BLUE_GREY_600
                                ),
                                padding=ft.padding.only(left=10, top=5)
                            )
                        ], spacing=8),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.BLUE_GREY_300),
                        border_radius=8,
                        bgcolor=ft.Colors.BLUE_GREY_50
                    ),
                    
                    # Interface Section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.TUNE, color=ft.Colors.ORANGE),
                                ft.Text("Interface", size=16, weight=ft.FontWeight.BOLD)
                            ]),
                            auto_scroll_checkbox,
                            ft.Container(height=10),
                            font_size_dropdown,
                            ft.Container(
                                content=ft.Text(
                                    "• Auto-scroll melhora a experiência de leitura\n• Tamanho da fonte afeta a legibilidade do texto",
                                    size=11,
                                    color=ft.Colors.BLUE_GREY_600
                                ),
                                padding=ft.padding.only(left=10, top=5)
                            )
                        ], spacing=8),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.ORANGE_300),
                        border_radius=8,
                        bgcolor=ft.Colors.ORANGE_50
                    )
                ], spacing=15),
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.GREY)
                ),
                save_button
            ]
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    config_button = ft.ElevatedButton(
        "Abrir Configurações Avançadas",
        icon=ft.Icons.SETTINGS,
        on_click=show_enhanced_settings,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
    )
    
    page.add(
        ft.Column([
            ft.Text("Enhanced Config Interface Test", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Click the button to test the enhanced config dialog:"),
            config_button,
            ft.Divider(),
            ft.Text("Current Settings:", size=16, weight=ft.FontWeight.BOLD),
            ft.Text(f"• API Key: {'***' if settings.get('openai_api_key') else 'Not set'}"),
            ft.Text(f"• Auto-scroll: {settings.get('auto_scroll_on_page_change', True)}"),
            ft.Text(f"• Font size: {settings.get('font_size', 14)}px")
        ], spacing=15)
    )

if __name__ == "__main__":
    print("Testing enhanced config interface...")
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")