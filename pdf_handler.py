"""
Handler para arquivos PDF
Substitui parte da funcionalidade do aplicativo original
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import io

try:
    import fitz  # PyMuPDF - better text extraction
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    import PyPDF2

class PdfHandler:
    def __init__(self):
        self.pdf_document = None
        self.pdf_reader = None  # Keep for compatibility
        self.pages = []
        self.metadata = {}
        self.pages_per_chapter = 10  # Páginas por "capítulo"
        self.use_pymupdf = PYMUPDF_AVAILABLE
        
    def load_book(self, file_path: str) -> Dict[str, Any]:
        """Carrega um arquivo PDF"""
        try:
            if self.use_pymupdf:
                self.pdf_document = fitz.open(file_path)
                pdf_pages_count = len(self.pdf_document)
            else:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    pdf_io = io.BytesIO(file_data)
                    self.pdf_reader = PyPDF2.PdfReader(pdf_io)
                    pdf_pages_count = len(self.pdf_reader.pages)
                
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
                'pdf_pages': pdf_pages_count
            }
                
        except Exception as e:
            print(f"Erro ao carregar PDF: {e}")
            raise Exception(f"Erro ao carregar PDF: {str(e)}")
    
    def load_book_from_data(self, file_data: bytes) -> Dict[str, Any]:
        """Carrega um arquivo PDF a partir de dados binários"""
        try:
            if self.use_pymupdf:
                self.pdf_document = fitz.open(stream=file_data, filetype="pdf")
                pdf_pages_count = len(self.pdf_document)
            else:
                pdf_io = io.BytesIO(file_data)
                self.pdf_reader = PyPDF2.PdfReader(pdf_io)
                pdf_pages_count = len(self.pdf_reader.pages)
            
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
                'pdf_pages': pdf_pages_count
            }
            
        except Exception as e:
            print(f"Erro ao carregar PDF dos dados: {e}")
            raise Exception(f"Erro ao carregar PDF dos dados: {str(e)}")
            
    def _extract_metadata(self) -> Dict[str, str]:
        """Extrai metadados do PDF"""
        metadata = {}
        
        try:
            if self.use_pymupdf and self.pdf_document:
                pdf_metadata = self.pdf_document.metadata
                metadata['title'] = pdf_metadata.get('title', 'Documento PDF') or 'Documento PDF'
                metadata['creator'] = pdf_metadata.get('author', 'Autor Desconhecido') or 'Autor Desconhecido'
                metadata['subject'] = pdf_metadata.get('subject', '') or ''
                metadata['producer'] = pdf_metadata.get('producer', '') or ''
                metadata['creation_date'] = pdf_metadata.get('creationDate', '') or ''
            elif self.pdf_reader:
                pdf_metadata = self.pdf_reader.metadata
                if pdf_metadata:
                    metadata['title'] = pdf_metadata.get('/Title', 'Documento PDF') or 'Documento PDF'
                    metadata['creator'] = pdf_metadata.get('/Author', 'Autor Desconhecido') or 'Autor Desconhecido'
                    metadata['subject'] = pdf_metadata.get('/Subject', '') or ''
                    metadata['producer'] = pdf_metadata.get('/Producer', '') or ''
                    metadata['creation_date'] = str(pdf_metadata.get('/CreationDate', '')) or ''
                else:
                    metadata['title'] = 'Documento PDF'
                    metadata['creator'] = 'Autor Desconhecido'
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
            if self.use_pymupdf and self.pdf_document:
                # Use PyMuPDF for better text extraction
                for page_num in range(len(self.pdf_document)):
                    try:
                        page = self.pdf_document[page_num]
                        text = page.get_text()
                        
                        if text.strip():
                            # Clean and format the text
                            cleaned_text = self._clean_extracted_text(text)
                            pages.append(cleaned_text)
                        else:
                            pages.append(f"[Página {page_num + 1} - Sem texto extraível]")
                    except Exception as e:
                        print(f"Erro ao extrair texto da página {page_num + 1}: {e}")
                        pages.append(f"[Página {page_num + 1} - Erro na extração]")
            else:
                # Fallback to PyPDF2
                for page_num, page in enumerate(self.pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            cleaned_text = self._clean_extracted_text(text)
                            pages.append(cleaned_text)
                        else:
                            pages.append(f"[Página {page_num + 1} - Sem texto extraível]")
                    except Exception as e:
                        print(f"Erro ao extrair texto da página {page_num + 1}: {e}")
                        pages.append(f"[Página {page_num + 1} - Erro na extração]")
                    
        except Exception as e:
            print(f"Erro ao extrair páginas: {e}")
            pages = ["Erro ao extrair conteúdo do PDF"]
            
        return pages
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespaces and normalize line breaks
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
        
        # Remove lines that are just numbers (page numbers, etc.)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip very short lines that are likely artifacts
            if len(line) < 2:
                if line == "":
                    cleaned_lines.append("")  # Keep empty lines for paragraph breaks
                continue
                
            # Skip lines that are just numbers (likely page numbers)
            if line.isdigit() and len(line) <= 3:
                continue
                
            # Skip lines with just punctuation or special characters
            if re.match(r'^[^\w\s]*$', line):
                continue
                
            cleaned_lines.append(line)
        
        # Join lines and clean up excessive spacing
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive line breaks
        
        return result.strip()
        
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
        
        if total_pages == 0:
            return []
        
        # Ajustar número de páginas por capítulo baseado no tamanho total
        if total_pages <= 10:
            pages_per_chapter = 2  # Very small docs: 2 pages per chapter
        elif total_pages <= 20:
            pages_per_chapter = 3  # Small docs: 3 pages per chapter
        elif total_pages <= 50:
            pages_per_chapter = 5  # Medium docs: 5 pages per chapter
        elif total_pages <= 100:
            pages_per_chapter = 8  # Large docs: 8 pages per chapter
        else:
            pages_per_chapter = 10  # Very large docs: 10 pages per chapter
            
        chapter_num = 1
        start_page = 0
        
        while start_page < total_pages:
            end_page = min(start_page + pages_per_chapter - 1, total_pages - 1)
            
            # Try to create a meaningful title from the first page content
            chapter_title = self._generate_chapter_title(start_page, end_page, chapter_num)
            
            chapters.append({
                'title': chapter_title,
                'start_page': start_page,
                'end_page': end_page,
                'index': chapter_num - 1
            })
            
            start_page = end_page + 1
            chapter_num += 1
            
        return chapters
    
    def _generate_chapter_title(self, start_page: int, end_page: int, chapter_num: int = None) -> str:
        """Generate a meaningful chapter title from page content"""
        try:
            if start_page < len(self.pages):
                first_page_text = self.pages[start_page]
                
                # Look for potential headings in the first few lines
                lines = first_page_text.split('\n')[:5]  # Check first 5 lines
                
                for line in lines:
                    line = line.strip()
                    # Look for lines that could be titles (reasonable length, not all caps unless short)
                    if 10 <= len(line) <= 80 and not line.isdigit():
                        # Avoid lines that are mostly punctuation or special chars
                        if len(re.sub(r'[^\w\s]', '', line)) >= len(line) * 0.7:
                            chap_num = chapter_num if chapter_num is not None else (start_page//5 + 1)
                            return f"Cap. {chap_num}: {line[:50]}{'...' if len(line) > 50 else ''}"
                
                # Fallback: use first meaningful sentence
                sentences = re.split(r'[.!?]+', first_page_text)
                for sentence in sentences[:3]:
                    sentence = sentence.strip()
                    if 15 <= len(sentence) <= 100:
                        chap_num = chapter_num if chapter_num is not None else (start_page//5 + 1)
                        return f"Cap. {chap_num}: {sentence[:50]}{'...' if len(sentence) > 50 else ''}"
            
        except Exception as e:
            print(f"Erro ao gerar título do capítulo: {e}")
        
        # Final fallback
        if start_page == end_page:
            return f'Página {start_page + 1}'
        else:
            return f'Páginas {start_page + 1}-{end_page + 1}'
        
    def get_chapter_content(self, chapter_index: int) -> str:
        """Obtém o conteúdo de um capítulo específico"""
        try:
            # Verificar se temos capítulos válidos
            if not hasattr(self, '_chapters') or not self._chapters:
                self._chapters = self._create_chapters()
                
            if not self._chapters:
                return "Erro: Nenhum capítulo disponível"
                
            if chapter_index < 0 or chapter_index >= len(self._chapters):
                return f"Erro: Índice de capítulo inválido ({chapter_index})"
                
            chapter = self._chapters[chapter_index]
            
            # Combinar texto das páginas do capítulo
            start_page = chapter.get('start_page', 0)
            end_page = chapter.get('end_page', 0)
            
            if start_page < 0 or end_page < 0:
                return "Erro: Páginas inválidas no capítulo"
            
            chapter_text = []
            for page_num in range(start_page, end_page + 1):
                if page_num < len(self.pages):
                    page_text = self.pages[page_num]
                    if page_text and page_text.strip():
                        chapter_text.append(f"--- Página {page_num + 1} ---\n{page_text}")
                    else:
                        chapter_text.append(f"--- Página {page_num + 1} ---\n[Página vazia ou sem texto]")
                    
            if not chapter_text:
                return f"[Capítulo {chapter_index + 1} vazio]"
                    
            content = '\n\n'.join(chapter_text)
            
            # Limpar formatação
            content = self._clean_text(content)
            
            return content
            
        except Exception as e:
            print(f"Erro ao obter conteúdo do capítulo: {e}")
            return f"Erro ao carregar conteúdo do capítulo {chapter_index + 1}: {str(e)}"
            
    def _clean_text(self, text: str) -> str:
        """Limpa e formata o texto extraído"""
        if not text:
            return ""
        
        # First pass: basic cleanup
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
        
        # Split into lines for detailed cleaning
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Keep empty lines for paragraph separation
            if line == '':
                cleaned_lines.append('')
                continue
            
            # Skip very short lines that are likely artifacts
            if len(line) < 3:
                continue
                
            # Skip lines that are just numbers (page numbers, etc.)
            if line.isdigit() and len(line) <= 4:
                continue
                
            # Skip lines with only punctuation or special characters
            if re.match(r'^[^\w\s]*$', line):
                continue
                
            # Skip lines that are mostly repetitive characters (artifacts)
            if len(set(line.replace(' ', ''))) <= 2 and len(line) > 10:
                continue
                
            cleaned_lines.append(line)
        
        # Join and final cleanup
        result = '\n'.join(cleaned_lines)
        
        # Remove excessive line breaks
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # Fix common PDF extraction issues
        result = re.sub(r'(\w)-\n(\w)', r'\1\2', result)  # Fix hyphenated words split across lines
        result = re.sub(r'([a-z])\n([a-z])', r'\1 \2', result)  # Join words split across lines
        
        return result.strip()
        
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
        pdf_pages = 0
        encrypted = False
        
        if self.use_pymupdf and self.pdf_document:
            pdf_pages = len(self.pdf_document)
            encrypted = self.pdf_document.needs_pass
        elif self.pdf_reader:
            pdf_pages = len(self.pdf_reader.pages)
            encrypted = self.pdf_reader.is_encrypted
            
        return {
            'metadata': self.metadata,
            'total_pages': len(self.pages),
            'file_type': 'PDF',
            'extraction_method': 'PyMuPDF' if self.use_pymupdf else 'PyPDF2',
            'pdf_info': {
                'pages': pdf_pages,
                'encrypted': encrypted
            }
        }
        
    def cleanup(self):
        """Limpa recursos"""
        if self.pdf_document:
            try:
                self.pdf_document.close()
            except:
                pass
            self.pdf_document = None
            
        self.pdf_reader = None
        self.pages = []
        self.metadata = {}
        if hasattr(self, '_chapters'):
            delattr(self, '_chapters')