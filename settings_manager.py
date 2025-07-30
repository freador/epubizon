"""
Gerenciador de configurações do aplicativo
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SettingsManager:
    def __init__(self):
        self.settings_dir = Path.home() / '.epubizon'
        self.settings_file = self.settings_dir / 'settings.json'
        self.settings = self._get_default_settings()
        
        # Criar diretório se não existir
        self.settings_dir.mkdir(exist_ok=True)
        
    def _get_default_settings(self) -> Dict[str, Any]:
        """Retorna configurações padrão"""
        return {
            'openai_api_key': '',
            'font_size': 12,
            'font_family': 'Georgia',
            'theme': 'light',
            'auto_save': True,
            'pages_per_chapter': 10,
            'summary_language': 'pt',
            'window_geometry': '1200x800',
            'recent_files': []
        }
        
    def load(self):
        """Carrega configurações do arquivo"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            
    def save(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de uma configuração"""
        return self.settings.get(key, default)
        
    def set(self, key: str, value: Any):
        """Define valor de uma configuração"""
        self.settings[key] = value
        if self.get('auto_save', True):
            self.save()
            
    def update(self, new_settings: Dict[str, Any]):
        """Atualiza múltiplas configurações"""
        self.settings.update(new_settings)
        if self.get('auto_save', True):
            self.save()
            
    def add_recent_file(self, file_path: str):
        """Adiciona arquivo à lista de recentes"""
        recent = self.get('recent_files', [])
        
        # Remover se já existir
        if file_path in recent:
            recent.remove(file_path)
            
        # Adicionar no início
        recent.insert(0, file_path)
        
        # Manter apenas os 10 mais recentes
        recent = recent[:10]
        
        self.set('recent_files', recent)
        
    def get_recent_files(self) -> list:
        """Retorna lista de arquivos recentes"""
        recent = self.get('recent_files', [])
        
        # Filtrar arquivos que ainda existem
        existing_files = []
        for file_path in recent:
            if os.path.exists(file_path):
                existing_files.append(file_path)
                
        # Atualizar lista se mudou
        if len(existing_files) != len(recent):
            self.set('recent_files', existing_files)
            
        return existing_files
        
    def clear_recent_files(self):
        """Limpa lista de arquivos recentes"""
        self.set('recent_files', [])
        
    def reset_to_defaults(self):
        """Restaura configurações padrão"""
        self.settings = self._get_default_settings()
        self.save()
        
    def export_settings(self, file_path: str):
        """Exporta configurações para arquivo"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao exportar configurações: {e}")
            return False
            
    def import_settings(self, file_path: str):
        """Importa configurações de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                
            # Validar configurações importadas
            valid_settings = {}
            defaults = self._get_default_settings()
            
            for key, value in imported_settings.items():
                if key in defaults:
                    valid_settings[key] = value
                    
            self.settings.update(valid_settings)
            self.save()
            return True
            
        except Exception as e:
            print(f"Erro ao importar configurações: {e}")
            return False