# OpenRouter AI Chatbot

A modern, sleek Python GUI application for chatting with AI models through OpenRouter's API.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 🎨 **Modern Dark Theme**: Sleek, professional interface with a dark color scheme
- 🤖 **Multiple AI Models**: Automatically fetches and displays all available models from OpenRouter
- 💬 **Conversation Memory**: Saves chat history to JSON file for persistence across sessions
- 🔊 **Text-to-Speech**: Optional TTS support for AI responses
- ⌨️ **Keyboard Shortcuts**: Press Enter to send messages, Shift+Enter for new lines
- 🕒 **Timestamps**: Each message includes timestamps for better conversation tracking
- 🎯 **Smart Context**: Maintains conversation context for more coherent responses

## Prerequisites

- Python 3.7 or higher
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hedinnh/openrouter-chatbot.git
cd openrouter-chatbot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python3 openrouter_chatbot.py
```

Or use the launcher script (Linux) to suppress ALSA warnings:
```bash
./run_chatbot.py
```

2. Enter your OpenRouter API key and click "Save Key"
3. Select an AI model from the dropdown list
4. Start chatting!

## Features in Detail

### API Key Management
- Secure API key input with masked entry field
- Automatic model fetching upon key validation

### Model Selection
- Dynamic dropdown populated with all available OpenRouter models
- Easy switching between different AI models

### Chat Interface
- Clean, distraction-free chat display
- Color-coded messages (user, assistant, system)
- Automatic scrolling to latest messages
- Timestamp display for each message

### Text-to-Speech
- Toggle TTS on/off with a simple checkbox
- Automatic reading of AI responses when enabled
- Clean text processing for better speech output

### Conversation Memory
- Automatic saving of conversation history
- Persistence across application restarts
- JSON-based storage for easy management
- Maintains last 50 messages for context

### User Controls
- **Send Button**: Send your message
- **Clear Button**: Clear chat and reset memory
- **Enter Key**: Quick send (Shift+Enter for new line)

## Configuration

The application stores conversation history in `chat_memory.json` in the same directory as the script. This file contains:
- Conversation history (last 50 messages)
- Last used model
- Timestamp of last update

## Troubleshooting

### Common Issues

1. **"Failed to fetch models" error**
   - Verify your API key is correct
   - Check your internet connection
   - Ensure OpenRouter service is accessible

2. **TTS not working**
   - Install system TTS engine if not present
   - Check audio output settings
   - Try disabling and re-enabling TTS

3. **Application won't start**
   - Ensure all dependencies are installed
   - Check Python version (3.7+ required)
   - Verify tkinter is installed (usually comes with Python)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI
- Uses [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for text-to-speech
- Powered by [OpenRouter](https://openrouter.ai) API

## Author

Created by hedinnh
