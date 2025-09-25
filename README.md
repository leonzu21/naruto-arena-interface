# Naruto Arena Interface

A Python bot for automatically playing on the Naruto Arena game website. This bot can search for games, handle battles, and make strategic decisions during gameplay.

## Features

- **Automatic Login**: Handles authentication with token persistence
- **Game Search**: Automatically searches for Quick games
- **Battle Management**: Manages turn-based combat with strategic decision making
- **Team Configuration**: Uses a predefined team (Haruno Sakura, Rock Lee, Kin Tsuchi)
- **Interactive Battle Interface**: Provides a CLI for manual battle decisions when needed

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd naruto-arena-interface
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the main bot:
```bash
python main.py
```

2. On first run, you'll be prompted to enter your Naruto Arena credentials:
   - Username
   - Password

3. The bot will automatically:
   - Save your authentication token for future sessions
   - Search for available games
   - Handle battles automatically or prompt for manual input

## Configuration

### Team Setup
The default team is configured in `main.py`:
```python
TEAM = ["Haruno Sakura", "Rock Lee", "Kin Tsuchi"]
```

You can modify this list to use different characters.

### Player ID
Update the player ID in the main execution block:
```python
player_id = "leonzu"  # Change this to your player ID
```

## Dependencies

- `requests` - HTTP requests to the Naruto Arena API
- `beautifulsoup4` - HTML parsing for game state extraction
- `json` - JSON data handling
- `time` - Timing and delays
- `sys` - System operations
- `os` - File operations

## How It Works

1. **Authentication**: The bot logs in using your credentials and stores the authentication token
2. **Game Search**: Searches for Quick games with your configured team
3. **Battle Handling**:
   - Extracts battle state from the game's HTML
   - Waits for your turn
   - Provides options for manual skill selection or automatic decisions
4. **Turn Management**: Handles skill usage, target selection, and chakra management

## Files

- `main.py` - Main bot implementation with NarutoArenaBot class
- `openai_handler.py` - OpenAI integration for potential AI decision making
- `requirements.txt` - Python dependencies
- `token.txt` - Stored authentication token (auto-generated)

## Notes

- The bot respects the game's turn-based nature and waits appropriately
- Authentication tokens are automatically managed and persisted
- The interface provides both automated and manual control options
- Games can be surrendered at any time through the interface

## Disclaimer

This bot is for educational purposes. Please ensure you comply with the Naruto Arena website's terms of service when using automated tools.