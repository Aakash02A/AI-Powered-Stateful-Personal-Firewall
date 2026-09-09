# Beta Testing Guide - AI-Powered Stateful Personal Firewall v1.1.0

Thank you for participating in the v1.1.0 Closed Beta! This guide will help you install the firewall, test its features, and provide valuable feedback to our team.

## 1. Installation Instructions
1. Navigate to the GitHub Releases page and download `AIFirewall_Setup_v1.1.0.exe`.
2. Double-click the installer.
   > **Note on Windows SmartScreen:** Because this beta is not yet signed with an EV Code Signing certificate, Windows may warn you about an "unrecognized app". Click **More info** -> **Run anyway**.
3. Follow the installation wizard. Ensure you install it with Administrator privileges, as it installs a native Windows Filtering Platform (WFP) driver.

## 2. Verifying Protection
Once installed, the application should start automatically.
1. Check your Windows System Tray (bottom right corner, near the clock) for the **AI Firewall shield icon**.
2. Right-click the icon and select **Open Dashboard**.
3. Verify that the **Global Status** shows as `Protected`.
4. Navigate to the **Network Flow** tab and verify that active connections (e.g., your web browser) are being logged.

## 3. How to Report Bugs
If you encounter a crash, false positive, or UI glitch, please open a GitHub Issue with the following information:
* Your Windows version (e.g., Windows 11 Pro 23H2).
* Steps to reproduce the issue.
* Expected behavior vs. Actual behavior.

## 4. Collecting Logs
When reporting issues, please attach the service logs. You can find them safely stored on your local disk at:
`C:\ProgramData\AIFirewall\service.log`
*(Note: Please review the log for any personal information before uploading).*

## 5. Submitting Feedback
For feature requests or general feedback on the new Futuristic UI (FUI) dashboard, please use the GitHub Discussions tab!
