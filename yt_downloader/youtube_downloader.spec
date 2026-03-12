# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import shutil
from urllib import request

block_cipher = None

# Função para baixar o FFmpeg se não for encontrado
def ensure_ffmpeg_exists():
    ffmpeg_paths = [
        './ffmpeg.exe',  # Mesmo diretório
        './ffmpeg/ffmpeg.exe',  # Subdiretório
        './ffmpeg/bin/ffmpeg.exe'  # Estrutura de diretório comum
    ]
    
    # Verifica se já existe
    for path in ffmpeg_paths:
        if os.path.exists(path):
            print(f"FFmpeg encontrado em: {path}")
            return path
    
    # Se não encontrar, baixa uma versão portátil
    print("FFmpeg não encontrado localmente. Tentando baixar...")
    try:
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
        zip_path = os.path.join(os.getcwd(), "ffmpeg.zip")
        
        # Baixa o arquivo
        request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extrai o arquivo
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("./ffmpeg")
        
        # Localiza o ffmpeg.exe dentro da pasta extraída
        for root, dirs, files in os.walk("./ffmpeg"):
            if "ffmpeg.exe" in files:
                ffmpeg_path = os.path.join(root, "ffmpeg.exe")
                # Copia para o diretório raiz para facilitar
                shutil.copy(ffmpeg_path, "./ffmpeg.exe")
                print(f"FFmpeg baixado e copiado para: ./ffmpeg.exe")
                return "./ffmpeg.exe"
        
        print("Não foi possível encontrar ffmpeg.exe no arquivo baixado")
        return None
    except Exception as e:
        print(f"Erro ao baixar FFmpeg: {e}")
        return None

# Obter caminho do FFmpeg
ffmpeg_path = ensure_ffmpeg_exists()
binaries = []
if ffmpeg_path:
    # Adiciona o FFmpeg aos binários
    binaries.append((ffmpeg_path, '.'))

# Lista de todas as dependências escondidas que precisam ser incluídas
hidden_imports = [
    'yt_dlp.utils',
    'yt_dlp.extractor', 
    'yt_dlp.extractors',  # Todos os extratores de sites
    'yt_dlp.downloader',
    'yt_dlp.postprocessor',
    'yt_dlp.compat',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'json',
    'threading',
    'datetime',
    'urllib.request',
    'zipfile',
    'shutil'
]

a = Analysis(
    ['execute.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mantenha True para ver mensagens de debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)