"""
Automated PDF to MCQ Converter
Processes PDF page by page: PDF -> Image -> OCR -> MCQ Parsing -> JSON
"""
import argparse
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# PDF to Image
from pdf2image import convert_from_path
from PIL import Image

# OCR
import pytesseract

# Progress bar
from tqdm import tqdm


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


def find_poppler():
    """Find Poppler binaries"""
    possible_paths = [
        r'poppler\poppler-24.08.0\Library\bin',
        r'poppler\Library\bin',
        r'C:\Program Files\poppler\Library\bin',
        r'C:\poppler\bin',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def pdf_to_images(pdf_path, start_page=1, end_page=None, dpi=300):
    """
    Convert PDF pages to images

    Args:
        pdf_path: Path to PDF file
        start_page: Starting page number (1-based)
        end_page: Ending page number (1-based, None for all)
        dpi: Image resolution (higher = better quality but slower)

    Returns:
        List of PIL Image objects
    """
    print(f"📄 Converting PDF to images (DPI: {dpi})...")

    # Find poppler
    poppler_path = find_poppler()

    try:
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=start_page,
            last_page=end_page,
            poppler_path=poppler_path
        )
        print(f"✅ Converted {len(images)} pages to images")
        return images
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        if "poppler" in str(e).lower() or "pdftoppm" in str(e).lower():
            print("\n" + "="*70)
            print("⚠️  Poppler not found!")
            print("="*70)
            print("Please install Poppler:")
            print("  Run: python install-poppler.py")
            print("="*70)
        return []


def ocr_image(image, lang='eng'):
    """Extract text from image using OCR"""
    try:
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return ""


def parse_mcq_from_text(text, page_num):
    """
    Parse MCQ questions from OCR text
    Simple pattern matching for questions with options
    """
    questions = []
    
    # Split by question numbers (e.g., "1.", "Q1.", "1)", etc.)
    # Pattern: number followed by dot or parenthesis
    parts = re.split(r'\n\s*(?:Q\.?\s*)?(\d+)[\.\)]\s+', text)
    
    if len(parts) < 2:
        return questions
    
    # First part is usually header/junk, skip it
    i = 1
    while i < len(parts) - 1:
        q_num = parts[i]
        content = parts[i + 1]
        
        # Look for options pattern (A), (B), (C), (D) or A), B), C), D)
        has_options = re.search(r'\([A-Da-d]\)', content) or re.search(r'[A-Da-d]\)', content)
        
        if has_options:
            parsed = parse_single_mcq(int(q_num), content, page_num)
            if parsed:
                questions.append(parsed)
        
        i += 2
    
    return questions


def parse_single_mcq(q_num, content, page_num):
    """Parse a single MCQ question"""
    
    # Find answer first (Ans: A, Answer: B, etc.)
    ans_match = re.search(r'(?:Ans(?:wer)?\.?\s*[:.]?\s*\(?([A-Da-d])\)?)', content, re.IGNORECASE)
    answer = None
    if ans_match:
        answer = ans_match.group(1).upper()
        # Remove answer from content
        content = content[:ans_match.start()]
    
    # Extract options - try multiple patterns
    options = {}
    
    # Pattern 1: (A) option text
    pattern1 = r'\(([A-Da-d])\)\s*([^\n(]+?)(?=\s*\([A-Da-d]\)|\s*$)'
    matches1 = re.findall(pattern1, content, re.IGNORECASE)
    
    # Pattern 2: A) option text
    pattern2 = r'([A-Da-d])\)\s*([^\n]+?)(?=\s*[A-Da-d]\)|\s*$)'
    matches2 = re.findall(pattern2, content, re.IGNORECASE)
    
    # Use whichever pattern found more options
    matches = matches1 if len(matches1) >= len(matches2) else matches2
    
    if len(matches) >= 3:  # At least 3 options
        # Extract question text (before first option)
        first_opt_pos = content.find(f"({matches[0][0]})") if matches1 else content.find(f"{matches[0][0]})")
        question_text = content[:first_opt_pos].strip()
        
        # Extract options
        for letter, text in matches:
            options[letter.upper()] = text.strip()
        
        # Clean question text
        question_text = ' '.join(question_text.split())
        
        if len(question_text) > 10 and len(options) >= 3:
            return {
                "question_no": q_num,
                "question": question_text,
                "options": options,
                "answer": answer,
                "page": page_num
            }
    
    return None


def process_pdf_auto(pdf_path, start_page=1, end_page=None, output_json=None, 
                     dpi=300, lang='eng', save_images=False):
    """
    Automatically process PDF: PDF -> Images -> OCR -> MCQ Parsing
    
    Args:
        pdf_path: Path to PDF file
        start_page: Starting page (1-based)
        end_page: Ending page (1-based, None for all)
        output_json: Output JSON path
        dpi: Image resolution
        lang: OCR language
        save_images: Save intermediate images
    """
    
    print(f"\n{'='*70}")
    print("Automated PDF to MCQ Converter")
    print(f"{'='*70}\n")
    
    # Convert PDF to images
    images = pdf_to_images(pdf_path, start_page, end_page, dpi)
    
    if not images:
        print("❌ No images generated from PDF")
        return
    
    # Process each page
    all_questions = []
    
    print(f"\n🔍 Processing {len(images)} pages with OCR...")
    
    for i, image in enumerate(tqdm(images, desc="Processing pages")):
        page_num = start_page + i
        
        # Save image if requested
        if save_images:
            img_path = f"page_{page_num:03d}.png"
            image.save(img_path)
        
        # OCR
        text = ocr_image(image, lang)
        
        # Parse MCQs
        questions = parse_mcq_from_text(text, page_num)
        all_questions.extend(questions)
    
    # Remove duplicates
    unique_questions = []
    seen = set()
    for q in all_questions:
        key = (q['question_no'], q['question'][:50])
        if key not in seen:
            seen.add(key)
            unique_questions.append(q)
    
    print(f"\n✅ Extracted {len(unique_questions)} unique questions")
    
    # Save to JSON
    if not output_json:
        output_json = Path(pdf_path).stem + "_mcqs.json"
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to: {output_json}")
    
    # Show sample
    if unique_questions:
        print(f"\n📌 Sample Questions:")
        print("="*70)
        for q in unique_questions[:3]:
            print(f"\n[Page {q['page']}] Q{q['question_no']}: {q['question'][:80]}...")
            for k, v in q['options'].items():
                marker = " ✓" if k == q.get('answer') else ""
                print(f"  {k}) {v[:60]}{marker}")
    
    return unique_questions


def main():
    parser = argparse.ArgumentParser(description='Automated PDF to MCQ Converter')
    parser.add_argument('pdf', help='Path to PDF file')
    parser.add_argument('--start', '-s', type=int, default=1, help='Start page (default: 1)')
    parser.add_argument('--end', '-e', type=int, help='End page (default: all)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--dpi', type=int, default=300, help='Image DPI (default: 300)')
    parser.add_argument('--lang', '-l', default='eng', help='OCR language (default: eng)')
    parser.add_argument('--save-images', action='store_true', help='Save intermediate images')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf):
        print(f"❌ Error: PDF file not found: {args.pdf}")
        return
    
    process_pdf_auto(
        args.pdf,
        start_page=args.start,
        end_page=args.end,
        output_json=args.output,
        dpi=args.dpi,
        lang=args.lang,
        save_images=args.save_images
    )


if __name__ == "__main__":
    main()

