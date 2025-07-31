#!/usr/bin/env python3
"""
Extremely simple test to isolate the config button issue
"""

import flet as ft

class SimpleApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        self.page.title = "Simple Config Test"
        self.page.window_width = 600
        self.page.window_height = 400
    
    def show_settings(self, e):
        print("Settings button clicked - working!")
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Text("This is a test settings dialog"),
            actions=[ft.TextButton("Close", on_click=close_dialog)]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def build_ui(self):
        config_button = ft.ElevatedButton(
            "Settings",
            icon=ft.Icons.SETTINGS,
            on_click=self.show_settings
        )
        
        self.page.add(
            ft.Column([
                ft.Text("Simple Config Button Test", size=20),
                ft.Text("Click the button below:"),
                config_button
            ], spacing=20)
        )

def main(page: ft.Page):
    app = SimpleApp(page)
    return app

if __name__ == "__main__":
    print("Starting simple config test...")
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")