import webview
import time
import requests
import sys

def check_server():
    # Wait for the API server to be reachable before showing the window
    for _ in range(10):
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/health")
            if r.status_code == 200:
                return True
        except:
            time.sleep(1)
    return False

if __name__ == '__main__':
    # Try to ensure the server is up
    check_server()
    
    # Create the webview window
    webview.create_window(
        'AI Firewall Dashboard', 
        'http://127.0.0.1:8000/', 
        width=1200, 
        height=800,
        min_size=(800, 600),
        background_color='#050508'
    )
    
    webview.start(private_mode=False)
