from pathlib import Path
import re


FRONTEND_DIR = Path(__file__).parent
PAGES = {
    "index.html",
    "rules.html",
    "logs.html",
    "analytics.html",
    "settings.html",
}


def test_all_dashboard_pages_and_shared_assets_exist():
    for page_name in PAGES:
        page = FRONTEND_DIR / page_name
        html = page.read_text(encoding="utf-8")
        assert 'href="style.css"' in html

        for target in re.findall(r'href="([^"]+\.html)"', html):
            assert target in PAGES
            assert (FRONTEND_DIR / target).is_file()


def test_dashboard_script_is_loaded_by_main_page():
    html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    assert '<script src="app.js"></script>' in html
    assert (FRONTEND_DIR / "app.js").is_file()


if __name__ == "__main__":
    test_all_dashboard_pages_and_shared_assets_exist()
    test_dashboard_script_is_loaded_by_main_page()