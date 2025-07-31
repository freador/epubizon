#!/usr/bin/env python3
"""
Test button click functionality in isolation
"""

import flet as ft

def main(page: ft.Page):
    page.title = "Button Click Test"
    page.window_width = 600
    page.window_height = 400
    
    def button_clicked(e):
        print("Button was clicked!")
        status_text.value = "Button clicked successfully!"
        page.update()
        
        # Show a dialog
        def close_dialog(e):
            page.dialog.open = False
            page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("Button click is working!"),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    status_text = ft.Text("Click the button to test")
    
    test_button = ft.ElevatedButton(
        "Test Button",
        icon=ft.Icons.SETTINGS,
        on_click=button_clicked
    )
    
    page.add(
        ft.Column([
            ft.Text("Button Click Test", size=20, weight=ft.FontWeight.BOLD),
            status_text,
            test_button
        ], spacing=20)
    )

if __name__ == "__main__":
    print("Testing button click...")
    try:
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")