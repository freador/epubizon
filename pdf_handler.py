"""
Handler para arquivos PDF
Substitui parte da funcionalidade do aplicativo original
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2
import re
import io

class PdfHandler:
    def __init__(self):
        self.pdf_reader = None
        self.pages = []
        self.metadata = {}
        self.pages_per_chapter = 10  # Páginas por "capítulo"
        
    def load_book(self, file_path: str) -> Dict[str, Any]:
        """Carrega um arquivo PDF"""
        try:
            with open(file_path, 'rb') as file:
                self.pdf_reader = PyPDF2.PdfReader(file)
                
                # Extrair metadata
                self.metadata = self._extract_metadata()
                
                # Extrair páginas
                self.pages = self._extract_pages()
                
                # Criar "capítulos" baseados em páginas
                chapters = self._create_chapters()
                
                return {
                    'handler': 'pdf',
                    'metadata': self.metadata,
                    'chapters': chapters,
                    'total_pages': len(self.pages),
                    'pdf_pages': len(self.pdf_reader.pages)
                }
                
        except Exception as e:
            raise Exception(f"Erro ao carregar PDF: {str(e)}")
    
    def load_book_from_data(self, file_data: bytes) -> Dict[str, Any]:
        """Carrega um arquivo PDF a partir de dados binários"""
        try:
            pdf_io = io.BytesIO(file_data)
            self.pdf_reader = PyPDF2.PdfReader(pdf_io)
            
            # Extrair metadata
            self.metadata = self._extract_metadata()
            
            # Extrair páginas
            self.pages = self._extract_pages()
            
            # Criar "capítulos" baseados em páginas
            chapters = self._create_chapters()
            
            return {
                'handler': 'pdf',
                'metadata': self.metadata,
                'chapters': chapters,
                'total_pages': len(self.pages),
                'pdf_pages': len(self.pdf_reader.pages)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao carregar PDF dos dados: {str(e)}")
            
    def _extract_metadata(self) -> Dict[str, str]:
        """Extrai metadados do PDF"""
        metadata = {}
        
        try:
            pdf_metadata = self.pdf_reader.metadata
            if pdf_metadata:
                metadata['title'] = pdf_metadata.get('/Title', 'Documento PDF')
                metadata['creator'] = pdf_metadata.get('/Author', 'Autor Desconhecido')
                metadata['subject'] = pdf_metadata.get('/Subject', '')
                metadata['producer'] = pdf_metadata.get('/Producer', '')
                metadata['creation_date'] = str(pdf_metadata.get('/CreationDate', ''))
            else:
                metadata['title'] = 'Documento PDF'
                metadata['creator'] = 'Autor Desconhecido'
                
        except Exception as e:
            print(f"Erro ao extrair metadados do PDF: {e}")
            metadata = {'title': 'Documento PDF', 'creator': 'Autor Desconhecido'}
            
        return metadata
        
    def _extract_pages(self) -> List[str]:
        """Extrai texto de todas as páginas"""
        pages = []
        
        try:
            for page_num, page in enumerate(self.pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        pages.append(text)
                    else:
                        pages.append(f"[Página {page_num + 1} - Sem texto extraível]")
                except Exception as e:
                    print(f"Erro ao extrair texto da página {page_num + 1}: {e}")
                    pages.append(f"[Página {page_num + 1} - Erro na extração]")
                    
        except Exception as e:
            print(f"Erro ao extrair páginas: {e}")
            pages = ["Erro ao extrair conteúdo do PDF"]
            
        return pages
        
    def _create_chapters(self) -> List[Dict[str, Any]]:
        """Cria "capítulos" baseados em páginas ou estrutura do PDF"""
        chapters = []
        
        try:
            # Tentar detectar capítulos reais através de padrões no texto
            detected_chapters = self._detect_chapters_from_content()
            
            if detected_chapters:
                chapters = detected_chapters
            else:
                # Fallback: dividir em grupos de páginas
                chapters = self._create_page_based_chapters()
                
        except Exception as e:
            print(f"Erro ao criar capítulos: {e}")
            chapters = [{'title': 'Documento Completo', 'start_page': 0, 'end_page': len(self.pages) - 1, 'index': 0}]
            
        return chapters
        
    def _detect_chapters_from_content(self) -> List[Dict[str, Any]]:
        """Tenta detectar capítulos baseado no conteúdo"""
        chapters = []
        
        # Padrões comuns para títulos de capítulos
        chapter_patterns = [
            r'^CAPÍTULO\s+(\d+|[IVXLC]+)[\s\.:]\s*(.+)$',
            r'^CHAPTER\s+(\d+|[IVXLC]+)[\s\.:]\s*(.+)$',
            r'^(\d+)[\s\.:]\s*(.+)$',
            r'^([IVXLC]+)[\s\.:]\s*(.+)$',
        ]
        
        try:
            chapter_matches = []
            
            for page_num, page_text in enumerate(self.pages):
                lines = page_text.split('\n')
                
                for line_num, line in enumerate(lines[:10]):  # Verificar apenas primeiras 10 linhas
                    line = line.strip()
                    if len(line) < 5 or len(line) > 100:  # Filtrar linhas muito curtas ou longas
                        continue
                        
                    for pattern in chapter_patterns:
                        match = re.match(pattern, line, re.IGNORECASE)
                        if match:
                            chapter_matches.append({
                                'page': page_num,
                                'line': line_num,
                                'title': line,
                                'groups': match.groups()
                            })
                            break
                            
            # Se encontrou capítulos, criar estrutura
            if len(chapter_matches) >= 2:  # Precisa de pelo menos 2 capítulos
                for i, match in enumerate(chapter_matches):
                    end_page = chapter_matches[i + 1]['page'] - 1 if i + 1 < len(chapter_matches) else len(self.pages) - 1
                    
                    chapters.append({
                        'title': match['title'],
                        'start_page': match['page'],
                        'end_page': end_page,
                        'index': i
                    })
                    
        except Exception as e:
            print(f"Erro na detecção de capítulos: {e}")
            
        return chapters
        
    def _create_page_based_chapters(self) -> List[Dict[str, Any]]:
        """Cria capítulos baseados em grupos de páginas"""
        chapters = []
        total_pages = len(self.pages)
        
        # Ajustar número de páginas por capítulo baseado no tamanho total
        if total_pages <= 20:
            pages_per_chapter = 5
        elif total_pages <= 50:
            pages_per_chapter = 10
        else:
            pages_per_chapter = 15
            
        chapter_num = 1
        start_page = 0
        
        while start_page < total_pages:
            end_page = min(start_page + pages_per_chapter - 1, total_pages - 1)
            
            chapters.append({
                'title': f'Seção {chapter_num} (Páginas {start_page + 1}-{end_page + 1})',
                'start_page': start_page,
                'end_page': end_page,
                'index': chapter_num - 1
            })
            
            start_page = end_page + 1
            chapter_num += 1
            
        return chapters
        
    def get_chapter_content(self, chapter_index: int) -> str:
        """Obtém o conteúdo de um capítulo específico"""
        if not hasattr(self, '_chapters'):
            # Recriar capítulos se não existirem
            self._chapters = self._create_chapters()
            
        if chapter_index < 0 or chapter_index >= len(self._chapters):
            raise IndexError("Índice de capítulo inválido")
            
        chapter = self._chapters[chapter_index]
        
        try:
            # Combinar texto das páginas do capítulo
            start_page = chapter['start_page']
            end_page = chapter['end_page']
            
            chapter_text = []
            for page_num in range(start_page, end_page + 1):
                if page_num < len(self.pages):
                    page_text = self.pages[page_num]
                    chapter_text.append(f"--- Página {page_num + 1} ---\n{page_text}")
                    
            content = '\n\n'.join(chapter_text)
            
            # Limpar formatação
            content = self._clean_text(content)
            
            return content
            
        except Exception as e:
            print(f"Erro ao obter conteúdo do capítulo: {e}")
            return f"Erro ao carregar conteúdo do capítulo {chapter_index + 1}"
            
    def _clean_text(self, text: str) -> str:
        """Limpa e formata o texto extraído"""
        # Remover espaços extras
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalizar quebras de linha
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remover linhas muito curtas (provavelmente artefatos)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) >= 3 or line == '':  # Manter linhas com pelo menos 3 caracteres ou vazias
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines).strip()
        
    def get_chapter_text_for_summary(self, chapter_index: int) -> str:
        """Obtém texto do capítulo otimizado para resumo"""
        content = self.get_chapter_content(chapter_index)
        
        # Remover marcadores de página para resumo
        content = re.sub(r'--- Página \d+ ---\n', '', content)
        
        # Limpar texto extra
        content = self._clean_text(content)
        
        return content
        
    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Busca por conteúdo no PDF"""
        results = []
        query_lower = query.lower()
        
        # Buscar nas páginas
        for page_num, page_text in enumerate(self.pages):
            if query_lower in page_text.lower():
                # Extrair trecho relevante
                index = page_text.lower().find(query_lower)
                start = max(0, index - 100)
                end = min(len(page_text), index + len(query) + 100)
                excerpt = page_text[start:end]
                
                if start > 0:
                    excerpt = "..." + excerpt
                if end < len(page_text):
                    excerpt = excerpt + "..."
                    
                # Encontrar qual capítulo contém esta página
                chapter_info = self._find_chapter_for_page(page_num)
                
                results.append({
                    'page': page_num + 1,
                    'chapter': chapter_info['index'] if chapter_info else 0,
                    'chapter_title': chapter_info['title'] if chapter_info else f'Página {page_num + 1}',
                    'excerpt': excerpt
                })
                
        return results
        
    def _find_chapter_for_page(self, page_num: int) -> Optional[Dict[str, Any]]:
        """Encontra o capítulo que contém uma página específica"""
        if not hasattr(self, '_chapters'):
            self._chapters = self._create_chapters()
            
        for chapter in self._chapters:
            if chapter['start_page'] <= page_num <= chapter['end_page']:
                return chapter
                
        return None
        
    def get_book_info(self) -> Dict[str, Any]:
        """Retorna informações completas do livro"""
        return {
            'metadata': self.metadata,
            'total_pages': len(self.pages),
            'file_type': 'PDF',
            'pdf_info': {
                'pages': len(self.pdf_reader.pages) if self.pdf_reader else 0,
                'encrypted': self.pdf_reader.is_encrypted if self.pdf_reader else False
            }
        }
        
    def cleanup(self):
        """Limpa recursos"""
        self.pdf_reader = None
        self.pages = []
        self.metadata = {}
        if hasattr(self, '_chapters'):
            delattr(self, '_chapters')