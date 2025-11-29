# 🤖 Multi-Language AI Discord Bot

An advanced AI-powered Discord bot built with Gemini API that automatically detects and responds in any language. Supports Bengali, English, Hindi, Urdu, Tamil, Arabic, Chinese, Japanese, Korean, Spanish, and more!

## ✨ Features

- 🌐 **Automatic Language Detection** - Detects user's language and responds naturally
- 💬 **Intelligent Conversations** - Powered by Google's Gemini AI
- 🎨 **Image Generation** - Create AI-generated images from text descriptions
- 🎵 **Music Playback** - Play music from YouTube in voice channels
- 🎭 **Funny Responses** - Humorous replies when used as messenger
- 📝 **Multi-Purpose Assistant** - Writing, coding, problem-solving, translations, and more
- 🔄 **Context-Aware** - Maintains conversation history per user/channel
- ⚙️ **Management Tools** - Status, say, repeat commands
- 🚀 **24/7 Availability** - Always ready to assist

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Gemini API Key

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** For music playback, you also need FFmpeg:
   - Download from: https://ffmpeg.org/download.html
   - Or install via: `winget install ffmpeg` (Windows) or `choco install ffmpeg`

3. **Configure environment variables:**
   
   Create a `.env` file in the project root:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Or edit `bot.py` directly with your credentials (not recommended for production).

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## 📋 Commands

### AI Commands
- `!chat <message>` or `!c <message>` - Chat with the AI assistant
- `!image <description>` or `!img <description>` - Generate an AI image
- `!clear` or `!reset` - Clear your chat history
- `$TNXINFO` or `$tnxinfo` - Show all commands

### Management Commands
- `!status` or `!info` or `!stats` - Show bot status and statistics
- `!say <message>` - Make bot send a message
- `!repeat <times> <message>` - Repeat message (max 5 times)
- `!ping` - Check bot latency
- `!help` or `!h` - Show help information

### Music/Audio Commands
- `!join` - Join voice channel
- `!leave` or `!dc` - Leave voice channel
- `!play <song>` or `!p <song>` - Play music from YouTube
- `!stop` or `!s` - Stop playback
- `!pause` - Pause playback
- `!resume` - Resume playback

## 💡 Usage

### Auto-Response Mode
- Mention the bot (`@YourBot`) in any channel
- Send a direct message (DM) to the bot
- The bot will automatically detect your language and respond

### Command Mode
Use commands with the `!` prefix:
```
!chat How do I learn Python?
!image A futuristic city at sunset
!clear
```

## 🌍 Supported Languages

The bot automatically supports:
- English
- Bengali (বাংলা)
- Hindi (हिंदी)
- Urdu (اردو)
- Tamil (தமிழ்)
- Arabic (العربية)
- Chinese (中文)
- Japanese (日本語)
- Korean (한국어)
- Spanish (Español)
- And many more!

## 🔧 Configuration

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" in the Bot settings
6. Invite the bot to your server with appropriate permissions

### Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Add it to your `.env` file

## 📝 Notes

- The bot maintains separate chat sessions for each user/channel combination
- Long responses are automatically split into multiple messages
- Image generation may require additional API setup depending on Gemini's capabilities
- For production use, store credentials securely using environment variables

## 🐛 Troubleshooting

**Bot not responding:**
- Check if the bot is online
- Verify the Discord token is correct
- Ensure "Message Content Intent" is enabled

**API errors:**
- Verify your Gemini API key is valid
- Check your API quota/limits
- Ensure you have internet connectivity

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Made with ❤️ using Discord.py and Google Gemini API**

