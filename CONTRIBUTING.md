# Contributing to VoxaCommunications Registry

Thank you for your interest in contributing to the VoxaCommunications Registry project! This document provides guidelines and instructions for contributing to this security-critical component of the VoxaCommunications network.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Security Considerations](#security-considerations)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Code Review Process](#code-review-process)
- [Documentation](#documentation)

## Code of Conduct

All contributors are expected to adhere to our code of conduct. Please be just be respectful and professional.

## Security Considerations

As the Registry is a critical security component of the VoxaCommunications network:

- **NEVER** commit secrets, private keys, or credentials
- Report security vulnerabilities according to our [SECURITY.md](SECURITY.md) process
- All security-related changes require additional review
- Consider security implications of all code changes

## Getting Started

1. Fork the repository
2. Clone your fork to your local development environment
3. Set up the development environment as described in [SETUP.md](SETUP.md)
4. Create a feature branch from the `dev` branch

## Development Environment

To set up your development environment:

```bash
# Clone your fork
git clone https://github.com/Voxa-Communications/VoxaCommunications-Registry.git
cd VoxaCommunications-Registry

# Set up the development container
./build.sh

# Install dependencies
pip install -r requirements.txt

```

## Coding Standards

We enforce the following standards:

- Follow PEP 8 Python style guidelines
- Use type hints for all functions and methods
- Document all public API functions with docstrings
- Keep line length to a maximum of 100 characters
- Ensure all code passes flake8 and mypy checks

You can check your code with:

```bash
# Run flake8
flake8 src tests

# Run mypy type checking
mypy src tests
```

## Testing Requirements

All contributions must include appropriate tests:

- New features must include unit tests
- Bug fixes must include regression tests
- Maintain or improve code coverage percentage
- All tests must pass before submitting a pull request

Run tests with:

```bash
# Run unit tests
pytest

# Check test coverage
pytest --cov=src
```

## Pull Request Process

1. Update the documentation to reflect any changes
2. Add or update tests to cover your changes
3. Ensure all tests pass and code quality checks succeed
4. Rebase your branch on the latest `develop` branch
5. Submit a pull request to the `develop` branch

Pull request titles should follow the format:
`[TYPE]: Brief description of change`

Where `TYPE` is one of:
- `FEATURE`: New functionality
- `FIX`: Bug fixes
- `DOCS`: Documentation changes
- `REFACTOR`: Code improvements without functional changes
- `TEST`: Adding or improving tests
- `SECURITY`: Security-related improvements

## Code Review Process

All submissions undergo a thorough review process:

1. Automated CI checks for tests, linting, and type checking
2. Initial review by at least one maintainer
3. Security review for any security-impacting changes
4. Changes may be requested before approval
5. Once approved, a maintainer will merge the pull request

## Documentation

Documentation is critical for this project:

- Update README.md if necessary
- Document all most added features, APIs, and configuration options
- Keep code comments clear and up-to-date
- Consider adding examples for complex features

---

Thank you for contributing to the VoxaCommunications Registry project!