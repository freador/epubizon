# 📚 Epubizon - EPUB & PDF Reader

Uma aplicação desktop moderna em Python para leitura de arquivos EPUB e PDF com resumos alimentados por IA.

## ✨ Recursos

- 📚 **Suporte EPUB & PDF** - Leia arquivos EPUB e PDF
- 🤖 **Resumos com IA** - Gere resumos de capítulos usando OpenAI API
- ⌨️ **Navegação por Teclado** - Navegue com setas e atalhos
- 🎨 **Interface Moderna** - Design limpo e responsivo
- 📖 **Navegação por Capítulos** - Salte diretamente para qualquer capítulo
- 🖼️ **Processamento de Imagens** - Suporte completo para imagens em EPUBs
- ⚙️ **Configurações Avançadas** - Personalize fontes, temas e mais

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+ 
- pip

### Passos

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd epubizon
```

2. **Crie um ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\\Scripts\\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação:**
```bash
python main.py
```

## 📖 Como Usar

1. **Abrir arquivo**: Clique em "📂 Abrir Arquivo" ou pressione `Ctrl+O`
2. **Navegar**: Use as setas do teclado ou clique nos botões de navegação
3. **Pular capítulos**: Clique nos capítulos na barra lateral
4. **Resumos com IA**: Configure sua chave OpenAI nas configurações, depois pressione `F1`

## ⌨️ Atalhos de Teclado

- `←` / `→` - Navegar entre capítulos
- `↑` / `↓` - Navegar entre capítulos  
- `F1` - Resumir capítulo atual
- `Ctrl+O` - Abrir arquivo
- `Ctrl+,` - Abrir configurações
- `Ctrl+Q` - Sair da aplicação

## ⚙️ Configuração

### Chave da API OpenAI

Para usar resumos com IA:

1. Obtenha uma chave da API em [OpenAI](https://platform.openai.com/api-keys)
2. Abra as Configurações na aplicação
3. Insira sua chave da API
4. Salve as configurações

A chave é armazenada localmente e usada apenas para gerar resumos.

## 📁 Estrutura do Projeto

```
epubizon/
├── main.py              # Aplicação principal
├── epub_handler.py      # Processamento de arquivos EPUB
├── pdf_handler.py       # Processamento de arquivos PDF
├── ai_summarizer.py     # Integração com OpenAI
├── settings_manager.py  # Gerenciamento de configurações
├── settings_dialog.py   # Interface de configurações
├── requirements.txt     # Dependências Python
├── venv/               # Ambiente virtual
└── README.md           # Este arquivo
```

## 🔧 Dependências

- **ebooklib** - Processamento de arquivos EPUB
- **PyPDF2** - Processamento de arquivos PDF  
- **Pillow** - Processamento de imagens
- **openai** - Integração com OpenAI API
- **beautifulsoup4** - Parsing de HTML/XML
- **tkinter** - Interface gráfica (incluída no Python)

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

MIT - veja o arquivo LICENSE para detalhes.

## 🆕 Changelog

### v2.0.0
- ✅ Reescrito completamente em Python (era Electron)
- ✅ Interface nativa com tkinter
- ✅ Melhor performance e menor uso de memória
- ✅ Suporte completo para navegação por capítulos
- ✅ Design moderno e responsivo
- ✅ Configurações avançadas