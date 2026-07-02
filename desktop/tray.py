import os
import sys
import threading
import pystray
from PIL import Image, ImageDraw
import subprocess

def create_image():
    # Generate a simple shield icon using PIL
    image = Image.new('RGB', (64, 64), color=(5, 5, 8))
    draw = ImageDraw.Draw(image)
    # Simple shield
    draw.polygon([(32, 10), (54, 20), (54, 40), (32, 60), (10, 40), (10, 20)], fill=(0, 240, 255))
    return image

def open_dashboard(icon, item):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "dashboard_app.py")
    
    # If compiled via pyinstaller, we run the executable, otherwise run the script
    if getattr(sys, 'frozen', False):
        dashboard_exe = os.path.join(script_dir, "ai_firewall_dashboard.exe")
        if os.path.exists(dashboard_exe):
            subprocess.Popen([dashboard_exe], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([sys.executable, dashboard_path], creationflags=subprocess.CREATE_NO_WINDOW)

def check_updates_action(icon, item):
    from updater import run_update_check_background
    import threading
    t = threading.Thread(target=run_update_check_background, daemon=True)
    t.start()

def exit_action(icon, item):
    icon.stop()

def setup_tray():
    image = create_image()
    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard", open_dashboard, default=True),
        pystray.MenuItem("Check for Updates", check_updates_action),
        pystray.MenuItem("Exit", exit_action)
    )
    icon = pystray.Icon("AIFirewall", image, "AI-Powered Firewall", menu)
    
    # Start auto updater in background
    from updater import start_background_updater
    start_background_updater()
    
    icon.run()

if __name__ == "__main__":
    setup_tray()
