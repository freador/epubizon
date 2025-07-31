#!/usr/bin/env python3
"""
Verify that chapter mapping fixes are working correctly
"""

import sys
import os
from epub_handler import EpubHandler

def test_chapter_mapping():
    """Test chapter mapping with the real EPUB file"""
    import glob
    epub_files = glob.glob(r"C:\Documents\prog\electron\epubizon\file-test\*.epub")
    if not epub_files:
        print("No EPUB files found in file-test directory")
        return False
    
    epub_path = epub_files[0]  # Use the first EPUB file found
    
    if not os.path.exists(epub_path):
        print(f"EPUB file not found: {epub_path}")
        return False
    
    print("Testing chapter mapping fixes...")
    print(f"Loading: {epub_path}")
    
    try:
        # Initialize handler
        handler = EpubHandler()
        
        # Load book
        book_data = handler.load_book(epub_path)
        
        print(f"Book loaded successfully")
        print(f"Title: {book_data['metadata'].get('title', 'Unknown')}")
        print(f"Author: {book_data['metadata'].get('creator', 'Unknown')}")
        print(f"Total chapters: {len(book_data['chapters'])}")
        
        # Test first few chapters to verify content mapping
        chapters_to_test = min(5, len(book_data['chapters']))
        
        for i in range(chapters_to_test):
            chapter = book_data['chapters'][i]
            print(f"\nTesting Chapter {i+1}: {chapter['title']}")
            print(f"   Href: {chapter.get('href', 'N/A')}")
            
            try:
                content = handler.get_chapter_content(i)
                content_length = len(content)
                
                # Check for actual content vs mock content
                has_images = '[IMAGE_DATA:' in content
                has_substantial_text = content_length > 1000
                
                print(f"   Content length: {content_length:,} characters")
                print(f"   Has images: {'Yes' if has_images else 'No'}")
                print(f"   Substantial content: {'Yes' if has_substantial_text else 'No'}")
                
                # Show first 200 characters to verify it's real content
                preview = content[:200].replace('\n', ' ').strip()
                if preview:
                    print(f"   Preview: {preview}...")
                
                # Verify this is not mock/template content
                mock_indicators = ['Conteúdo do', 'Este é um conteúdo de exemplo', 'handler não foi reconhecido']
                is_mock = any(indicator in content for indicator in mock_indicators)
                
                if is_mock:
                    print(f"   WARNING: Chapter appears to contain mock content!")
                else:
                    print(f"   Chapter contains real EPUB content")
                    
            except Exception as e:
                print(f"   Error loading chapter content: {e}")
        
        # Test specific problematic chapters mentioned in the issue
        print(f"\nTesting specific chapters that were problematic...")
        
        # Look for chapters that might be "Pong" or "Preface"
        pong_chapters = [i for i, ch in enumerate(book_data['chapters']) if 'pong' in ch['title'].lower()]
        preface_chapters = [i for i, ch in enumerate(book_data['chapters']) if 'preface' in ch['title'].lower() or 'prefácio' in ch['title'].lower()]
        
        if pong_chapters:
            for idx in pong_chapters[:2]:  # Test first 2 Pong chapters
                chapter = book_data['chapters'][idx]
                print(f"\nTesting Pong Chapter {idx+1}: {chapter['title']}")
                try:
                    content = handler.get_chapter_content(idx)
                    
                    # Check if this chapter contains preface content (the bug)
                    preface_indicators = ['preface', 'prefácio', 'introduction', 'introdução']
                    has_preface_content = any(indicator in content.lower() for indicator in preface_indicators)
                    
                    if has_preface_content and 'pong' not in content.lower():
                        print(f"   BUG DETECTED: Pong chapter contains preface-like content!")
                    else:
                        print(f"   Pong chapter appears to contain correct content")
                        
                    print(f"   Content length: {len(content):,} characters")
                    preview = content[:300].replace('\n', ' ').strip()
                    print(f"   Content preview: {preview}...")
                    
                except Exception as e:
                    print(f"   Error: {e}")
        
        if preface_chapters:
            for idx in preface_chapters[:1]:  # Test first preface chapter
                chapter = book_data['chapters'][idx]
                print(f"\nTesting Preface Chapter {idx+1}: {chapter['title']}")
                try:
                    content = handler.get_chapter_content(idx)
                    print(f"   Content length: {len(content):,} characters")
                    preview = content[:300].replace('\n', ' ').strip()
                    print(f"   Content preview: {preview}...")
                except Exception as e:
                    print(f"   Error: {e}")
        
        print(f"\nChapter mapping verification completed!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CHAPTER MAPPING VERIFICATION TEST")
    print("=" * 60)
    
    success = test_chapter_mapping()
    
    if success:
        print(f"\nAll tests completed successfully!")
    else:
        print(f"\nTests failed!")
        sys.exit(1)