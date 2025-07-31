#!/usr/bin/env python3
"""
Dedicated configuration page for Epubizon
"""

import flet as ft
from settings_manager import SettingsManager

class ConfigPage:
    def __init__(self, page: ft.Page, main_app=None):
        self.page = page
        self.main_app = main_app
        self.settings = SettingsManager()
        self.settings.load()
        
    def validate_api_key(self, api_key):
        """Validate OpenAI API key format"""
        if not api_key:
            return True, ""  # Empty is allowed
        if not api_key.startswith('sk-'):
            return False, "Chave da API deve começar com 'sk-'"
        if len(api_key) < 40:
            return False, "Chave da API parece muito curta"
        return True, ""
    
    def on_api_key_change(self, e):
        """Validate API key as user types"""
        api_key = self.api_key_field.value.strip()
        is_valid, error_msg = self.validate_api_key(api_key)
        
        if not is_valid:
            self.api_key_field.error_text = error_msg
            self.save_button.disabled = True
        else:
            self.api_key_field.error_text = None
            self.save_button.disabled = False
        
        self.page.update()
    
    def save_settings(self, e):
        """Save all settings"""
        print("Saving settings from config page...")
        
        # Validate API key before saving
        api_key = self.api_key_field.value.strip()
        is_valid, error_msg = self.validate_api_key(api_key)
        
        if not is_valid:
            self.api_key_field.error_text = error_msg
            self.page.update()
            return
        
        # Save API key (allow empty for removal)
        self.settings.set('openai_api_key', api_key)
        print(f"API key saved: {'***' if api_key else 'removed'}")
            
        # Save auto-scroll setting
        auto_scroll_value = self.auto_scroll_checkbox.value
        self.settings.set('auto_scroll_on_page_change', auto_scroll_value)
        print(f"Auto-scroll setting saved: {auto_scroll_value}")
        
        # Save font size setting
        font_size_value = int(self.font_size_dropdown.value)
        self.settings.set('font_size', font_size_value)
        print(f"Font size saved: {font_size_value}")
        
        self.settings.save()
        
        # Show success message
        self.show_success_message()
    
    def show_success_message(self):
        """Show success feedback"""
        # Temporarily change button to show success
        original_text = self.save_button.text
        original_color = self.save_button.style.bgcolor if self.save_button.style else None
        
        self.save_button.text = "Salvo!"
        self.save_button.style = ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
        self.page.update()
        
        # Reset after 2 seconds
        import threading
        def reset_button():
            import time
            time.sleep(2)
            self.save_button.text = original_text
            self.save_button.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            if hasattr(self, 'page'):
                self.page.update()
        
        threading.Thread(target=reset_button, daemon=True).start()
    
    def go_back(self, e):
        """Return to main application"""
        print("Returning to main application...")
        if self.main_app:
            self.main_app.show_main_page()
    
    def build_config_page(self):
        """Build the configuration page UI"""
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.BLUE,
                    tooltip="Voltar",
                    on_click=self.go_back
                ),
                ft.Text(
                    "Configurações do Epubizon",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE
                ),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE, size=30)
            ]),
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10
        )
        
        # API key field with validation
        self.api_key_field = ft.TextField(
            label="Chave da API OpenAI",
            value=self.settings.get('openai_api_key', ''),
            password=True,
            hint_text="sk-...",
            helper_text="Obtenha gratuitamente em: https://platform.openai.com/api-keys",
            on_change=self.on_api_key_change,
            border_radius=8,
            filled=True,
            width=500
        )
        
        # Auto-scroll checkbox
        self.auto_scroll_checkbox = ft.Checkbox(
            label="Rolar automaticamente para o topo ao trocar páginas",
            value=self.settings.get('auto_scroll_on_page_change', True),
            check_color=ft.Colors.WHITE,
            active_color=ft.Colors.BLUE
        )
        
        # Font size dropdown
        self.font_size_dropdown = ft.Dropdown(
            label="Tamanho da fonte",
            value=str(self.settings.get('font_size', 14)),
            options=[
                ft.dropdown.Option("10", "Muito pequeno (10px)"),
                ft.dropdown.Option("12", "Pequeno (12px)"),
                ft.dropdown.Option("14", "Normal (14px)"),
                ft.dropdown.Option("16", "Grande (16px)"),
                ft.dropdown.Option("18", "Muito grande (18px)"),
                ft.dropdown.Option("20", "Extra grande (20px)")
            ],
            border_radius=8,
            filled=True,
            width=300
        )
        
        # Save button
        self.save_button = ft.ElevatedButton(
            "Salvar Configurações",
            icon=ft.Icons.SAVE,
            on_click=self.save_settings,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            ),
            width=200,
            height=50
        )
        
        # OpenAI API Section
        api_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.GREEN, size=24),
                    ft.Text("Inteligência Artificial", size=20, weight=ft.FontWeight.BOLD)
                ]),
                ft.Divider(color=ft.Colors.GREEN),
                self.api_key_field,
                ft.Container(
                    content=ft.Column([
                        ft.Text("• Necessário para gerar resumos inteligentes", size=12),
                        ft.Text("• Sua chave é armazenada localmente com segurança", size=12),
                        ft.Text("• Nunca compartilhamos seus dados", size=12)
                    ]),
                    padding=ft.padding.only(left=20, top=10)
                )
            ], spacing=15),
            padding=20,
            border=ft.border.all(2, ft.Colors.GREEN_300),
            border_radius=10,
            bgcolor=ft.Colors.GREEN_50
        )
        
        # Interface Section
        interface_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TUNE, color=ft.Colors.ORANGE, size=24),
                    ft.Text("Interface", size=20, weight=ft.FontWeight.BOLD)
                ]),
                ft.Divider(color=ft.Colors.ORANGE),
                self.auto_scroll_checkbox,
                ft.Container(height=15),
                self.font_size_dropdown,
                ft.Container(
                    content=ft.Column([
                        ft.Text("• Auto-scroll melhora a experiência de leitura", size=12),
                        ft.Text("• Tamanho da fonte afeta a legibilidade do texto", size=12)
                    ]),
                    padding=ft.padding.only(left=20, top=10)
                )
            ], spacing=15),
            padding=20,
            border=ft.border.all(2, ft.Colors.ORANGE_300),
            border_radius=10,
            bgcolor=ft.Colors.ORANGE_50
        )
        
        # Action buttons
        action_row = ft.Row([
            ft.Container(expand=True),  # Spacer
            ft.ElevatedButton(
                "Cancelar",
                icon=ft.Icons.CANCEL,
                on_click=self.go_back,
                style=ft.ButtonStyle(color=ft.Colors.GREY)
            ),
            ft.Container(width=20),  # Spacer
            self.save_button
        ])
        
        # Main content
        main_content = ft.Column([
            header,
            ft.Container(height=20),
            api_section,
            ft.Container(height=20),
            interface_section,
            ft.Container(height=30),
            action_row,
            ft.Container(height=20)
        ])
        
        # Scrollable container
        config_container = ft.Container(
            content=ft.Column([main_content], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=20
        )
        
        return config_container