import click
import time
import json
from firewall.firewall import PersonalFirewall

fw_instance = None

@click.group()
def cli():
    """AI-Powered Stateful Personal Firewall CLI"""
    pass

@cli.command()
@click.option('--config', default='firewall/config/rules.json', help='Path to rules config file')
@click.option('--db', default='sqlite:///data/firewall.db', help='Path to database')
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

@cli.command(name="start-api")
@click.option('--config', default='firewall/config/rules.json', help='Path to rules config file')
@click.option('--db', default='sqlite:///data/firewall.db', help='Path to database')
@click.option('--host', default='127.0.0.1', help='API Host')
@click.option('--port', default=8000, help='API Port')
def start_api(config, db, host, port):
    """Start the firewall and the FastAPI server"""
    import uvicorn
    global fw_instance
    fw_instance = PersonalFirewall(config_path=config, db_path=db)
    fw_instance.start()
    
    click.echo(f"[*] Starting FastAPI server on {host}:{port}")
    try:
        uvicorn.run("api.main:app", host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        pass
    finally:
        fw_instance.stop()

@cli.command()
def stop():
    """Stop the firewall (if running in background)"""
    # MVP version assumes running in foreground via `start`. 
    # To truly stop a background daemon, IPC or a pid file is required.
    click.echo("To stop the firewall, send SIGINT (Ctrl+C) to the terminal running `start`.")

@cli.command()
def status():
    """Show firewall status and statistics"""
    # Again, requires IPC to get live stats from the daemon.
    # For MVP, we point the user to the dashboard or logs.
    click.echo("Status command requires the firewall daemon or API to be running.")
    click.echo("Please use the dashboard (Tier 2) for live stats or check database for offline logs.")

@cli.command()
@click.option('--config', default='firewall/config/rules.json', help='Path to rules config file')
def rules(config):
    """List current firewall rules"""
    try:
        with open(config, 'r') as f:
            data = json.load(f)
            click.echo(f"{'Rule ID':<25} | {'Action':<8} | {'Protocol':<8} | {'Direction':<10} | {'Description'}")
            click.echo("-" * 80)
            for r in data.get("rules", []):
                click.echo(f"{r.get('rule_id', ''):<25} | {r.get('action', ''):<8} | {r.get('protocol', ''):<8} | {r.get('direction', ''):<10} | {r.get('description', '')}")
    except FileNotFoundError:
        click.echo(f"Config file not found: {config}")

@cli.command()
@click.option('--severity', default=None, help='Filter alerts by severity')
def alerts(severity):
    """Show recent alerts"""
    from firewall.database import FirewallDatabase
    db = FirewallDatabase()
    results = db.query_alerts(severity=severity, limit=20)
    for r in results:
        click.echo(f"[{r['timestamp']}] {r['severity'].upper()} - {r['alert_type']}: {r['description']}")

@cli.command()
@click.option('--limit', default=10, help='Number of recent connections to show')
def queries(limit):
    """Query recent connections from database"""
    from firewall.database import FirewallDatabase
    db = FirewallDatabase()
    results = db.query_connections(limit=limit)
    click.echo(f"{'State':<12} | {'Src':<20} | {'Dst':<20} | {'Protocol'}")
    click.echo("-" * 70)
    for r in results:
        src = f"{r['src_ip']}:{r['src_port']}"
        dst = f"{r['dst_ip']}:{r['dst_port']}"
        click.echo(f"{r['state']:<12} | {src:<20} | {dst:<20} | {r['protocol']}")

if __name__ == '__main__':
    cli()
