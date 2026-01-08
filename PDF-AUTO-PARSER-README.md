# Automated PDF to MCQ Parser

Automatically process PDF files page by page: **PDF → Images → OCR → MCQ Parsing → JSON**

No manual screenshots needed! Just pass the PDF and it processes everything automatically.

## 🚀 Quick Start

### 1. Install Dependencies (One-time setup)

**Install Tesseract OCR:**
```bash
python install-tesseract.py
```
Follow the installation wizard. This is required for text recognition.

**Install Poppler:**
```bash
python install-poppler.py
```
This is required to convert PDF pages to images.

### 2. Process Your PDF

**Process entire PDF:**
```bash
python pdf-auto-ocr-parser.py your_mcq_book.pdf
```

**Process specific page range:**
```bash
python pdf-auto-ocr-parser.py your_mcq_book.pdf --start 1 --end 50
```

**Process with custom output:**
```bash
python pdf-auto-ocr-parser.py your_mcq_book.pdf -s 151 -e 200 -o mcqs_151-200.json
```

## 📖 Usage Examples

### Example 1: Process Pages 1-100
```bash
python pdf-auto-ocr-parser.py files/yct/yct-computer.pdf --start 1 --end 100
```

### Example 2: High Quality OCR (slower but better)
```bash
python pdf-auto-ocr-parser.py mybook.pdf --dpi 400
```

### Example 3: Multi-language Support
```bash
python pdf-auto-ocr-parser.py mybook.pdf --lang eng+hin
```

### Example 4: Save Intermediate Images (for debugging)
```bash
python pdf-auto-ocr-parser.py mybook.pdf --save-images
```

## 🎯 Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `pdf` | | PDF file path (required) | - |
| `--start` | `-s` | Start page number | 1 |
| `--end` | `-e` | End page number | All pages |
| `--output` | `-o` | Output JSON file | `{pdf_name}_mcqs.json` |
| `--dpi` | | Image resolution (100-600) | 300 |
| `--lang` | `-l` | OCR language | eng |
| `--save-images` | | Save page images | False |

## 🔧 How It Works

```
┌─────────────┐
│   PDF File  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Convert to Images   │  (using Poppler)
│ Page by Page        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ OCR Text Extraction │  (using Tesseract)
│ from Each Image     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Parse MCQ Questions │  (Pattern Matching)
│ Options & Answers   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Save to JSON       │
└─────────────────────┘
```

## 📊 Output Format

The script generates a JSON file with this structure:

```json
[
  {
    "question_no": 1,
    "question": "What is the capital of France?",
    "options": {
      "A": "London",
      "B": "Paris",
      "C": "Berlin",
      "D": "Madrid"
    },
    "answer": "B",
    "page": 1
  }
]
```

## 💡 Tips for Best Results

### 1. **DPI Settings**
- **DPI 200**: Fast, good for clear text
- **DPI 300**: Balanced (default)
- **DPI 400-600**: Slow, best for small or unclear text

### 2. **Page Range**
- Process in batches (e.g., 50-100 pages at a time)
- Helps identify issues early
- Easier to debug

### 3. **Language Settings**
- English only: `--lang eng`
- Hindi + English: `--lang eng+hin`
- Download additional languages from Tesseract

### 4. **Quality Check**
- Use `--save-images` first time to verify image quality
- Check sample output before processing entire PDF
- Adjust DPI if text is unclear

## 🔍 Troubleshooting

### "Poppler not found" error
```bash
python install-poppler.py
```

### "Tesseract not found" error
```bash
python install-tesseract.py
```
Then follow the installation wizard.

### Poor OCR accuracy
- Increase DPI: `--dpi 400`
- Check if PDF is scanned (image-based) vs text-based
- For text-based PDFs, use the regular `mcq-parser-yct-columns.py` instead

### Few questions extracted
- The PDF might have unusual formatting
- Try `--save-images` to see what OCR is reading
- May need to adjust parsing patterns in the script

### Out of memory
- Process smaller page ranges
- Reduce DPI to 200

## 📝 Complete Workflow Example

```bash
# 1. Setup (one-time)
python install-tesseract.py
python install-poppler.py

# 2. Test on small range first
python pdf-auto-ocr-parser.py mybook.pdf -s 1 -e 10 -o test.json

# 3. Check the output
cat test.json

# 4. If good, process full range
python pdf-auto-ocr-parser.py mybook.pdf -s 1 -e 100 -o mcqs_1-100.json

# 5. Convert to Word (optional)
python json-to-word.py mcqs_1-100.json
```

## ⚡ Performance

Approximate processing times (on average hardware):

| Pages | DPI 200 | DPI 300 | DPI 400 |
|-------|---------|---------|---------|
| 10    | ~30s    | ~1min   | ~2min   |
| 50    | ~3min   | ~5min   | ~10min  |
| 100   | ~6min   | ~10min  | ~20min  |

*Times vary based on PDF complexity and hardware*

## 🆚 When to Use This vs Regular Parser

**Use `pdf-auto-ocr-parser.py` when:**
- PDF is scanned (image-based)
- PDF has complex layouts
- Text extraction doesn't work

**Use `mcq-parser-yct-columns.py` when:**
- PDF has selectable text
- Faster processing needed
- Better accuracy required

## 🎓 Advanced Usage

### Batch Processing Multiple PDFs
```bash
# Process multiple PDFs
for pdf in *.pdf; do
    python pdf-auto-ocr-parser.py "$pdf" -s 1 -e 50
done
```

### Custom Parsing
Edit `parse_mcq_from_text()` function in `pdf-auto-ocr-parser.py` to customize question detection patterns.

