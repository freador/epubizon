#!/usr/bin/env python3
"""
Test page navigation for config
"""

import flet as ft
from config_page import ConfigPage

class TestApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_page = "main"
        self.config_page = ConfigPage(self.page, self)
        self.setup_page()
        self.show_main_page()
    
    def setup_page(self):
        self.page.title = "Test Page Navigation"
        self.page.window_width = 900
        self.page.window_height = 700
    
    def show_config_page(self):
        """Show the configuration page"""
        print("Navigating to config page...")
        self.current_page = "config"
        
        # Clear the page
        self.page.controls.clear()
        
        # Add config page content
        config_content = self.config_page.build_config_page()
        self.page.add(config_content)
        self.page.update()
        
        print("Config page displayed")
    
    def show_main_page(self):
        """Show the main page"""
        print("Navigating to main page...")
        self.current_page = "main"
        
        # Clear the page
        self.page.controls.clear()
        
        # Build simple main page
        header = ft.Container(
            content=ft.Row([
                ft.Text("Test Main Page", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Open Config",
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda e: self.show_config_page(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE
                    )
                )
            ]),
            padding=20,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10
        )
        
        content = ft.Container(
            content=ft.Column([
                ft.Text("This is the main page", size=16),
                ft.Text("Click 'Open Config' to test navigation", size=14),
                ft.Divider(),
                ft.Text("Page navigation test:", weight=ft.FontWeight.BOLD),
                ft.Text("• Main page loads correctly"),
                ft.Text("• Config button navigates to config page"),
                ft.Text("• Config page has back button"),
                ft.Text("• Back button returns to main page")
            ], spacing=10),
            padding=20
        )
        
        self.page.add(
            ft.Column([
                header,
                ft.Container(height=20),
                content
            ])
        )
        self.page.update()
        
        print("Main page displayed")

def main(page: ft.Page):
    print("Starting page navigation test...")
    try:
        app = TestApp(page)
        return app
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error on page
        page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))
        page.update()

if __name__ == "__main__":
    print("=== PAGE NAVIGATION TEST ===")
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")