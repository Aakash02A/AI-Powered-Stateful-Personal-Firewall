import pytest
from click.testing import CliRunner

from firewall.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_status(runner):
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "Status command requires the firewall daemon" in result.output


def test_cli_stop(runner):
    result = runner.invoke(cli, ["stop"])
    assert result.exit_code == 0
    assert "To stop the firewall, send SIGINT" in result.output


def test_cli_rules(runner, tmp_path):
    config_file = tmp_path / "rules.json"
    config_file.write_text('{"rules": [{"rule_id": "test_rule", "action": "allow"}]}')

    result = runner.invoke(cli, ["rules", "--config", str(config_file)])
    assert result.exit_code == 0
    assert "test_rule" in result.output


def test_cli_alerts(runner, tmp_path):
    import unittest.mock
    from datetime import datetime

    from firewall.database import FirewallDatabase
    from firewall.models import Alert

    db = FirewallDatabase("sqlite:///:memory:")
    db.log_alert(
        Alert(timestamp=datetime.now(), alert_type="test_cli_alert", severity="low")
    )

    with unittest.mock.patch("firewall.database.FirewallDatabase", return_value=db):
        result = runner.invoke(cli, ["alerts"])
        assert result.exit_code == 0
        assert "test_cli_alert" in result.output


def test_cli_queries(runner):
    import unittest.mock

    from firewall.database import FirewallDatabase

    db = FirewallDatabase("sqlite:///:memory:")

    with unittest.mock.patch("firewall.database.FirewallDatabase", return_value=db):
        result = runner.invoke(cli, ["queries", "--limit", "10"])
        assert result.exit_code == 0
        assert "Src" in result.output
