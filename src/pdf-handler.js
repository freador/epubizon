// PDF file handler using PDF.js library
class PdfHandler {
    constructor() {
        this.pdfDocument = null;
        this.totalPages = 0;
        this.pages = [];
        this.textContent = new Map(); // Cache for extracted text
        this.pdfjsLib = null;
    }

    async loadBook(arrayBuffer) {
        try {
            // Load PDF.js library
            this.pdfjsLib = await this.loadPdfJs();
            
            // Create PDF document
            this.pdfDocument = await this.pdfjsLib.getDocument({
                data: arrayBuffer,
                cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/cmaps/',
                cMapPacked: true,
            }).promise;
            
            this.totalPages = this.pdfDocument.numPages;
            
            // Create page info array
            this.pages = Array.from({length: this.totalPages}, (_, i) => ({
                pageNumber: i + 1,
                width: 612,  // Will be updated when pages are rendered
                height: 792
            }));

            // Create chapters based on page ranges (simple implementation)
            const chapters = this.createChaptersFromPages();

            // Get document metadata
            const metadata = await this.getDocumentInfo();

            return {
                totalPages: this.totalPages,
                chapters: chapters,
                metadata: metadata.info || {}
            };
            
        } catch (error) {
            console.error('Error loading PDF:', error);
            console.warn('Falling back to mock PDF implementation');
            return await this.mockLoadPdf(arrayBuffer);
        }
    }

    async loadPdfJs() {
        try {
            // Try to load PDF.js from installed node_modules first
            if (typeof window !== 'undefined' && !window.pdfjsLib) {
                return new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = './node_modules/pdfjs-dist/build/pdf.min.js';
                    script.onload = () => {
                        if (window.pdfjsLib) {
                            // Configure worker from node_modules
                            window.pdfjsLib.GlobalWorkerOptions.workerSrc = 
                                './node_modules/pdfjs-dist/build/pdf.worker.min.js';
                            resolve(window.pdfjsLib);
                        } else {
                            reject(new Error('pdfjsLib not available after loading'));
                        }
                    };
                    script.onerror = () => {
                        console.warn('Failed to load PDF.js from node_modules, trying CDN fallback');
                        // Fallback to CDN
                        this.loadPdfJsFromCDN().then(resolve).catch(reject);
                    };
                    document.head.appendChild(script);
                });
            } else if (window.pdfjsLib) {
                return window.pdfjsLib;
            } else {
                throw new Error('pdfjsLib not available');
            }
        } catch (error) {
            throw new Error('Could not load PDF.js library');
        }
    }

    async loadPdfJsFromCDN() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.js';
            script.onload = () => {
                if (window.pdfjsLib) {
                    // Configure worker from CDN
                    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 
                        'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.worker.min.js';
                    resolve(window.pdfjsLib);
                } else {
                    reject(new Error('pdfjsLib not available after loading'));
                }
            };
            script.onerror = () => reject(new Error('Failed to load PDF.js'));
            document.head.appendChild(script);
        });
    }

    createChaptersFromPages() {
        // Simple chapter creation - could be enhanced with outline parsing
        const chaptersPerSection = Math.max(1, Math.floor(this.totalPages / 7));
        const chapters = [];
        
        for (let i = 0; i < this.totalPages; i += chaptersPerSection) {
            const startPage = i + 1;
            const endPage = Math.min(i + chaptersPerSection, this.totalPages);
            const chapterNum = Math.floor(i / chaptersPerSection) + 1;
            
            chapters.push({
                title: startPage === 1 ? 'Introduction' : 
                       endPage === this.totalPages ? 'Conclusion' :
                       `Chapter ${chapterNum}`,
                pageStart: startPage,
                pageEnd: endPage
            });
        }
        
        return chapters;
    }

    // Mock implementation for demonstration
    async mockLoadPdf(arrayBuffer) {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mock PDF data
        this.totalPages = 45;
        this.pages = Array.from({length: this.totalPages}, (_, i) => ({
            pageNumber: i + 1,
            width: 612,
            height: 792
        }));

        // Create mock chapters based on page ranges
        const chapters = [
            { title: 'Table of Contents', pageStart: 1, pageEnd: 2 },
            { title: 'Introduction', pageStart: 3, pageEnd: 8 },
            { title: 'Chapter 1: Fundamentals', pageStart: 9, pageEnd: 18 },
            { title: 'Chapter 2: Advanced Concepts', pageStart: 19, pageEnd: 28 },
            { title: 'Chapter 3: Practical Applications', pageStart: 29, pageEnd: 38 },
            { title: 'Chapter 4: Case Studies', pageStart: 39, pageEnd: 43 },
            { title: 'Conclusion', pageStart: 44, pageEnd: 45 }
        ];

        return {
            totalPages: this.totalPages,
            chapters: chapters,
            metadata: {
                title: 'Sample PDF Document',
                author: 'Demo Author',
                subject: 'Educational Content',
                creator: 'PDF Creator',
                creationDate: new Date().toISOString()
            }
        };
    }

    async renderPage(pageNumber) {
        if (pageNumber < 1 || pageNumber > this.totalPages) {
            throw new Error('Invalid page number');
        }

        try {
            if (this.pdfDocument && this.pdfjsLib) {
                const page = await this.pdfDocument.getPage(pageNumber);
                const scale = 1.5;
                const viewport = page.getViewport({ scale });

                // Create canvas
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                // Render page
                await page.render({
                    canvasContext: context,
                    viewport: viewport
                }).promise;

                // Update page dimensions
                if (this.pages[pageNumber - 1]) {
                    this.pages[pageNumber - 1].width = viewport.width;
                    this.pages[pageNumber - 1].height = viewport.height;
                }

                // Return canvas wrapped in container
                return `
                    <div class="pdf-container">
                        <div class="pdf-page" style="display: flex; justify-content: center; align-items: center; padding: 20px;">
                            ${canvas.outerHTML}
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error rendering real PDF page:', error);
        }

        // Fallback to mock rendering
        return await this.mockRenderPage(pageNumber);
    }

    async mockRenderPage(pageNumber) {
        // Create a mock PDF page representation
        const mockContent = `
            <div class="pdf-container">
                <div class="pdf-page" style="width: 612px; height: 792px; background: white; border: 1px solid #ccc; margin: 0 auto; padding: 40px; position: relative;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50; font-size: 24px; margin-bottom: 10px;">Sample PDF Document</h1>
                        <p style="color: #7f8c8d; font-size: 14px;">Page ${pageNumber} of ${this.totalPages}</p>
                    </div>
                    
                    <div style="font-size: 14px; line-height: 1.6; color: #2c3e50;">
                        <h2 style="color: #34495e; margin-bottom: 15px;">Page ${pageNumber} Content</h2>
                        
                        <p style="margin-bottom: 15px;">
                            This is a mock representation of page ${pageNumber} in the PDF document. 
                            In a real implementation, this would show the actual rendered PDF content 
                            using PDF.js canvas rendering.
                        </p>
                        
                        <p style="margin-bottom: 15px;">
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
                            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
                            veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
                            commodo consequat.
                        </p>
                        
                        <p style="margin-bottom: 15px;">
                            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum 
                            dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non 
                            proident, sunt in culpa qui officia deserunt mollit anim id est 
                            laborum.
                        </p>
                        
                        ${pageNumber > 1 ? `
                        <div style="margin-top: 30px; padding: 15px; background: #ecf0f1; border-radius: 5px;">
                            <h3 style="color: #2c3e50; margin-bottom: 10px;">Section ${Math.ceil(pageNumber / 5)}.${pageNumber % 5 || 5}</h3>
                            <p style="margin-bottom: 10px;">
                                Sed ut perspiciatis unde omnis iste natus error sit voluptatem 
                                accusantium doloremque laudantium, totam rem aperiam, eaque ipsa 
                                quae ab illo inventore veritatis.
                            </p>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div style="position: absolute; bottom: 20px; right: 20px; font-size: 12px; color: #95a5a6;">
                        Page ${pageNumber}
                    </div>
                </div>
            </div>
        `;
        
        return mockContent;
    }

    async getPageText(pageNumber) {
        if (pageNumber < 1 || pageNumber > this.totalPages) {
            throw new Error('Invalid page number');
        }

        // Check cache first
        if (this.textContent.has(pageNumber)) {
            return this.textContent.get(pageNumber);
        }

        try {
            if (this.pdfDocument && this.pdfjsLib) {
                const page = await this.pdfDocument.getPage(pageNumber);
                const textContent = await page.getTextContent();
                
                // Extract text from content items
                const textItems = textContent.items
                    .filter(item => item.str && item.str.trim())
                    .map(item => item.str);
                
                const rawText = textItems.join(' ');
                
                // Clean up the text
                const cleanedText = rawText
                    .replace(/\s+/g, ' ')           // Normalize whitespace
                    .replace(/(.)\1{3,}/g, '$1')    // Remove excessive repeated characters
                    .trim();
                
                this.textContent.set(pageNumber, cleanedText);
                return cleanedText;
            }
        } catch (error) {
            console.error('Error extracting real PDF text:', error);
        }

        // Fallback to mock text extraction
        const text = await this.mockExtractPageText(pageNumber);
        this.textContent.set(pageNumber, text);
        return text;
    }

    async mockExtractPageText(pageNumber) {
        return `Page ${pageNumber} Content

This is the extracted text content from page ${pageNumber} of the PDF document. In a real implementation, this would contain the actual text extracted from the PDF using PDF.js text extraction capabilities.

This mock text represents what would typically be found on a PDF page, including headings, paragraphs, and structured content that could be used for generating summaries or performing searches.

The content includes detailed information about the topic covered on this page, with explanations, examples, and references that would be valuable for AI-powered summary generation.

Section ${Math.ceil(pageNumber / 5)}.${pageNumber % 5 || 5}: Advanced Topics

This section covers advanced concepts and practical applications related to the main topic. It provides in-depth analysis and real-world examples that help readers understand complex concepts.

The information presented here builds upon previous chapters and provides foundational knowledge for subsequent sections of the document.`;
    }

    async search(query) {
        const results = [];
        
        for (let pageNum = 1; pageNum <= this.totalPages; pageNum++) {
            const pageText = await this.getPageText(pageNum);
            if (pageText.toLowerCase().includes(query.toLowerCase())) {
                results.push({
                    page: pageNum,
                    excerpt: this.extractExcerpt(pageText, query)
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

    async getDocumentInfo() {
        try {
            if (this.pdfDocument) {
                const metadata = await this.pdfDocument.getMetadata();
                return {
                    info: metadata.info || {
                        Title: 'PDF Document',
                        Author: 'Unknown',
                        Subject: '',
                        Creator: '',
                        CreationDate: new Date().toISOString()
                    },
                    metadata: metadata.metadata
                };
            }
        } catch (error) {
            console.error('Error getting PDF metadata:', error);
        }
        
        // Fallback
        return {
            info: {
                Title: 'PDF Document',
                Author: 'Unknown',
                Subject: '',
                Creator: '',
                CreationDate: new Date().toISOString()
            },
            metadata: null
        };
    }

    async getOutline() {
        try {
            if (this.pdfDocument) {
                const outline = await this.pdfDocument.getOutline();
                return outline;
            }
        } catch (error) {
            console.error('Error getting PDF outline:', error);
        }
        
        return null; // No outline available
    }

    getTotalPages() {
        return this.totalPages;
    }

    destroy() {
        if (this.pdfDocument) {
            this.pdfDocument.destroy();
        }
        this.pdfDocument = null;
        this.totalPages = 0;
        this.pages = [];
        this.textContent.clear();
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.PdfHandler = PdfHandler;
}