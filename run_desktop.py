#!/usr/bin/env python3
"""
Executar Epubizon como aplicação desktop nativa
"""

import flet as ft
from main import main

if __name__ == "__main__":
    print("🚀 Iniciando Epubizon (Desktop)...")
    ft.app(target=main, view=ft.FLET_APP)