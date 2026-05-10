# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

import os

block_cipher = None

# Icon path - use if exists, otherwise None
icon_path = 'app/static/icon.ico'
if not os.path.exists(icon_path):
    icon_path = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../frontend/dist', 'frontend/dist'),
        ('app/static', 'app/static'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'passlib.handlers.bcrypt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的大型库以加速打包
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'keras',
        'sklearn', 'scikit-learn',
        'pandas', 'numpy', 'scipy',
        'matplotlib', 'PIL', 'pillow',
        'cv2', 'opencv-python',
        'transformers', 'langchain', 'langchain_community',
        'nltk', 'spacy',
        'jupyter', 'notebook', 'ipython',
        'pytest', 'unittest',
        'PyQt5', 'PyQt6',
        'sphinx', 'docutils',
        'boto3', 'botocore',
        'dask', 'distributed',
        'numba', 'llvmlite',
        'bokeh', 'plotly', 'altair',
        'xarray', 'h5py', 'tables',
        'statsmodels', 'patsy',
        'imageio', 'skimage',
        'zmq', 'nacl',
        'black', 'yapf',
        'rich', 'pygments',
        'onnxruntime',
        'sentence_transformers',
        'rapidfuzz',
        'pyarrow', 'fsspec', 'lz4',
        'panel', 'pyviz_comms',
        'intake', 'xyzservices',
    ],
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
    name='语音转换助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
