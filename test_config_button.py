#!/usr/bin/env python3
"""
Test config button functionality
"""

import flet as ft
from settings_manager import SettingsManager

def main(page: ft.Page):
    page.title = "Config Button Test"
    page.window_width = 800
    page.window_height = 600
    
    settings = SettingsManager()
    settings.load()
    
    def test_show_settings(e):
        """Test settings dialog"""
        print("Config button clicked!")
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
            
        def save_settings(e):
            print("Save button clicked!")
            # Save API key
            api_key = api_key_field.value.strip()
            if api_key:
                settings.set('openai_api_key', api_key)
                
            # Save auto-scroll setting
            settings.set('auto_scroll_on_page_change', auto_scroll_checkbox.value)
            settings.save()
            print(f"Settings saved - API Key: {'***' if api_key else 'empty'}, Auto-scroll: {auto_scroll_checkbox.value}")
                
            close_dialog(e)
            show_info("Sucesso", "Configurações salvas!")
            
        # API key field
        api_key_field = ft.TextField(
            label="Chave da API OpenAI",
            value=settings.get('openai_api_key', ''),
            password=True,
            helper_text="Obtenha em: https://platform.openai.com/api-keys"
        )
        
        # Auto-scroll checkbox
        auto_scroll_checkbox = ft.Checkbox(
            label="Auto-scroll para o topo ao trocar páginas",
            value=settings.get('auto_scroll_on_page_change', True)
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Config Test"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("API OpenAI", size=16, weight=ft.FontWeight.BOLD),
                    api_key_field,
                    ft.Text(
                        "A chave é armazenada localmente e usada apenas para gerar resumos.",
                        size=12,
                        color=ft.Colors.BLUE_GREY_600
                    ),
                    ft.Divider(),
                    ft.Text("Interface", size=16, weight=ft.FontWeight.BOLD),
                    auto_scroll_checkbox,
                    ft.Text(
                        "Quando habilitado, a página rola automaticamente para o topo ao mudar de capítulo.",
                        size=12,
                        color=ft.Colors.BLUE_GREY_600
                    )
                ], spacing=10),
                width=450
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=save_settings)
            ]
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        print("Dialog should be visible now")
    
    def show_info(title: str, message: str):
        """Show info dialog"""
        def close_info(e):
            page.dialog.open = False
            page.update()
            
        info_dialog = ft.AlertDialog(
            title=ft.Text(f"ℹ️ {title}"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_info)]
        )
        
        page.dialog = info_dialog
        info_dialog.open = True
        page.update()
    
    # Simple test UI
    config_button = ft.ElevatedButton(
        "⚙️ Test Config",
        icon=ft.Icons.SETTINGS,
        on_click=test_show_settings
    )
    
    page.add(
        ft.Column([
            ft.Text("Config Button Test", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Click the button below to test the config dialog:"),
            config_button,
            ft.Text(f"Current auto-scroll setting: {settings.get('auto_scroll_on_page_change', True)}")
        ], spacing=20)
    )

if __name__ == "__main__":
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")