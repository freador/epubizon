#!/usr/bin/env python3
"""
Executar Epubizon como aplicação web (navegador)
"""

import flet as ft
from main import main

if __name__ == "__main__":
    print("🌐 Iniciando Epubizon (Web)...")
    print("📱 Acesse: http://localhost:8550")
    ft.app(target=main, view=ft.WEB_BROWSER, port=8550)