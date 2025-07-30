// Keyboard navigation handler
class KeyboardHandler {
    constructor(app) {
        this.app = app;
        this.setupKeyboardListeners();
    }

    setupKeyboardListeners() {
        document.addEventListener('keydown', (event) => {
            // Prevent default behavior for our handled keys
            if (this.shouldHandleKey(event)) {
                event.preventDefault();
                this.handleKeyPress(event);
            }
        });

        // Also handle keyup for better responsiveness
        document.addEventListener('keyup', (event) => {
            if (this.shouldHandleKey(event)) {
                event.preventDefault();
            }
        });
    }

    shouldHandleKey(event) {
        // Don't handle keys when user is typing in input fields
        const activeElement = document.activeElement;
        if (activeElement && (
            activeElement.tagName === 'INPUT' || 
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.contentEditable === 'true'
        )) {
            return false;
        }

        // Don't handle keys when modals are open (except for Escape)
        const modalOpen = !document.getElementById('settingsModal').classList.contains('hidden');
        if (modalOpen && event.key !== 'Escape') {
            return false;
        }

        // List of keys we want to handle
        const handledKeys = [
            'ArrowLeft', 
            'ArrowRight', 
            'ArrowUp', 
            'ArrowDown',
            'KeyS',
            'Escape',
            'Enter',
            'Space'
        ];

        return handledKeys.includes(event.code) || handledKeys.includes(event.key);
    }

    async handleKeyPress(event) {
        try {
            switch (event.code || event.key) {
                case 'ArrowLeft':
                    await this.handleLeftArrow();
                    break;
                
                case 'ArrowRight':
                    await this.handleRightArrow();
                    break;
                
                case 'ArrowUp':
                    await this.handleUpArrow();
                    break;
                
                case 'ArrowDown':
                    await this.handleDownArrow();
                    break;
                
                case 'KeyS':
                    if (!event.ctrlKey && !event.metaKey) {
                        await this.handleSummarize();
                    }
                    break;
                
                case 'Escape':
                    this.handleEscape();
                    break;
                
                case 'Enter':
                    if (event.ctrlKey || event.metaKey) {
                        this.handleOpenFile();
                    }
                    break;
                
                case 'Space':
                    if (!this.isModalOpen()) {
                        await this.handleSpace(event);
                    }
                    break;
            }
        } catch (error) {
            console.error('Error handling key press:', error);
        }
    }

    // Arrow key handlers
    async handleLeftArrow() {
        // Left arrow = previous page
        if (this.app.currentBook) {
            await this.app.previousPage();
            this.showNavigationFeedback('Previous Page');
        }
    }

    async handleRightArrow() {
        // Right arrow = next page
        if (this.app.currentBook) {
            await this.app.nextPage();
            this.showNavigationFeedback('Next Page');
        }
    }

    async handleUpArrow() {
        // Up arrow = next chapter
        if (this.app.currentBook) {
            await this.app.nextChapter();
            this.showNavigationFeedback('Next Chapter');
        }
    }

    async handleDownArrow() {
        // Down arrow = previous chapter
        if (this.app.currentBook) {
            await this.app.previousChapter();
            this.showNavigationFeedback('Previous Chapter');
        }
    }

    // Other key handlers
    async handleSummarize() {
        if (this.app.currentBook && !this.isModalOpen()) {
            await this.app.generateSummary();
        }
    }

    handleEscape() {
        // Close any open modals or panels
        if (!document.getElementById('settingsModal').classList.contains('hidden')) {
            this.app.closeSettings();
        } else if (!document.getElementById('summaryPanel').classList.contains('hidden')) {
            this.app.closeSummary();
        }
    }

    handleOpenFile() {
        // Ctrl/Cmd + Enter to open file
        if (!this.isModalOpen()) {
            this.app.openFile();
        }
    }

    async handleSpace(event) {
        // Space = next page, Shift+Space = previous page
        if (this.app.currentBook) {
            if (event.shiftKey) {
                await this.app.previousPage();
                this.showNavigationFeedback('Previous Page');
            } else {
                await this.app.nextPage();
                this.showNavigationFeedback('Next Page');
            }
        }
    }

    // Utility methods
    isModalOpen() {
        return !document.getElementById('settingsModal').classList.contains('hidden') ||
               !document.getElementById('summaryPanel').classList.contains('hidden');
    }

    showNavigationFeedback(action) {
        // Show brief visual feedback for navigation actions
        this.createTemporaryNotification(action);
    }

    createTemporaryNotification(message) {
        // Remove any existing notification
        const existing = document.querySelector('.keyboard-notification');
        if (existing) {
            existing.remove();
        }

        // Create new notification
        const notification = document.createElement('div');
        notification.className = 'keyboard-notification';
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: 'rgba(52, 152, 219, 0.9)',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '4px',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '9999',
            opacity: '0',
            transition: 'opacity 0.2s ease',
            pointerEvents: 'none'
        });

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);

        // Remove after delay
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 200);
        }, 1500);
    }

    // Method to disable keyboard handling (useful when editing text)
    disable() {
        this.disabled = true;
    }

    // Method to re-enable keyboard handling
    enable() {
        this.disabled = false;
    }

    // Check if handler is disabled
    isDisabled() {
        return this.disabled === true;
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.KeyboardHandler = KeyboardHandler;
}