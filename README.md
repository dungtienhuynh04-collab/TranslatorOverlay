# TranslatorOverlay

**TranslatorOverlay** is a powerful desktop application that provides real-time, on-screen text translation (especially useful for gaming).  

The application utilizes a local Vision Large Language Model (VLM) running via **LM Studio** to scan the screen, recognize text, and translate it into your desired language entirely automatically and safely on your local machine.

## ✨ Key Features

- 🌍 **Real-Time Translation**: Automatically captures the specified screen region and translates immediately when new UI dialogues or text are detected. Minimizes API calls through an intelligent pixel-change-detection algorithm.
- 🎨 **Premium UI/UX**:
  - **Capture Box**: Intuitive drag-and-drop design, styled like professional crop tools with 8 resize handles.
  - **Display Box**: Features a draggable bar, adjustable background opacity, and flexible long-text handling (Scroll bar vs Auto-fit text size).
  - **Click-through Mode**: The translation display box won't interfere with your in-game mouse clicks.
- 🌓 **Theme Customization**: Switch seamlessly between Dark Mode and Light Mode.
- 🌐 **Multilingual UI**: The application interface supports both English and Vietnamese.
- ⚙️ **Settings Memory**: All your configurations, prompts, and server URLs are saved persistently in `settings.json`.
- 🔍 **Background Execution**: Features a System Tray integration so you can minimize the app (to the bottom right corner) while continuing to translate in the background.
- 📝 **Live debug Logs**: A dedicated Logs tab tracks detailed sent/received requests to LM Studio for easy troubleshooting.

## 🚀 System Requirements

1. **Python 3.10+** (if running from source).
2. **LM Studio**: You must install [LM Studio](https://lmstudio.ai/) and download a **Vision LLM** model. The author's recommended model is `mistralai/ministral-3-3b` (or other Vision models like `LLaVA`, `Qwen-VL`, etc.).

## 🛠 Installation & Setup

### Method 1: Run from Source Code

1. Clone this Repository to your machine:
   ```bash
   git clone https://github.com/your-username/TranslatorOverlay.git
   cd TranslatorOverlay
   ```
2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   # Activate on Windows:
   .\venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the application:
   ```bash
   python main.py
   ```

### Method 2: Build a Standalone Executable (.exe)
If you want to package the app into a single executable so you can run it without Python installed, use PyInstaller:
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "src;src" --name "TranslatorOverlay" main.py
```
*The executable will be located in the `dist/TranslatorOverlay/TranslatorOverlay.exe` folder.*

## ⚙️ How to use with LM Studio

1. **Open LM Studio**, search for a model that supports Vision (e.g., search for `vision`) and download it.
2. Navigate to the **Local Server (↔️)** tab on the left sidebar.
3. Select the Vision model you just downloaded at the top, and adjust the RAM/VRAM settings according to your PC specs.
4. Click **Start Server**. Note the running port (usually `http://localhost:1234/v1`).
5. **Open TranslatorOverlay**:
   - In the **Settings** tab, set the **API URL** to match the LM Studio server. (The app will automatically append `/v1` if you forget).
   - Click `Capture Box` and drag it over the chat/dialogue area in your game.
   - Click `Display Box` and drag it to a convenient spot to read translations.
   - Click the **Start Translating** button!

## File Structure

```
📦TranslatorOverlay
 ┣ 📂src
 ┃ ┣ 📜capture_overlay.py  # Transparent screen capture UI logic.
 ┃ ┣ 📜display_overlay.py  # Always-on-top translation result UI logic.
 ┃ ┣ 📜llm_service.py      # Background worker handling image diffing and LM API calls.
 ┃ ┗ 📜main_window.py      # Main application GUI, Themes, and Multilingual logic.
 ┣ 📜main.py               # Application entry-point and System Tray setup.
 ┣ 📜requirements.txt      # Python library dependencies.
 ┗ 📜README.md
```

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
