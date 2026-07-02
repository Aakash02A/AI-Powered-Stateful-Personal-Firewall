# Windows Desktop Edition Installation Guide

Welcome to the **AI-Powered Stateful Personal Firewall (v1.1.0)**! We have upgraded the firewall from a CLI tool to a consumer-ready Windows Desktop Application.

## System Requirements
- Windows 10 or Windows 11 (64-bit)
- Administrator privileges (required for the Windows Filtering Platform driver)

## Installation Steps

1. **Download the Installer**
   Navigate to the [GitHub Releases](https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall/releases) page and download `AIFirewall_Setup_v1.1.0.exe`.

2. **Run the Installer**
   Double-click the downloaded `.exe` file.
   *Note: Windows SmartScreen may warn you about an unrecognized app. Click "More info" -> "Run anyway".*

3. **Follow the Setup Wizard**
   - Accept the license agreement.
   - Choose the installation directory (default is `C:\Program Files\AIFirewall`).
   - The installer will automatically:
     - Install the `AIFirewallService` Windows Service.
     - Configure the WFP packet filtering drivers natively.
     - Add the System Tray app to your startup programs.
     - Create desktop shortcuts.

4. **Launch the Application**
   - The firewall service starts automatically in the background.
   - Check your System Tray (bottom right of your screen) for the **AI Firewall shield icon**.
   - Right-click the tray icon and select **Open Dashboard** to view live traffic and alerts.

## Upgrading

The firewall features an **Auto-Updater**. 
To manually check for updates:
1. Right-click the AI Firewall icon in your System Tray.
2. Select **Check for Updates**.
3. If an update is found, it will automatically download and install in the background silently. Your service will restart automatically.

## Uninstallation

To completely remove the firewall:
1. Open Windows **Settings** > **Apps** > **Installed apps**.
2. Search for "AI-Powered Personal Firewall" and click **Uninstall**.
3. The uninstaller will safely stop and unregister the background service and remove all files.

## Troubleshooting

- **Tray icon does not appear on reboot**: Ensure `ai_firewall_tray.exe` is enabled in Task Manager -> Startup tab.
- **No traffic appearing in Dashboard**: Ensure the service is running. Open `services.msc` via the Windows Run dialog (`Win + R`), locate `AIFirewallService`, and ensure its status is **Running**.
- **Permission Errors**: Ensure you installed the application as an Administrator.
