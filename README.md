# HOCR - Screen OCR and Translation Tool

A simple desktop overlay app that captures text from your screen using Azure AI Vision and translates it with Azure Translator. Perfect for reading foreign text in games, websites, or any application. Because it uses Azure, the latency is really low, and the accuracy is high.

[![image.png](https://i.postimg.cc/d3sLRhq2/image.png)](https://postimg.cc/xJZfnTN8)

## Features

- **Draggable selection box**: Move and resize the green overlay to select text areas
- **Real-time OCR**: Uses Azure AI Vision to extract text from screenshots
- **Instant translation**: Translates captured text using Azure Translator
- **Always on top**: Stays visible over other applications
- **Floating text display**: Shows OCR results and translations as text attached to the overlay

## Usage

1. **Position the box**: Drag the green overlay over the text you want to translate
2. **Resize if needed**: Drag from the bottom-right corner to resize the selection area
3. **Right-click to capture**: The app will OCR the selected area and translate the text
4. **Close when done**: Middle-click or press Escape to exit

## Setup

### Prerequisites

- Python 3.7+
- Azure AI Services account (Vision + Translator)

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Azure credentials in `main.py`:
   ```python
   AZURE_VISION_ENDPOINT = "your-vision-endpoint"
   AZURE_VISION_KEY = "your-vision-key"
   AZURE_TRANSLATOR_ENDPOINT = "your-translator-endpoint"
   AZURE_TRANSLATOR_KEY = "your-translator-key"
   AZURE_TRANSLATOR_REGION = "your-region"
   SOURCE_LANGUAGE = "source-language"  # e.g., "zh" for Chinese | can leave empty for auto-detection
   ```

### Getting Azure Credentials

1. Create an Azure account at [portal.azure.com](https://portal.azure.com)
2. Create a **Computer Vision** resource for OCR
3. Create a **Translator** resource for translation
4. Copy the endpoints and keys to the config section in `main.py`

You can use the free tiers of both resources (F0) for limited usage, which is usually enough for personal use.

## Usage

Run the application:
```bash
python main.py
```

### Controls

- **Left-click + drag**: Move the overlay
- **Left-click bottom-right corner + drag**: Resize the overlay
- **Right-click**: Capture and translate text in the selected area
- **Middle-click** or **Escape**: Close the application

## Current Limitations

- Minimum selection size is 50x50 pixels (Azure requirement)
- Requires active internet connection for Azure services (and keys)

## Potential Improvements

- [ ] Support for multiple target languages (unlikely)
- [ ] Offline OCR option
- [ ] Offline translation option (unlikely)
- [ ] Configuration file for Azure credentials
- [ ] Hotkey support for capture without clicking
- [ ] Text history/clipboard integration

## Dependencies

- **PyQt6**: GUI framework
- **mss**: Fast screenshot capture
- **azure-ai-vision-imageanalysis**: Azure Computer Vision OCR
- **azure-ai-translation-text**: Azure Translator service
- **Pillow**: Image processing support

## Why "HOCR"?

It just stands for "Hovering OCR".

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.