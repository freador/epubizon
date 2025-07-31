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
                print("ToC não encontrada, usando spine items...")
                spine_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]
                print(f"Encontrados {len(spine_items)} spine items")
                
                for i, item in enumerate(spine_items):
                    title = self._extract_title_from_content(item) or f'Capítulo {i+1}'
                    print(f"Spine item {i}: {title} ({item.get_name()})")
                    chapters.append({
                        'title': title,
                        'href': item.get_name(),
                        'id': item.get_id() or f'chapter-{i}',
                        'index': i,
                        'item': item
                    })
                    
        except Exception as e:
            print(f"Erro ao extrair capítulos: {e}")
            # Fallback final - tentar pelo menos obter alguns spine items
            try:
                spine_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]
                if spine_items:
                    chapters = [{
                        'title': f'Seção {i+1}',
                        'href': item.get_name(),
                        'id': item.get_id() or f'section-{i}',
                        'index': i,
                        'item': item
                    } for i, item in enumerate(spine_items[:10])]  # Limitar a 10 itens
                else:
                    chapters = []
            except:
                chapters = []
            
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
        print(f"Carregando capítulo {chapter_index}: {chapter['title']}")
        
        try:
            # Primeiro, tentar obter pelo href do ToC
            href = chapter.get('href', '')
            if href:
                print(f"Tentando carregar por href: {href}")
                
                # Remover âncora se existir (exemplo: file.html#section)
                base_href = href.split('#')[0]
                
                # Tentar obter item pelo href base
                item = self.book.get_item_with_href(base_href)
                if item:
                    print(f"Item encontrado: {item.get_name()}")
                    content = self._process_chapter_content(item)
                    
                    # Se há uma âncora, tentar encontrar a seção específica
                    if '#' in href:
                        anchor = href.split('#')[1]
                        print(f"Procurando âncora: {anchor}")
                        content = self._extract_section_content(item, anchor, content)
                    
                    if content and len(content.strip()) > 20:  # Verificar se há conteúdo suficiente
                        return content
                        
            # Fallback: se não conseguiu pelo ToC, tentar pelo spine item armazenado
            if 'item' in chapter:
                print("Usando item armazenado do spine")
                return self._process_chapter_content(chapter['item'])
                
            # Fallback final: usar o índice do capítulo no spine
            spine_items = [item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]
            if chapter_index < len(spine_items):
                print(f"Usando spine item {chapter_index}")
                return self._process_chapter_content(spine_items[chapter_index])
            else:
                return f"Capítulo {chapter_index + 1} não encontrado no arquivo EPUB."
            
        except Exception as e:
            print(f"Erro ao obter conteúdo do capítulo: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro ao carregar capítulo {chapter_index + 1}: {str(e)}"
            
    def _extract_section_content(self, item, anchor: str, full_content: str) -> str:
        """Extrai conteúdo de uma seção específica usando âncora"""
        try:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Procurar elemento com ID correspondente à âncora
            target_element = soup.find(id=anchor)
            if target_element:
                # Coletar conteúdo a partir deste elemento
                section_content = []
                current = target_element
                
                # Incluir o próprio elemento e próximos elementos até encontrar outro cabeçalho
                while current:
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and current != target_element:
                        break  # Parar no próximo cabeçalho
                    
                    if hasattr(current, 'get_text'):
                        text = current.get_text().strip()
                        if text:
                            section_content.append(text)
                    
                    current = current.find_next_sibling()
                
                if section_content:
                    result = '\n\n'.join(section_content)
                    # Processar imagens nesta seção
                    self._process_images_in_content(soup)
                    return self._html_to_text(soup)
                    
        except Exception as e:
            print(f"Erro ao extrair seção {anchor}: {e}")
        
        # Se não conseguiu extrair a seção específica, retornar conteúdo completo
        return full_content
            
    def _process_chapter_content(self, item) -> str:
        """Processa o conteúdo de um capítulo"""
        try:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remover elementos desnecessários
            for tag in soup.find_all(['script', 'style', 'head']):
                tag.decompose()
            
            # Processar imagens primeiro
            self._process_images_in_content(soup)
            
            # Converter HTML para texto preservando estrutura
            text_content = self._html_to_text(soup)
            
            return text_content
            
        except Exception as e:
            print(f"Erro ao processar conteúdo: {e}")
            return f"Erro ao processar capítulo: {str(e)}"
            
    def _html_to_text(self, soup: BeautifulSoup) -> str:
        """Converte HTML para texto preservando estrutura e imagens"""
        result_parts = []
        
        for element in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'img']):
            if element.name == 'img':
                data_src = element.get('data-src')
                if data_src:
                    result_parts.append(f"\n[IMAGE_DATA:{data_src}]\n")
                else:
                    alt_text = element.get('alt', 'Imagem')
                    result_parts.append(f"\n[IMAGEM: {alt_text}]\n")
            elif element.name == 'br':
                result_parts.append('\n')
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = element.get_text().strip()
                if text:
                    result_parts.append(f'\n\n{text}\n\n')
            else:  # p, div
                text = element.get_text().strip()
                if text:
                    result_parts.append(f'{text}\n\n')
        
        # Se não encontrou elementos estruturados, extrair todo o texto
        if not result_parts:
            result_parts.append(soup.get_text())
        
        # Juntar e limpar
        full_text = ''.join(result_parts)
        
        # Limpar formatação
        full_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', full_text)  # Múltiplas quebras
        full_text = re.sub(r'[ \t]+', ' ', full_text)  # Espaços extras
        full_text = full_text.strip()
        
        return full_text
            
    def _process_images_in_content(self, soup: BeautifulSoup):
        """Processa imagens no conteúdo HTML"""
        try:
            for img in soup.find_all('img'):
                src = img.get('src', '')
                
                # Limpar src de possíveis caminhos relativos
                if src.startswith('./'):
                    src = src[2:]
                elif src.startswith('../'):
                    # Para caminhos com ../ tentar encontrar a imagem
                    base_name = src.split('/')[-1]
                    for img_name in self.images.keys():
                        if img_name.endswith(base_name):
                            src = img_name
                            break
                
                if src and src in self.images:
                    # Converter imagem para base64
                    image_data = self.images[src]
                    try:
                        # Tentar determinar formato da imagem
                        with Image.open(io.BytesIO(image_data)) as pil_image:
                            format_name = pil_image.format.lower()
                            if format_name == 'jpeg':
                                format_name = 'jpg'
                            mime_type = f"image/{format_name}"
                            
                        # Codificar em base64
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                        data_uri = f"data:{mime_type};base64,{base64_data}"
                        
                        # Armazenar data URI
                        img['data-src'] = data_uri
                        img['data-original-src'] = src
                        print(f"Processada imagem: {src} -> data URI de {len(data_uri)} chars")
                        
                    except Exception as img_error:
                        print(f"Erro ao processar imagem {src}: {img_error}")
                        img['alt'] = f'Erro ao carregar: {src}'
                else:
                    print(f"Imagem não encontrada: {src}")
                    print(f"Imagens disponíveis: {list(self.images.keys())[:5]}...")  # Mostrar apenas 5 primeiras
                    img['alt'] = f'Imagem não encontrada: {src}'
                        
        except Exception as e:
            print(f"Erro ao processar imagens: {e}")
            
        
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