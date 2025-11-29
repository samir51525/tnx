# How to Upload to GitHub

Since Git is not installed, here are two options:

## Option 1: Install Git and Upload via Command Line

1. **Install Git:**
   - Download from: https://git-scm.com/download/win
   - Or use: `winget install Git.Git`

2. **After installing Git, run these commands:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Multi-language AI Discord bot"
   git branch -M main
   git remote add origin https://github.com/samir51525/tnx.git
   git push -u origin main
   ```

## Option 2: Upload via GitHub Web Interface

1. Go to: https://github.com/samir51525/tnx
2. Click "Add file" → "Upload files"
3. Drag and drop these files:
   - `bot.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `start.bat`
4. **DO NOT upload:**
   - `config.txt` (contains sensitive tokens)
   - `__pycache__/` folder
   - `.env` file (if exists)
5. Click "Commit changes"

## Important Notes

- **Never upload `config.txt`** - it contains your Discord token and API keys
- The `.gitignore` file will prevent sensitive files from being uploaded
- Make sure to remove any hardcoded tokens from `bot.py` before uploading (use environment variables instead)

