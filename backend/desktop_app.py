import os
import sys
import threading
import webbrowser
import logging
import time

import uvicorn
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# Ensure we're in the right directory
if getattr(sys, 'frozen', False):
    # PyInstaller execution
    os.chdir(sys._MEIPASS)
else:
    # Normal python execution
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("desktop_app")

# Global reference to firewall for shutdown
backend_server = None
fw_thread = None

def create_icon():
    # Generate a simple shield icon using Pillow
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.polygon([(32, 5), (60, 20), (60, 50), (32, 60), (4, 50), (4, 20)], fill=(0, 120, 215))
    dc.polygon([(32, 12), (54, 25), (54, 46), (32, 53), (10, 46), (10, 25)], fill=(0, 160, 240))
    return image

def start_backend():
    global backend_server
    try:
        from api.config import settings
        from firewall.cli import fw_instance, setup_firewall
        
        # Start Firewall daemon
        logger.info("Starting Firewall Daemon in desktop app...")
        setup_firewall()
        if fw_instance:
            fw_instance.start()
            
        # Start API using uvicorn
        logger.info("Starting FastAPI backend...")
        # Configure uvicorn
        config = uvicorn.Config(
            "api.main:app", 
            host=settings.HOST, 
            port=settings.PORT, 
            log_level="warning",
            loop="asyncio"
        )
        backend_server = uvicorn.Server(config)
        backend_server.run()
    except Exception as e:
        logger.error(f"Backend crashed: {e}")

def open_dashboard(icon, item):
    webbrowser.open("http://127.0.0.1:8000")

def quit_app(icon, item):
    icon.stop()
    logger.info("Shutting down Firewall and Backend...")
    
    # Stop firewall instance
    from firewall.cli import fw_instance
    if fw_instance:
        fw_instance.stop()
        
    # Stop uvicorn server
    global backend_server
    if backend_server:
        backend_server.should_exit = True
    
    # Allow time to shutdown gracefully
    time.sleep(2)
    os._exit(0)

def main():
    # Check for Admin privileges on Windows (required for pydivert)
    if sys.platform == "win32":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Privilege Error", "AI Personal Firewall requires Administrator privileges to capture network traffic.\n\nPlease right-click the executable and select 'Run as Administrator'.")
            sys.exit(1)

    # Start the backend in a separate thread
    global fw_thread
    fw_thread = threading.Thread(target=start_backend, daemon=True)
    fw_thread.start()

    # Create system tray icon
    image = create_icon()
    menu = pystray.Menu(
        item('Open Dashboard', open_dashboard, default=True),
        item('Quit', quit_app)
    )
    icon = pystray.Icon("AIFirewall", image, "AI Personal Firewall", menu)
    
    # Run the system tray loop (this blocks until quit_app is called)
    icon.run()

if __name__ == "__main__":
    main()
