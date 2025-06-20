# Contributing to ScrapeMaster Intelligence 🕷️

Thank you for your interest in contributing to ScrapeMaster Intelligence! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with code changes
- **Documentation**: Improve or add documentation
- **Testing**: Help test the application and report issues
- **Translation**: Help translate the application to other languages

### Before You Start

1. **Check Existing Issues**: Search existing issues to avoid duplicates
2. **Read Documentation**: Familiarize yourself with the project structure
3. **Set Up Development Environment**: Follow the installation guide in README.md

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip
- Virtual environment tool

### Local Development

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/scrapemaster-intelligence.git
   cd scrapemaster-intelligence
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set Up Environment**
   ```bash
   cp config/env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python -c "from src.core.database import DatabaseManager; DatabaseManager().initialize_database()"
   ```

## 📝 Code Style Guidelines

### Python Code Style

We follow PEP 8 style guidelines with some modifications:

- **Line Length**: Maximum 88 characters (Black formatter default)
- **Imports**: Grouped and ordered according to PEP 8
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for function parameters and return values

### Code Formatting

We use automated tools to maintain code quality:

```bash
# Format code with Black
black src/

# Sort imports with isort
isort src/

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

### Example Code Style

```python
"""Module docstring describing the purpose of this module."""

from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


def scrape_website(url: str, selectors: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Scrape data from a website using provided selectors.
    
    Args:
        url: The target URL to scrape
        selectors: Dictionary of CSS selectors for data extraction
        
    Returns:
        List of dictionaries containing scraped data
        
    Raises:
        ValueError: If URL is invalid
        ConnectionError: If connection fails
    """
    if not url:
        raise ValueError("URL cannot be empty")
    
    # Implementation here
    return []
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_scraper.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for all new features
- Aim for at least 80% code coverage
- Use descriptive test names
- Group related tests in classes
- Mock external dependencies

### Example Test

```python
"""Tests for the scraper module."""

import pytest
from unittest.mock import Mock, patch
from src.core.scraper import WebScraper


class TestWebScraper:
    """Test cases for WebScraper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scraper = WebScraper()
    
    def test_scrape_valid_url(self):
        """Test scraping a valid URL."""
        with patch('requests.get') as mock_get:
            mock_get.return_value.content = '<html><body><h1>Test</h1></body></html>'
            result = self.scraper.scrape('https://example.com')
            assert result is not None
            assert 'Test' in result
    
    def test_scrape_invalid_url(self):
        """Test scraping an invalid URL raises exception."""
        with pytest.raises(ValueError):
            self.scraper.scrape('')
```

## 🔄 Pull Request Process

### Creating a Pull Request

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new scraping feature"
   ```

4. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template

### Pull Request Guidelines

- **Title**: Use conventional commit format (e.g., "feat: add proxy support")
- **Description**: Clearly describe what the PR does and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation
- **Screenshots**: Include screenshots for UI changes

### Commit Message Format

We use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(scraper): add proxy rotation support
fix(database): resolve connection timeout issue
docs(readme): update installation instructions
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues for duplicates
2. Try to reproduce the issue
3. Check if it's a configuration issue

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 12.0]
- Python Version: [e.g. 3.9.7]
- ScrapeMaster Version: [e.g. 1.0.0]

**Additional Context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Why this feature would be useful.

**Proposed Solution**
How you think this could be implemented.

**Alternatives Considered**
Any alternative solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

## 📚 Documentation

### Documentation Guidelines

- Write clear, concise documentation
- Include code examples
- Keep documentation up to date
- Use proper markdown formatting
- Include screenshots for UI features

### Documentation Structure

```
docs/
├── api/              # API documentation
├── guides/           # User guides
├── development/      # Developer documentation
└── deployment/       # Deployment guides
```

## 🏷️ Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version is bumped
- [ ] Release notes are written

## 🆘 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions
- **Discord**: For real-time chat (if available)

### Before Asking for Help

1. Check the documentation
2. Search existing issues
3. Try to reproduce the problem
4. Provide detailed information

## 🏆 Recognition

Contributors will be recognized in:

- Project README
- Release notes
- Contributor hall of fame (if applicable)

## 📄 License

By contributing to ScrapeMaster Intelligence, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ScrapeMaster Intelligence! 🕷️ 