# ─── Eden Music Scene Launcher ───
# Run this in PowerShell (right-click > Run with PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "`n🎶  Initializing Eden Music Scene environment...`n"

# 1. Go to project root
Set-Location "C:\EdenOS_Origin\98_GitHub_Downloads\Eden_Music_Scene"

# 3. Upgrade pip & install likely dependencies
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install numpy sounddevice soundfile pygame spleeter pyyaml requests pytest tqdm whisper transformers torch pyttsx3

# 4. Optional: environment variables
$env:PYTHONPATH = (Get-Location).Path
$env:EDEN_MUSIC_HOME = (Get-Location).Path

# 5. Launch main program (EchoSplit core)
Write-Host "`n🚀  Launching EchoSplit main engine...`n"
python ".\EchoSplit\04_src\00_core\main.py"

Write-Host "`n✅  Program exited.  Virtual environment remains active.`n"
