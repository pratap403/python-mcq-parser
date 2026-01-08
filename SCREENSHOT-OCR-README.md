# Screenshot to Text Converter (OCR)

Convert screenshots and images to text using Optical Character Recognition (OCR).

## 🚀 Quick Start

### 1. Install Tesseract OCR

First, you need to install Tesseract OCR engine:

```bash
python install-tesseract.py
```

This will download and guide you through the installation process.

**OR** download manually from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Take Screenshot and Extract Text

```bash
# Take a screenshot with 3 second delay (gives you time to switch windows)
python screenshot-to-text.py --screenshot --delay 3

# Take screenshot immediately
python screenshot-to-text.py --screenshot
```

### 3. Extract Text from Existing Image

```bash
# Extract text from an image file
python screenshot-to-text.py --image myimage.png

# Extract text with Hindi support
python screenshot-to-text.py --image myimage.png --lang eng+hin
```

## 📖 Usage Examples

### Example 1: Quick Screenshot OCR
```bash
python screenshot-to-text.py -s -d 5
```
- Takes screenshot after 5 seconds
- Extracts text automatically
- Saves both screenshot and text file

### Example 2: Custom Output Paths
```bash
python screenshot-to-text.py -s -o my_screenshot.png -t extracted_text.txt
```
- Takes screenshot and saves as `my_screenshot.png`
- Saves extracted text as `extracted_text.txt`

### Example 3: Process Existing Image
```bash
python screenshot-to-text.py -i files/yct/page1.png
```
- Reads `page1.png`
- Extracts text and saves as `page1.txt`

### Example 4: Multi-language OCR
```bash
python screenshot-to-text.py -i document.png -l eng+hin
```
- Extracts text in both English and Hindi

### Example 5: Print Only (Don't Save)
```bash
python screenshot-to-text.py -i myimage.png --no-save-text
```
- Extracts and prints text
- Does not save to file

## 🎯 Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--screenshot` | `-s` | Take a new screenshot |
| `--image PATH` | `-i PATH` | Use existing image file |
| `--delay SECONDS` | `-d SECONDS` | Delay before screenshot (default: 0) |
| `--lang LANG` | `-l LANG` | OCR language (default: eng) |
| `--output PATH` | `-o PATH` | Screenshot output path |
| `--text-output PATH` | `-t PATH` | Text output path |
| `--no-save-text` | | Don't save text to file |

## 🌍 Supported Languages

Common language codes:
- `eng` - English
- `hin` - Hindi
- `eng+hin` - English + Hindi
- `fra` - French
- `deu` - German
- `spa` - Spanish

For more languages, download additional language packs from Tesseract.

## 💡 Tips

1. **Better OCR Quality**: Use high-resolution screenshots for better text recognition
2. **Delay for Window Switching**: Use `--delay 3` to give yourself time to switch to the window you want to capture
3. **Multi-language**: Combine languages with `+` (e.g., `eng+hin`)
4. **Clean Images**: OCR works best on clear, high-contrast text

## 🔧 Troubleshooting

### "Tesseract not found" error
- Run `python install-tesseract.py` to install Tesseract
- Or manually install and add to PATH

### Poor OCR accuracy
- Use higher resolution images
- Ensure good contrast between text and background
- Try different language settings

### Screenshot not capturing correctly
- Increase delay: `--delay 5`
- Make sure the window is visible and not minimized

## 📝 Workflow Example

**Scenario**: Extract MCQs from PDF screenshots

1. Open your PDF
2. Run: `python screenshot-to-text.py -s -d 3`
3. Switch to PDF window within 3 seconds
4. Screenshot is taken and text is extracted
5. Find results in `screenshot_YYYYMMDD_HHMMSS.png` and `.txt`

## 🎓 Use Cases

- Extract text from PDF screenshots
- Convert images to editable text
- OCR scanned documents
- Extract MCQs from images
- Convert handwritten notes (with varying accuracy)
- Extract text from presentations

