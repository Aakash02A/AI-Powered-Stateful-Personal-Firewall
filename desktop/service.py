import sys
import os
import time
import threading
import servicemanager
import win32serviceutil
import win32service
import win32event
import logging

# Ensure the parent directory is in sys.path so we can import 'api' and 'firewall'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
from firewall.firewall import PersonalFirewall

class FirewallService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AIFirewallService"
    _svc_display_name_ = "AI-Powered Stateful Personal Firewall"
    _svc_description_ = "Background service for packet inspection, IDS, and API."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.fw_instance = None
        self.server = None
        self.server_thread = None

        # Basic logging for the service
        log_path = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "AIFirewall", "service.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logging.basicConfig(filename=log_path, level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info("Service initialized.")

    def SvcStop(self):
        logging.info("Stop signal received.")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)
        
        # Stop Uvicorn if it's running
        if self.server:
            self.server.should_exit = True
            
        # Stop Firewall
        if self.fw_instance:
            self.fw_instance.stop()

    def SvcDoRun(self):
        logging.info("Service starting.")
        try:
            self.start_firewall_and_api()
        except Exception as e:
            logging.error(f"Service failed to start: {e}", exc_info=True)
            self.SvcStop()
        
        # Wait until stop event is signaled
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        logging.info("Service stopped.")

    def run_uvicorn(self):
        config = uvicorn.Config("api.main:app", host="127.0.0.1", port=8000, log_level="info")
        self.server = uvicorn.Server(config)
        self.server.run()

    def start_firewall_and_api(self):
        logging.info("Starting Firewall instance...")
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'firewall', 'config', 'rules.json'))
        db_path = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'firewall.db'))
        
        # Ensure data dir exists
        os.makedirs(os.path.dirname(db_path.replace("sqlite:///", "")), exist_ok=True)
        
        self.fw_instance = PersonalFirewall(config_path=config_path, db_path=db_path)
        self.fw_instance.start()
        
        logging.info("Starting API server in background thread...")
        self.server_thread = threading.Thread(target=self.run_uvicorn, daemon=True)
        self.server_thread.start()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FirewallService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FirewallService)
