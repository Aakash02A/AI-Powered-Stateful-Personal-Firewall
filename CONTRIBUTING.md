# Contributing to AI-Powered Stateful Personal Firewall

Thank you for your interest in contributing to this open-source firewall project! Contributions from developers, security researchers, and enthusiasts are welcome to help improve security, performance, documentation, and new features.

## Code of Conduct
Please be respectful and constructive in all interactions. Discriminatory or harassing behavior will not be tolerated.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aakash02A/AI-Powered-Stateful-Personal-Firewall.git
   cd AI-Powered-Stateful-Personal-Firewall
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Initialize Database:**
   ```bash
   python -m alembic upgrade head
   ```

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Write clean, documented code and include type hints where applicable.
3. Ensure all tests pass: `pytest tests/`
4. Make sure your code is formatted with Black and passes Flake8 (pre-commit handles this).
5. Open a Pull Request detailing the problem solved or the feature added.
6. The CI pipeline will automatically run CodeQL, Bandit, Pip-Audit, and Pytest. Your PR must pass all checks before review.

## Architecture
Before making major changes, please review the `ARCHITECTURE.md` file to understand the multi-threaded queue-based design.

Thank you for contributing!
