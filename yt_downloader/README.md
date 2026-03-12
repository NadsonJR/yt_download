# 📹 YouTube Downloader

Um downloader de vídeos e áudios do YouTube com interface gráfica intuitiva, desenvolvido em Python com sistema de validação de qualidade e controles visuais claros.

## 🎯 **Características Principais**

- ✅ **Interface Gráfica Intuitiva** - Tkinter com orientações visuais claras
- ✅ **Download de Áudio** - MP3, FLAC, WAV, AAC, OGG, M4A
- ✅ **Download de Vídeo + Áudio** - MP4, WebM, AVI, MKV, MOV
- ✅ **Seleção de Qualidade** - Escolha entre 720p, 1080p, 4K, etc.
- ✅ **Verificação Prévia** - Veja as qualidades disponíveis antes de baixar
- ✅ **Sistema de Validação** - Impede downloads sem verificar qualidade
- ✅ **Barra de Progresso** - Acompanhe o progresso em tempo real
- ✅ **Logs Detalhados** - Sistema completo de logging para debugging
- ✅ **Configurações Persistentes** - Lembra pasta e formato escolhidos

## 🖥️ **Interface do Software**

```
┌─────────────────────────────────────────────────────────┐
│ 📹 YouTube Downloader                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Link do Vídeo: [________________] [Verificar Qualidade] │
│                                                         │
│ Pasta de Destino: [___________] [Selecionar]            │
│                                                         │
│ Tipo de Download: ○ Áudio ○ Áudio e Vídeo              │
│                                                         │
│ Qualidade do Vídeo: [⚠️ Clique em 'Verificar Qualidade' primeiro ▼] │
│                                                         │
│ Formato de Saída: [MP4 (melhor qualidade) ▼]           │
│                                                         │
│ Progresso: [████████████████████] 100%                 │
│ Status: Aguardando...                                   │
│ 💡 Para download de vídeo: Cole o link e clique em 'Verificar Qualidade' primeiro │
│                                                         │
│            [⚠️ Verificar qualidade primeiro]              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 **Como Usar**

### 📹 **Para Baixar Vídeos (Áudio + Vídeo):**

1. **📋 Cole o link** do YouTube no campo "Link do Vídeo"
2. **🔍 Clique em "Verificar Qualidade"** para ver as opções disponíveis
3. **🎯 Selecione a qualidade** desejada (720p, 1080p, etc.)
4. **📁 Escolha a pasta** de destino clicando em "Selecionar"
5. **⚙️ Selecione "Áudio e Vídeo"** no tipo de download
6. **🎨 Escolha o formato** de saída (MP4 recomendado)
7. **📥 Clique em "Baixar"** (agora habilitado)

### 🎵 **Para Baixar Apenas Áudio:**

1. **📋 Cole o link** do YouTube no campo "Link do Vídeo"
2. **📁 Escolha a pasta** de destino clicando em "Selecionar"
3. **🎵 Selecione "Áudio"** no tipo de download
4. **🎨 Escolha o formato** de áudio (MP3 192kbps recomendado)
5. **📥 Clique em "Baixar"** (habilitado automaticamente)

> **💡 Dica:** Para áudio, não é necessário verificar qualidade!

## 📋 **Requisitos do Sistema**

### **Sistema Operacional:**
- Windows 10/11
- macOS 10.14+
- Linux Ubuntu 18.04+

### **Dependências Python:**
```
Python 3.8+
yt-dlp >= 2025.9.5
tkinter (incluído no Python)
```

### **Dependências Externas:**
- **FFmpeg** (para conversão de formatos)

## 🛠️ **Instalação**

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/youtube-downloader.git
cd youtube-downloader
```

### **2. Instale o Python**
Baixe e instale Python 3.8+ de [python.org](https://python.org)

### **3. Instale as Dependências**
```bash
pip install yt-dlp
```

### **4. Instale o FFmpeg**

#### **Windows:**
1. Baixe FFmpeg de [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extraia para `C:\ffmpeg`
3. Adicione `C:\ffmpeg\bin` ao PATH do sistema
4. **OU** coloque `ffmpeg.exe` na mesma pasta do script

#### **macOS:**
```bash
brew install ffmpeg
```

#### **Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### **5. Execute o Software**
```bash
python execute_copy.py
```

## 📁 **Estrutura do Projeto**

```
youtube-downloader/
├── 📄 execute.py              # Arquivo principal
├── 📄 config.json                  # Configurações do usuário
├── 📄 youtube_downloader.log       # Logs do sistema
├── 📄 ffmpeg.exe                   # FFmpeg (Windows)
├── 📄 README.md                    # Este arquivo
├── 📁 build/                       # Arquivos de build (PyInstaller)
├── 📁 Backup/                      # Backups de versões anteriores

```

## 🎨 **Formatos Suportados**

### **📹 Vídeo:**
| Formato | Extensão | Descrição |
|---------|----------|-----------|
| MP4 (H.264) | `.mp4` | Melhor compatibilidade |
| MP4 (melhor qualidade) | `.mp4` | Qualidade adaptativa |
| WebM (VP9) | `.webm` | Código aberto |
| AVI | `.avi` | Compatibilidade antiga |
| MKV | `.mkv` | Alta qualidade |
| MOV | `.mov` | Formato Apple |

### **🎵 Áudio:**
| Formato | Extensão | Qualidade |
|---------|----------|-----------|
| MP3 (320kbps) | `.mp3` | Alta qualidade |
| MP3 (192kbps) | `.mp3` | Qualidade padrão |
| FLAC | `.flac` | Sem perda |
| WAV | `.wav` | Sem compressão |
| AAC | `.aac` | Boa compressão |
| OGG | `.ogg` | Código aberto |
| M4A | `.m4a` | Formato Apple |

## 🎯 **Qualidades de Vídeo Disponíveis**

O software detecta automaticamente e oferece:
- **4K (2160p)** - Ultra HD
- **1440p** - 2K/QHD  
- **1080p** - Full HD
- **720p** - HD
- **480p** - SD
- **360p** - Baixa qualidade
- **Melhor qualidade disponível** - Automático

## 🔧 **Sistema de Validação**

### **🚦 Estados da Interface:**

| Estado | Botão | Campo Qualidade | Orientação |
|--------|-------|-----------------|------------|
| **Inicial** | `⚠️ Verificar qualidade primeiro` | `⚠️ Clique em 'Verificar Qualidade' primeiro` | 💡 Instrução azul |
| **Áudio selecionado** | `📥 Baixar` | - | 🎵 Texto verde |
| **Qualidade verificada** | `📥 Baixar` | Lista de qualidades | ✅ Sucesso verde |
| **URL alterada** | `⚠️ Verificar qualidade primeiro` | Reset | 💡 Instrução azul |

### **🛡️ Proteções Implementadas:**
- ✅ **Impossível baixar vídeo** sem verificar qualidade
- ✅ **Reset automático** quando URL é alterada  
- ✅ **Validações múltiplas** em diferentes camadas
- ✅ **Mensagens claras** sobre o que fazer

## 📊 **Sistema de Logs**

O software gera logs detalhados em `youtube_downloader.log`:

```
2025-09-18 22:39:44 - INFO - Iniciando YouTube Downloader
2025-09-18 22:39:44 - DEBUG - FFmpeg encontrado no PATH do sistema
2025-09-18 22:39:44 - INFO - Interface gráfica inicializada com sucesso
2025-09-18 22:39:47 - INFO - Verificando qualidades disponíveis para: [URL]
2025-09-18 22:39:50 - INFO - Download concluído com sucesso
```

**Níveis de Log:**
- `INFO` - Operações principais
- `DEBUG` - Detalhes técnicos
- `WARNING` - Avisos não críticos
- `ERROR` - Erros que impedem operação
- `CRITICAL` - Erros fatais

## 🐛 **Resolução de Problemas**

### **❌ Problema:** "FFmpeg não encontrado"
**✅ Solução:** 
1. Instale FFmpeg seguindo as instruções acima
2. OU coloque `ffmpeg.exe` na pasta do programa
3. Reinicie o software

### **❌ Problema:** "Erro de postprocessamento"
**✅ Solução:**
1. Tente um formato diferente (MP4 H.264)
2. Baixe apenas áudio primeiro
3. Verifique os logs em `youtube_downloader.log`

### **❌ Problema:** "Botão Baixar desabilitado"
**✅ Solução:**
1. Para vídeo: Clique em "Verificar Qualidade" primeiro
2. Para áudio: Selecione "Áudio" no tipo de download
3. Verifique se inseriu o link corretamente

### **❌ Problema:** "Não consegue baixar vídeo específico"
**✅ Solução:**
1. Verifique se o vídeo não é privado/restrito
2. Tente uma qualidade menor (720p em vez de 1080p)
3. Use formato MP4 padrão

## 🔄 **Atualizações e Melhorias**

### **Versão Atual (v2.0):**
- ✅ Sistema de validação de qualidade
- ✅ Interface com indicações visuais
- ✅ Orientações contextuais
- ✅ Texto dinâmico nos botões
- ✅ Sistema de logs aprimorado

### **Melhorias Implementadas:**
- 🔧 Correção de erros de postprocessamento
- 🎨 Interface mais intuitiva e clara
- 🛡️ Sistema robusto de validação
- 📊 Logs detalhados para debugging
- 🚀 Performance otimizada

## 🤝 **Contribuição**

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 **Agradecimentos**

- **yt-dlp** - Biblioteca principal para download
- **FFmpeg** - Processamento de mídia
- **Python tkinter** - Interface gráfica
- **Comunidade open source** - Suporte e feedback

## 📞 **Suporte**

- 🐛 **Issues:** [GitHub Issues](https://github.com/seu-usuario/youtube-downloader/issues)
- 📖 **Documentação:** Pasta `Documentação/` no projeto
- 📝 **Logs:** Arquivo `youtube_downloader.log` para debugging

---

**💡 Dica:** Mantenha sempre o yt-dlp atualizado com `pip install --upgrade yt-dlp` para melhor compatibilidade!

---
*Feito com ❤️ em Python*