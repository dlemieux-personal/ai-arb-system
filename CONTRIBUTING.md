# Contributing to AI-ARB

First off, thank you for considering contributing to AI-ARB! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead**
- **Include screenshots and animated GIFs if needed**
- **Include your environment details** (OS, Python version, CrewAI version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain the motivation behind this change**

### Pull Requests

- Fill in the required template
- Follow the Python **PEP 8** style guide
- Include appropriate test cases
- Update documentation as needed
- End all files with a newline

## Development Process

### Setting Up Your Development Environment

1. Fork the repository and clone your fork
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black pylint mypy bandit
   ```

### Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Description of changes"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
4. Submit a pull request to the `main` branch

### Code Style

This project uses:

- **Black** for code formatting:
  ```bash
  black src/ tests/ --line-length=100
  ```

- **Pylint** for linting:
  ```bash
  pylint src/ --disable=C0111,C0103
  ```

- **mypy** for type checking:
  ```bash
  mypy src/ --ignore-missing-imports
  ```

Run all checks before submitting a PR:
```bash
black src/ tests/
pylint src/
mypy src/
pytest tests/ -v
```

### Testing

All new features should have corresponding tests. Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_specific.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Documentation

- Update README.md if your changes affect user-facing functionality
- Update SOFTWARE_DESIGN_DOCUMENT.md for architectural changes
- Add docstrings to all public functions and classes
- Include examples in docstrings for complex functions

## Project Structure Guidelines

When adding new features:

1. **New agents**: Add to `src/agents/definitions/` with system prompts in `src/agents/system_prompts/`
2. **New tools**: Add to `src/tools/` with proper tool decorators
3. **Tests**: Add corresponding tests in `tests/` with same directory structure
4. **Config**: Add config options to `config/` with reasonable defaults

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Fix null pointer exception in recommendation crew

- Handle None values in action item processing
- Add defensive checks for effort estimation
- Add test cases for edge conditions

Fixes #123
```

## Pull Request Process

1. Ensure all tests pass and code quality checks succeed
2. Update the README.md and SOFTWARE_DESIGN_DOCUMENT.md with details of changes
3. Increase version numbers in pyproject.toml following [Semantic Versioning](https://semver.org/)
4. Request review from maintainers
5. Address any review feedback
6. Once approved, maintainers will merge your PR

## Review Process

PRs will be reviewed for:

- **Correctness**: Does the code do what it claims?
- **Quality**: Is the code well-written and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the change documented?
- **Performance**: Does it introduce any performance issues?
- **Security**: Are there any security concerns?

## Additional Notes

### Development Tips

- Run tests frequently during development
- Use meaningful variable and function names
- Keep functions focused and small
- Add comments for complex logic
- Avoid hardcoding values—use configuration

### Common Issues

**Import errors**: Make sure your virtual environment is activated and dependencies are installed
**Test failures**: Check that you have all required environment variables in `.env`
**Neo4j connection failures**: Ensure Neo4j instance is running (or tests will skip Neo4j-specific tests)

## Recognition

Contributors will be recognized in:
- Project README
- Release notes for their PR
- GitHub contributors page

## Questions?

Feel free to open a GitHub issue labeled `question` or start a discussion in GitHub Discussions.

---

Thank you for contributing to AI-ARB! 🎉
