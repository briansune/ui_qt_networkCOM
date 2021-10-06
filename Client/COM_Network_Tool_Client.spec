# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\python_test\\uart2network\\Client'],
             binaries=[(r'C:\Anaconda\envs\py27_32\Library\plugins\platforms', r'./platforms')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='COM_Network_Tool_Server',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='qorvo_ico.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='COM_Network_Tool_Server')
