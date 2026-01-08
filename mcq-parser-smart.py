"""
Smart MCQ Parser - Automatically detects PDF format and uses best extraction method
Combines: column-based extraction + pymupdf4llm for reliability
"""
import pdfplumber
import pymupdf4llm
import pymupdf
import re
import json
import argparse

PDF_PATH = "D:\\pdf_files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"
OUTPUT_JSON = "mcqs_smart.json"


def detect_layout(pdf_path, sample_page=0):
    """Detect if PDF uses multi-column layout by analyzing word positions"""
    with pdfplumber.open(pdf_path) as pdf:
        if sample_page >= len(pdf.pages):
            sample_page = 0
        page = pdf.pages[sample_page]
        words = page.extract_words()

        if not words:
            return "unknown"

        # Analyze x-positions to detect columns
        page_width = page.width
        mid = page_width / 2

        left_count = sum(1 for w in words if w['x0'] < mid - 50)
        right_count = sum(1 for w in words if w['x0'] > mid + 50)

        # If significant text on both sides, it's multi-column
        if left_count > 20 and right_count > 20:
            return "multi-column"
        return "single-column"


def extract_column_text(page):
    """Extract text from left and right columns separately"""
    words = page.extract_words()
    if not words:
        return "", ""

    page_width = page.width
    mid = page_width / 2

    left_words = [(w['top'], w['x0'], w['text']) for w in words if w['x0'] < mid]
    right_words = [(w['top'], w['x0'], w['text']) for w in words if w['x0'] >= mid]

    def words_to_text(word_list):
        if not word_list:
            return ""
        word_list.sort(key=lambda w: (w[0], w[1]))
        lines, current_line, current_y = [], [], word_list[0][0]
        for y, x, text in word_list:
            if abs(y - current_y) > 5:
                lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y
            else:
                current_line.append(text)
        if current_line:
            lines.append(' '.join(current_line))
        return '\n'.join(lines)

    return words_to_text(left_words), words_to_text(right_words)


def parse_questions_from_text(text, page_num=0):
    """Parse MCQs from extracted text"""
    questions = []

    # Split by question number patterns: "459." or "172."
    # Match 2-4 digit numbers followed by period/paren and a word character
    # This captures questions like "459. A Group..." or "172. Select..."
    blocks = re.split(r'(?=(?:^|\n)\s*(\d{2,4})\s*[.\)]\s+\w)', text)

    current_num = None
    current_text = []

    for block in blocks:
        # Check if block starts with a question number
        match = re.match(r'^\s*(\d{2,4})\s*[.\)]\s+(.+)$', block, re.DOTALL)
        if match:
            q_num = int(match.group(1))
            q_text_start = match.group(2).strip()

            # Filter: question numbers should be reasonable (10-9999)
            # Also skip if it looks like an answer explanation (starts with Ans)
            if 10 <= q_num <= 9999 and not q_text_start.lower().startswith('ans'):
                # Save previous question
                if current_num and current_text:
                    q = parse_single_question(current_num, '\n'.join(current_text), page_num)
                    if q and len(q['options']) >= 2:  # Must have at least 2 options
                        questions.append(q)
                current_num = q_num
                current_text = [q_text_start]
            elif current_num:
                # This might be part of previous question (like numbered list in explanation)
                current_text.append(block)
        elif current_num:
            current_text.append(block)

    # Last question
    if current_num and current_text:
        q = parse_single_question(current_num, '\n'.join(current_text), page_num)
        if q and len(q['options']) >= 2:
            questions.append(q)

    return questions


def parse_single_question(q_num, text, page_num):
    """Parse question text, options, and answer"""
    # Clean text
    text = re.sub(r'\*+', '', text)

    # Split at answer marker
    parts = re.split(r'Ans[\.\s]*[:\(]', text, maxsplit=1, flags=re.IGNORECASE)
    q_part = parts[0]
    ans_part = parts[1] if len(parts) > 1 else ""

    # Extract options: (a) text (b) text...
    options = {}
    opt_pattern = re.compile(r'\(([a-dA-D])\)\s*([^(]+?)(?=\([a-dA-D]\)|$)', re.DOTALL)
    matches = list(opt_pattern.finditer(q_part))

    if matches:
        question_text = q_part[:matches[0].start()].strip()
        for m in matches:
            opt_text = re.sub(r'\s+', ' ', m.group(2)).strip()
            # Remove exam info from options
            opt_text = re.sub(r'\s*(UPPCL|UPRVUNL|YCT|Shift|Bihar|S\.?S\.?C\.?|CPO|PGT|TRE|Exam|DSSSB|EMRS|ARO|Alld|HC,|\d{1,2}\.\d{1,2}\.\d{2,4}).*$', '', opt_text, flags=re.I)
            # Also clean trailing punctuation and whitespace
            opt_text = opt_text.rstrip(' ,')
            if opt_text:
                options[m.group(1).upper()] = opt_text
    else:
        question_text = q_part.strip()

    question_text = re.sub(r'\s+', ' ', question_text).strip()

    # Extract answer
    answer = None
    if ans_part:
        ans_match = re.search(r'\(?([a-dA-D])\)?', ans_part)
        if ans_match:
            answer = ans_match.group(1).upper()

    if len(question_text) < 5:
        return None

    return {
        'question_no': q_num,
        'question': question_text,
        'options': options,
        'answer': answer,
        'page': page_num
    }


def extract_multicolumn(pdf_path, start_page, end_page):
    """Extract from multi-column PDF using coordinate-based approach"""
    questions = []

    with pdfplumber.open(pdf_path) as pdf:
        end_page = min(len(pdf.pages), end_page)

        for page_num in range(start_page, end_page):
            page = pdf.pages[page_num]
            left_text, right_text = extract_column_text(page)

            # Parse each column
            left_qs = parse_questions_from_text(left_text, page_num + 1)
            right_qs = parse_questions_from_text(right_text, page_num + 1)

            questions.extend(left_qs)
            questions.extend(right_qs)

    return questions


def extract_singlecolumn(pdf_path, start_page, end_page):
    """Extract from single-column PDF using pymupdf4llm"""
    md_text = pymupdf4llm.to_markdown(
        pdf_path,
        pages=list(range(start_page, end_page)),
        show_progress=True
    )
    return parse_questions_from_text(md_text, start_page + 1)


def smart_extract(pdf_path, start_page, end_page):
    """Intelligently extract MCQs using best method for the PDF"""

    # Detect layout
    layout = detect_layout(pdf_path, start_page)
    print(f"📐 Detected layout: {layout}")

    if layout == "multi-column":
        print("   Using column-based extraction...")
        questions = extract_multicolumn(pdf_path, start_page, end_page)
    else:
        print("   Using ML-based extraction...")
        questions = extract_singlecolumn(pdf_path, start_page, end_page)

    # Validate and deduplicate
    unique = {}
    for q in questions:
        key = q['question_no']
        if key not in unique or len(q['options']) > len(unique[key]['options']):
            unique[key] = q

    return sorted(unique.values(), key=lambda x: x['question_no'])


def main():
    parser = argparse.ArgumentParser(description='Smart MCQ Parser - auto-detects format')
    parser.add_argument('--start', type=int, default=172, help='Start page (1-indexed)')
    parser.add_argument('--end', type=int, default=200, help='End page (1-indexed)')
    parser.add_argument('--pdf', type=str, default=PDF_PATH, help='PDF file path')
    parser.add_argument('--output', type=str, default=OUTPUT_JSON, help='Output JSON file')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print("Smart MCQ Parser - Auto Format Detection")
    print(f"{'='*70}\n")
    print(f"📄 Processing pages {args.start} to {args.end}...")

    # Extract (convert to 0-indexed)
    questions = smart_extract(args.pdf, args.start - 1, args.end)

    print(f"\n✅ Found {len(questions)} unique questions")

    # Stats
    with_opts = sum(1 for q in questions if len(q['options']) >= 4)
    with_ans = sum(1 for q in questions if q['answer'])
    print(f"   With 4 options: {with_opts}/{len(questions)}")
    print(f"   With answers: {with_ans}/{len(questions)}")

    # Save
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved to {args.output}")

    # Samples
    print(f"\n📌 Sample Questions:")
    print(f"{'='*70}")
    for q in questions[:3]:
        print(f"\n[Page {q['page']}] Q{q['question_no']}: {q['question'][:80]}...")
        for k, v in sorted(q['options'].items()):
            print(f"  {k}) {v[:50]}{'...' if len(v) > 50 else ''}")
        print(f"  ✓ Answer: {q.get('answer', 'N/A')}")


if __name__ == "__main__":
    main()
