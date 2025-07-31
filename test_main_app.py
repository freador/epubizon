#!/usr/bin/env python3
"""
Test the main app with config button fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import main
import flet as ft

if __name__ == "__main__":
    print("=== Testing Main App Config Button ===")
    try:
        print("Starting app...")
        ft.app(target=main, view=ft.FLET_APP)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")