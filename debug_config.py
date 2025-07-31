#!/usr/bin/env python3
"""
Debug config button in main app
"""

import flet as ft
from settings_manager import SettingsManager

def debug_main(page: ft.Page):
    page.title = "Debug Config Button"
    page.window_width = 800
    page.window_height = 600
    
    # Initialize settings
    settings = SettingsManager()
    settings.load()
    
    def debug_show_settings(e):
        print("=== DEBUG: Config button clicked! ===")
        
        try:
            def close_dialog(e):
                print("Close dialog clicked")
                page.dialog.open = False
                page.update()
                
            def save_settings(e):
                print("Save settings clicked")
                close_dialog(e)
            
            print("Creating dialog...")
            dialog = ft.AlertDialog(
                title=ft.Text("Debug Config"),
                content=ft.Text("This is a test config dialog"),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.TextButton("Save", on_click=save_settings)
                ]
            )
            
            print("Setting dialog...")
            page.dialog = dialog
            dialog.open = True
            page.update()
            print("Dialog should be visible!")
            
        except Exception as ex:
            print(f"Exception in show_settings: {ex}")
            import traceback
            traceback.print_exc()
    
    # Test if the button works
    config_button = ft.ElevatedButton(
        "Config",
        icon=ft.Icons.SETTINGS,
        on_click=debug_show_settings
    )
    
    # Add status text
    status_text = ft.Text("Click Config button to test")
    
    page.add(
        ft.Column([
            ft.Text("Config Button Debug", size=20, weight=ft.FontWeight.BOLD),
            status_text,
            config_button,
            ft.Text(f"Settings loaded: auto_scroll = {settings.get('auto_scroll_on_page_change', 'Not found')}")
        ], spacing=20)
    )

if __name__ == "__main__":
    print("=== Starting Config Button Debug ===")
    try:
        ft.app(target=debug_main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")