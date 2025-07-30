#!/usr/bin/env python3
"""
Epubizon - Leitor EPUB e PDF em Python
Versão reescrita do aplicativo Electron original
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import threading
import json
from typing import Optional, Dict, List, Any

# Importa os módulos principais
from epub_handler import EpubHandler
from pdf_handler import PdfHandler
from settings_manager import SettingsManager
from ai_summarizer import AISummarizer

class EpubizonApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📚 Epubizon - Leitor EPUB & PDF")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Configurar estilo moderno
        self.setup_styles()
        
        # Gerenciadores
        self.settings = SettingsManager()
        self.epub_handler = EpubHandler()
        self.pdf_handler = PdfHandler()
        self.ai_summarizer = AISummarizer()
        
        # Estado da aplicação
        self.current_book = None
        self.current_chapter = 0
        self.chapters = []
        self.book_metadata = {}
        
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.load_settings()
        
    def setup_styles(self):
        """Configura estilos modernos da aplicação"""
        # Configurar cores e tema
        self.root.configure(bg="#ecf0f1")
        
        # Configurar estilos ttk
        style = ttk.Style()
        
        # Estilo para buttons
        style.configure("Modern.TButton",
                       padding=(15, 8),
                       font=("Segoe UI", 10),
                       relief="flat")
        
        # Estilo para labels
        style.configure("Modern.TLabel",
                       font=("Segoe UI", 10),
                       background="#ecf0f1")
        
        # Estilo para frames
        style.configure("Modern.TFrame",
                       background="#ecf0f1",
                       relief="flat")
        
        # Estilo para labelframes
        style.configure("Modern.TLabelframe",
                       background="#ecf0f1",
                       relief="solid",
                       borderwidth=1)
        
        style.configure("Modern.TLabelframe.Label",
                       background="#ecf0f1",
                       font=("Segoe UI", 11, "bold"),
                       foreground="#2c3e50")
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Menu principal
        self.create_menu()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Frame de conteúdo (sidebar + viewer)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Sidebar
        self.create_sidebar(content_frame)
        
        # Viewer principal
        self.create_viewer(content_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_menu(self):
        """Cria o menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Resumir Capítulo", command=self.summarize_chapter, accelerator="F1")
        tools_menu.add_separator()
        tools_menu.add_command(label="Configurações", command=self.open_settings, accelerator="Ctrl+,")
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        
    def create_toolbar(self, parent):
        """Cria a barra de ferramentas"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Botão abrir arquivo
        self.open_btn = ttk.Button(toolbar, text="📂 Abrir Arquivo", command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Informações do livro
        self.book_info_label = ttk.Label(toolbar, text="Nenhum livro carregado", 
                                        font=("Segoe UI", 12, "bold"),
                                        foreground="#2c3e50")
        self.book_info_label.pack(side=tk.LEFT, padx=15)
        
        # Botões do lado direito
        right_frame = ttk.Frame(toolbar)
        right_frame.pack(side=tk.RIGHT)
        
        self.summary_btn = ttk.Button(right_frame, text="✨ Resumir", command=self.summarize_chapter, state=tk.DISABLED)
        self.summary_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        self.settings_btn = ttk.Button(right_frame, text="⚙️ Configurações", command=self.open_settings)
        self.settings_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
    def create_sidebar(self, parent):
        """Cria a sidebar com navegação"""
        sidebar_frame = ttk.LabelFrame(parent, text="📚 Navegação", width=320, style="Modern.TLabelframe")
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # Lista de capítulos
        chapters_frame = ttk.LabelFrame(sidebar_frame, text="📖 Capítulos", style="Modern.TLabelframe")
        chapters_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Treeview para capítulos
        self.chapters_tree = ttk.Treeview(chapters_frame, show="tree")
        scrollbar_chapters = ttk.Scrollbar(chapters_frame, orient=tk.VERTICAL, command=self.chapters_tree.yview)
        self.chapters_tree.configure(yscrollcommand=scrollbar_chapters.set)
        
        self.chapters_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_chapters.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chapters_tree.bind("<<TreeviewSelect>>", self.on_chapter_select)
        
        # Controles de navegação
        nav_frame = ttk.Frame(sidebar_frame)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Anterior", command=self.prev_chapter, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.next_btn = ttk.Button(nav_frame, text="Próximo →", command=self.next_chapter, state=tk.DISABLED)
        self.next_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Informações de página
        self.page_info = ttk.Label(sidebar_frame, text="Página: - / -")
        self.page_info.pack(pady=5)
        
        # Ajuda de teclado
        help_frame = ttk.LabelFrame(sidebar_frame, text="⌨️ Atalhos", style="Modern.TLabelframe")
        help_frame.pack(fill=tk.X, padx=8, pady=8)
        
        help_text = "← → Navegar capítulos\n↑ ↓ Navegar capítulos\nF1 Resumir capítulo\nCtrl+O Abrir arquivo\nCtrl+, Configurações"
        help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 8))
        help_label.pack(padx=5, pady=5)
        
    def create_viewer(self, parent):
        """Cria o visualizador principal"""
        viewer_frame = ttk.LabelFrame(parent, text="📄 Conteúdo", style="Modern.TLabelframe")
        viewer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Área de conteúdo com scroll
        self.content_text = scrolledtext.ScrolledText(
            viewer_frame, 
            wrap=tk.WORD, 
            font=("Georgia", 13),
            padx=30,
            pady=25,
            state=tk.DISABLED,
            bg="#fafafa",
            fg="#2c3e50",
            insertbackground="#3498db",
            selectbackground="#3498db",
            selectforeground="white",
            relief=tk.FLAT,
            borderwidth=0
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar tags para formatação
        self.content_text.tag_configure("title", 
                                      font=("Georgia", 20, "bold"), 
                                      spacing1=15, spacing3=15, 
                                      foreground="#2c3e50",
                                      justify=tk.CENTER)
        self.content_text.tag_configure("subtitle", 
                                      font=("Georgia", 16, "bold"), 
                                      spacing1=10, spacing3=10,
                                      foreground="#34495e")
        self.content_text.tag_configure("paragraph", 
                                      font=("Georgia", 13), 
                                      spacing1=5, spacing3=8,
                                      foreground="#2c3e50",
                                      lmargin1=10, lmargin2=10)
        self.content_text.tag_configure("highlight", 
                                      background="#f1c40f", 
                                      foreground="#2c3e50")
        
        # Mensagem de boas-vindas
        self.show_welcome_message()
        
    def create_status_bar(self):
        """Cria a barra de status"""
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def show_welcome_message(self):
        """Mostra mensagem de boas-vindas"""
        welcome_text = """
        
        Bem-vindo ao Epubizon
        
        Seu leitor moderno de EPUB e PDF com resumos alimentados por IA
        
        ✨ Recursos Principais:
        • Interface nativa e responsiva
        • Navegação intuitiva por capítulos
        • Resumos inteligentes com IA
        • Suporte completo para EPUB e PDF
        • Atalhos de teclado avançados
        
        🚀 Para começar:
        1. Clique em "📂 Abrir Arquivo" ou pressione Ctrl+O
        2. Selecione um arquivo EPUB ou PDF
        3. Use as setas do teclado para navegar entre capítulos
        4. Pressione F1 para gerar um resumo inteligente
        
        💡 Dica: Configure sua chave da API OpenAI nas configurações para usar os resumos!
        
        """
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        
        # Inserir título
        self.content_text.insert(tk.END, "📚 Epubizon v2.0\n", "title")
        
        # Inserir conteúdo
        self.content_text.insert(tk.END, welcome_text, "paragraph")
        self.content_text.config(state=tk.DISABLED)
        
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado"""
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-comma>", lambda e: self.open_settings())
        self.root.bind("<F1>", lambda e: self.summarize_chapter())
        self.root.bind("<Left>", lambda e: self.prev_chapter())
        self.root.bind("<Right>", lambda e: self.next_chapter())
        self.root.bind("<Up>", lambda e: self.prev_chapter())
        self.root.bind("<Down>", lambda e: self.next_chapter())
        
    def open_file(self):
        """Abre diálogo para selecionar arquivo"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[
                ("Todos os suportados", "*.epub;*.pdf"),
                ("Arquivos EPUB", "*.epub"),
                ("Arquivos PDF", "*.pdf"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            self.load_book(file_path)
            
    def load_book(self, file_path: str):
        """Carrega um livro"""
        self.update_status("Carregando livro...")
        
        # Executar em thread separada para não travar a UI
        threading.Thread(target=self._load_book_thread, args=(file_path,), daemon=True).start()
        
    def _load_book_thread(self, file_path: str):
        """Thread para carregar livro"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.epub':
                book_data = self.epub_handler.load_book(file_path)
            elif file_ext == '.pdf':
                book_data = self.pdf_handler.load_book(file_path)
            else:
                raise ValueError(f"Formato não suportado: {file_ext}")
                
            # Atualizar UI na thread principal
            self.root.after(0, self._on_book_loaded, book_data, file_path)
            
        except Exception as e:
            self.root.after(0, self._on_book_load_error, str(e))
            
    def _on_book_loaded(self, book_data: Dict[str, Any], file_path: str):
        """Callback quando livro é carregado com sucesso"""
        self.current_book = book_data
        self.chapters = book_data.get('chapters', [])
        self.book_metadata = book_data.get('metadata', {})
        self.current_chapter = 0
        
        # Atualizar UI
        self.update_book_info()
        self.populate_chapters_tree()
        self.load_chapter(0)
        
        # Habilitar controles
        self.summary_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        
        self.update_status(f"Livro carregado: {self.book_metadata.get('title', Path(file_path).name)}")
        
    def _on_book_load_error(self, error_msg: str):
        """Callback quando ocorre erro ao carregar livro"""
        messagebox.showerror("Erro", f"Erro ao carregar livro:\n{error_msg}")
        self.update_status("Erro ao carregar livro")
        
    def update_book_info(self):
        """Atualiza informações do livro na UI"""
        title = self.book_metadata.get('title', 'Título desconhecido')
        author = self.book_metadata.get('creator', self.book_metadata.get('author', ''))
        
        if author:
            info_text = f"{title} - {author}"
        else:
            info_text = title
            
        self.book_info_label.config(text=info_text)
        
    def populate_chapters_tree(self):
        """Popula a árvore de capítulos"""
        # Limpar árvore existente
        for item in self.chapters_tree.get_children():
            self.chapters_tree.delete(item)
            
        # Adicionar capítulos
        for i, chapter in enumerate(self.chapters):
            title = chapter.get('title', f'Capítulo {i+1}')
            self.chapters_tree.insert('', 'end', iid=str(i), text=title)
            
    def on_chapter_select(self, event):
        """Callback quando capítulo é selecionado"""
        selection = self.chapters_tree.selection()
        if selection:
            chapter_index = int(selection[0])
            self.load_chapter(chapter_index)
            
    def load_chapter(self, chapter_index: int):
        """Carrega um capítulo específico"""
        if not self.chapters or chapter_index < 0 or chapter_index >= len(self.chapters):
            return
            
        self.current_chapter = chapter_index
        chapter = self.chapters[chapter_index]
        
        self.update_status(f"Carregando capítulo: {chapter.get('title', f'Capítulo {chapter_index+1}')}")
        
        # Executar em thread separada
        threading.Thread(target=self._load_chapter_thread, args=(chapter_index,), daemon=True).start()
        
    def _load_chapter_thread(self, chapter_index: int):
        """Thread para carregar capítulo"""
        try:
            if self.current_book.get('handler') == 'epub':
                content = self.epub_handler.get_chapter_content(chapter_index)
            elif self.current_book.get('handler') == 'pdf':
                content = self.pdf_handler.get_chapter_content(chapter_index)
            else:
                # Fallback para dados já carregados
                chapter = self.chapters[chapter_index]
                content = chapter.get('content', f"Conteúdo do {chapter.get('title', f'Capítulo {chapter_index+1}')}")
                
            self.root.after(0, self._on_chapter_loaded, content, chapter_index)
            
        except Exception as e:
            self.root.after(0, self._on_chapter_load_error, str(e))
            
    def _on_chapter_loaded(self, content: str, chapter_index: int):
        """Callback quando capítulo é carregado"""
        # Atualizar conteúdo
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        
        # Inserir título
        chapter_title = self.chapters[chapter_index].get('title', f'Capítulo {chapter_index+1}')
        self.content_text.insert(tk.END, f"{chapter_title}\n\n", "title")
        
        # Inserir conteúdo
        self.content_text.insert(tk.END, content, "paragraph")
        self.content_text.config(state=tk.DISABLED)
        
        # Atualizar seleção na árvore
        self.chapters_tree.selection_set(str(chapter_index))
        self.chapters_tree.see(str(chapter_index))
        
        # Atualizar informações de página
        self.update_page_info()
        
        self.update_status(f"Capítulo carregado: {chapter_title}")
        
    def _on_chapter_load_error(self, error_msg: str):
        """Callback quando ocorre erro ao carregar capítulo"""
        messagebox.showerror("Erro", f"Erro ao carregar capítulo:\n{error_msg}")
        self.update_status("Erro ao carregar capítulo")
        
    def update_page_info(self):
        """Atualiza informações de página"""
        if self.chapters:
            page_text = f"Página: {self.current_chapter + 1} / {len(self.chapters)}"
            self.page_info.config(text=page_text)
        else:
            self.page_info.config(text="Página: - / -")
            
    def prev_chapter(self):
        """Navega para o capítulo anterior"""
        if self.current_chapter > 0:
            self.load_chapter(self.current_chapter - 1)
            
    def next_chapter(self):
        """Navega para o próximo capítulo"""
        if self.current_chapter < len(self.chapters) - 1:
            self.load_chapter(self.current_chapter + 1)
            
    def summarize_chapter(self):
        """Gera resumo do capítulo atual usando IA"""
        if not self.chapters or not self.current_book:
            messagebox.showwarning("Aviso", "Nenhum capítulo carregado para resumir")
            return
            
        api_key = self.settings.get('openai_api_key')
        if not api_key:
            messagebox.showwarning("Aviso", "Configure sua chave da API OpenAI nas configurações")
            self.open_settings()
            return
            
        # Executar em thread separada
        threading.Thread(target=self._summarize_chapter_thread, daemon=True).start()
        
    def _summarize_chapter_thread(self):
        """Thread para gerar resumo"""
        try:
            # Obter texto do capítulo atual
            chapter_content = self.content_text.get(1.0, tk.END).strip()
            
            if not chapter_content:
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "Nenhum conteúdo para resumir"))
                return
                
            api_key = self.settings.get('openai_api_key')
            summary = self.ai_summarizer.generate_summary(chapter_content, api_key)
            
            self.root.after(0, self._on_summary_generated, summary)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao gerar resumo:\n{str(e)}"))
            
    def _on_summary_generated(self, summary: str):
        """Callback quando resumo é gerado"""
        self.show_summary_dialog(summary)
        
    def show_summary_dialog(self, summary: str):
        """Mostra diálogo com o resumo"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Resumo do Capítulo")
        dialog.geometry("600x400")
        dialog.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="✨ Resumo Gerado por IA", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Texto do resumo
        summary_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Georgia", 11))
        summary_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
        
        # Botão fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=dialog.destroy)
        close_btn.pack(pady=5)
        
        # Centralizar diálogo
        dialog.transient(self.root)
        dialog.grab_set()
        
    def open_settings(self):
        """Abre diálogo de configurações"""
        from settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.root, self.settings)
        self.root.wait_window(dialog.dialog)
        
    def load_settings(self):
        """Carrega configurações salvas"""
        self.settings.load()
        
    def show_about(self):
        """Mostra diálogo sobre o aplicativo"""
        about_text = """
        Epubizon v2.0
        
        Leitor moderno de EPUB e PDF em Python
        
        Recursos:
        • Suporte para EPUB e PDF
        • Interface nativa
        • Resumos com IA (OpenAI)
        • Navegação por teclado
        • Multiplataforma
        
        Reescrito do Electron para Python
        """
        
        messagebox.showinfo("Sobre o Epubizon", about_text)
        
    def update_status(self, message: str):
        """Atualiza barra de status"""
        self.status_bar.config(text=message)
        
    def run(self):
        """Executa o aplicativo"""
        self.root.mainloop()

def main():
    """Função principal"""
    app = EpubizonApp()
    app.run()

if __name__ == "__main__":
    main()