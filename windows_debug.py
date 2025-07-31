#!/usr/bin/env python3
"""
Windows-specific debug for config button
"""

import flet as ft
import os
import sys

def main(page: ft.Page):
    page.title = "Windows Config Debug"
    page.window_width = 600
    page.window_height = 400
    
    # Status text to show what's happening
    status = ft.Text("Ready - click buttons to test", color=ft.Colors.BLUE)
    
    def test_basic_click(e):
        print("=== BASIC BUTTON CLICKED ===")
        status.value = "Basic button works!"
        status.color = ft.Colors.GREEN
        page.update()
    
    def test_config_style_click(e):
        print("=== CONFIG STYLE BUTTON CLICKED ===")
        status.value = "Config style button works!"
        status.color = ft.Colors.ORANGE
        page.update()
        
        # Try to show a simple dialog
        def close_simple(e):
            page.dialog.open = False
            page.update()
            
        simple_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("Windows dialog is working!"),
            actions=[ft.TextButton("OK", on_click=close_simple)]
        )
        
        page.dialog = simple_dialog
        simple_dialog.open = True
        page.update()
    
    def test_lambda_click(e):
        print("=== LAMBDA BUTTON CLICKED ===")
        status.value = "Lambda button works!"
        status.color = ft.Colors.PURPLE
        page.update()
    
    # Test different button configurations
    basic_button = ft.ElevatedButton(
        "Test Basic Click", 
        on_click=test_basic_click
    )
    
    config_button = ft.ElevatedButton(
        "Test Config Style",
        icon=ft.Icons.SETTINGS,
        on_click=test_config_style_click
    )
    
    lambda_button = ft.ElevatedButton(
        "Test Lambda",
        icon=ft.Icons.SETTINGS,
        on_click=lambda e: test_lambda_click(e)
    )
    
    # Add system info
    system_info = ft.Column([
        ft.Text(f"Platform: {sys.platform}", size=12),
        ft.Text(f"Python: {sys.version.split()[0]}", size=12),
        ft.Text(f"OS: {os.name}", size=12),
        ft.Text(f"Encoding: {sys.stdout.encoding}", size=12)
    ])
    
    page.add(
        ft.Column([
            ft.Text("Windows Button Debug", size=20, weight=ft.FontWeight.BOLD),
            status,
            ft.Divider(),
            ft.Text("Test each button:", size=14, weight=ft.FontWeight.BOLD),
            basic_button,
            config_button, 
            lambda_button,
            ft.Divider(),
            ft.Text("System Info:", size=14, weight=ft.FontWeight.BOLD),
            system_info
        ], spacing=10)
    )

if __name__ == "__main__":
    print("=== WINDOWS CONFIG DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Encoding: {sys.stdout.encoding}")
    
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")