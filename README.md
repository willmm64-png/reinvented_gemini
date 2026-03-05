# Gemini Desktop (Python + CustomTkinter)

A native-style Gemini desktop client for Windows with streaming chat, model selection, persistent conversation history, personas, and configurable generation settings.

## Features

- First-run API key setup and secure key storage via `keyring`
- Multi-turn streaming chat with Gemini models
- SQLite conversation persistence in `%LOCALAPPDATA%\Gemini Desktop\conversations.db`
- Sidebar conversation navigation + deletion
- System prompt panel + named persona saving
- Message input with Enter/Shift+Enter behavior and file attachment
- Settings panel for temperature, max tokens, top-p/top-k, theme, font size, data export/clear
- Build artifacts for PyInstaller and Inno Setup installer

## Project structure

- `main.py`: app entrypoint
- `app/`: UI components and main window logic
- `core/`: Gemini API client, database, key storage, markdown helpers
- `assets/styles`: theme token definitions
- `build.spec`: PyInstaller spec
- `installer.iss`: Inno Setup script

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Gemini API key

1. Get your key from Google AI Studio.
2. Launch the app and paste the key in the first-run prompt.
3. The key is stored in your OS keychain using `keyring`.

## Build for Windows

```bat
REM 1. Build the .exe
pyinstaller build.spec

REM 2. Compile the installer (requires Inno Setup 6 in PATH)
iscc installer.iss

REM Output: dist\installer\GeminiDesktop-Setup-1.0.0.exe
```

## Notes

- App data is stored per user in `%LOCALAPPDATA%\Gemini Desktop\`.
- On uninstall, installer prompts before deleting saved conversations/settings.
