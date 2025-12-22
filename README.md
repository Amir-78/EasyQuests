# EasyQuests

An automated tool that simulates watching Discord video quests, supporting both PC and mobile video quest types. Complete your Discord quests efficiently and claim rewards with ease!

## ✨ Features

- 🎥 Supports both **PC** and **Mobile** video quests
- 🤖 Realistic video progress simulation
- ⚡ Automatic quest enrollment and completion
- 🔄 Smart rate limiting and retry logic
- 📊 Beautiful terminal interface with progress tracking
- 🛡️ Safe and reliable quest solving

## 📥 Installation

### Option 1: Download Pre-built Executable
Download the latest `.exe` file from the [Releases](https://github.com/Amir-78/EasyQuests/releases) page.

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/Amir-78/EasyQuests.git
cd EasyQuests

# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py
```

## 🚀 Usage

1. Run the application (either `.exe` or `python main.py`)
2. Enter your Discord account token when prompted
3. The tool will automatically:
   - Fetch available video quests
   - Enroll in each quest
   - Simulate realistic video watching
   - Mark quests as ready to claim
4. Go back to Discord and claim your rewards!

## 🔑 How to Get Your Discord Token

> ⚠️ **Warning**: Never share your Discord token with anyone! Keep it private and secure.

### Method 1: Network Tab

1. Open Discord in your web browser
2. Press `F12` to open Developer Tools
3. Go to the **Network** tab
4. Press `F5` to reload the page
5. Type `api` in the filter box
6. Click on any request
7. Go to the **Headers** tab
8. Scroll down to find **Request Headers**
9. Look for `authorization:` - the value after it is your token

## 📋 Requirements

```
colorama
curl-cffi
random-user-agent
python-dateutil
```

## ⚙️ Configuration

The tool includes built-in configuration for optimal performance:
- Rate limiting (2 seconds between requests)
- Automatic retry logic (3 attempts)
- Request timeout (30 seconds)
- Smart progress simulation

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs by [opening an issue](https://github.com/Amir-78/EasyQuests/issues)
- 💡 Suggest new features
- 🔧 Submit pull requests

## ⭐ Support

If you find this tool helpful, please consider:
- ⭐ **Starring** the repository
- 🐛 **Reporting issues** if you encounter problems
- 📢 **Sharing** with others who might find it useful

## 📝 Disclaimer

This tool is for educational purposes only. Use at your own risk. The author is not responsible for any consequences resulting from the use of this tool, including but not limited to Discord account restrictions or bans. Always comply with Discord's Terms of Service.

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **GitHub**: [https://github.com/Amir-78](https://github.com/Amir-78)
- **Issues**: [Report a problem](https://github.com/Amir-78/EasyQuests/issues)
- **Releases**: [Download latest version](https://github.com/Amir-78/EasyQuests/releases)

---

Made with ❤️ by [Amir-78](https://github.com/Amir-78)

*Star ⭐ this repository if you found it helpful!*
