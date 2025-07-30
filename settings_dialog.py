"""
Diálogo de configurações do aplicativo
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import threading

class SettingsDialog:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings = settings_manager
        self.dialog = None
        self.result = None
        
        self.create_dialog()
        
    def create_dialog(self):
        """Cria o diálogo de configurações"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configurações")
        self.dialog.geometry("500x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centralizar diálogo
        self.center_dialog()
        
        # Notebook para abas
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de IA
        self.create_ai_tab(notebook)
        
        # Aba de Interface
        self.create_interface_tab(notebook)
        
        # Aba de Leitura
        self.create_reading_tab(notebook)
        
        # Aba de Arquivos
        self.create_files_tab(notebook)
        
        # Botões
        self.create_buttons()
        
        # Carregar valores atuais
        self.load_current_settings()
        
    def center_dialog(self):
        """Centraliza o diálogo na tela"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
    def create_ai_tab(self, notebook):
        """Cria aba de configurações de IA"""
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="IA & Resumos")
        
        # Frame principal com scroll
        canvas = tk.Canvas(ai_frame)
        scrollbar = ttk.Scrollbar(ai_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configuração da API OpenAI
        ai_group = ttk.LabelFrame(scrollable_frame, text="OpenAI API")
        ai_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ai_group, text="Chave da API:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        api_frame = ttk.Frame(ai_group)
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.test_api_btn = ttk.Button(api_frame, text="Testar", command=self.test_api_key)
        self.test_api_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Mostrar/ocultar chave
        show_frame = ttk.Frame(ai_group)
        show_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.show_key_var = tk.BooleanVar()\n        show_check = ttk.Checkbutton(show_frame, text=\"Mostrar chave\", variable=self.show_key_var, command=self.toggle_api_key_visibility)\n        show_check.pack(anchor=tk.W)\n        \n        # Ajuda\n        help_text = \"\"\"Obtenha sua chave da API em: https://platform.openai.com/api-keys\nA chave é armazenada localmente e usada apenas para gerar resumos.\"\"\"\n        help_label = ttk.Label(ai_group, text=help_text, font=(\"Arial\", 8), foreground=\"gray\")\n        help_label.pack(anchor=tk.W, padx=5, pady=(0, 5))\n        \n        # Configurações de resumo\n        summary_group = ttk.LabelFrame(scrollable_frame, text=\"Configurações de Resumo\")\n        summary_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        ttk.Label(summary_group, text=\"Idioma dos resumos:\").pack(anchor=tk.W, padx=5, pady=(5, 0))\n        \n        self.language_var = tk.StringVar()\n        language_combo = ttk.Combobox(summary_group, textvariable=self.language_var, state=\"readonly\")\n        language_combo['values'] = ('Português', 'English', 'Español')\n        language_combo.pack(fill=tk.X, padx=5, pady=5)\n        \n        canvas.pack(side=\"left\", fill=\"both\", expand=True)\n        scrollbar.pack(side=\"right\", fill=\"y\")\n        \n    def create_interface_tab(self, notebook):\n        \"\"\"Cria aba de configurações de interface\"\"\"\n        interface_frame = ttk.Frame(notebook)\n        notebook.add(interface_frame, text=\"Interface\")\n        \n        # Fonte\n        font_group = ttk.LabelFrame(interface_frame, text=\"Fonte\")\n        font_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        ttk.Label(font_group, text=\"Família da fonte:\").pack(anchor=tk.W, padx=5, pady=(5, 0))\n        \n        self.font_family_var = tk.StringVar()\n        font_combo = ttk.Combobox(font_group, textvariable=self.font_family_var, state=\"readonly\")\n        font_combo['values'] = ('Georgia', 'Arial', 'Times New Roman', 'Calibri', 'Verdana')\n        font_combo.pack(fill=tk.X, padx=5, pady=5)\n        \n        ttk.Label(font_group, text=\"Tamanho da fonte:\").pack(anchor=tk.W, padx=5, pady=(5, 0))\n        \n        self.font_size_var = tk.IntVar()\n        font_size_spin = ttk.Spinbox(font_group, from_=8, to=24, textvariable=self.font_size_var)\n        font_size_spin.pack(fill=tk.X, padx=5, pady=5)\n        \n        # Tema\n        theme_group = ttk.LabelFrame(interface_frame, text=\"Tema\")\n        theme_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        self.theme_var = tk.StringVar()\n        themes = [('Claro', 'light'), ('Escuro', 'dark')]\n        \n        for text, value in themes:\n            ttk.Radiobutton(theme_group, text=text, variable=self.theme_var, value=value).pack(anchor=tk.W, padx=5, pady=2)\n            \n    def create_reading_tab(self, notebook):\n        \"\"\"Cria aba de configurações de leitura\"\"\"\n        reading_frame = ttk.Frame(notebook)\n        notebook.add(reading_frame, text=\"Leitura\")\n        \n        # Configurações de página\n        page_group = ttk.LabelFrame(reading_frame, text=\"Paginação\")\n        page_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        ttk.Label(page_group, text=\"Páginas por capítulo (PDF):\").pack(anchor=tk.W, padx=5, pady=(5, 0))\n        \n        self.pages_per_chapter_var = tk.IntVar()\n        pages_spin = ttk.Spinbox(page_group, from_=5, to=50, textvariable=self.pages_per_chapter_var)\n        pages_spin.pack(fill=tk.X, padx=5, pady=5)\n        \n        help_text = \"Define quantas páginas PDF formam um 'capítulo' para navegação\"\n        ttk.Label(page_group, text=help_text, font=(\"Arial\", 8), foreground=\"gray\").pack(anchor=tk.W, padx=5, pady=(0, 5))\n        \n    def create_files_tab(self, notebook):\n        \"\"\"Cria aba de configurações de arquivos\"\"\"\n        files_frame = ttk.Frame(notebook)\n        notebook.add(files_frame, text=\"Arquivos\")\n        \n        # Auto-salvar\n        auto_group = ttk.LabelFrame(files_frame, text=\"Salvamento\")\n        auto_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        self.auto_save_var = tk.BooleanVar()\n        ttk.Checkbutton(auto_group, text=\"Salvar configurações automaticamente\", variable=self.auto_save_var).pack(anchor=tk.W, padx=5, pady=5)\n        \n        # Arquivos recentes\n        recent_group = ttk.LabelFrame(files_frame, text=\"Arquivos Recentes\")\n        recent_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        recent_info = ttk.Label(recent_group, text=f\"Arquivos recentes: {len(self.settings.get_recent_files())}\")\n        recent_info.pack(anchor=tk.W, padx=5, pady=5)\n        \n        ttk.Button(recent_group, text=\"Limpar Lista\", command=self.clear_recent_files).pack(anchor=tk.W, padx=5, pady=5)\n        \n        # Backup/Restore\n        backup_group = ttk.LabelFrame(files_frame, text=\"Backup de Configurações\")\n        backup_group.pack(fill=tk.X, padx=5, pady=5)\n        \n        backup_frame = ttk.Frame(backup_group)\n        backup_frame.pack(fill=tk.X, padx=5, pady=5)\n        \n        ttk.Button(backup_frame, text=\"Exportar\", command=self.export_settings).pack(side=tk.LEFT, padx=(0, 5))\n        ttk.Button(backup_frame, text=\"Importar\", command=self.import_settings).pack(side=tk.LEFT)\n        \n        ttk.Button(backup_group, text=\"Restaurar Padrões\", command=self.reset_settings).pack(anchor=tk.W, padx=5, pady=5)\n        \n    def create_buttons(self):\n        \"\"\"Cria botões do diálogo\"\"\"\n        button_frame = ttk.Frame(self.dialog)\n        button_frame.pack(fill=tk.X, padx=10, pady=10)\n        \n        ttk.Button(button_frame, text=\"Cancelar\", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))\n        ttk.Button(button_frame, text=\"OK\", command=self.ok).pack(side=tk.RIGHT)\n        \n    def load_current_settings(self):\n        \"\"\"Carrega configurações atuais nos controles\"\"\"\n        self.api_key_var.set(self.settings.get('openai_api_key', ''))\n        self.font_family_var.set(self.settings.get('font_family', 'Georgia'))\n        self.font_size_var.set(self.settings.get('font_size', 12))\n        self.theme_var.set(self.settings.get('theme', 'light'))\n        self.pages_per_chapter_var.set(self.settings.get('pages_per_chapter', 10))\n        self.auto_save_var.set(self.settings.get('auto_save', True))\n        \n        # Idioma do resumo\n        lang_map = {'pt': 'Português', 'en': 'English', 'es': 'Español'}\n        current_lang = self.settings.get('summary_language', 'pt')\n        self.language_var.set(lang_map.get(current_lang, 'Português'))\n        \n    def toggle_api_key_visibility(self):\n        \"\"\"Alterna visibilidade da chave da API\"\"\"\n        if self.show_key_var.get():\n            self.api_key_entry.config(show=\"\")\n        else:\n            self.api_key_entry.config(show=\"*\")\n            \n    def test_api_key(self):\n        \"\"\"Testa a chave da API OpenAI\"\"\"\n        api_key = self.api_key_var.get().strip()\n        if not api_key:\n            messagebox.showwarning(\"Aviso\", \"Digite uma chave da API primeiro\")\n            return\n            \n        # Testar em thread separada\n        self.test_api_btn.config(state=tk.DISABLED, text=\"Testando...\")\n        threading.Thread(target=self._test_api_key_thread, args=(api_key,), daemon=True).start()\n        \n    def _test_api_key_thread(self, api_key):\n        \"\"\"Thread para testar chave da API\"\"\"\n        try:\n            from ai_summarizer import AISummarizer\n            summarizer = AISummarizer()\n            result = summarizer.test_api_key(api_key)\n            \n            self.dialog.after(0, self._on_api_test_complete, result)\n            \n        except Exception as e:\n            result = {\"success\": False, \"error\": str(e)}\n            self.dialog.after(0, self._on_api_test_complete, result)\n            \n    def _on_api_test_complete(self, result):\n        \"\"\"Callback quando teste da API termina\"\"\"\n        self.test_api_btn.config(state=tk.NORMAL, text=\"Testar\")\n        \n        if result[\"success\"]:\n            messagebox.showinfo(\"Sucesso\", \"Chave da API válida!\")\n        else:\n            messagebox.showerror(\"Erro\", f\"Erro na chave da API:\\n{result['error']}\")\n            \n    def clear_recent_files(self):\n        \"\"\"Limpa lista de arquivos recentes\"\"\"\n        if messagebox.askyesno(\"Confirmar\", \"Limpar lista de arquivos recentes?\"):\n            self.settings.clear_recent_files()\n            messagebox.showinfo(\"Sucesso\", \"Lista de arquivos recentes limpa\")\n            \n    def export_settings(self):\n        \"\"\"Exporta configurações\"\"\"\n        file_path = filedialog.asksaveasfilename(\n            title=\"Exportar Configurações\",\n            defaultextension=\".json\",\n            filetypes=[(\"JSON files\", \"*.json\"), (\"All files\", \"*.*\")]\n        )\n        \n        if file_path:\n            if self.settings.export_settings(file_path):\n                messagebox.showinfo(\"Sucesso\", \"Configurações exportadas com sucesso\")\n            else:\n                messagebox.showerror(\"Erro\", \"Erro ao exportar configurações\")\n                \n    def import_settings(self):\n        \"\"\"Importa configurações\"\"\"\n        file_path = filedialog.askopenfilename(\n            title=\"Importar Configurações\",\n            filetypes=[(\"JSON files\", \"*.json\"), (\"All files\", \"*.*\")]\n        )\n        \n        if file_path:\n            if messagebox.askyesno(\"Confirmar\", \"Importar configurações irá sobrescrever as atuais. Continuar?\"):\n                if self.settings.import_settings(file_path):\n                    messagebox.showinfo(\"Sucesso\", \"Configurações importadas com sucesso\")\n                    self.load_current_settings()\n                else:\n                    messagebox.showerror(\"Erro\", \"Erro ao importar configurações\")\n                    \n    def reset_settings(self):\n        \"\"\"Restaura configurações padrão\"\"\"\n        if messagebox.askyesno(\"Confirmar\", \"Restaurar todas as configurações para os valores padrão?\"):\n            self.settings.reset_to_defaults()\n            messagebox.showinfo(\"Sucesso\", \"Configurações restauradas para padrão\")\n            self.load_current_settings()\n            \n    def save_settings(self):\n        \"\"\"Salva as configurações\"\"\"\n        # Mapear idioma de volta\n        lang_map = {'Português': 'pt', 'English': 'en', 'Español': 'es'}\n        summary_lang = lang_map.get(self.language_var.get(), 'pt')\n        \n        new_settings = {\n            'openai_api_key': self.api_key_var.get().strip(),\n            'font_family': self.font_family_var.get(),\n            'font_size': self.font_size_var.get(),\n            'theme': self.theme_var.get(),\n            'pages_per_chapter': self.pages_per_chapter_var.get(),\n            'auto_save': self.auto_save_var.get(),\n            'summary_language': summary_lang\n        }\n        \n        self.settings.update(new_settings)\n        \n    def ok(self):\n        \"\"\"Salva e fecha o diálogo\"\"\"\n        try:\n            self.save_settings()\n            self.result = 'ok'\n            self.dialog.destroy()\n        except Exception as e:\n            messagebox.showerror(\"Erro\", f\"Erro ao salvar configurações:\\n{str(e)}\")\n            \n    def cancel(self):\n        \"\"\"Cancela e fecha o diálogo\"\"\"\n        self.result = 'cancel'\n        self.dialog.destroy()"