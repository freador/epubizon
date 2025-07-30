#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🧹 Limpando projeto...');

const dirsToClean = [
    'dist',
    'build', 
    'out',
    'release',
    '.cache',
    'coverage'
];

function cleanDirectory(dir) {
    const fullPath = path.join(__dirname, dir);
    if (fs.existsSync(fullPath)) {
        console.log(`  🗑️  Removendo ${dir}/`);
        fs.rmSync(fullPath, { recursive: true, force: true });
    }
}

function cleanFiles(pattern) {
    const files = fs.readdirSync(__dirname);
    files.forEach(file => {
        if (file.match(pattern)) {
            console.log(`  🗑️  Removendo ${file}`);
            fs.unlinkSync(path.join(__dirname, file));
        }
    });
}

// Limpar diretórios
dirsToClean.forEach(cleanDirectory);

// Limpar arquivos de log
cleanFiles(/.*\.log$/);

// Limpar arquivos temporários
cleanFiles(/.*\.tmp$/);
cleanFiles(/.*\.temp$/);

console.log('✅ Limpeza concluída!');
console.log('💡 Para limpar node_modules, execute: npm run clean:all');