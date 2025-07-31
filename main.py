#!/usr/bin/env python3
"""
Epubizon - Versão Simples com Flet
Interface moderna e estável
"""

import flet as ft
import os
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any

# Importa os módulos principais
from epub_handler import EpubHandler
from pdf_handler import PdfHandler
from settings_manager import SettingsManager
from ai_summarizer import AISummarizer


class EpubizonApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # Gerenciadores
        self.settings = SettingsManager()
        self.epub_handler = EpubHandler()
        self.pdf_handler = PdfHandler()
        self.ai_summarizer = AISummarizer()
        
        # Estado
        self.current_book = None
        self.current_chapter = 0
        self.chapters = []
        self.book_metadata = {}
        
        # UI Components
        self.book_title = ft.Text("Nenhum livro carregado", size=16, weight=ft.FontWeight.BOLD)
        self.content_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.chapters_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
        self.status_bar = ft.Text("Pronto", size=12, color=ft.Colors.BLUE_GREY_600)
        self.page_info = ft.Text("Página: - / -", size=12)
        
        self.build_ui()
        
    def setup_page(self):
        """Configura a página"""
        self.page.title = "📚 Epubizon - Leitor EPUB & PDF"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.padding = 20
        
    def build_ui(self):
        """Constrói a interface"""
        # File picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.file_picker)
        
        # Header
        header = ft.Row([
            ft.ElevatedButton(
                "📂 Abrir Arquivo",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: self.file_picker.pick_files(
                    allowed_extensions=["epub", "pdf"],
                    dialog_title="Selecionar arquivo EPUB ou PDF"
                )
            ),
            ft.Container(width=20),
            self.book_title,
            ft.Container(expand=True),
            ft.ElevatedButton(
                "✨ Resumir",
                icon=ft.Icons.AUTO_AWESOME,
                on_click=self.summarize_chapter,
                disabled=True,
                ref=ft.Ref[ft.ElevatedButton]()
            ),
            ft.ElevatedButton(
                "⚙️ Config",
                icon=ft.Icons.SETTINGS,
                on_click=self.show_settings
            )
        ])
        
        # Sidebar
        sidebar = ft.Container(
            content=ft.Column([
                ft.Text("📚 Navegação", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=2),
                
                ft.Text("📖 Capítulos", size=14, weight=ft.FontWeight.W_500),
                ft.Container(
                    content=self.chapters_list,
                    height=400,
                    width=300,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=8,
                    padding=10
                ),
                
                # Navigation buttons
                ft.Row([
                    ft.ElevatedButton(
                        "← Anterior",
                        on_click=self.prev_chapter,
                        disabled=True,
                        ref=ft.Ref[ft.ElevatedButton]()
                    ),
                    ft.ElevatedButton(
                        "Próximo →",
                        on_click=self.next_chapter,
                        disabled=True,
                        ref=ft.Ref[ft.ElevatedButton]()  
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                self.page_info,
                
                ft.Divider(),
                ft.Text("⌨️ Atalhos", size=12, weight=ft.FontWeight.W_500),
                ft.Text(
                    "← → Navegar\nF1 Resumir\nCtrl+O Abrir",
                    size=10,
                    color=ft.Colors.BLUE_GREY_600
                )
            ], spacing=10),
            padding=20
        )
        
        # Content area
        content_area = ft.Container(
            content=ft.Column([
                ft.Text("📄 Conteúdo", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=2),
                ft.Container(
                    content=self.content_column,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=8,
                    padding=20
                )
            ]),
            expand=True,
            padding=20
        )
        
        # Main layout
        main_row = ft.Row([
            sidebar,
            ft.VerticalDivider(width=1),
            content_area
        ], expand=True)
        
        # Add to page
        self.page.add(
            ft.Column([
                header,
                ft.Divider(),
                main_row,
                ft.Divider(),
                self.status_bar
            ], expand=True, spacing=10)
        )
        
        self.show_welcome()
        
        # Store refs
        self.summary_btn = header.controls[4]
        self.prev_btn = sidebar.content.controls[4].controls[0]
        self.next_btn = sidebar.content.controls[4].controls[1]
        
    def show_welcome(self):
        """Mostra mensagem de boas-vindas"""
        welcome = ft.Column([
            ft.Text("🎉 Bem-vindo ao Epubizon v2.0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Text("Interface moderna com Flet + Flutter", size=16, color=ft.Colors.BLUE_GREY),
            ft.Divider(),
            
            ft.Text("✨ Recursos:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("• Interface moderna e responsiva"),
            ft.Text("• Navegação rápida por capítulos"),
            ft.Text("• Resumos inteligentes com IA"),
            ft.Text("• Suporte para EPUB e PDF"),
            
            ft.Divider(),
            ft.Text("🚀 Como usar:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("1. Clique em '📂 Abrir Arquivo' para começar"),
            ft.Text("2. Navegue pelos capítulos na barra lateral"),
            ft.Text("3. Use '✨ Resumir' para gerar resumos com IA"),
            
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Text(
                        "💡 Configure sua chave OpenAI nas configurações para usar resumos!",
                        color=ft.Colors.WHITE
                    ),
                    padding=15
                ),
                color=ft.Colors.ORANGE
            )
        ], spacing=10)
        
        self.content_column.controls = [welcome]
        self.page.update()
        
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """Callback quando arquivo é selecionado"""
        print(f"File picker event: {e}")
        if e.files:
            file_info = e.files[0]
            print(f"Selected file: {file_info.name}, size: {file_info.size}")
            
            # Try to use file path if available
            if hasattr(file_info, 'path') and file_info.path:
                # Desktop mode - use file path
                print(f"Using file path: {file_info.path}")
                threading.Thread(target=self.load_book_thread, args=(file_info.path,), daemon=True).start()
            elif hasattr(file_info, 'read') or hasattr(e, 'read'):
                # Web/mobile mode - handle file data
                print("Web mode detected - reading file data")
                threading.Thread(target=self.load_book_from_picker, args=(file_info,), daemon=True).start()
            else:
                # Fallback - try to construct path from name
                print("Trying fallback path construction")
                file_name = file_info.name
                # Check if file exists in current directory
                if os.path.exists(file_name):
                    threading.Thread(target=self.load_book_thread, args=(file_name,), daemon=True).start()
                else:
                    self.show_error("Erro", f"Não foi possível acessar o arquivo '{file_name}'. Certifique-se de que o arquivo esteja acessível ou copie-o para a pasta do aplicativo.")
        else:
            print("No files selected")
    
    def load_book_from_picker(self, file_info):
        """Carrega livro a partir do file picker (modo web)"""
        try:
            print(f"Loading book from picker: {file_info.name}")
            self.update_status("Lendo arquivo...")
            
            # Try to read file data
            file_data = None
            if hasattr(file_info, 'read'):
                file_data = file_info.read()
            elif hasattr(file_info, 'data'):
                file_data = file_info.data
            else:
                raise ValueError("Não foi possível ler os dados do arquivo")
                
            file_ext = Path(file_info.name).suffix.lower()
            print(f"File extension: {file_ext}")
            
            if file_ext == '.epub':
                print("Loading EPUB from data...")
                book_data = self.epub_handler.load_book_from_data(file_data)
            elif file_ext == '.pdf':
                print("Loading PDF from data...")
                book_data = self.pdf_handler.load_book_from_data(file_data)
            else:
                raise ValueError(f"Formato não suportado: {file_ext}")
            
            print(f"Book loaded successfully: {book_data.get('metadata', {}).get('title', 'No title')}")
                
            # Update state
            self.current_book = book_data
            self.chapters = book_data.get('chapters', [])
            self.book_metadata = book_data.get('metadata', {})
            self.current_chapter = 0
            
            # Update UI in main thread
            self.page.run_thread(self.on_book_loaded)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error loading book from picker: {error_msg}")
            self.page.run_thread(lambda: self.show_error("Erro ao carregar livro", error_msg))
    
    def load_book_thread(self, file_path: str):
        """Carrega livro em thread separada"""
        try:
            print(f"Loading book: {file_path}")
            self.update_status("Carregando livro...")
            
            file_ext = Path(file_path).suffix.lower()
            print(f"File extension: {file_ext}")
            
            if file_ext == '.epub':
                print("Loading EPUB...")
                book_data = self.epub_handler.load_book(file_path)
            elif file_ext == '.pdf':
                print("Loading PDF...")
                book_data = self.pdf_handler.load_book(file_path)
            else:
                raise ValueError(f"Formato não suportado: {file_ext}")
            
            print(f"Book loaded successfully: {book_data.get('metadata', {}).get('title', 'No title')}")
                
            # Update state
            self.current_book = book_data
            self.chapters = book_data.get('chapters', [])
            self.book_metadata = book_data.get('metadata', {})
            self.current_chapter = 0
            
            # Update UI in main thread
            self.page.run_thread(self.on_book_loaded)
            
        except Exception as e:
            error_msg = str(e)
            self.page.run_thread(lambda: self.show_error("Erro ao carregar livro", error_msg))
            
    def on_book_loaded(self):
        """Callback quando livro é carregado"""
        print("Book loaded callback started")
        
        # Update title
        title = self.book_metadata.get('title', 'Título desconhecido')
        author = self.book_metadata.get('creator', self.book_metadata.get('author', ''))
        
        if author:
            self.book_title.value = f"{title} - {author}"
        else:
            self.book_title.value = title
            
        print(f"Book title set: {self.book_title.value}")
        print(f"Total chapters: {len(self.chapters)}")
            
        # Update chapters list
        self.update_chapters_list()
        
        # Load first chapter
        if self.chapters:
            print("Loading first chapter")
            self.load_chapter(0)
        else:
            print("No chapters found")
        
        # Enable buttons
        print("Enabling buttons")
        try:
            self.summary_btn.disabled = False
            self.prev_btn.disabled = False
            self.next_btn.disabled = False
        except Exception as e:
            print(f"Error enabling buttons: {e}")
        
        self.update_status(f"Livro carregado: {title}")
        self.page.update()
        print("Book loaded callback completed")
        
    def update_chapters_list(self):
        """Atualiza lista de capítulos"""
        self.chapters_list.controls.clear()
        
        for i, chapter in enumerate(self.chapters):
            title = chapter.get('title', f'Capítulo {i+1}')
            
            # Create chapter button
            btn = ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=16),
                    ft.Column([
                        ft.Text(title, size=12, weight=ft.FontWeight.W_500),
                        ft.Text(f"Cap. {i+1}", size=10, color=ft.Colors.BLUE_GREY_600)
                    ], spacing=2, expand=True)
                ], spacing=10),
                on_click=lambda e, idx=i: self.select_chapter(idx),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_50 if i == self.current_chapter else None,
                    side=ft.BorderSide(1, ft.Colors.BLUE) if i == self.current_chapter else None
                )
            )
            
            self.chapters_list.controls.append(btn)
            
        self.page.update()
        
    def select_chapter(self, chapter_index: int):
        """Seleciona um capítulo"""
        threading.Thread(target=self.load_chapter_thread, args=(chapter_index,), daemon=True).start()
        
    def load_chapter_thread(self, chapter_index: int):
        """Carrega capítulo em thread"""
        try:
            print(f"Loading chapter {chapter_index}")
            if not self.chapters or chapter_index < 0 or chapter_index >= len(self.chapters):
                print(f"Invalid chapter index: {chapter_index}, total chapters: {len(self.chapters) if self.chapters else 0}")
                return
                
            self.current_chapter = chapter_index
            chapter = self.chapters[chapter_index]
            
            chapter_title = chapter.get('title', f'Capítulo {chapter_index+1}')
            print(f"Loading chapter: {chapter_title}")
            self.update_status(f"Carregando: {chapter_title}")
            
            content = ""
            handler_type = self.current_book.get('handler') if self.current_book else None
            print(f"Handler type: {handler_type}")
            
            if handler_type == 'epub':
                print("Using EPUB handler")
                content = self.epub_handler.get_chapter_content(chapter_index)
            elif handler_type == 'pdf':
                print("Using PDF handler")
                # Store chapters in PDF handler for content retrieval
                if not hasattr(self.pdf_handler, '_chapters'):
                    self.pdf_handler._chapters = self.chapters
                content = self.pdf_handler.get_chapter_content(chapter_index)
            else:
                print(f"Unknown or missing handler: {handler_type}")
                content = f"Conteúdo do {chapter_title}\n\nEste é um conteúdo de exemplo. O handler '{handler_type}' não foi reconhecido ou o livro não foi carregado corretamente."
                
            print(f"Content loaded, length: {len(content)} characters")
                
            # Update UI in main thread
            self.page.run_thread(lambda: self.on_chapter_loaded(content, chapter_index))
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error loading chapter {chapter_index}: {error_msg}")
            self.page.run_thread(lambda: self.show_error("Erro ao carregar capítulo", error_msg))
            
    def on_chapter_loaded(self, content: str, chapter_index: int):
        """Callback quando capítulo é carregado"""
        chapter = self.chapters[chapter_index]
        title = chapter.get('title', f'Capítulo {chapter_index+1}')
        
        # Update content
        self.content_column.controls = [
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Divider(),
            ft.Text(content, size=14, selectable=True)
        ]
        
        # Update chapters list selection
        self.update_chapters_list()
        
        # Update page info
        self.page_info.value = f"Página: {chapter_index + 1} / {len(self.chapters)}"
        
        self.update_status(f"Capítulo carregado: {title}")
        self.page.update()
        
    def load_chapter(self, chapter_index: int):
        """Carrega capítulo (versão síncrona)"""
        threading.Thread(target=self.load_chapter_thread, args=(chapter_index,), daemon=True).start()
        
    def prev_chapter(self, e):
        """Capítulo anterior"""
        if self.current_chapter > 0:
            self.load_chapter(self.current_chapter - 1)
            
    def next_chapter(self, e):
        """Próximo capítulo"""
        if self.current_chapter < len(self.chapters) - 1:
            self.load_chapter(self.current_chapter + 1)
            
    def summarize_chapter(self, e):
        """Gera resumo do capítulo"""
        if not self.chapters:
            self.show_error("Aviso", "Nenhum capítulo carregado")
            return
            
        api_key = self.settings.get('openai_api_key')
        if not api_key:
            self.show_error("Aviso", "Configure sua chave OpenAI nas configurações")
            return
            
        threading.Thread(target=self.summarize_thread, daemon=True).start()
        
    def summarize_thread(self):
        """Thread para gerar resumo"""
        try:
            # Get chapter content (simple text extraction)
            if len(self.content_column.controls) >= 3:
                content = self.content_column.controls[2].value
            else:
                content = "Sem conteúdo"
                
            if not content or content == "Sem conteúdo":
                self.page.run_thread(lambda: self.show_error("Aviso", "Nenhum conteúdo para resumir"))
                return
                
            self.update_status("Gerando resumo...")
            
            api_key = self.settings.get('openai_api_key')
            summary = self.ai_summarizer.generate_summary(content, api_key)
            
            self.page.run_thread(lambda: self.show_summary(summary))
            
        except Exception as e:
            self.page.run_thread(lambda: self.show_error("Erro", f"Erro ao gerar resumo: {str(e)}"))
            
    def show_summary(self, summary: str):
        """Mostra resumo em diálogo"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text("✨ Resumo Gerado por IA"),
            content=ft.Container(
                content=ft.Text(summary, selectable=True),
                width=500,
                height=300
            ),
            actions=[
                ft.TextButton("Fechar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.update_status("Resumo gerado")
        self.page.update()
        
    def show_settings(self, e):
        """Mostra configurações"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        def save_settings(e):
            # Save API key
            api_key = api_key_field.value.strip()
            if api_key:
                self.settings.set('openai_api_key', api_key)
                self.settings.save()
                
            close_dialog(e)
            self.show_info("Sucesso", "Configurações salvas!")
            
        # API key field
        api_key_field = ft.TextField(
            label="Chave da API OpenAI",
            value=self.settings.get('openai_api_key', ''),
            password=True,
            helper_text="Obtenha em: https://platform.openai.com/api-keys"
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("⚙️ Configurações"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("API OpenAI", size=16, weight=ft.FontWeight.BOLD),
                    api_key_field,
                    ft.Text(
                        "A chave é armazenada localmente e usada apenas para gerar resumos.",
                        size=12,
                        color=ft.Colors.BLUE_GREY_600
                    )
                ], spacing=10),
                width=400
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Salvar", on_click=save_settings)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def show_error(self, title: str, message: str):
        """Mostra erro"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text(f"❌ {title}"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def show_info(self, title: str, message: str):
        """Mostra informação"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text(f"ℹ️ {title}"),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def update_status(self, message: str):
        """Atualiza status"""
        self.status_bar.value = message
        if hasattr(self, 'page'):
            self.page.update()


def main(page: ft.Page):
    EpubizonApp(page)


if __name__ == "__main__":
    # Try different modes based on environment
    import os
    if os.environ.get('WSL_DISTRO_NAME'):
        # Running in WSL - try desktop mode first, fallback to web
        try:
            ft.app(target=main, view=ft.FLET_APP)
        except:
            print("Desktop mode failed, trying web mode...")
            print("Open http://localhost:8550 in your Windows browser")
            ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
    else:
        # Not in WSL - use desktop mode
        ft.app(target=main, view=ft.FLET_APP)