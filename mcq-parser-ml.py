"""
MCQ Parser using pymupdf4llm - ML-based PDF to Markdown conversion
Handles complex layouts, columns, and varying formats automatically
"""
import pymupdf4llm
import pymupdf
import re
import json
import argparse

PDF_PATH = "D:\\pdf_files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"
OUTPUT_JSON = "mcqs_extracted.json"


def extract_markdown(pdf_path, start_page=0, end_page=None):
    """Extract PDF pages as clean Markdown text"""
    
    doc = pymupdf.open(pdf_path)
    if end_page is None:
        end_page = len(doc)
    
    print(f"📄 Extracting pages {start_page + 1} to {end_page}...")
    
    # Extract specific pages as markdown
    md_text = pymupdf4llm.to_markdown(
        pdf_path,
        pages=list(range(start_page, end_page)),
        show_progress=True
    )
    
    return md_text


def parse_mcqs_from_markdown(md_text):
    """Parse MCQs from markdown text"""

    questions = []

    # Split text into blocks - each question starts with **NUMBER.** or **NUMBER.**
    # Pattern: **172. Question text** or **172.** **Question text**

    # First, let's split by question patterns
    # Questions appear as: **172. Select the INVALID...**
    question_blocks = re.split(r'(?=\*\*\d+[\.\)]\s*\*?\*?)', md_text)

    for block in question_blocks:
        if not block.strip():
            continue

        # Try to extract question number from start
        # Handles: **172. Question** or **176.** **Question**
        q_match = re.match(r'\*\*(\d+)[\.\)]\s*\*?\*?\s*(.+)', block, re.DOTALL)

        if q_match:
            q_num = int(q_match.group(1))
            rest = q_match.group(2)

            # Find where answer starts (to separate question from explanation)
            ans_split = re.split(r'\*\*Ans\.', rest, maxsplit=1)
            question_part = ans_split[0]
            answer_part = ans_split[1] if len(ans_split) > 1 else ""

            # Parse the question
            parsed = parse_single_question(q_num, question_part, answer_part)
            if parsed:
                questions.append(parsed)

    return questions


def parse_single_question(q_num, question_part, answer_part=""):
    """Parse a single question's text to extract question, options, and answer"""

    # Clean up markdown formatting
    text = question_part
    text = re.sub(r'\*\*', '', text)  # Remove bold markers
    text = text.strip()

    # Find options - they appear as: (a) text (b) text OR on separate lines
    options = {}

    # Pattern for inline options: (a) option1 (b) option2
    # Handle both inline and multiline options
    opt_pattern = re.compile(r'\(([a-dA-D])\)\s*([^(]+?)(?=\([a-dA-D]\)|$)', re.DOTALL)

    opt_matches = list(opt_pattern.finditer(text))

    question_text = text
    if opt_matches:
        # Question text is everything before first option
        question_text = text[:opt_matches[0].start()].strip()

        for match in opt_matches:
            letter = match.group(1).upper()
            opt_text = match.group(2).strip()
            # Clean up option text - remove line breaks and extra spaces
            opt_text = re.sub(r'\s+', ' ', opt_text).strip()
            # Remove any trailing exam info
            opt_text = re.sub(r'\s*UPPCL.*$', '', opt_text, flags=re.IGNORECASE)
            opt_text = re.sub(r'\s*UPRVUNL.*$', '', opt_text, flags=re.IGNORECASE)
            if opt_text:
                options[letter] = opt_text

    # Clean question text
    question_text = re.sub(r'\s+', ' ', question_text).strip()

    # Extract answer from answer part
    answer = None
    if answer_part:
        # Multiple patterns for answers:
        # Pattern 1: (** c **)  - with markdown
        # Pattern 2: (c) or (d): - simple
        # Pattern 3: : (c) - with colon before
        patterns = [
            r'\(\s*\*?\*?\s*([a-dA-D])\s*\*?\*?\s*\)',  # (** c **) or ( c )
            r':\s*\(?([a-dA-D])\)?',                      # : (c) or :c
            r'\(\s*([a-dA-D])\s*\)',                      # simple (c)
        ]
        for pattern in patterns:
            ans_match = re.search(pattern, answer_part)
            if ans_match:
                answer = ans_match.group(1).upper()
                break

    if not question_text or len(question_text) < 5:
        return None

    return {
        'question_no': q_num,
        'question': question_text,
        'options': options,
        'answer': answer
    }


def main():
    parser = argparse.ArgumentParser(description='Extract MCQs from PDF using ML-based parsing')
    parser.add_argument('--start', type=int, default=172, help='Start page (1-indexed)')
    parser.add_argument('--end', type=int, default=200, help='End page (1-indexed)')
    parser.add_argument('--pdf', type=str, default=PDF_PATH, help='PDF file path')
    parser.add_argument('--output', type=str, default=OUTPUT_JSON, help='Output JSON file')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print("MCQ Parser - ML-based (pymupdf4llm)")
    print(f"{'='*70}\n")
    
    # Extract markdown (convert to 0-indexed)
    md_text = extract_markdown(args.pdf, args.start - 1, args.end)
    
    # Save raw markdown for debugging
    with open('extracted_raw.md', 'w', encoding='utf-8') as f:
        f.write(md_text)
    print(f"📝 Raw markdown saved to extracted_raw.md")
    
    # Parse MCQs
    questions = parse_mcqs_from_markdown(md_text)
    
    print(f"\n✅ Found {len(questions)} questions")
    
    # Statistics
    with_opts = sum(1 for q in questions if len(q['options']) >= 2)
    with_answer = sum(1 for q in questions if q['answer'])
    
    print(f"   With options: {with_opts}/{len(questions)}")
    print(f"   With answers: {with_answer}/{len(questions)}")
    
    # Save
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved to {args.output}")
    
    # Show samples
    print(f"\n📌 Sample Questions:")
    print(f"{'='*70}")
    for q in questions[:3]:
        print(f"\nQ{q['question_no']}: {q['question'][:100]}...")
        for k, v in sorted(q['options'].items()):
            print(f"  {k}) {v[:50]}{'...' if len(v) > 50 else ''}")
        print(f"  ✓ Answer: {q.get('answer', 'N/A')}")


if __name__ == "__main__":
    main()

