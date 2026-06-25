import click
import time
from firewall.firewall import PersonalFirewall

fw_instance = None

@click.group()
def cli():
    """AI-Powered Stateful Personal Firewall CLI"""
    pass

@cli.command()
@click.option('--config', default='firewall/config/rules.json', help='Path to rules config file')
@click.option('--db', default='sqlite:///firewall.db', help='Path to database')
def start(config, db):
    """Start the firewall"""
    global fw_instance
    fw_instance = PersonalFirewall(config_path=config, db_path=db)
    fw_instance.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        fw_instance.stop()

@cli.command()
def status():
    """Show firewall status and statistics"""
    # Note: In a real system, CLI would query a running daemon via IPC/socket.
    # For this MVP, if we run status it would start a new instance.
    # To truly show live status, we would need the FastAPI backend (Tier 2).
    click.echo("Status command requires the firewall daemon or API to be running.")
    click.echo("Please use the dashboard for live stats or check database for offline logs.")

@cli.command()
@click.option('--severity', default=None, help='Filter alerts by severity')
def alerts(severity):
    """Show recent alerts"""
    from firewall.database import FirewallDatabase
    db = FirewallDatabase()
    results = db.query_alerts(severity=severity, limit=20)
    for r in results:
        click.echo(f"[{r['timestamp']}] {r['severity'].upper()} - {r['alert_type']}: {r['description']}")

if __name__ == '__main__':
    cli()
