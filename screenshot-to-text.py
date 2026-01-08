"""
Screenshot to Text Converter using OCR
Supports: Taking screenshots, loading images, and extracting text
"""
import argparse
import os
import sys
from PIL import ImageGrab, Image
import pytesseract
from datetime import datetime
import pyautogui
import time


# Try to find Tesseract executable
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
    print("⚠️  Warning: Tesseract not found in common locations.")
    print("   If OCR fails, please install Tesseract:")
    print("   Run: python install-tesseract.py")
    print()


def take_screenshot(output_path=None, delay=0):
    """
    Take a screenshot and save it
    
    Args:
        output_path: Path to save screenshot (default: auto-generated)
        delay: Delay in seconds before taking screenshot
    
    Returns:
        Path to saved screenshot
    """
    if delay > 0:
        print(f"⏳ Waiting {delay} seconds before taking screenshot...")
        for i in range(delay, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        print("   📸 Taking screenshot now!")
    
    # Take screenshot
    screenshot = ImageGrab.grab()
    
    # Generate filename if not provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"screenshot_{timestamp}.png"
    
    # Save screenshot
    screenshot.save(output_path)
    print(f"✅ Screenshot saved to: {output_path}")
    
    return output_path


def extract_text_from_image(image_path, lang='eng'):
    """
    Extract text from an image using OCR

    Args:
        image_path: Path to image file
        lang: Language for OCR (default: 'eng', can use 'eng+hin' for Hindi)

    Returns:
        Extracted text
    """
    print(f"📖 Reading image: {image_path}")

    # Open image
    image = Image.open(image_path)

    # Perform OCR
    print(f"🔍 Extracting text (language: {lang})...")

    try:
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except pytesseract.TesseractNotFoundError:
        print("\n" + "="*70)
        print("❌ ERROR: Tesseract OCR is not installed!")
        print("="*70)
        print("\nPlease install Tesseract OCR:")
        print("1. Run: python install-tesseract.py")
        print("2. Or download manually from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("\nAfter installation, add Tesseract to your PATH or")
        print("set pytesseract.pytesseract.tesseract_cmd in the script.")
        print("="*70)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during OCR: {e}")
        sys.exit(1)


def save_text(text, output_path):
    """Save extracted text to file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"💾 Text saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Screenshot to Text Converter using OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Take screenshot and extract text
  python screenshot-to-text.py --screenshot --delay 3
  
  # Extract text from existing image
  python screenshot-to-text.py --image myimage.png
  
  # Take screenshot with custom output
  python screenshot-to-text.py --screenshot --output my_screenshot.png
  
  # Extract text with Hindi support
  python screenshot-to-text.py --image myimage.png --lang eng+hin
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--screenshot', '-s', action='store_true',
                            help='Take a new screenshot')
    input_group.add_argument('--image', '-i', type=str,
                            help='Path to existing image file')
    
    # Screenshot options
    parser.add_argument('--delay', '-d', type=int, default=0,
                       help='Delay in seconds before taking screenshot (default: 0)')
    
    # OCR options
    parser.add_argument('--lang', '-l', type=str, default='eng',
                       help='OCR language (default: eng, use eng+hin for Hindi)')
    
    # Output options
    parser.add_argument('--output', '-o', type=str,
                       help='Output file path for screenshot (default: auto-generated)')
    parser.add_argument('--text-output', '-t', type=str,
                       help='Output file path for extracted text (default: same name as image with .txt)')
    parser.add_argument('--no-save-text', action='store_true',
                       help='Do not save extracted text to file, only print')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print("Screenshot to Text Converter")
    print(f"{'='*70}\n")
    
    # Get image path
    if args.screenshot:
        image_path = take_screenshot(args.output, args.delay)
    else:
        image_path = args.image
        if not os.path.exists(image_path):
            print(f"❌ Error: Image file not found: {image_path}")
            return
    
    # Extract text
    text = extract_text_from_image(image_path, args.lang)
    
    # Print extracted text
    print(f"\n{'='*70}")
    print("Extracted Text:")
    print(f"{'='*70}\n")
    print(text)
    print(f"\n{'='*70}")
    print(f"Total characters: {len(text)}")
    print(f"Total lines: {len(text.splitlines())}")
    print(f"{'='*70}\n")
    
    # Save text to file
    if not args.no_save_text:
        if args.text_output:
            text_output = args.text_output
        else:
            # Generate text output path from image path
            base_name = os.path.splitext(image_path)[0]
            text_output = f"{base_name}.txt"
        
        save_text(text, text_output)


if __name__ == "__main__":
    main()

