#!/usr/bin/env python3
"""
Windows workaround for config dialog
"""

import flet as ft
import os
import sys
from settings_manager import SettingsManager

class WindowsConfigApp:
    def __init__(self, page):
        self.page = page
        self.settings = SettingsManager()
        self.settings.load()
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        self.page.title = "Windows Config Workaround"
        self.page.window_width = 800
        self.page.window_height = 600
        
    def show_config_native(self, e):
        """Show config using native Windows approach"""
        print("Native config called!")
        
        # Simple dialog approach
        def close_config(e):
            print("Closing config")
            self.page.dialog.open = False
            self.page.update()
        
        def save_config(e):
            print("Saving config")
            
            # Get values
            api_key = self.api_key_input.value.strip() if hasattr(self, 'api_key_input') else ""
            auto_scroll = self.auto_scroll_cb.value if hasattr(self, 'auto_scroll_cb') else True
            
            # Save settings
            if api_key:
                self.settings.set('openai_api_key', api_key)
            self.settings.set('auto_scroll_on_page_change', auto_scroll)
            self.settings.save()
            
            print(f"Saved: API={bool(api_key)}, Scroll={auto_scroll}")
            
            close_config(e)
            
            # Show success message
            self.show_success("Settings saved successfully!")
        
        # Create input fields
        self.api_key_input = ft.TextField(
            label="OpenAI API Key",
            value=self.settings.get('openai_api_key', ''),
            password=True,
            width=400
        )
        
        self.auto_scroll_cb = ft.Checkbox(
            label="Auto-scroll on page change",
            value=self.settings.get('auto_scroll_on_page_change', True)
        )
        
        # Create dialog
        config_dialog = ft.AlertDialog(
            title=ft.Text("Configuration"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("OpenAI Settings", weight=ft.FontWeight.BOLD),
                    self.api_key_input,
                    ft.Text("Get your key at: https://platform.openai.com/api-keys", size=10),
                    ft.Divider(),
                    ft.Text("Interface Settings", weight=ft.FontWeight.BOLD),
                    self.auto_scroll_cb,
                ], spacing=10),
                width=450,
                height=250
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_config),
                ft.ElevatedButton("Save", on_click=save_config)
            ]
        )
        
        # Show dialog
        self.page.dialog = config_dialog
        config_dialog.open = True
        self.page.update()
        print("Dialog should be visible")
    
    def show_success(self, message):
        """Show success message"""
        def close_success(e):
            self.page.dialog.open = False
            self.page.update()
        
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_success)]
        )
        
        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()
        
    def test_simple_click(self, e):
        """Test if basic clicks work"""
        print("Simple click works!")
        self.status_text.value = "Simple click successful!"
        self.status_text.color = ft.Colors.GREEN
        self.page.update()
    
    def build_ui(self):
        # Status text
        self.status_text = ft.Text("Ready", color=ft.Colors.BLUE)
        
        # Test buttons
        simple_btn = ft.ElevatedButton(
            "Test Simple Click",
            on_click=self.test_simple_click
        )
        
        config_btn = ft.ElevatedButton(
            "Open Config",
            icon=ft.Icons.SETTINGS,
            on_click=self.show_config_native
        )
        
        # Current settings display
        current_settings = ft.Column([
            ft.Text("Current Settings:", weight=ft.FontWeight.BOLD),
            ft.Text(f"API Key: {'Set' if self.settings.get('openai_api_key') else 'Not set'}"),
            ft.Text(f"Auto-scroll: {self.settings.get('auto_scroll_on_page_change', True)}")
        ])
        
        # Main layout
        self.page.add(
            ft.Column([
                ft.Text("Windows Config Workaround", size=20, weight=ft.FontWeight.BOLD),
                self.status_text,
                ft.Divider(),
                ft.Text("Test buttons:", weight=ft.FontWeight.BOLD),
                simple_btn,
                config_btn,
                ft.Divider(),
                current_settings
            ], spacing=15)
        )

def main(page: ft.Page):
    print("Starting Windows workaround app...")
    try:
        app = WindowsConfigApp(page)
        return app
    except Exception as e:
        print(f"Error creating app: {e}")
        import traceback
        traceback.print_exc()
        
        # Show basic error
        page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
        page.update()

if __name__ == "__main__":
    print("=== WINDOWS WORKAROUND TEST ===")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    try:
        # Try different Flet modes
        if len(sys.argv) > 1 and sys.argv[1] == "web":
            print("Using web mode...")
            ft.app(target=main, view=ft.WEB_BROWSER, port=8080)
        else:
            print("Using desktop mode...")
            ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")