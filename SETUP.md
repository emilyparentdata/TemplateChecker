# TemplateChecker - Setup Guide

This is a quick guide to get TemplateChecker running on your computer.

## What you need first

You need **Python** installed (version 3.9 or newer).

**To check if you already have it:** Open a terminal and type:

```
python --version
```

If you see something like `Python 3.11.5`, you're good. If you get an error, download Python from https://www.python.org/downloads/ and install it. During installation, **check the box that says "Add Python to PATH"**.

### Opening a terminal

- **Windows:** Press `Win + R`, type `cmd`, and hit Enter
- **Mac:** Press `Cmd + Space`, type `Terminal`, and hit Enter

## Setup (one-time only)

1. **Download this repository.** Click the green **Code** button on GitHub, then **Download ZIP**. Unzip it to a folder on your computer (or use `git clone` if you're comfortable with git).

2. **Open a terminal** and navigate to the folder. For example if you unzipped to your Desktop:

   ```
   cd Desktop/TemplateChecker
   ```

3. **Install the dependencies** by running:

   ```
   pip install -r requirements.txt
   ```

   Wait for it to finish. You only need to do this once.

## Running the app

1. In your terminal, make sure you're in the TemplateChecker folder, then run:

   ```
   python app.py
   ```

2. You should see output that includes:

   ```
   * Running on http://127.0.0.1:5000
   ```

3. **Open your web browser** and go to: **http://127.0.0.1:5000**

4. That's it! The app is now running. You can use the Compatibility Checker and Template Comparator from the browser.

## Stopping the app

Go back to the terminal and press `Ctrl + C`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` is not recognized | Try `python3` instead of `python` everywhere above. If that doesn't work, reinstall Python and make sure "Add to PATH" is checked. |
| `pip` is not recognized | Try `pip3` instead, or `python -m pip install -r requirements.txt` |
| "Port already in use" error | Another app is using port 5000. Close it, or run with: `python app.py` and wait a moment. |
| Page won't load in browser | Make sure the terminal still shows the app running. Try http://localhost:5000 instead. |
