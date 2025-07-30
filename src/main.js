const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    show: false
  });

  // Load the app
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
    
    // Suppress DevTools protocol warnings
    mainWindow.webContents.on('console-message', (event, level, message) => {
      if (message.includes('Autofill.enable') || message.includes('Autofill.setAddresses')) {
        event.preventDefault();
      }
    });
  }

  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC handlers for file operations
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'eBooks', extensions: ['epub', 'pdf'] },
      { name: 'EPUB files', extensions: ['epub'] },
      { name: 'PDF files', extensions: ['pdf'] },
      { name: 'All files', extensions: ['*'] }
    ]
  });

  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0];
    const fileName = path.basename(filePath);
    const fileExtension = path.extname(filePath).toLowerCase();
    
    // Check file size before loading
    const stats = fs.statSync(filePath);
    const fileSizeMB = stats.size / (1024 * 1024);
    
    console.log(`Loading file: ${fileName} (${fileSizeMB.toFixed(2)} MB)`);
    
    // For very large files, consider streaming or chunked reading
    if (fileSizeMB > 100) {
      console.warn('Large file detected, this may take some time to load...');
    }
    
    const fileBuffer = fs.readFileSync(filePath);
    
    return {
      name: fileName,
      path: filePath,
      extension: fileExtension,
      buffer: fileBuffer,
      sizeMB: fileSizeMB
    };
  }
  
  return null;
});

// IPC handler for OpenAI API calls
ipcMain.handle('generate-summary', async (event, { text, apiKey }) => {
  try {
    if (!apiKey || apiKey.trim() === '') {
      throw new Error('OpenAI API key is required');
    }

    // Import OpenAI dynamically to avoid issues if not installed
    let OpenAI;
    try {
      OpenAI = require('openai');
    } catch (importError) {
      console.error('OpenAI package not found:', importError);
      throw new Error('OpenAI package is required for AI-powered summaries. Please ensure it is installed.');
    }

    const openai = new OpenAI({ 
      apiKey: apiKey.trim()
    });

    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant that creates concise, informative summaries of book chapters. Focus on the main points, key concepts, and important details. Keep summaries between 2-4 paragraphs."
        },
        {
          role: "user",
          content: `Please provide a summary of the following chapter content:\n\n${text}`
        }
      ],
      max_tokens: 300,
      temperature: 0.7
    });

    const summary = completion.choices[0]?.message?.content || 'No summary generated';

    return {
      success: true,
      summary: summary
    };

  } catch (error) {
    console.error('OpenAI API Error:', error);
    
    // Provide helpful error messages
    let errorMessage = error.message;
    if (error.code === 'invalid_api_key') {
      errorMessage = 'Invalid OpenAI API key. Please check your API key in Settings.';
    } else if (error.code === 'insufficient_quota') {
      errorMessage = 'OpenAI API quota exceeded. Please check your OpenAI account billing.';
    } else if (error.message.includes('network') || error.message.includes('fetch')) {
      errorMessage = 'Network error. Please check your internet connection.';
    }

    return {
      success: false,
      error: errorMessage
    };
  }
});

// Store user settings (API key, etc.)
let userSettings = {
  openaiApiKey: ''
};

ipcMain.handle('save-settings', async (event, settings) => {
  userSettings = { ...userSettings, ...settings };
  return { success: true };
});

ipcMain.handle('get-settings', async () => {
  return userSettings;
});