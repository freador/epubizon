"""
Handler para arquivos EPUB
Substitui a funcionalidade do epub-handler.js original
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from PIL import Image
import io
import base64

class EpubHandler:
    def __init__(self):
        self.book = None
        self.chapters = []
        self.metadata = {}
        self.images = {}
        
    def load_book(self, file_path: str) -> Dict[str, Any]:
        """Carrega um arquivo EPUB"""
        try:
            self.book = epub.read_epub(file_path)
            
            # Extrair metadata
            self.metadata = self._extract_metadata()
            
            # Extrair capítulos
            self.chapters = self._extract_chapters()
            
            # Extrair imagens
            self.images = self._extract_images()
            
            return {
                'handler': 'epub',
                'metadata': self.metadata,
                'chapters': self.chapters,
                'total_pages': len(self.chapters),
                'images': list(self.images.keys())
            }
            
        except Exception as e:
            raise Exception(f"Erro ao carregar EPUB: {str(e)}")
    
    def load_book_from_data(self, file_data: bytes) -> Dict[str, Any]:
        """Carrega um arquivo EPUB a partir de dados binários"""
        try:
            # Create a temporary file-like object from the data
            book_io = io.BytesIO(file_data)
            self.book = epub.read_epub(book_io)
            
            # Extrair metadata
            self.metadata = self._extract_metadata()
            
            # Extrair capítulos
            self.chapters = self._extract_chapters()
            
            # Extrair imagens
            self.images = self._extract_images()
            
            return {
                'handler': 'epub',
                'metadata': self.metadata,
                'chapters': self.chapters,
                'total_pages': len(self.chapters),
                'images': list(self.images.keys())
            }
            
        except Exception as e:
            raise Exception(f"Erro ao carregar EPUB dos dados: {str(e)}")
            
    def _extract_metadata(self) -> Dict[str, str]:
        """Extrai metadados do EPUB"""
        metadata = {}
        
        try:
            metadata['title'] = self.book.get_metadata('DC', 'title')[0][0] if self.book.get_metadata('DC', 'title') else 'Título Desconhecido'
            metadata['creator'] = self.book.get_metadata('DC', 'creator')[0][0] if self.book.get_metadata('DC', 'creator') else 'Autor Desconhecido'
            metadata['language'] = self.book.get_metadata('DC', 'language')[0][0] if self.book.get_metadata('DC', 'language') else 'pt'
            metadata['publisher'] = self.book.get_metadata('DC', 'publisher')[0][0] if self.book.get_metadata('DC', 'publisher') else ''
            metadata['description'] = self.book.get_metadata('DC', 'description')[0][0] if self.book.get_metadata('DC', 'description') else ''
        except Exception as e:
            print(f"Erro ao extrair metadados: {e}")
            
        return metadata
        
    def _extract_chapters(self) -> List[Dict[str, Any]]:
        """Extrai capítulos do EPUB"""
        chapters = []
        
        try:
            # Usar tabela de conteúdos se disponível
            if hasattr(self.book, 'toc') and self.book.toc:
                for i, item in enumerate(self.book.toc):
                    # Se item é uma tupla (section, children)
                    if isinstance(item, tuple) and len(item) >= 2:
                        section, children = item
                        if hasattr(section, 'title') and hasattr(section, 'href'):
                            chapters.append({
                                'title': section.title or f'Capítulo {i+1}',
                                'href': section.href,
                                'id': f'chapter-{i}',
                                'index': i
                            })
                        # Processar children se existirem
                        if children:
                            for j, child in enumerate(children):
                                if hasattr(child, 'title') and hasattr(child, 'href'):
                                    chapters.append({
                                        'title': child.title or f'Seção {i+1}.{j+1}',
                                        'href': child.href,
                                        'id': f'chapter-{i}-{j}',
                                        'index': len(chapters)
                                    })
                    # Se item é um Link direto
                    elif hasattr(item, 'title') and hasattr(item, 'href'):
                        chapters.append({
                            'title': item.title or f'Capítulo {i+1}',
                            'href': item.href,
                            'id': f'chapter-{i}',
                            'index': i
                        })
                    # Se item é uma lista de Links
                    elif isinstance(item, list):
                        for j, link in enumerate(item):
                            if hasattr(link, 'title') and hasattr(link, 'href'):
                                chapters.append({
                                    'title': link.title or f'Capítulo {i+1}.{j+1}',
                                    'href': link.href,
                                    'id': f'chapter-{i}-{j}',
                                    'index': len(chapters)
                                })
            
            # Fallback: usar spine se ToC não estiver disponível ou vazio
            if not chapters:
                spine_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]
                
                for i, item in enumerate(spine_items):
                    title = self._extract_title_from_content(item) or f'Capítulo {i+1}'
                    chapters.append({
                        'title': title,
                        'href': item.get_name(),
                        'id': item.get_id() or f'chapter-{i}',
                        'index': i,
                        'item': item
                    })
                    
        except Exception as e:
            print(f"Erro ao extrair capítulos: {e}")
            # Fallback final
            chapters = [{'title': 'Capítulo 1', 'href': '', 'id': 'chapter-0', 'index': 0}]
            
        return chapters
        
    def _extract_title_from_content(self, item) -> Optional[str]:
        """Extrai título do conteúdo HTML"""
        try:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Procurar por tags de título
            for tag in ['h1', 'h2', 'h3', 'title']:
                title_elem = soup.find(tag)
                if title_elem and title_elem.get_text().strip():
                    return title_elem.get_text().strip()
                    
        except Exception:
            pass
            
        return None
        
    def _extract_images(self) -> Dict[str, bytes]:
        """Extrai imagens do EPUB"""
        images = {}
        
        try:
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE:
                    images[item.get_name()] = item.get_content()
                    
        except Exception as e:
            print(f"Erro ao extrair imagens: {e}")
            
        return images
        
    def get_chapter_content(self, chapter_index: int) -> str:
        """Obtém o conteúdo de um capítulo específico"""
        if chapter_index < 0 or chapter_index >= len(self.chapters):
            raise IndexError("Índice de capítulo inválido")
            
        chapter = self.chapters[chapter_index]
        
        try:
            # Tentar obter conteúdo pelo href
            if chapter['href']:
                item = self.book.get_item_with_href(chapter['href'])
                if item:
                    return self._process_chapter_content(item)
                    
            # Tentar obter pelo ID
            if chapter.get('id'):
                item = self.book.get_item_with_id(chapter['id'])
                if item:
                    return self._process_chapter_content(item)
                    
            # Tentar usar item armazenado
            if 'item' in chapter:
                return self._process_chapter_content(chapter['item'])
                
            # Fallback para conteúdo genérico
            return self._generate_mock_content(chapter)
            
        except Exception as e:
            print(f"Erro ao obter conteúdo do capítulo: {e}")
            return self._generate_mock_content(chapter)
            
    def _process_chapter_content(self, item) -> str:
        """Processa o conteúdo de um capítulo"""
        try:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remover elementos desnecessários
            for tag in soup.find_all(['script', 'style', 'head']):
                tag.decompose()
                
            # Processar imagens
            self._process_images_in_content(soup)
            
            # Extrair texto limpo
            text_content = soup.get_text()
            
            # Limpar formatação
            text_content = re.sub(r'\n\s*\n', '\n\n', text_content)  # Normalizar quebras
            text_content = re.sub(r'[ \t]+', ' ', text_content)       # Normalizar espaços
            text_content = text_content.strip()
            
            return text_content
            
        except Exception as e:
            print(f"Erro ao processar conteúdo: {e}")
            return f"Conteúdo não disponível: {str(e)}"
            
    def _process_images_in_content(self, soup: BeautifulSoup):
        """Processa imagens no conteúdo HTML"""
        try:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src and src in self.images:
                    # Converter imagem para base64
                    image_data = self.images[src]
                    try:
                        # Tentar determinar formato da imagem
                        with Image.open(io.BytesIO(image_data)) as pil_image:
                            format_name = pil_image.format.lower()
                            mime_type = f"image/{format_name}"
                            
                        # Codificar em base64
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                        data_uri = f"data:{mime_type};base64,{base64_data}"
                        
                        # Criar elemento de placeholder para imagem
                        img.replace_with(soup.new_string(f"\n[IMAGEM: {src}]\n"))
                        
                    except Exception as img_error:
                        print(f"Erro ao processar imagem {src}: {img_error}")
                        img.replace_with(soup.new_string(f"\n[IMAGEM: {src}]\n"))
                        
        except Exception as e:
            print(f"Erro ao processar imagens: {e}")
            
    def _generate_mock_content(self, chapter: Dict[str, Any]) -> str:
        """Gera conteúdo mock para demonstração"""
        title = chapter.get('title', 'Capítulo')
        return f"""
        {title}
        
        Este é o conteúdo do {title.lower()}. Em uma implementação real, este texto seria extraído diretamente do arquivo EPUB.
        
        O capítulo contém informações detalhadas sobre o tópico, com múltiplas seções e subseções. Inclui exemplos, explicações e orientações práticas para os leitores.
        
        Este conteúdo representa o texto real que seria usado para gerar resumos significativos usando IA.
        
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """.strip()
        
    def get_chapter_text_for_summary(self, chapter_index: int) -> str:
        """Obtém texto do capítulo otimizado para resumo"""
        content = self.get_chapter_content(chapter_index)
        
        # Remover marcadores de imagem para resumo
        content = re.sub(r'\[IMAGEM:.*?\]', '', content)
        
        # Limpar espaços extras
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
        
    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Busca por conteúdo nos capítulos"""
        results = []
        query_lower = query.lower()
        
        for i, chapter in enumerate(self.chapters):
            try:
                content = self.get_chapter_content(i)
                if query_lower in content.lower():
                    # Extrair trecho relevante
                    index = content.lower().find(query_lower)
                    start = max(0, index - 100)
                    end = min(len(content), index + len(query) + 100)
                    excerpt = content[start:end]
                    
                    if start > 0:
                        excerpt = "..." + excerpt
                    if end < len(content):
                        excerpt = excerpt + "..."
                        
                    results.append({
                        'chapter': i,
                        'title': chapter['title'],
                        'excerpt': excerpt
                    })
                    
            except Exception as e:
                print(f"Erro ao buscar no capítulo {i}: {e}")
                
        return results
        
    def get_book_info(self) -> Dict[str, Any]:
        """Retorna informações completas do livro"""
        return {
            'metadata': self.metadata,
            'chapters': self.chapters,
            'total_chapters': len(self.chapters),
            'total_images': len(self.images),
            'file_type': 'EPUB'
        }
        
    def cleanup(self):
        """Limpa recursos"""
        self.book = None
        self.chapters = []
        self.metadata = {}
        self.images = {}