# Epubizon - EPUB & PDF Reader

A modern desktop application for reading EPUB and PDF files with AI-powered chapter summaries.

## Features

- 📚 **EPUB & PDF Support** - Read both EPUB and PDF files
- 🖼️ **Image Display** - Proper image loading and display for illustrated books
- 🤖 **AI Summaries** - Generate chapter summaries using OpenAI API
- ⌨️ **Keyboard Navigation** - Navigate with arrow keys and shortcuts
- 📱 **Large File Optimization** - Efficient handling of books with 1000+ pages
- 🎨 **Modern Interface** - Clean, responsive design

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd epubizon
```

2. Install dependencies:
```bash
npm install
```

3. Run the application:
```bash
npm start
```

For development with DevTools:
```bash
npm run dev
```

## Usage

1. **Open a file**: Click "Open File" and select an EPUB or PDF
2. **Navigate**: Use arrow keys or click navigation buttons
3. **Chapter jumping**: Click on chapters in the sidebar
4. **AI Summaries**: Set your OpenAI API key in Settings, then click "Summarize Chapter"

## Keyboard Shortcuts

- `←` Previous page
- `→` Next page  
- `↑` Next chapter
- `↓` Previous chapter
- `S` Summarize current chapter

## Build

To build the application for distribution:

```bash
npm run build
```

For Windows specifically:
```bash
npm run build:win
```

## Maintenance

### Clean build artifacts:
```bash
npm run clean
```

### Complete reset (clean + reinstall dependencies):
```bash
npm run reset
```

## Configuration

### OpenAI API Key
To use AI-powered summaries, you need to:
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Open Settings in the app
3. Enter your API key
4. Save settings

The API key is stored locally and only used for generating summaries.

## Project Structure

```
epubizon/
├── src/
│   ├── main.js           # Electron main process
│   ├── preload.js        # Secure IPC bridge
│   ├── index.html        # Main UI
│   ├── styles.css        # UI styling
│   ├── renderer.js       # Main app logic
│   ├── keyboard-handler.js # Keyboard navigation
│   ├── epub-handler.js   # EPUB file processing
│   └── pdf-handler.js    # PDF file processing
├── package.json          # Project configuration
└── README.md            # This file
```

## Technical Details

- **Framework**: Electron
- **EPUB Processing**: epub.js
- **PDF Processing**: PDF.js
- **AI Integration**: OpenAI API
- **Image Handling**: Blob URLs with proper resource management

## License

MIT
