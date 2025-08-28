# package_echosplit.py
# Automates packaging EchoSplit into a clickable desktop app with PyInstaller.
# Built with care for the next dev, ensuring clarity and reliability.

import os
import subprocess
import platform

def ensure_dependencies():
    """Install required dependencies for packaging."""
    dependencies = ['pyinstaller', 'kivy', 'pygame', 'pydub', 'librosa', 'numpy', 'spleeter']
    for dep in dependencies:
        subprocess.run(['pip', 'install', dep], check=True)

def create_spec_file():
    """Generate and customize the PyInstaller spec file."""
    spec_content = """
from kivy_deps import sdl2, glew
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('src/ui/*', 'src/ui'),
        ('src/logic/*', 'src/logic'),
        ('outputs/stems', 'outputs/stems'),
        ('outputs/exports', 'outputs/exports')
    ],
    hiddenimports=['pydub', 'librosa', 'spleeter'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EchoSplit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[sdl2.dep_bins, glew.dep_bins],
    strip=False,
    upx=True,
    name='EchoSplit'
)
"""
    if platform.system() == "Darwin":
        spec_content += """
app = BUNDLE(
    coll,
    name='EchoSplit.app',
    icon=None,
    bundle_identifier=None
)
"""
    with open("EchoSplit.spec", "w") as f:
        f.write(spec_content)

def build_app():
    """Run PyInstaller to build the executable."""
    subprocess.run(['pyinstaller', 'EchoSplit.spec'], check=True)
    print("Build complete. Executable is in dist/EchoSplit/")

def main():
    """Main function to package EchoSplit."""
    print("Packaging EchoSplit into a clickable app...")
    try:
        ensure_dependencies()
        create_spec_file()
        build_app()
    except Exception as e:
        print(f"Error during packaging: {str(e)}")

if __name__ == "__main__":
    main()