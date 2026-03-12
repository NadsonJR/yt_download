import os
import sys
import json
import shutil
import tempfile
import subprocess
import yt_dlp
import tkinter as tk
import logging
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Progressbar, Combobox
from threading import Thread
from datetime import datetime

# Configuração do sistema de logging
def setup_logger():
    # Configurar o logger principal
    logger = logging.getLogger('youtube_downloader')
    logger.setLevel(logging.DEBUG)  # Captura todos os níveis de log
    
    # Criar manipulador para console com formatação colorida
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Definir formato detalhado dos logs
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(log_format)
    
    # Adicionar o manipulador ao logger
    logger.addHandler(console_handler)
    
    # Também salvar logs em arquivo
    file_handler = logging.FileHandler('youtube_downloader.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    return logger

# Inicializar o logger
logger = setup_logger()
logger.info("Iniciando YouTube Downloader")

# Dicionário de formatos disponíveis
FORMAT_OPTIONS = {
    # Formatos de Vídeo
    'MP4 (H.264)': {'ext': 'mp4', 'vcodec': 'h264', 'acodec': 'aac'},
    'MP4 (melhor qualidade)': {'ext': 'mp4', 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'},
    'WebM (VP9)': {'ext': 'webm', 'vcodec': 'vp9', 'acodec': 'opus'},
    'AVI': {'ext': 'avi', 'vcodec': 'libx264', 'acodec': 'mp3'},
    'MKV': {'ext': 'mkv', 'vcodec': 'h264', 'acodec': 'aac'},
    'MOV': {'ext': 'mov', 'vcodec': 'h264', 'acodec': 'aac'},
    
    # Formatos de Áudio
    'MP3 (320kbps)': {'ext': 'mp3', 'acodec': 'mp3', 'abr': '320'},
    'MP3 (192kbps)': {'ext': 'mp3', 'acodec': 'mp3', 'abr': '192'},
    'WAV': {'ext': 'wav', 'acodec': 'wav'},
    'FLAC': {'ext': 'flac', 'acodec': 'flac'},
    'AAC': {'ext': 'aac', 'acodec': 'aac'},
    'OGG': {'ext': 'ogg', 'acodec': 'vorbis'},
    'M4A': {'ext': 'm4a', 'acodec': 'aac'}
}

# Configuração da janela principal executável
def get_base_dir():
    """Retorna o diretório base da aplicação, funcionando tanto em desenvolvimento quanto no executável."""
    if hasattr(sys, '_MEIPASS'):
        # Executando de um arquivo .exe criado pelo PyInstaller
        base_dir = sys._MEIPASS
        logger.debug(f"Executando a partir de executável empacotado. Base dir: {base_dir}")
        return base_dir
    else:
        # Executando normalmente
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Executando a partir de script Python. Base dir: {base_dir}")
        return base_dir

def get_config_path():
    """Retorna o caminho para o arquivo de configuração."""
    # Quando executado como .exe, salva no mesmo diretório do executável
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        logger.debug(f"Modo executável: Diretório de configuração: {app_dir}")
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Modo desenvolvimento: Diretório de configuração: {app_dir}")
    
    config_path = os.path.join(app_dir, 'config.json')
    logger.debug(f"Caminho do arquivo de configuração: {config_path}")
    return config_path

# Função para salvar a pasta destino e formato no arquivo config.json
def save_config(destination_folder, output_format=None):
    logger.info(f"Salvando configuração: pasta destino = {destination_folder}, formato = {output_format}")
    try:
        config_path = get_config_path()
        config_data = {'destination_folder': destination_folder}
        if output_format:
            config_data['output_format'] = output_format
        
        with open(config_path, 'w') as config_file:
            json.dump(config_data, config_file)
        logger.debug("Configuração salva com sucesso")
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")

def is_ffmpeg_available():
    logger.info("Verificando disponibilidade do FFmpeg")
    try:
        # Verifica se FFmpeg está no PATH
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        logger.debug(f"FFmpeg encontrado no PATH do sistema: {result.stdout.decode('utf-8', errors='ignore').splitlines()[0] if result.stdout else 'N/A'}")
        return True
    except FileNotFoundError:
        logger.warning("FFmpeg não encontrado no PATH do sistema. Procurando em diretórios alternativos...")
        try:
            # Locais adicionais para procurar o FFmpeg
            possible_paths = [
                # No mesmo diretório do executável (quando empacotado)
                os.path.join(os.path.dirname(sys.executable), 'ffmpeg.exe'),
                # No diretório base da aplicação (pode ser dentro do arquivo .exe extraído pelo PyInstaller)
                os.path.join(get_base_dir(), 'ffmpeg.exe'),
                # No diretório atual
                os.path.join(os.getcwd(), 'ffmpeg.exe')
            ]
            
            logger.debug(f"Caminhos possíveis para FFmpeg: {possible_paths}")
            
            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"FFmpeg encontrado em: {path}")
                    # Adiciona ao PATH temporariamente
                    os.environ['PATH'] += os.pathsep + os.path.dirname(path)
                    logger.debug(f"PATH atualizado: {os.environ['PATH']}")
                    return True
            
            # Se estiver executando a partir do PyInstaller (executável)
            if getattr(sys, 'frozen', False):
                logger.info("Tentando extrair FFmpeg do executável...")
                # O ffmpeg está incorporado no executável, então precisamos extraí-lo
                temp_dir = os.path.join(tempfile.gettempdir(), 'youtube_downloader')
                logger.debug(f"Diretório temporário para FFmpeg: {temp_dir}")
                os.makedirs(temp_dir, exist_ok=True)
                
                ffmpeg_temp_path = os.path.join(temp_dir, 'ffmpeg.exe')
                
                # Se já extraímos anteriormente, verifica se ainda existe
                if os.path.exists(ffmpeg_temp_path):
                    logger.info(f"FFmpeg já extraído encontrado em: {ffmpeg_temp_path}")
                    os.environ['PATH'] += os.pathsep + temp_dir
                    return True
                
                # Tenta copiar do recurso embutido
                try:
                    ffmpeg_bundled = os.path.join(sys._MEIPASS, 'ffmpeg.exe')
                    logger.debug(f"Procurando FFmpeg embutido em: {ffmpeg_bundled}")
                    if os.path.exists(ffmpeg_bundled):
                        logger.info(f"Copiando FFmpeg embutido para: {ffmpeg_temp_path}")
                        shutil.copy2(ffmpeg_bundled, ffmpeg_temp_path)
                        os.environ['PATH'] += os.pathsep + temp_dir
                        logger.info(f"FFmpeg extraído para: {ffmpeg_temp_path}")
                        return True
                    else:
                        logger.warning(f"FFmpeg embutido não encontrado em: {ffmpeg_bundled}")
                except Exception as e:
                    logger.error(f"Erro ao extrair FFmpeg: {e}")
            
            logger.error("FFmpeg não encontrado em nenhum local")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar FFmpeg: {e}", exc_info=True)
            return False

# No início do seu programa:
if not is_ffmpeg_available():
    logger.warning("FFmpeg não disponível, mostrando aviso ao usuário")
    messagebox.showwarning("FFmpeg não encontrado", 
                         "FFmpeg não foi encontrado. Algumas funcionalidades podem não funcionar corretamente.\n"
                         "Por favor, instale o FFmpeg ou coloque-o na mesma pasta deste programa.")

# Função para carregar a pasta destino e formato do arquivo config.json
def load_config():
    logger.info("Carregando configuração")
    try:
        config_path = get_config_path()
        if os.path.exists(config_path):
            logger.debug(f"Arquivo de configuração encontrado: {config_path}")
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                folder = config.get('destination_folder', '')
                format_name = config.get('output_format', 'MP4 (melhor qualidade)')
                logger.info(f"Configuração carregada - Pasta: {folder}, Formato: {format_name}")
                return folder, format_name
        else:
            logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}", exc_info=True)
    return '', 'MP4 (melhor qualidade)'

# Função para atualizar formatos disponíveis baseado no tipo de download
def update_format_options():
    download_type = download_type_var.get()
    logger.debug(f"Atualizando opções de formato para tipo: {download_type}")
    
    if download_type == "audio":
        # Mostrar apenas formatos de áudio
        audio_formats = [fmt for fmt in FORMAT_OPTIONS.keys() if any(
            keyword in fmt.lower() for keyword in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']
        )]
        format_combobox['values'] = audio_formats
        if format_var.get() not in audio_formats:
            format_var.set('MP3 (192kbps)')
    else:
        # Mostrar apenas formatos de vídeo
        video_formats = [fmt for fmt in FORMAT_OPTIONS.keys() if any(
            keyword in fmt.lower() for keyword in ['mp4', 'webm', 'avi', 'mkv', 'mov']
        )]
        format_combobox['values'] = video_formats
        if format_var.get() not in video_formats:
            format_var.set('MP4 (melhor qualidade)')
    
    logger.debug(f"Formatos atualizados: {format_combobox['values']}")

# Função para atualizar a barra de progresso
def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()
    logger.debug(f"Progresso atualizado: {percent}%")

# Função de download do conteúdo (áudio ou vídeo)
def download_content(url, destination_folder, download_type, output_format, progress_var, progress_bar, status_label):
    logger.info(f"Iniciando download: URL={url}, tipo={download_type}, formato={output_format}, destino={destination_folder}")
    
    format_config = FORMAT_OPTIONS.get(output_format, FORMAT_OPTIONS['MP4 (melhor qualidade)'])
    logger.debug(f"Configuração do formato: {format_config}")
    
    # Configurações base
    ydl_opts = {
        'outtmpl': os.path.join(destination_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: progress_hook(d, progress_var, progress_bar, status_label)]
    }
    
    if download_type == "audio":
        logger.debug("Configurando opções para download de áudio")
        
        if 'format' in format_config:
            ydl_opts['format'] = format_config['format']
        else:
            ydl_opts['format'] = 'bestaudio/best'
        
        # Configurar pós-processamento para áudio
        postprocessor = {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format_config.get('acodec', 'mp3'),
        }
        
        if 'abr' in format_config:
            postprocessor['preferredquality'] = format_config['abr']
        
        ydl_opts['postprocessors'] = [postprocessor]
        success_message = f"O áudio foi baixado com sucesso no formato {output_format}."
        
    elif download_type == "video":  # apenas vídeo
        logger.debug("Configurando opções para download de vídeo")
        
        if 'format' in format_config:
            ydl_opts['format'] = format_config['format']
        else:
            # Construir string de formato baseada nas especificações
            format_parts = []
            if format_config.get('ext'):
                format_parts.append(f"best[ext={format_config['ext']}]")
            if format_config.get('vcodec'):
                format_parts.append(f"best[vcodec={format_config['vcodec']}]")
            
            if format_parts:
                ydl_opts['format'] = '/'.join(format_parts) + '/best'
            else:
                ydl_opts['format'] = 'best'
        
        # Configurar pós-processamento se necessário
        if format_config.get('ext') and format_config['ext'] not in ['mp4', 'webm']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': format_config['ext'],
            }]
        
        success_message = f"O vídeo foi baixado com sucesso no formato {output_format}."
        
    else:  # áudio e vídeo na melhor qualidade
        logger.debug("Configurando opções para download de áudio+vídeo em alta qualidade")
        
        if 'format' in format_config:
            ydl_opts['format'] = format_config['format']
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        
        ydl_opts['merge_output_format'] = format_config.get('ext', 'mp4')
        success_message = f"O vídeo e áudio foram baixados na melhor qualidade no formato {output_format}."
    
    try:
        logger.info("Iniciando o processo de download com yt_dlp")
        logger.debug(f"Opções do yt_dlp: {ydl_opts}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug("Obtendo informações do vídeo")
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Desconhecido')
            duration = info.get('duration', 0)
            logger.info(f"Vídeo encontrado: Título='{title}', Duração={duration}s")
            
            logger.debug("Iniciando download efetivo")
            ydl.download([url])
        
        logger.info(f"Download concluído com sucesso: {success_message}")
        messagebox.showinfo("Download completo", success_message)
    except Exception as e:
        logger.error(f"Erro durante o download: {e}", exc_info=True)
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Função para mostrar formatos disponíveis
def show_available_formats():
    url = url_entry.get()
    if not url:
        logger.warning("Tentativa de mostrar formatos sem URL")
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo.")
        return
        
    logger.info(f"Obtendo formatos disponíveis para: {url}")
    status_label.config(text="Obtendo informações do vídeo...")
    
    def get_formats():
        try:
            logger.debug("Iniciando extração de informações de formato")
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug("Extraindo metadados do vídeo")
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                logger.info(f"Encontrados {len(formats)} formatos disponíveis")
                
                # Ordenar por qualidade (resolução)
                formats.sort(key=lambda x: (
                    x.get('height', 0) or 0, 
                    x.get('tbr', 0) or 0
                ), reverse=True)
                
                formats_text = "Formatos disponíveis:\n\n"
                
                # Primeiro listar formatos com vídeo e áudio
                logger.debug("Processando formatos de vídeo+áudio")
                formats_text += "== VÍDEO + ÁUDIO ==\n"
                video_audio_count = 0
                for f in formats:
                    if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') != 'none':
                        resolution = f"{f.get('width', '?')}x{f.get('height', '?')}"
                        size = f.get('filesize') or f.get('filesize_approx')
                        size_text = f"{size/1024/1024:.1f} MB" if size else "Tamanho desconhecido"
                        formats_text += f"[{f.get('format_id')}] {resolution} - {f.get('ext')} ({f.get('format_note', '')}) - {size_text}\n"
                        video_audio_count += 1
                logger.info(f"Encontrados {video_audio_count} formatos com vídeo+áudio")
                
                # Depois listar formatos só de vídeo
                logger.debug("Processando formatos de apenas vídeo")
                formats_text += "\n== APENAS VÍDEO ==\n"
                video_only_count = 0
                for f in formats:
                    if f.get('vcodec', 'none') != 'none' and f.get('acodec', 'none') == 'none':
                        resolution = f"{f.get('width', '?')}x{f.get('height', '?')}"
                        formats_text += f"[{f.get('format_id')}] {resolution} - {f.get('ext')} ({f.get('format_note', '')})\n"
                        video_only_count += 1
                logger.info(f"Encontrados {video_only_count} formatos apenas de vídeo")
                
                # Título e duração do vídeo
                title = info.get('title', 'Desconhecido')
                duration = int(info.get('duration', 0) or 0)
                logger.info(f"Vídeo: '{title}', Duração: {duration//60}:{duration%60:02d}")
                
                formats_text = f"Título: {title}\n" + \
                               f"Duração: {duration // 60}:{duration % 60:02d}\n\n" + \
                               formats_text
                
                logger.debug("Exibindo janela de formatos")
                root.after(0, show_formats_window, formats_text)
                
        except Exception as e:
            logger.error(f"Erro ao obter formatos: {e}", exc_info=True)
            root.after(0, lambda: messagebox.showerror("Erro", f"Não foi possível obter os formatos: {e}"))
        finally:
            logger.debug("Finalizando processo de obtenção de formatos")
            root.after(0, lambda: status_label.config(text="Aguardando..."))
    
    logger.debug("Iniciando thread para obter formatos")
    Thread(target=get_formats).start()

# Função para exibir janela de formatos
def show_formats_window(formats_text):
    logger.debug("Criando janela para exibir formatos disponíveis")
    format_window = tk.Toplevel(root)
    format_window.title("Formatos Disponíveis")
    format_window.geometry("600x500")
    
    text_widget = tk.Text(format_window, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(text_widget)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_widget.yview)
    
    text_widget.insert(tk.END, formats_text)
    text_widget.config(state=tk.DISABLED)  # Torna o texto não editável
    logger.info("Janela de formatos exibida com sucesso")

# Função de hook para a barra de progresso
def progress_hook(d, progress_var, progress_bar, status_label):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = int(downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
        speed = d.get('speed', 0) or 0
        size_in_mib = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
        speed_in_kib = speed / 1024 if speed > 0 else 0
        
        update_progress(percent, progress_var, progress_bar)
        status_text = f"Baixando: {percent}% - Velocidade: {speed_in_kib:.2f} KiB/s - Tamanho: {size_in_mib:.2f} MiB"
        status_label.config(text=status_text)
        
        # Log menos frequente para não sobrecarregar o console (a cada 5%)
        if percent % 5 == 0:
            logger.info(status_text)
        else:
            logger.debug(status_text)
            
    elif d['status'] == 'finished':
        update_progress(100, progress_var, progress_bar)
        download_type = getattr(status_label, 'download_type', 'audio')
        output_format = getattr(status_label, 'output_format', 'Desconhecido')
        
        if download_type == 'audio':
            logger.info(f"Download de áudio concluído, formato: {output_format}")
            status_label.config(text=f"Conversão para {output_format} concluída")
        elif download_type == 'video':
            logger.info(f"Download de vídeo concluído, formato: {output_format}")
            status_label.config(text=f"Download do vídeo em {output_format} concluído")
        else:
            logger.info(f"Download concluído, formato: {output_format}")
            status_label.config(text=f"Download e combinação em {output_format} concluídos")

# Função para iniciar o download em uma thread separada
def start_download():
    url = url_entry.get()
    if not url:
        logger.warning("Tentativa de download sem URL")
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo.")
        return

    destination_folder = destination_folder_var.get()
    if not destination_folder:
        logger.warning("Tentativa de download sem pasta de destino")
        messagebox.showwarning("Aviso", "Por favor, escolha a pasta de destino.")
        return

    download_type = download_type_var.get()
    output_format = format_var.get()
    
    logger.info(f"Iniciando download: URL={url}, tipo={download_type}, formato={output_format}, destino={destination_folder}")
    save_config(destination_folder, output_format)
    
    logger.info(f"Tipo de download selecionado: {download_type}")
    logger.info(f"Formato de saída selecionado: {output_format}")
    
    # Armazenar informações para usar no progress_hook
    status_label.download_type = download_type
    status_label.output_format = output_format
    
    logger.debug("Criando thread para download")
    download_thread = Thread(target=download_content, 
                           args=(url, destination_folder, download_type, output_format, progress_var, progress_bar, status_label))
    download_thread.start()
    logger.debug("Thread de download iniciada")

# Função para selecionar a pasta de destino
def select_destination_folder():
    logger.debug("Abrindo diálogo para selecionar pasta de destino")
    folder = filedialog.askdirectory()
    if folder:
        logger.info(f"Pasta de destino selecionada: {folder}")
        destination_folder_var.set(folder)
    else:
        logger.debug("Seleção de pasta cancelada pelo usuário")

# GUI
logger.info("Inicializando interface gráfica")
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("700x500")  # Aumentei um pouco para acomodar os novos elementos
logger.debug("Janela principal criada")

# Centralizar os widgets no root
frame = tk.Frame(root)
frame.pack(expand=True)

# URL Entry
logger.debug("Criando campo de entrada para URL")
tk.Label(frame, text="Link do Vídeo:").pack(pady=5)
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5)

# Destination Folder
logger.debug("Criando campo para pasta de destino")
tk.Label(frame, text="Pasta de Destino:").pack(pady=5)
destination_folder_var = tk.StringVar()
loaded_folder, loaded_format = load_config()
destination_folder_var.set(loaded_folder)
logger.debug(f"Pasta de destino padrão: {loaded_folder}")

destination_frame = tk.Frame(frame)
destination_frame.pack(pady=5)
tk.Entry(destination_frame, textvariable=destination_folder_var, width=50).pack(side=tk.LEFT, padx=5)
tk.Button(destination_frame, text="Selecionar", command=select_destination_folder).pack(side=tk.LEFT, padx=5)

# Download Type Selection
logger.debug("Criando seleção de tipo de download")
download_type_frame = tk.Frame(frame)
download_type_frame.pack(pady=5)
download_type_var = tk.StringVar(value="audio")
tk.Label(download_type_frame, text="Tipo de Download:").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(download_type_frame, text="Áudio", variable=download_type_var, value="audio", command=update_format_options).pack(side=tk.LEFT)
tk.Radiobutton(download_type_frame, text="Vídeo", variable=download_type_var, value="video", command=update_format_options).pack(side=tk.LEFT)
tk.Radiobutton(download_type_frame, text="Áudio e Vídeo (Melhor Qualidade)", variable=download_type_var, value="both", command=update_format_options).pack(side=tk.LEFT)

# Format Selection
logger.debug("Criando seleção de formato de saída")
format_frame = tk.Frame(frame)
format_frame.pack(pady=5)
tk.Label(format_frame, text="Formato de Saída:").pack(side=tk.LEFT, padx=5)
format_var = tk.StringVar(value=loaded_format)
format_combobox = Combobox(format_frame, textvariable=format_var, width=25, state="readonly")
format_combobox.pack(side=tk.LEFT, padx=5)

# Inicializar as opções de formato
update_format_options()

# Progress Bar
logger.debug("Criando barra de progresso")
tk.Label(frame, text="Progresso:").pack(pady=5)
progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=100, variable=progress_var)
progress_bar.pack(pady=5)

# Status Label
logger.debug("Criando label de status")
status_label = tk.Label(frame, text="Aguardando...")
status_label.pack(pady=5)

# Botões
logger.debug("Criando botões")
buttons_frame = tk.Frame(frame)
buttons_frame.pack(pady=10)

tk.Button(buttons_frame, text="Baixar", command=start_download).pack(side=tk.LEFT, padx=10)
tk.Button(buttons_frame, text="Ver Formatos Disponíveis", command=show_available_formats).pack(side=tk.LEFT, padx=10)

logger.info("Interface gráfica inicializada com sucesso")

# No final do arquivo, substitua o root.mainloop() por:
try:
    logger.info("Iniciando loop principal da aplicação")
    root.mainloop()
except Exception as e:
    # Registra o erro em um arquivo
    error_msg = f"Erro fatal na aplicação: {e}"
    logger.critical(error_msg, exc_info=True)
    
    error_file = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'error_log.txt')
    with open(error_file, 'w') as f:
        f.write(f"Erro: {str(e)}")
    
    messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}\nDetalhes foram salvos em {error_file}")