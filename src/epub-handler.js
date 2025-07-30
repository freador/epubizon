// EPUB file handler using epub.js library
class EpubHandler {
    constructor() {
        this.book = null;
        this.rendition = null;
        this.chapters = [];
        this.currentLocation = null;
        this.textContent = new Map(); // Cache for extracted text
        this.imageBlobUrls = new Set(); // Track blob URLs for cleanup
    }

    async loadBook(arrayBuffer) {
        try {
            console.log('Loading EPUB with real implementation...');
            console.log('File size:', Math.round(arrayBuffer.byteLength / 1024 / 1024), 'MB');
            
            // Import epub.js - it should be available in the renderer process
            const ePub = await this.loadEpubJs();
            
            // Create book from array buffer
            this.book = ePub(arrayBuffer);
            await this.book.ready;
            
            console.log('EPUB loaded successfully, extracting metadata...');
            
            // Get metadata first (lightweight operation)
            const metadata = await this.book.loaded.metadata;
            console.log('EPUB metadata:', metadata);
            
            // Extract chapters lazily (don't load all content at once)
            await this.extractChaptersLazy();
            
            // For large books, estimate pages more intelligently
            const estimatedPages = this.estimateTotalPages();
            
            const bookData = {
                chapters: this.chapters,
                totalPages: estimatedPages,
                metadata: {
                    title: metadata.title || 'Unknown Title',
                    creator: metadata.creator || 'Unknown Author',
                    language: metadata.language || 'en',
                    publisher: metadata.publisher || '',
                    description: metadata.description || ''
                },
                isLargeFile: this.chapters.length > 50 || estimatedPages > 500
            };
            
            console.log(`EPUB processing complete: ${this.chapters.length} chapters, ~${estimatedPages} pages`);
            return bookData;
            
        } catch (error) {
            console.error('Error loading EPUB:', error);
            // Fallback to mock if real implementation fails
            console.warn('Falling back to mock EPUB implementation');
            return await this.mockLoadBook(arrayBuffer);
        }
    }

    async loadEpubJs() {
        try {
            // Try to use installed epub.js package via require in main process
            if (typeof window !== 'undefined' && !window.ePub) {
                return new Promise((resolve, reject) => {
                    // Load JSZip first from node_modules
                    if (!window.JSZip) {
                        const jszipScript = document.createElement('script');
                        jszipScript.src = './node_modules/jszip/dist/jszip.min.js';
                        jszipScript.onload = () => {
                            // Now load epub.js from node_modules
                            const epubScript = document.createElement('script');
                            epubScript.src = './node_modules/epubjs/dist/epub.min.js';
                            epubScript.onload = () => {
                                if (window.ePub) {
                                    resolve(window.ePub);
                                } else {
                                    reject(new Error('ePub not available after loading'));
                                }
                            };
                            epubScript.onerror = () => {
                                console.warn('Failed to load epub.js from node_modules, trying CDN fallback');
                                // Fallback to CDN
                                this.loadEpubJsFromCDN().then(resolve).catch(reject);
                            };
                            document.head.appendChild(epubScript);
                        };
                        jszipScript.onerror = () => {
                            console.warn('Failed to load JSZip from node_modules, trying CDN fallback');
                            // Fallback to CDN
                            this.loadEpubJsFromCDN().then(resolve).catch(reject);
                        };
                        document.head.appendChild(jszipScript);
                    } else {
                        // JSZip already loaded, just load epub.js
                        const script = document.createElement('script');
                        script.src = './node_modules/epubjs/dist/epub.min.js';
                        script.onload = () => {
                            if (window.ePub) {
                                resolve(window.ePub);
                            } else {
                                reject(new Error('ePub not available after loading'));
                            }
                        };
                        script.onerror = () => {
                            console.warn('Failed to load epub.js from node_modules, trying CDN fallback');
                            this.loadEpubJsFromCDN().then(resolve).catch(reject);
                        };
                        document.head.appendChild(script);
                    }
                });
            } else if (window.ePub) {
                return window.ePub;
            } else {
                throw new Error('ePub not available');
            }
        } catch (error) {
            throw new Error('Could not load epub.js library');
        }
    }

    async loadEpubJsFromCDN() {
        return new Promise((resolve, reject) => {
            // Load JSZip first (required by epub.js)
            if (!window.JSZip) {
                const jszipScript = document.createElement('script');
                jszipScript.src = 'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js';
                jszipScript.onload = () => {
                    // Now load epub.js
                    const epubScript = document.createElement('script');
                    epubScript.src = 'https://cdn.jsdelivr.net/npm/epubjs@0.3.93/dist/epub.min.js';
                    epubScript.onload = () => {
                        if (window.ePub) {
                            resolve(window.ePub);
                        } else {
                            reject(new Error('ePub not available after loading'));
                        }
                    };
                    epubScript.onerror = () => reject(new Error('Failed to load epub.js'));
                    document.head.appendChild(epubScript);
                };
                jszipScript.onerror = () => reject(new Error('Failed to load JSZip'));
                document.head.appendChild(jszipScript);
            } else {
                // JSZip already loaded, just load epub.js
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/epubjs@0.3.93/dist/epub.min.js';
                script.onload = () => {
                    if (window.ePub) {
                        resolve(window.ePub);
                    } else {
                        reject(new Error('ePub not available after loading'));
                    }
                };
                script.onerror = () => reject(new Error('Failed to load epub.js'));
                document.head.appendChild(script);
            }
        });
    }

    // Mock implementation for demonstration
    async mockLoadBook(arrayBuffer) {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Mock chapters data
        this.chapters = [
            { title: 'Chapter 1: Introduction', href: 'chapter1.xhtml', pageCount: 15 },
            { title: 'Chapter 2: Getting Started', href: 'chapter2.xhtml', pageCount: 20 },
            { title: 'Chapter 3: Advanced Topics', href: 'chapter3.xhtml', pageCount: 25 },
            { title: 'Chapter 4: Examples', href: 'chapter4.xhtml', pageCount: 18 },
            { title: 'Chapter 5: Conclusion', href: 'chapter5.xhtml', pageCount: 12 }
        ];

        return {
            chapters: this.chapters,
            totalPages: this.chapters.reduce((total, chapter) => total + chapter.pageCount, 0),
            metadata: {
                title: 'Sample EPUB Book',
                creator: 'Demo Author',
                language: 'en'
            }
        };
    }

    async extractChapters() {
        if (!this.book) return;

        try {
            const navigation = await this.book.loaded.navigation;
            
            if (navigation.toc && navigation.toc.length > 0) {
                this.chapters = navigation.toc.map((chapter, index) => ({
                    title: chapter.label || `Chapter ${index + 1}`,
                    href: chapter.href,
                    id: chapter.id || `chapter-${index}`,
                    pageCount: 1
                }));
            } else {
                // Fallback: create chapters based on spine
                const spine = await this.book.loaded.spine;
                this.chapters = spine.spineItems.map((item, index) => ({
                    title: `Chapter ${index + 1}`,
                    href: item.href,
                    id: item.id || `chapter-${index}`,
                    pageCount: 1
                }));
            }
        } catch (error) {
            console.error('Error extracting chapters:', error);
            // Final fallback
            this.chapters = [{ title: 'Chapter 1', href: '', id: 'chapter-0', pageCount: 1 }];
        }
    }

    async extractChaptersLazy() {
        if (!this.book) return;

        try {
            console.log('Extracting chapters (lazy mode)...');
            const navigation = await this.book.loaded.navigation;
            
            if (navigation.toc && navigation.toc.length > 0) {
                // Use table of contents for better chapter organization
                this.chapters = navigation.toc.map((chapter, index) => ({
                    title: chapter.label || `Chapter ${index + 1}`,
                    href: chapter.href,
                    id: chapter.id || `chapter-${index}`,
                    pageCount: null,
                    loaded: false
                }));
            } else {
                // Fallback: create chapters based on spine (but limit for performance)
                const spine = await this.book.loaded.spine;
                const maxChapters = Math.min(spine.spineItems.length, 200);
                
                this.chapters = spine.spineItems.slice(0, maxChapters).map((item, index) => ({
                    title: item.href.includes('chapter') || item.href.includes('ch') ? 
                           `Chapter ${index + 1}` : 
                           `Section ${index + 1}`,
                    href: item.href,
                    id: item.id || `section-${index}`,
                    pageCount: null,
                    loaded: false
                }));
            }
        } catch (error) {
            console.error('Error extracting chapters (lazy):', error);
            // Final fallback
            this.chapters = [{ 
                title: 'Chapter 1', 
                href: '', 
                id: 'chapter-0', 
                pageCount: null,
                loaded: false 
            }];
        }
    }

    estimateTotalPages() {
        // Estimate total pages based on file size and chapter count
        if (!this.book || !this.chapters.length) return 1;
        
        try {
            // Rough estimation: 1-3 pages per chapter on average for large books
            const baseEstimate = this.chapters.length * 2;
            
            // Adjust based on file size if available
            // Large EPUBs typically have 1-5 pages per chapter
            if (this.chapters.length > 100) {
                return Math.max(baseEstimate, this.chapters.length * 1.5);
            } else if (this.chapters.length > 50) {
                return Math.max(baseEstimate, this.chapters.length * 2);
            } else {
                return Math.max(baseEstimate, this.chapters.length * 3);
            }
        } catch (error) {
            console.error('Error estimating pages:', error);
            return this.chapters.length;
        }
    }

    async renderChapter(chapterIndex) {
        if (chapterIndex < 0 || chapterIndex >= this.chapters.length) {
            throw new Error('Invalid chapter index');
        }

        const chapter = this.chapters[chapterIndex];
        console.log('Rendering chapter:', chapterIndex, chapter.title);
        
        // Show loading indicator for large files
        if (this.chapters.length > 50) {
            console.log('Large file detected, using optimized rendering...');
        }
        
        try {
            if (this.book && chapter.href) {
                console.log('Loading chapter content from:', chapter.href);
                
                // Get the section directly from the book
                const section = this.book.section(chapter.href);
                if (section) {
                    // Load and render the section
                    await section.load(this.book.load.bind(this.book));
                    
                    // Get the document content
                    const doc = section.document;
                    if (doc) {
                        const body = doc.querySelector('body') || doc.documentElement;
                        let htmlContent = body ? body.innerHTML : '';
                        
                        if (htmlContent) {
                            console.log('Successfully extracted chapter content, length:', htmlContent.length);
                            return await this.processHtmlContent(htmlContent, section);
                        }
                    }
                }
                
                // Alternative approach using spine
                const spine = await this.book.loaded.spine;
                const spineItem = spine.get(chapter.href) || spine.spineItems[chapterIndex];
                
                if (spineItem) {
                    console.log('Loading from spine item:', spineItem.href);
                    const content = await this.book.load(spineItem.url);
                    
                    if (content) {
                        // Parse the content as text/html
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(content, 'text/html');
                        const body = doc.querySelector('body') || doc.documentElement;
                        
                        if (body) {
                            const htmlContent = body.innerHTML;
                            console.log('Successfully extracted spine content, length:', htmlContent.length);
                            
                            // Try alternative image loading approach for spine content
                            return await this.processHtmlContentWithDirectLoad(htmlContent, spineItem);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error rendering real EPUB chapter:', error);
        }
        
        console.log('Falling back to mock content for chapter:', chapterIndex);
        // Before falling back to mock, try one more approach for images
        const mockContent = this.mockRenderChapter(chapter, chapterIndex);
        
        // Process mock content for any test images that might be there
        return await this.processHtmlContent(mockContent, null);
    }

    async processHtmlContent(htmlContent, section) {
        try {
            // Create a temporary DOM to process images
            const parser = new DOMParser();
            const doc = parser.parseFromString(`<div>${htmlContent}</div>`, 'text/html');
            const container = doc.querySelector('div');
            
            // Process all images in the content
            const images = container.querySelectorAll('img');
            if (images.length > 0) {
                console.log(`Processing ${images.length} images in chapter`);
            }
            
            for (const img of images) {
                await this.processImage(img, section);
            }
            
            // Clean up the HTML content but preserve images
            let processedContent = container.innerHTML;
            processedContent = processedContent
                .replace(/<script[^>]*>.*?<\/script>/gi, '') // Remove scripts
                .replace(/<head[^>]*>.*?<\/head>/gi, '')     // Remove head elements
                .trim();
            
            return processedContent;
        } catch (error) {
            console.error('Error processing HTML content:', error);
            return this.cleanHtmlContentBasic(htmlContent);
        }
    }

    async processImage(imgElement, section) {
        try {
            const src = imgElement.getAttribute('src');
            if (!src) return;
            
            // Handle different image path formats
            if (!src.startsWith('http') && !src.startsWith('data:')) {
                try {
                    const imageUrl = await this.loadImageFromEpub(src, section);
                    if (imageUrl) {
                        imgElement.setAttribute('src', imageUrl);
                        imgElement.setAttribute('style', 'max-width: 100%; height: auto; display: block; margin: 10px auto;');
                        console.log('✅ Image loaded:', src);
                    }
                } catch (imgError) {
                    console.warn('Failed to load image:', src);
                }
            }
        } catch (error) {
            console.error('Error processing image:', error);
        }
    }

    async loadImageFromEpub(imagePath, section) {
        try {
            if (!this.book) return null;
            
            // Debug the manifest once per book load
            await this.debugManifestImages();
            
            // First try to find the exact image in the manifest
            const manifestPath = await this.findImageInManifest(imagePath);
            if (manifestPath) {
                try {
                    const imageData = await this.book.load(manifestPath);
                    if (imageData && imageData.byteLength > 0) {
                        const mimeType = this.getImageMimeType(imagePath);
                        const blob = new Blob([imageData], { type: mimeType });
                        const blobUrl = URL.createObjectURL(blob);
                        this.imageBlobUrls.add(blobUrl);
                        return blobUrl;
                    }
                } catch (manifestError) {
                    // Continue to fallback methods
                }
            }
            
            // Fallback to path resolution strategies
            const pathsToTry = this.resolveImagePaths(imagePath, section);
            
            for (const fullImagePath of pathsToTry) {
                try {
                    // Clean up the path
                    let cleanPath = fullImagePath.replace(/^\/+/, '').replace(/\/+/g, '/');
                    
                    let imageData = null;
                    
                    // Try standard loading first
                    try {
                        imageData = await this.book.load(cleanPath);
                    } catch (loadError) {
                        // Try URL resolution as fallback
                        try {
                            const resolvedUrl = this.book.resolve(cleanPath);
                            imageData = await this.book.load(resolvedUrl);
                        } catch (resolveError) {
                            // Try section-relative loading if available
                            if (section && section.load) {
                                const sectionUrl = section.resolve ? section.resolve(cleanPath) : cleanPath;
                                imageData = await section.load(sectionUrl);
                            } else {
                                throw loadError;
                            }
                        }
                    }
                    
                    if (imageData && imageData.byteLength > 0) {
                        // Handle SVG images specially
                        const mimeType = this.getImageMimeType(imagePath);
                        let blobUrl;
                        
                        if (mimeType === 'image/svg+xml') {
                            // For SVG, create a data URL to avoid CORS issues
                            const svgText = new TextDecoder().decode(imageData);
                            blobUrl = 'data:image/svg+xml;base64,' + btoa(svgText);
                        } else {
                            // Convert to blob URL for other image types
                            const blob = new Blob([imageData], { type: mimeType });
                            blobUrl = URL.createObjectURL(blob);
                            
                            // Track for cleanup (only blob URLs need cleanup)
                            this.imageBlobUrls.add(blobUrl);
                        }
                        
                        console.log('Successfully loaded image:', fullImagePath);
                        return blobUrl;
                    }
                } catch (pathError) {
                    console.warn('Failed to load image with path:', fullImagePath, pathError.message);
                }
            }
        } catch (error) {
            console.error('Failed to load image from EPUB:', imagePath, error);
        }
        
        return null;
    }

    resolveImagePaths(imagePath, section) {
        const paths = [];
        
        // Try original path first
        paths.push(imagePath);
        
        // If section has a base path, resolve relative to it
        if (section && section.href) {
            const sectionDir = section.href.substring(0, section.href.lastIndexOf('/') + 1);
            
            // Relative path resolution
            if (!imagePath.startsWith('../') && !imagePath.startsWith('/') && !imagePath.startsWith('http')) {
                paths.push(sectionDir + imagePath);
            }
            
            // Try removing leading directory separators
            if (imagePath.startsWith('../')) {
                const cleanPath = imagePath.replace(/^\.\.\/+/, '');
                paths.push(cleanPath);
                paths.push(sectionDir + cleanPath);
            }
        }
        
        // Try common EPUB image directories - be more specific based on the original path
        const imageBasename = imagePath.split('/').pop();
        const imageDir = imagePath.includes('/') ? imagePath.substring(0, imagePath.lastIndexOf('/') + 1) : '';
        
        // If original path had 'images' directory, try variations
        if (imageDir.toLowerCase().includes('image')) {
            const commonDirs = [
                'images/', 'Images/', 'IMAGE/', 'img/', 
                'OEBPS/images/', 'OEBPS/Images/', 'OEBPS/IMAGE/',
                'Text/images/', 'Text/Images/', 'text/images/',
                'content/images/', 'content/Images/'
            ];
            
            for (const dir of commonDirs) {
                paths.push(dir + imageBasename);
            }
        } else {
            // Try all common patterns
            const commonDirs = [
                'images/', 'Images/', 'IMAGE/', 'img/', 'graphics/', 'Graphics/', 'media/',
                'OEBPS/images/', 'OEBPS/Images/', 'OEBPS/IMAGE/', 'OEBPS/img/',
                'Text/images/', 'Text/Images/', 'text/images/',
                'content/images/', 'content/Images/',
                // Also try the original directory structure
                imageDir
            ];
            
            for (const dir of commonDirs) {
                if (dir) paths.push(dir + imageBasename);
            }
        }
        
        // Remove duplicates
        return [...new Set(paths)];
    }

    async debugManifestImages() {
        try {
            // Only run this debug once per book load
            if (this._manifestDebugDone) return;
            this._manifestDebugDone = true;
            
            if (!this.book || !this.book.loaded) return;
            
            const manifest = await this.book.loaded.manifest;
            let imageCount = 0;
            
            for (const [id, item] of Object.entries(manifest)) {
                if (item.type && item.type.startsWith('image/')) {
                    imageCount++;
                }
            }
            
            if (imageCount > 0) {
                console.log(`Found ${imageCount} images in EPUB manifest`);
            }
        } catch (error) {
            // Silently continue if manifest debug fails
        }
    }

    async findImageInManifest(imagePath) {
        try {
            const manifest = await this.book.loaded.manifest;
            const imageBasename = imagePath.split('/').pop().toLowerCase();
            
            // Look for exact filename matches in manifest
            for (const [id, item] of Object.entries(manifest)) {
                if (item.type && item.type.startsWith('image/')) {
                    const manifestBasename = item.href.split('/').pop().toLowerCase();
                    if (manifestBasename === imageBasename) {
                        return item.href;
                    }
                }
            }
            
            // Try partial matches
            for (const [id, item] of Object.entries(manifest)) {
                if (item.type && item.type.startsWith('image/')) {
                    if (item.href.toLowerCase().includes(imageBasename)) {
                        return item.href;
                    }
                }
            }
            
            return null;
        } catch (error) {
            return null;
        }
    }

    getImageMimeType(imagePath) {
        const extension = imagePath.toLowerCase().split('.').pop();
        const mimeTypes = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',  
            'png': 'image/png',
            'gif': 'image/gif',
            'svg': 'image/svg+xml',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        };
        return mimeTypes[extension] || 'image/jpeg';
    }

    async processHtmlContentWithDirectLoad(htmlContent, spineItem) {
        console.log('🖼️ Using direct load approach for images');
        
        try {
            // First try the normal approach
            const normalResult = await this.processHtmlContent(htmlContent, spineItem);
            
            // If no images were found or processed, try a more direct approach
            if (!normalResult.includes('blob:') && !normalResult.includes('data:image')) {
                console.log('🖼️ No processed images found, trying direct manifest approach');
                return await this.processImagesFromManifest(htmlContent);
            }
            
            return normalResult;
        } catch (error) {
            console.error('❌ Error in direct load approach:', error);
            return this.cleanHtmlContentBasic(htmlContent);
        }
    }

    async processImagesFromManifest(htmlContent) {
        try {
            if (!this.book) return htmlContent;
            
            console.log('🖼️ Processing images using manifest approach');
            
            // Get the manifest to find all images
            const manifest = await this.book.loaded.manifest;
            const imageItems = {};
            
            // Build a map of image resources
            for (const [id, item] of Object.entries(manifest)) {
                if (item.type && item.type.startsWith('image/')) {
                    const filename = item.href.split('/').pop();
                    imageItems[filename] = item.href;
                    console.log('📋 Found manifest image:', filename, '->', item.href);
                }
            }
            
            // Replace image sources with loaded data
            let processedContent = htmlContent;
            const imgRegex = /<img[^>]*src\s*=\s*["']([^"']+)["'][^>]*>/gi;
            let match;
            
            while ((match = imgRegex.exec(htmlContent)) !== null) {
                const fullMatch = match[0];
                const srcValue = match[1];
                const filename = srcValue.split('/').pop();
                
                console.log('🖼️ Processing image from regex:', srcValue, 'filename:', filename);
                
                if (imageItems[filename]) {
                    try {
                        const imageData = await this.book.load(imageItems[filename]);
                        if (imageData && imageData.byteLength > 0) {
                            const mimeType = this.getImageMimeType(filename);
                            const blob = new Blob([imageData], { type: mimeType });
                            const blobUrl = URL.createObjectURL(blob);
                            this.imageBlobUrls.add(blobUrl);
                            
                            const newImg = fullMatch.replace(srcValue, blobUrl);
                            processedContent = processedContent.replace(fullMatch, newImg);
                            console.log('✅ Replaced image:', filename);
                        }
                    } catch (imgError) {
                        console.warn('❌ Failed to load image from manifest:', filename, imgError);
                    }
                }
            }
            
            return processedContent;
        } catch (error) {
            console.error('❌ Error processing images from manifest:', error);
            return htmlContent;
        }
    }

    cleanHtmlContentBasic(htmlContent) {
        // Basic cleaning as fallback
        return htmlContent
            .replace(/<script[^>]*>.*?<\/script>/gi, '') // Remove scripts
            .replace(/<style[^>]*>.*?<\/style>/gi, '')   // Remove inline styles
            .replace(/<head[^>]*>.*?<\/head>/gi, '')     // Remove head elements
            .trim();
    }

    mockRenderChapter(chapter, chapterIndex) {
        // Generate mock content for demonstration
        const mockContent = `
            <h1>${chapter.title}</h1>
            <p>This is a mock rendering of ${chapter.title}. In a real implementation, this would contain the actual EPUB chapter content.</p>
            
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            
            <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            
            <h2>Section ${chapterIndex + 1}.1</h2>
            <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
            
            <p>Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.</p>
            
            <h2>Section ${chapterIndex + 1}.2</h2>
            <p>Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.</p>
            
            <p>Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?</p>
        `;
        
        return mockContent;
    }

    async getChapterText(chapterIndex) {
        if (chapterIndex < 0 || chapterIndex >= this.chapters.length) {
            throw new Error('Invalid chapter index');
        }

        // Check cache first
        if (this.textContent.has(chapterIndex)) {
            console.log('Using cached text for chapter:', chapterIndex);
            return this.textContent.get(chapterIndex);
        }

        const chapter = this.chapters[chapterIndex];
        console.log('Loading text for chapter:', chapterIndex, chapter.title);
        
        try {
            if (this.book && chapter.href) {
                // Get the section/spine item
                const spine = await this.book.loaded.spine;
                const spineItem = spine.get(chapter.href) || spine.spineItems[chapterIndex];
                
                if (spineItem) {
                    try {
                        // Load the chapter content
                        const content = await this.book.load(spineItem.url || spineItem.href);
                        
                        // Parse the content as XML/HTML
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(content, 'application/xhtml+xml');
                        
                        // Extract text content
                        let textContent = '';
                        if (doc.documentElement) {
                            const body = doc.querySelector('body') || doc.documentElement;
                            textContent = body.textContent || body.innerText || '';
                        }
                    } catch (loadError) {
                        console.warn('Alternative load method failed:', loadError);
                        // Try direct section loading
                        const section = this.book.section(chapter.href);
                        if (section) {
                            await section.load(this.book.load.bind(this.book));
                            const doc = section.document;
                            if (doc && doc.documentElement) {
                                const body = doc.querySelector('body') || doc.documentElement;
                                textContent = body.textContent || body.innerText || '';
                            }
                        }
                    }
                    
                    // Clean up the text
                    const cleanedText = textContent
                        .replace(/\s+/g, ' ')           // Normalize whitespace
                        .replace(/\n\s*\n/g, '\n\n')    // Normalize line breaks
                        .trim();
                    
                    // Add title and cache
                    const fullText = `${chapter.title}\n\n${cleanedText}`;
                    this.textContent.set(chapterIndex, fullText);
                    return fullText;
                }
            }
        } catch (error) {
            console.error('Error extracting real EPUB text:', error);
        }
        
        // Fallback to mock text
        const mockText = `${chapter.title}

This is the text content of ${chapter.title} extracted from the EPUB file. In a real implementation, this would contain the actual chapter text for summary generation.

The chapter contains detailed information about the topic, with multiple sections and subsections. It includes examples, explanations, and practical guidance for readers.

This represents the actual textual content that would be used to generate meaningful summaries using AI.`;

        this.textContent.set(chapterIndex, mockText);
        return mockText;
    }

    async search(query) {
        // Implementation for searching within the EPUB
        // This would search through all chapters and return matches
        const results = [];
        
        for (let i = 0; i < this.chapters.length; i++) {
            const chapterText = await this.getChapterText(i);
            if (chapterText.toLowerCase().includes(query.toLowerCase())) {
                results.push({
                    chapter: i,
                    title: this.chapters[i].title,
                    excerpt: this.extractExcerpt(chapterText, query)
                });
            }
        }
        
        return results;
    }

    extractExcerpt(text, query, contextLength = 100) {
        const index = text.toLowerCase().indexOf(query.toLowerCase());
        if (index === -1) return '';
        
        const start = Math.max(0, index - contextLength);
        const end = Math.min(text.length, index + query.length + contextLength);
        
        let excerpt = text.substring(start, end);
        if (start > 0) excerpt = '...' + excerpt;
        if (end < text.length) excerpt = excerpt + '...';
        
        return excerpt;
    }

    getCurrentLocation() {
        return this.currentLocation;
    }

    async goToLocation(location) {
        // Implementation to navigate to a specific location in the EPUB
        this.currentLocation = location;
    }

    destroy() {
        // Clean up blob URLs to prevent memory leaks
        this.imageBlobUrls.forEach(url => {
            URL.revokeObjectURL(url);
        });
        this.imageBlobUrls.clear();
        
        if (this.book) {
            this.book.destroy();
        }
        this.book = null;
        this.rendition = null;
        this.chapters = [];
        this.currentLocation = null;
        this.textContent.clear();
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.EpubHandler = EpubHandler;
}