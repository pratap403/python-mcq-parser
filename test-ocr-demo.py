"""
Demo script to test OCR functionality
Creates a sample image with MCQ text and tests OCR
"""
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import os


def find_tesseract():
    """Find Tesseract executable on Windows"""
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


# Set Tesseract path
tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"✅ Found Tesseract at: {tesseract_path}")
else:
    print("⚠️  Tesseract not found. Please install it first.")
    print("   Run: python install-tesseract.py")
    exit(1)


# Create a test image with MCQ text
def create_test_image():
    """Create a sample image with MCQ questions"""
    
    # Create white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Draw MCQ text
    y = 50
    text_lines = [
        "Computer Science MCQs",
        "",
        "1. What does CPU stand for?",
        "(A) Central Processing Unit",
        "(B) Computer Personal Unit",
        "(C) Central Program Utility",
        "(D) Computer Processing Unit",
        "Ans: A",
        "",
        "2. Which of the following is an input device?",
        "(A) Monitor",
        "(B) Printer",
        "(C) Keyboard",
        "(D) Speaker",
        "Ans: C",
        "",
        "3. What is the brain of the computer?",
        "(A) RAM",
        "(B) CPU",
        "(C) Hard Disk",
        "(D) Monitor",
        "Ans: B",
    ]
    
    for line in text_lines:
        if line.startswith("Computer") or line.startswith("Ans:"):
            draw.text((50, y), line, fill='black', font=font_bold)
        else:
            draw.text((50, y), line, fill='black', font=font)
        y += 25
    
    # Save image
    img.save('test_mcq_image.png')
    print("✅ Created test image: test_mcq_image.png")
    
    return img


# Test OCR
def test_ocr(image):
    """Test OCR on the image"""
    print("\n🔍 Running OCR...")
    
    try:
        text = pytesseract.image_to_string(image)
        print("\n" + "="*70)
        print("Extracted Text:")
        print("="*70)
        print(text)
        print("="*70)
        
        # Save to file
        with open('test_ocr_output.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("\n💾 Saved OCR output to: test_ocr_output.txt")
        
        return text
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return None


def main():
    print("\n" + "="*70)
    print("OCR Demo - Testing Tesseract Installation")
    print("="*70 + "\n")
    
    # Create test image
    img = create_test_image()
    
    # Test OCR
    text = test_ocr(img)
    
    if text:
        print("\n✅ OCR is working correctly!")
        print("\nYou can now use:")
        print("  - screenshot-to-text.py for screenshots")
        print("  - pdf-auto-ocr-parser.py for PDF processing")
    else:
        print("\n❌ OCR test failed. Please check Tesseract installation.")


if __name__ == "__main__":
    main()

