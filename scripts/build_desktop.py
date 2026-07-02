import os
import subprocess
import sys
import shutil

def run_cmd(cmd, cwd=None):
    print(f"[*] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"[!] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    frontend_dir = os.path.join(root_dir, 'frontend')
    
    print("=== Phase 1: Build Frontend ===")
    # npm is handled via cmd on windows
    run_cmd(['cmd', '/c', 'npm', 'run', 'build'], cwd=frontend_dir)
    
    print("=== Phase 2: Build Executables ===")
    # Build Service
    run_cmd([
        sys.executable, '-m', 'PyInstaller',
        '--name', 'firewall_service',
        '--hidden-import', 'win32timezone',
        '--hidden-import', 'uvicorn.logging',
        '--hidden-import', 'uvicorn.loops',
        '--hidden-import', 'uvicorn.loops.auto',
        '--hidden-import', 'uvicorn.protocols',
        '--hidden-import', 'uvicorn.protocols.http',
        '--hidden-import', 'uvicorn.protocols.http.auto',
        '--hidden-import', 'uvicorn.protocols.websockets',
        '--hidden-import', 'uvicorn.protocols.websockets.auto',
        '--hidden-import', 'uvicorn.lifespan',
        '--hidden-import', 'uvicorn.lifespan.on',
        '--hidden-import', 'uvicorn.lifespan.off',
        '--hidden-import', 'scipy',
        '--hidden-import', 'sklearn',
        '--collect-all', 'pydivert',
        '--onedir',
        'desktop/service.py'
    ], cwd=root_dir)

    # Build Tray
    run_cmd([
        sys.executable, '-m', 'PyInstaller',
        '--name', 'ai_firewall_tray',
        '--windowed',
        '--icon', 'NONE',
        '--onedir',
        'desktop/tray.py'
    ], cwd=root_dir)
    
    # Build Dashboard App
    run_cmd([
        sys.executable, '-m', 'PyInstaller',
        '--name', 'ai_firewall_dashboard',
        '--windowed',
        '--onedir',
        'desktop/dashboard_app.py'
    ], cwd=root_dir)

    print("=== Phase 3: Assembly ===")
    dist_dir = os.path.join(root_dir, 'dist', 'AIFirewall')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Merge pyinstaller outputs into one dist dir to save space or just copy them
    shutil.copytree(os.path.join(root_dir, 'dist', 'firewall_service'), dist_dir, dirs_exist_ok=True)
    shutil.copytree(os.path.join(root_dir, 'dist', 'ai_firewall_tray'), dist_dir, dirs_exist_ok=True)
    shutil.copytree(os.path.join(root_dir, 'dist', 'ai_firewall_dashboard'), dist_dir, dirs_exist_ok=True)
    
    # Copy frontend
    shutil.copytree(os.path.join(frontend_dir, 'dist'), os.path.join(dist_dir, 'frontend', 'dist'))
    
    # Copy models and config
    shutil.copytree(os.path.join(root_dir, 'firewall', 'config'), os.path.join(dist_dir, 'firewall', 'config'))
    if os.path.exists(os.path.join(root_dir, 'models')):
        shutil.copytree(os.path.join(root_dir, 'models'), os.path.join(dist_dir, 'models'))
    
    print("[+] Desktop Build Complete. You can now run Inno Setup on installer/setup.iss")

if __name__ == "__main__":
    main()
