import requests
import os
import subprocess
import threading
import logging
from packaging import version

GITHUB_REPO = "Aakash02A/AI-Powered-Stateful-Personal-Firewall"
CURRENT_VERSION = "1.1.0"

def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        latest_version = data.get("tag_name", "").lstrip("v")
        
        if latest_version and version.parse(latest_version) > version.parse(CURRENT_VERSION):
            # Find the installer asset
            assets = data.get("assets", [])
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    return latest_version, download_url
    except Exception as e:
        logging.error(f"Update check failed: {e}")
    return None, None

def download_and_install_update(download_url):
    try:
        temp_dir = os.environ.get("TEMP", "C:\\Temp")
        installer_path = os.path.join(temp_dir, "AIFirewall_Update.exe")
        
        logging.info(f"Downloading update from {download_url}...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(installer_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logging.info("Update downloaded. Executing installer...")
        # Run installer silently. Inno Setup supports /SILENT or /VERYSILENT
        subprocess.Popen([installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        
        # We can exit the tray app here, as the installer will stop the service, update files, and restart things.
        os._exit(0)
    except Exception as e:
        logging.error(f"Failed to download or install update: {e}")

def run_update_check_background():
    latest_version, download_url = check_for_updates()
    if latest_version and download_url:
        logging.info(f"New version {latest_version} found. Downloading...")
        download_and_install_update(download_url)
    else:
        logging.info("No updates found.")

def start_background_updater():
    t = threading.Thread(target=run_update_check_background, daemon=True)
    t.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_background_updater()
