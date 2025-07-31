#!/usr/bin/env python3
"""
Epubizon - Versão Simples com Flet
Interface moderna e estável
"""

import flet as ft
import os
import sys
import threading
import tempfile
import base64
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any

# Importa os módulos principais
from epub_handler import EpubHandler
from pdf_handler import PdfHandler
from settings_manager import SettingsManager
from ai_summarizer import AISummarizer
from config_page import ConfigPage


class EpubizonApp:
    def __init__(self, page: ft.Page):
        try:
            print("Inicializando EpubizonApp...")
            self.page = page
            print("Configurando página...")
            self.setup_page()
            
            print("Inicializando gerenciadores...")
            # Gerenciadores
            self.settings = SettingsManager()
            self.settings.load()  # Load settings from file
            self.epub_handler = EpubHandler()
            self.pdf_handler = PdfHandler()
            self.ai_summarizer = AISummarizer()
            
            print("Inicializando estado...")
            # Estado
            self.current_book = None
            self.current_chapter = 0
            self.chapters = []
            self.book_metadata = {}
            
            # Page navigation
            self.current_page = "main"  # "main" or "config"
            self.config_page = ConfigPage(self.page, self)
            
            print("Criando componentes UI...")
            # UI Components
            self.book_title = ft.Text("Nenhum livro carregado", size=16, weight=ft.FontWeight.BOLD)
            self.content_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
            self.chapters_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)
            self.status_bar = ft.Text("Pronto", size=12, color=ft.Colors.BLUE_GREY_600)
            self.page_info = ft.Text("Página: - / -", size=12)
            
            # Loading indicator - centered vertically and horizontally
            self.loading_overlay = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(color=ft.Colors.BLUE, stroke_width=4),
                    ft.Text("Carregando...", size=16, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
                    ft.Text("", size=12, color=ft.Colors.BLUE_GREY_600, ref=ft.Ref[ft.Text]())
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                spacing=10),
                bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                alignment=ft.alignment.center,
                visible=False,
                expand=True
            )
            self.loading_message = self.loading_overlay.content.controls[2]
            
            print("Construindo UI...")
            self.build_ui()
            # Diretório temporário para imagens
            self.temp_images = {}
            self.temp_dir = tempfile.mkdtemp(prefix="epubizon_images_")
            print(f"Diretório temporário criado: {self.temp_dir}")
            
            print("EpubizonApp inicializado com sucesso!")
            
        except Exception as e:
            print(f"ERRO na inicialização do EpubizonApp: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def setup_page(self):
        """Configura a página"""
        self.page.title = "📚 Epubizon - Leitor EPUB & PDF"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.padding = 20
        
        # Set application icon
        try:
            self.page.window_icon = "assets/faicon.png"
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
        
        # Set up keyboard shortcuts
        self.page.on_keyboard_event = self.on_keyboard_event
        
        # Set up cleanup on close
        self.page.on_window_event = self.on_window_event
        
    def build_ui(self):
        """Constrói a interface"""
        # File picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.file_picker)
        
        # Header
        header = ft.Row([
            # Logo
            ft.Container(
                content=ft.Image(
                    src="assets/logo.png",
                    width=40,
                    height=40,
                    fit=ft.ImageFit.CONTAIN,
                    error_content=ft.Icon(ft.Icons.BOOK, size=40, color=ft.Colors.BLUE)
                ),
                margin=ft.margin.only(right=10)
            ),
            ft.ElevatedButton(
                "Abrir Arquivo",
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
                "Resumir",
                icon=ft.Icons.AUTO_AWESOME,
                on_click=self.summarize_chapter,
                disabled=True,
                ref=ft.Ref[ft.ElevatedButton]()
            ),
            ft.ElevatedButton(
                "Config",
                icon=ft.Icons.SETTINGS,
                on_click=lambda e: self.debug_show_settings(e)
            )
        ])
        
        # Sidebar
        sidebar = ft.Container(
            content=ft.Column([
                ft.Text("Navegação", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=2),
                
                ft.Text("Capítulos", size=14, weight=ft.FontWeight.W_500),
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
                    "← → ↑ ↓ Navegar\nF1 Resumir\nCtrl+O Abrir",
                    size=10,
                    color=ft.Colors.BLUE_GREY_600
                )
            ], spacing=10),
            padding=20
        )
        
        # Scroll indicator
        self.scroll_indicator = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=ft.Colors.BLUE_GREY_400),
                ft.Text("Role para ver mais conteúdo", size=11, color=ft.Colors.BLUE_GREY_600),
                ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=ft.Colors.BLUE_GREY_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_GREY_50,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            visible=False
        )
        
        # Content area
        content_area = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📄 Conteúdo", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.scroll_indicator
                ]),
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
        
        # Main content
        main_content = ft.Column([
            header,
            ft.Divider(),
            main_row,
            ft.Divider(),
            self.status_bar
        ], expand=True, spacing=10)
        
        # Add to page with loading overlay
        self.page.add(
            ft.Stack([
                main_content,
                self.loading_overlay
            ], expand=True)
        )
        
        self.show_welcome()
        
        # Store refs
        self.summary_btn = header.controls[5]  # Updated index due to logo container
        self.prev_btn = sidebar.content.controls[4].controls[0]
        self.next_btn = sidebar.content.controls[4].controls[1]
        
    def show_welcome(self):
        """Mostra mensagem de boas-vindas"""
        welcome = ft.Column([
            # Logo and title
            ft.Row([
                ft.Image(
                    src="assets/logo.png",
                    width=60,
                    height=60,
                    fit=ft.ImageFit.CONTAIN,
                    error_content=ft.Icon(ft.Icons.BOOK, size=60, color=ft.Colors.BLUE)
                ),
                ft.Column([
                    ft.Text("Bem-vindo ao Epubizon v2.0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                    ft.Text("Interface moderna com Flet + Flutter", size=16, color=ft.Colors.BLUE_GREY),
                ], spacing=5)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Divider(),
            
            ft.Text("Recursos:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("• Interface moderna e responsiva"),
            ft.Text("• Navegação rápida por capítulos"),
            ft.Text("• Resumos inteligentes com IA"),
            ft.Text("• Suporte para EPUB e PDF"),
            
            ft.Divider(),
            ft.Text("Como usar:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("1. Clique em 'Abrir Arquivo' para começar"),
            ft.Text("2. Navegue pelos capítulos na barra lateral"),
            ft.Text("3. Use 'Resumir' para gerar resumos com IA"),
            
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Text(
                        "Configure sua chave OpenAI nas configurações para usar resumos!",
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
            self.page.run_thread(lambda: self.show_loading("Carregando livro..."))
            
            file_ext = Path(file_path).suffix.lower()
            print(f"File extension: {file_ext}")
            
            if file_ext == '.epub':
                print("Loading EPUB...")
                self.page.run_thread(lambda: self.show_loading("Processando arquivo EPUB..."))
                book_data = self.epub_handler.load_book(file_path)
            elif file_ext == '.pdf':
                print("Loading PDF...")
                self.page.run_thread(lambda: self.show_loading("Processando arquivo PDF..."))
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
            self.page.run_thread(lambda: self.hide_loading())
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
        
        self.hide_loading()
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
        
        # Limpar imagens temporárias anteriores
        if hasattr(self, 'temp_images'):
            for temp_path in self.temp_images.values():
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
            self.temp_images.clear()
        
        # Process content to extract images and text
        content_controls = [
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Divider()
        ]
        
        # Split content by image markers
        import re
        parts = re.split(r'\[IMAGE_DATA:(data:image/[^;]+;base64,[^\]]+)\]', content)
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text part
                if part.strip():
                    font_size = self.settings.get('font_size', 14)
                    content_controls.append(ft.Text(part.strip(), size=font_size, selectable=True))
            else:  # Image part (data URI)
                try:
                    print(f"Processando imagem: {part[:50]}...")
                    
                    # Salvar imagem temporariamente
                    temp_path = self.save_temp_image(part)
                    
                    if temp_path and os.path.exists(temp_path):
                        # Usar arquivo temporário
                        content_controls.append(
                            ft.Container(
                                content=ft.Image(
                                    src=temp_path,
                                    width=400,
                                    height=300,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=ft.Text("❌ Erro ao carregar imagem")
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.symmetric(vertical=10)
                            )
                        )
                        print(f"Imagem carregada do arquivo: {temp_path}")
                    else:
                        # Fallback: tentar data URI direto
                        content_controls.append(
                            ft.Container(
                                content=ft.Image(
                                    src=part,
                                    width=400,
                                    height=300,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=ft.Text("❌ Erro ao carregar imagem")
                                ),
                                alignment=ft.alignment.center,
                                margin=ft.margin.symmetric(vertical=10)
                            )
                        )
                        print("Usando data URI direto")
                        
                except Exception as e:
                    print(f"Erro ao carregar imagem: {e}")
                    import traceback
                    traceback.print_exc()
                    content_controls.append(
                        ft.Container(
                            content=ft.Text(f"❌ Erro ao carregar imagem: {str(e)[:100]}", color=ft.Colors.RED),
                            margin=ft.margin.symmetric(vertical=10)
                        )
                    )
        
        # Update content
        self.content_column.controls = content_controls
        
        # Check if content needs scrolling and show indicator
        try:
            self.check_scroll_needed()
        except Exception as e:
            print(f"Error checking scroll indicator: {e}")
        
        # Auto-scroll to top if enabled
        if self.settings.get('auto_scroll_on_page_change', True):
            self.content_column.scroll_to(offset=0, duration=300)
        
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
        if self.chapters and self.current_chapter > 0:
            self.load_chapter(self.current_chapter - 1)
            
    def next_chapter(self, e):
        """Próximo capítulo"""
        if self.chapters and self.current_chapter < len(self.chapters) - 1:
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
            # Show loading
            chapter_title = self.chapters[self.current_chapter].get('title', f'Capítulo {self.current_chapter+1}') if self.chapters else "Capítulo"
            self.page.run_thread(lambda: self.show_loading(f"Analisando {chapter_title}..."))
            
            # Get chapter content properly
            content = ""
            handler_type = self.current_book.get('handler') if self.current_book else None
            
            if handler_type == 'epub':
                content = self.epub_handler.get_chapter_text_for_summary(self.current_chapter)
            elif handler_type == 'pdf':
                if not hasattr(self.pdf_handler, '_chapters'):
                    self.pdf_handler._chapters = self.chapters
                content = self.pdf_handler.get_chapter_text_for_summary(self.current_chapter)
            else:
                # Fallback: extract text from UI controls
                text_parts = []
                for control in self.content_column.controls[2:]:  # Skip title and divider
                    if hasattr(control, 'value') and control.value:
                        text_parts.append(control.value)
                content = '\n'.join(text_parts)
                
            if not content or len(content.strip()) < 10:
                self.page.run_thread(lambda: self.hide_loading())
                self.page.run_thread(lambda: self.show_error("Aviso", "Nenhum conteúdo suficiente para resumir"))
                return
            
            # Update loading message
            self.page.run_thread(lambda: self.show_loading("Gerando resumo com IA..."))
            
            api_key = self.settings.get('openai_api_key')
            summary = self.ai_summarizer.generate_summary(content, api_key)
            
            self.page.run_thread(lambda: self.hide_loading())
            self.page.run_thread(lambda: self.show_summary(summary, chapter_title))
            
        except Exception as e:
            self.page.run_thread(lambda: self.hide_loading())
            self.page.run_thread(lambda: self.show_error("Erro", f"Erro ao gerar resumo: {str(e)}"))
            
    def show_summary(self, summary: str, chapter_title: str = "Capítulo"):
        """Mostra resumo em diálogo melhorado"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        def copy_summary(e):
            try:
                self.page.set_clipboard(summary)
                copy_btn.text = "✓ Copiado!"
                copy_btn.color = ft.Colors.GREEN
                self.page.update()
                # Reset button after 2 seconds
                import time
                threading.Timer(2.0, lambda: self.reset_copy_button(copy_btn)).start()
            except Exception as ex:
                print(f"Error copying to clipboard: {ex}")
        
        def reset_copy_button(btn):
            try:
                btn.text = "📋 Copiar"
                btn.color = ft.Colors.BLUE
                if hasattr(self, 'page'):
                    self.page.update()
            except:
                pass
        
        # Create copy button reference
        copy_btn = ft.TextButton(
            "📋 Copiar",
            on_click=copy_summary,
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.PURPLE),
                ft.Text(f"Resumo: {chapter_title}", size=18, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            summary, 
                            selectable=True,
                            size=14,
                            color=ft.Colors.BLACK87
                        ),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                        padding=15,
                        border=ft.border.all(1, ft.Colors.GREY_300)
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_GREY),
                        ft.Text(
                            f"Resumo gerado por IA • {len(summary.split())} palavras",
                            size=12,
                            color=ft.Colors.BLUE_GREY_600
                        )
                    ])
                ], scroll=ft.ScrollMode.AUTO),
                width=600,
                height=400
            ),
            actions=[
                copy_btn,
                ft.TextButton(
                    "Fechar", 
                    on_click=close_dialog,
                    style=ft.ButtonStyle(color=ft.Colors.GREY)
                )
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.update_status("Resumo gerado com sucesso")
        self.page.update()
        
    def debug_show_settings(self, e):
        """Navigate to config page"""
        print("=== CONFIG BUTTON CLICKED ===")
        print("Navigating to config page...")
        
        try:
            self.update_status("Abrindo configurações...")
            self.show_config_page()
            
        except Exception as ex:
            print(f"ERROR in debug_show_settings: {ex}")
            import traceback
            traceback.print_exc()
            
            # Try to show a basic error
            try:
                self.update_status(f"Erro: {str(ex)}")
            except:
                print("Could not update status")
    
    def show_config_page(self):
        """Show the configuration page"""
        print("Showing config page...")
        self.current_page = "config"
        
        # Clear the page
        self.page.controls.clear()
        
        # Add config page content
        config_content = self.config_page.build_config_page()
        self.page.add(config_content)
        self.page.update()
        
        print("Config page displayed")
    
    def show_main_page(self):
        """Show the main application page"""
        print("Showing main page...")
        self.current_page = "main"
        
        # Clear the page
        self.page.controls.clear()
        
        # Rebuild main UI
        self.build_ui()
        
        # If there was a book loaded, restore it
        if self.current_book and self.chapters:
            print("Restoring book state...")
            self.on_book_loaded()
            if self.current_chapter < len(self.chapters):
                self.load_chapter(self.current_chapter)
        
        print("Main page displayed")
    
    def show_settings(self, e):
        """Mostra configurações"""
        try:
            print("show_settings called!")
            
            def close_dialog(e):
                self.page.dialog.open = False
                self.page.update()
                
            def validate_api_key(api_key):
                """Validate OpenAI API key format"""
                if not api_key:
                    return True, ""  # Empty is allowed
                if not api_key.startswith('sk-'):
                    return False, "Chave da API deve começar com 'sk-'"
                if len(api_key) < 40:
                    return False, "Chave da API parece muito curta"
                return True, ""
            
            def on_api_key_change(e):
                """Validate API key as user types"""
                api_key = api_key_field.value.strip()
                is_valid, error_msg = validate_api_key(api_key)
                
                if not is_valid:
                    api_key_field.error_text = error_msg
                    save_button.disabled = True
                else:
                    api_key_field.error_text = None
                    save_button.disabled = False
                
                self.page.update()
            
            def save_settings(e):
                print("save_settings called!")
                
                # Validate API key before saving
                api_key = api_key_field.value.strip()
                is_valid, error_msg = validate_api_key(api_key)
                
                if not is_valid:
                    api_key_field.error_text = error_msg
                    self.page.update()
                    return
                
                # Save API key (allow empty for removal)
                self.settings.set('openai_api_key', api_key)
                print(f"API key saved: {'***' if api_key else 'removed'}")
                    
                # Save auto-scroll setting
                auto_scroll_value = auto_scroll_checkbox.value
                self.settings.set('auto_scroll_on_page_change', auto_scroll_value)
                print(f"Auto-scroll setting saved: {auto_scroll_value}")
                
                # Save font size setting
                font_size_value = int(font_size_dropdown.value)
                self.settings.set('font_size', font_size_value)
                print(f"Font size saved: {font_size_value}")
                
                self.settings.save()
                    
                close_dialog(e)
                self.show_info("Sucesso", "Configurações salvas com sucesso!")
                
            # API key field with validation
            api_key_field = ft.TextField(
                label="Chave da API OpenAI",
                value=self.settings.get('openai_api_key', ''),
                password=True,
                hint_text="sk-...",
                helper_text="Obtenha gratuitamente em: https://platform.openai.com/api-keys",
                on_change=on_api_key_change,
                border_radius=8,
                filled=True
            )
            
            # Auto-scroll checkbox
            auto_scroll_checkbox = ft.Checkbox(
                label="Rolar automaticamente para o topo ao trocar páginas",
                value=self.settings.get('auto_scroll_on_page_change', True),
                check_color=ft.Colors.WHITE,
                active_color=ft.Colors.BLUE
            )
            
            # Font size dropdown
            font_size_dropdown = ft.Dropdown(
                label="Tamanho da fonte",
                value=str(self.settings.get('font_size', 14)),
                options=[
                    ft.dropdown.Option("10", "Muito pequeno (10px)"),
                    ft.dropdown.Option("12", "Pequeno (12px)"),
                    ft.dropdown.Option("14", "Normal (14px)"),
                    ft.dropdown.Option("16", "Grande (16px)"),
                    ft.dropdown.Option("18", "Muito grande (18px)"),
                    ft.dropdown.Option("20", "Extra grande (20px)")
                ],
                border_radius=8,
                filled=True
            )
            
            # Create save button reference for validation
            save_button = ft.ElevatedButton(
                "Salvar",
                on_click=save_settings,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE
                )
            )
            
            dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE),
                    ft.Text("Configurações do Epubizon", size=18, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Container(
                    content=ft.Column([
                        # OpenAI API Section
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.GREEN),
                                    ft.Text("Inteligência Artificial", size=16, weight=ft.FontWeight.BOLD)
                                ]),
                                api_key_field,
                                ft.Container(
                                    content=ft.Text(
                                        "• Necessário para gerar resumos inteligentes\n• Sua chave é armazenada localmente com segurança\n• Nunca compartilhamos seus dados",
                                        size=11,
                                        color=ft.Colors.BLUE_GREY_600
                                    ),
                                    padding=ft.padding.only(left=10, top=5)
                                )
                            ], spacing=8),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.BLUE_GREY_300),
                            border_radius=8,
                            bgcolor=ft.Colors.BLUE_GREY_50
                        ),
                        
                        # Interface Section
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.TUNE, color=ft.Colors.ORANGE),
                                    ft.Text("Interface", size=16, weight=ft.FontWeight.BOLD)
                                ]),
                                auto_scroll_checkbox,
                                ft.Container(height=10),
                                font_size_dropdown,
                                ft.Container(
                                    content=ft.Text(
                                        "• Auto-scroll melhora a experiência de leitura\n• Tamanho da fonte afeta a legibilidade do texto",
                                        size=11,
                                        color=ft.Colors.BLUE_GREY_600
                                    ),
                                    padding=ft.padding.only(left=10, top=5)
                                )
                            ], spacing=8),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.ORANGE_300),
                            border_radius=8,
                            bgcolor=ft.Colors.ORANGE_50
                        )
                    ], spacing=15),
                    width=500,
                    height=400
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=close_dialog,
                        style=ft.ButtonStyle(color=ft.Colors.GREY)
                    ),
                    save_button
                ]
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print("Dialog should be visible now")
            
        except Exception as e:
            print(f"Error in show_settings: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.show_error("Erro", f"Erro ao abrir configurações: {str(e)}")
            except:
                print("Failed to show error dialog")
        
    def show_error(self, title: str, message: str):
        """Mostra erro"""
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
            
        dialog = ft.AlertDialog(
            title=ft.Text(f"Erro - {title}"),
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
            title=ft.Text(f"Info - {title}"),
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
    
    def show_loading(self, message: str = "Carregando..."):
        """Show loading overlay"""
        try:
            if hasattr(self, 'loading_overlay') and hasattr(self, 'loading_message'):
                self.loading_overlay.visible = True
                self.loading_message.value = message
                if hasattr(self, 'page'):
                    self.page.update()
        except Exception as e:
            print(f"Error showing loading: {e}")
    
    def hide_loading(self):
        """Hide loading overlay"""
        try:
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.visible = False
                if hasattr(self, 'page'):
                    self.page.update()
        except Exception as e:
            print(f"Error hiding loading: {e}")
            
    def save_temp_image(self, data_uri: str) -> Optional[str]:
        """Salva imagem temporariamente e retorna o caminho"""
        try:
            # Extrair dados base64
            if not data_uri.startswith('data:'):
                return None
                
            header, data = data_uri.split(',', 1)
            
            # Determinar extensão
            if 'image/jpeg' in header or 'image/jpg' in header:
                ext = '.jpg'
            elif 'image/png' in header:
                ext = '.png'
            elif 'image/gif' in header:
                ext = '.gif'
            else:
                ext = '.jpg'  # fallback
            
            # Decodificar base64
            image_data = base64.b64decode(data)
            
            # Criar arquivo temporário
            image_id = str(uuid.uuid4())
            temp_path = os.path.join(self.temp_dir, f"{image_id}{ext}")
            
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            # Armazenar referência
            self.temp_images[image_id] = temp_path
            print(f"Imagem salva temporariamente: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            print(f"Erro ao salvar imagem temporária: {e}")
            return None
            
    def cleanup_temp_images(self):
        """Limpa imagens temporárias"""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("Diretório temporário limpo")
        except Exception as e:
            print(f"Erro ao limpar imagens temporárias: {e}")
            
    def on_keyboard_event(self, e: ft.KeyboardEvent):
        """Handles keyboard shortcuts"""
        if e.key == "Arrow Left" and not e.ctrl and not e.alt and not e.shift:
            self.prev_chapter(None)
        elif e.key == "Arrow Right" and not e.ctrl and not e.alt and not e.shift:
            self.next_chapter(None)
        elif e.key == "Arrow Up" and not e.ctrl and not e.alt and not e.shift:
            self.prev_chapter(None)
        elif e.key == "Arrow Down" and not e.ctrl and not e.alt and not e.shift:
            self.next_chapter(None)
        elif e.key == "F1":
            self.summarize_chapter(None)
        elif e.key == "O" and e.ctrl:
            # Open file shortcut
            self.file_picker.pick_files(
                allowed_extensions=["epub", "pdf"],
                dialog_title="Selecionar arquivo EPUB ou PDF"
            )
            
    def on_window_event(self, e):
        """Handle window events"""
        if e.data == "close":
            print("Aplicação sendo fechada, limpando recursos...")
            self.cleanup_temp_images()
    
    def check_scroll_needed(self):
        """Check if content needs scrolling and show/hide indicator"""
        try:
            if not hasattr(self, 'scroll_indicator'):
                return
                
            # Estimate if content height exceeds container height based on content length
            total_text_length = 0
            for control in self.content_column.controls[2:]:  # Skip title and divider
                if hasattr(control, 'value') and control.value:
                    total_text_length += len(str(control.value))
            
            # Rough estimate: if content is longer than ~3000 characters, it likely needs scroll
            if total_text_length > 3000 or len(self.content_column.controls) > 8:
                self.scroll_indicator.visible = True
            else:
                self.scroll_indicator.visible = False
        except Exception as e:
            print(f"Error checking scroll: {e}")
    
    def hide_scroll_indicator(self):
        """Hide scroll indicator"""
        try:
            if hasattr(self, 'scroll_indicator'):
                self.scroll_indicator.visible = False
                # Don't call page.update() here to avoid threading issues
        except Exception as e:
            print(f"Error hiding scroll indicator: {e}")


def main(page: ft.Page):
    try:
        print("Iniciando aplicação...")
        app = EpubizonApp(page)
        print("Aplicação iniciada com sucesso")
        return app
    except Exception as e:
        print(f"ERRO CRÍTICO ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()
        
        # Mostrar erro na página se possível
        try:
            page.add(ft.Text(f"ERRO: {str(e)}", color=ft.Colors.RED))
            page.update()
        except:
            pass


if __name__ == "__main__":
    print("=== INICIANDO EPUBIZON ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        # Try different modes based on environment
        import os
        if os.environ.get('WSL_DISTRO_NAME'):
            # Running in WSL - try desktop mode first, fallback to web
            try:
                print("Tentando modo desktop (WSL)...")
                ft.app(target=main, view=ft.FLET_APP)
            except Exception as e:
                print(f"Desktop mode failed: {e}, trying web mode...")
                print("Open http://localhost:8550 in your Windows browser")
                ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
        else:
            # Not in WSL - use desktop mode
            print("Tentando modo desktop...")
            print("If config button doesn't work, check console for debug messages")
            ft.app(target=main, view=ft.FLET_APP)
            
    except Exception as e:
        print(f"ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para fechar...")