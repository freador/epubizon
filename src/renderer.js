// Main renderer process - handles UI interactions and coordinates between modules
class EpubizonApp {
    constructor() {
        this.currentBook = null;
        this.currentChapter = 0;
        this.currentPage = 0;
        this.totalPages = 0;
        this.chapters = [];
        this.settings = {};
        
        this.init();
    }

    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        this.initializeKeyboardHandler();
    }

    async loadSettings() {
        try {
            this.settings = await window.electronAPI.getSettings();
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.settings = {};
        }
    }

    setupEventListeners() {
        // File operations
        document.getElementById('openFileBtn').addEventListener('click', () => this.openFile());
        document.getElementById('openFileWelcome').addEventListener('click', () => this.openFile());
        
        // Navigation
        document.getElementById('prevPageBtn').addEventListener('click', () => this.previousPage());
        document.getElementById('nextPageBtn').addEventListener('click', () => this.nextPage());
        
        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
        document.getElementById('closeSettingsBtn').addEventListener('click', () => this.closeSettings());
        document.getElementById('saveSettingsBtn').addEventListener('click', () => this.saveSettings());
        document.getElementById('cancelSettingsBtn').addEventListener('click', () => this.closeSettings());
        
        // Summary
        document.getElementById('summaryBtn').addEventListener('click', () => this.generateSummary());
        document.getElementById('closeSummaryBtn').addEventListener('click', () => this.closeSummary());
        
        // Chapter selection
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('chapter-item')) {
                const chapterIndex = parseInt(e.target.dataset.index);
                this.goToChapter(chapterIndex);
            }
        });

        // Modal backdrop clicks
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettings();
            }
        });
    }

    initializeKeyboardHandler() {
        // Initialize keyboard navigation
        if (window.KeyboardHandler) {
            this.keyboardHandler = new KeyboardHandler(this);
        }
    }

    async openFile() {
        try {
            this.showLoading(true);
            
            const fileData = await window.electronAPI.selectFile();
            if (!fileData) {
                this.showLoading(false);
                return;
            }

            this.currentBook = fileData;
            
            // Handle different file types
            if (fileData.extension === '.epub') {
                await this.loadEpub(fileData);
            } else if (fileData.extension === '.pdf') {
                await this.loadPdf(fileData);
            } else {
                throw new Error('Unsupported file format');
            }

            this.updateUI();
            this.showLoading(false);
            
        } catch (error) {
            console.error('Error opening file:', error);
            this.showError('Failed to open file: ' + error.message);
            this.showLoading(false);
        }
    }

    async loadEpub(fileData) {
        if (window.EpubHandler) {
            // Clean up previous handler if exists
            if (this.epubHandler) {
                this.epubHandler.destroy();
            }
            
            this.epubHandler = new EpubHandler();
            
            // Show processing message for large files
            const loadingElement = document.querySelector('#loadingOverlay .loading-content p');
            if (loadingElement) {
                loadingElement.textContent = 'Processing EPUB file...';
            }
            
            const bookData = await this.epubHandler.loadBook(fileData.buffer);
            
            this.chapters = bookData.chapters;
            this.totalPages = bookData.totalPages;
            this.currentChapter = 0;
            this.currentPage = 1;
            this.isLargeFile = bookData.isLargeFile;
            
            // Update loading message based on file size
            if (this.isLargeFile) {
                if (loadingElement) {
                    loadingElement.textContent = 'Loading large file, please wait...';
                }
            }
            
            await this.renderCurrentChapter();
        } else {
            throw new Error('EPUB handler not available');
        }
    }

    async loadPdf(fileData) {
        if (window.PdfHandler) {
            this.pdfHandler = new PdfHandler();
            const bookData = await this.pdfHandler.loadBook(fileData.buffer);
            
            this.chapters = bookData.chapters || [{ title: 'PDF Document', pageStart: 1, pageEnd: bookData.totalPages }];
            this.totalPages = bookData.totalPages;
            this.currentChapter = 0;
            this.currentPage = 1;
            
            await this.renderCurrentPage();
        } else {
            throw new Error('PDF handler not available');
        }
    }

    async renderCurrentChapter() {
        if (this.epubHandler && this.chapters[this.currentChapter]) {
            const content = await this.epubHandler.renderChapter(this.currentChapter);
            const container = document.getElementById('documentContainer');
            container.innerHTML = `<div class="epub-content">${content}</div>`;
        }
    }

    async renderCurrentPage() {
        if (this.pdfHandler) {
            const content = await this.pdfHandler.renderPage(this.currentPage);
            const container = document.getElementById('documentContainer');
            container.innerHTML = content;
        }
    }

    updateUI() {
        // Update book info
        document.getElementById('bookTitle').textContent = this.currentBook.name;
        document.getElementById('bookMeta').textContent = `${this.chapters.length} chapters • ${this.totalPages} pages`;
        
        // Update chapters list
        this.updateChaptersList();
        
        // Update navigation
        this.updateNavigation();
        
        // Hide welcome screen
        const welcomeScreen = document.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
        
        // Enable summary button
        document.getElementById('summaryBtn').disabled = false;
    }

    updateChaptersList() {
        const chaptersList = document.getElementById('chaptersList');
        chaptersList.innerHTML = '';
        
        // For large files, implement virtual scrolling or pagination
        if (this.isLargeFile && this.chapters.length > 100) {
            // Show a limited number of chapters around the current one
            const maxVisible = 50;
            const start = Math.max(0, this.currentChapter - 25);
            const end = Math.min(this.chapters.length, start + maxVisible);
            
            if (start > 0) {
                const jumpStart = document.createElement('li');
                jumpStart.className = 'chapter-jump';
                jumpStart.textContent = `... (${start} chapters before)`;
                jumpStart.onclick = () => this.showChapterRange(0, 50);
                chaptersList.appendChild(jumpStart);
            }
            
            for (let index = start; index < end; index++) {
                const chapter = this.chapters[index];
                const li = document.createElement('li');
                li.className = `chapter-item ${index === this.currentChapter ? 'active' : ''}`;
                li.dataset.index = index;
                li.textContent = chapter.title || `Chapter ${index + 1}`;
                chaptersList.appendChild(li);
            }
            
            if (end < this.chapters.length) {
                const jumpEnd = document.createElement('li');
                jumpEnd.className = 'chapter-jump';
                jumpEnd.textContent = `... (${this.chapters.length - end} chapters after)`;
                jumpEnd.onclick = () => this.showChapterRange(end, Math.min(this.chapters.length, end + 50));
                chaptersList.appendChild(jumpEnd);
            }
            
            // Add chapter counter
            const counter = document.createElement('li');
            counter.className = 'chapter-counter';
            counter.textContent = `Showing ${end - start} of ${this.chapters.length} chapters`;
            chaptersList.appendChild(counter);
            
        } else {
            // Normal display for smaller files
            this.chapters.forEach((chapter, index) => {
                const li = document.createElement('li');
                li.className = `chapter-item ${index === this.currentChapter ? 'active' : ''}`;
                li.dataset.index = index;
                li.textContent = chapter.title || `Chapter ${index + 1}`;
                chaptersList.appendChild(li);
            });
        }
    }

    showChapterRange(start, end) {
        // Helper method for virtual scrolling in large files
        const chaptersList = document.getElementById('chaptersList');
        chaptersList.innerHTML = '';
        
        if (start > 0) {
            const jumpStart = document.createElement('li');
            jumpStart.className = 'chapter-jump';
            jumpStart.textContent = `... (${start} chapters before)`;
            jumpStart.onclick = () => this.showChapterRange(Math.max(0, start - 50), start);
            chaptersList.appendChild(jumpStart);
        }
        
        for (let index = start; index < end && index < this.chapters.length; index++) {
            const chapter = this.chapters[index];
            const li = document.createElement('li');
            li.className = `chapter-item ${index === this.currentChapter ? 'active' : ''}`;
            li.dataset.index = index;
            li.textContent = chapter.title || `Chapter ${index + 1}`;
            chaptersList.appendChild(li);
        }
        
        if (end < this.chapters.length) {
            const jumpEnd = document.createElement('li');
            jumpEnd.className = 'chapter-jump';
            jumpEnd.textContent = `... (${this.chapters.length - end} chapters after)`;
            jumpEnd.onclick = () => this.showChapterRange(end, Math.min(this.chapters.length, end + 50));
            chaptersList.appendChild(jumpEnd);
        }
    }

    updateNavigation() {
        // Update page info
        document.getElementById('currentPage').textContent = this.currentPage;
        document.getElementById('totalPages').textContent = this.totalPages;
        
        // Update button states
        document.getElementById('prevPageBtn').disabled = this.currentPage <= 1;
        document.getElementById('nextPageBtn').disabled = this.currentPage >= this.totalPages;
    }

    // Navigation methods
    async previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            await this.renderCurrentContent();
            this.updateNavigation();
        }
    }

    async nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            await this.renderCurrentContent();
            this.updateNavigation();
        }
    }

    async previousChapter() {
        if (this.currentChapter > 0) {
            this.currentChapter--;
            await this.goToChapter(this.currentChapter);
        }
    }

    async nextChapter() {
        if (this.currentChapter < this.chapters.length - 1) {
            this.currentChapter++;
            await this.goToChapter(this.currentChapter);
        }
    }

    async goToChapter(chapterIndex) {
        if (chapterIndex >= 0 && chapterIndex < this.chapters.length) {
            this.currentChapter = chapterIndex;
            
            // Update current page based on chapter
            if (this.chapters[chapterIndex].pageStart) {
                this.currentPage = this.chapters[chapterIndex].pageStart;
            }
            
            await this.renderCurrentContent();
            this.updateChaptersList();
            this.updateNavigation();
        }
    }

    async renderCurrentContent() {
        if (this.currentBook.extension === '.epub') {
            await this.renderCurrentChapter();
        } else if (this.currentBook.extension === '.pdf') {
            await this.renderCurrentPage();
        }
    }

    // Settings management
    openSettings() {
        document.getElementById('settingsModal').classList.remove('hidden');
        document.getElementById('openaiKey').value = this.settings.openaiApiKey || '';
    }

    closeSettings() {
        document.getElementById('settingsModal').classList.add('hidden');
    }

    async saveSettings() {
        const apiKey = document.getElementById('openaiKey').value.trim();
        
        this.settings.openaiApiKey = apiKey;
        
        try {
            await window.electronAPI.saveSettings(this.settings);
            this.closeSettings();
            this.showMessage('Settings saved successfully!');
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError('Failed to save settings');
        }
    }

    // Summary generation
    async generateSummary() {
        if (!this.settings.openaiApiKey) {
            this.showMessage('Please set your OpenAI API key in Settings first.');
            this.openSettings();
            return;
        }

        if (!this.currentBook || this.chapters.length === 0) {
            this.showError('No book loaded or no chapters available');
            return;
        }

        try {
            // Show summary panel and loading state
            const summaryPanel = document.getElementById('summaryPanel');
            const summaryLoading = document.getElementById('summaryLoading');
            const summaryText = document.getElementById('summaryText');
            
            summaryPanel.classList.remove('hidden');
            summaryLoading.classList.remove('hidden');
            summaryText.innerHTML = '';

            // Get current chapter content for summary
            let chapterContent = '';
            const currentChapterData = this.chapters[this.currentChapter];
            
            if (this.currentBook.extension === '.epub' && this.epubHandler) {
                chapterContent = await this.epubHandler.getChapterText(this.currentChapter);
            } else if (this.currentBook.extension === '.pdf' && this.pdfHandler) {
                chapterContent = await this.pdfHandler.getPageText(this.currentPage);
            }

            // Call OpenAI API
            const result = await window.electronAPI.generateSummary({
                text: chapterContent,
                apiKey: this.settings.openaiApiKey
            });

            summaryLoading.classList.add('hidden');

            if (result.success) {
                summaryText.innerHTML = `<h4>${currentChapterData.title || 'Chapter ' + (this.currentChapter + 1)}</h4><p>${result.summary}</p>`;
            } else {
                summaryText.innerHTML = `<div class="error">Failed to generate summary: ${result.error}</div>`;
            }

        } catch (error) {
            console.error('Error generating summary:', error);
            document.getElementById('summaryLoading').classList.add('hidden');
            document.getElementById('summaryText').innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    }

    closeSummary() {
        document.getElementById('summaryPanel').classList.add('hidden');
    }

    // Utility methods
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    showMessage(message) {
        // Simple alert for now - could be improved with a toast notification
        alert(message);
    }

    showError(message) {
        console.error(message);
        alert('Error: ' + message);
    }
}

// Initialize the app when DOM is ready
window.domAPI.ready(() => {
    window.app = new EpubizonApp();
});