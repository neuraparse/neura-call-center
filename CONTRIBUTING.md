# Contributing to Neura Call Center

Thank you for your interest in contributing to Neura Call Center! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/neuraparse/neura-call-center.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `make test`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Install dependencies
make install
make dev

# Start services
make docker-up

# Run migrations
make migrate

# Run the application
make run
```

## Code Style

We use:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing

Before committing, run:

```bash
make lint
make format
make test
```

## Commit Messages

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Example: `feat: add support for Vonage telephony provider`

## Pull Request Guidelines

1. **Description**: Clearly describe what your PR does
2. **Tests**: Add tests for new features
3. **Documentation**: Update docs if needed
4. **Breaking Changes**: Clearly mark breaking changes
5. **Small PRs**: Keep PRs focused and small

## Adding New Providers

### STT Provider

1. Create `apps/providers/stt/your_provider.py`
2. Implement `STTProvider` interface
3. Add to factory in `apps/providers/stt/factory.py`
4. Add configuration in `apps/core/config.py`
5. Add tests in `tests/providers/test_stt.py`

### TTS Provider

1. Create `apps/providers/tts/your_provider.py`
2. Implement `TTSProvider` interface
3. Add to factory in `apps/providers/tts/factory.py`
4. Add configuration in `apps/core/config.py`
5. Add tests in `tests/providers/test_tts.py`

### Telephony Provider

1. Create `apps/providers/telephony/your_provider.py`
2. Implement `TelephonyProvider` interface
3. Add to factory in `apps/providers/telephony/factory.py`
4. Add configuration in `apps/core/config.py`
5. Add tests in `tests/providers/test_telephony.py`

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_check
```

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Suggestions for improvements

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

