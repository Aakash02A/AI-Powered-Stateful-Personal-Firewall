$ErrorActionPreference = "Stop"

Write-Host "Building React Frontend..."
cd frontend
npm install
npm run build
cd ..

Write-Host "Installing Python requirements..."
pip install -r requirements.txt

Write-Host "Packaging with PyInstaller..."
pyinstaller --name "AIFirewall" --onefile --windowed `
    --add-data "frontend/dist;frontend/dist" `
    --add-data "ml/models;ml/models" `
    --add-data "firewall/config/rules.json;firewall/config" `
    desktop_app.py

Write-Host "Build complete! Executable is located in dist/AIFirewall.exe"
