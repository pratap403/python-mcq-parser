"""
MCQ Parser for GATE Academy PDFs
Extracts questions in Q.1, Q.2 format with (A), (B), (C), (D) options
"""
import pdfplumber
import re
import json
import argparse
from pathlib import Path


def extract_questions_from_page(page, page_num):
    """Extract MCQ questions from a single page"""
    text = page.extract_text()
    if not text:
        return []
    
    questions = []
    
    # Split by question pattern: Q.1, Q.2, etc.
    parts = re.split(r'\n(Q\.\d+)\s+', text)
    
    if len(parts) < 2:
        return questions
    
    # First part is header/junk, skip it
    i = 1
    while i < len(parts) - 1:
        q_marker = parts[i]  # e.g., "Q.1"
        content = parts[i + 1]
        
        # Extract question number
        q_num_match = re.search(r'Q\.(\d+)', q_marker)
        if not q_num_match:
            i += 2
            continue
        
        q_num = int(q_num_match.group(1))
        
        # Parse the question
        parsed = parse_single_question(q_num, content, page_num)
        if parsed:
            questions.append(parsed)
        
        i += 2
    
    return questions


def parse_single_question(q_num, content, page_num):
    """Parse a single MCQ question"""
    
    # Check if it has options
    has_options = re.search(r'\([A-D]\)', content)
    if not has_options:
        return None
    
    # Find where options start
    first_option = re.search(r'\n\([A-D]\)', content)
    if not first_option:
        return None
    
    # Split into question text and options section
    question_text = content[:first_option.start()].strip()
    options_section = content[first_option.start():]
    
    # Extract options - pattern: (A) text until next (B) or end
    option_pattern = r'\(([A-D])\)\s+(.*?)(?=\n\([A-D]\)|$)'
    option_matches = re.findall(option_pattern, options_section, re.DOTALL)
    
    if len(option_matches) < 2:
        return None
    
    # Build options dict
    options = {}
    for letter, text in option_matches:
        # Clean option text
        opt_text = ' '.join(text.split())
        opt_text = opt_text.strip()

        # Remove common section headers that leak into options
        opt_text = re.sub(r'Self-Practice Questions\s*:.*$', '', opt_text, flags=re.IGNORECASE)
        opt_text = re.sub(r'Classroom Practice Questions\s*:.*$', '', opt_text, flags=re.IGNORECASE)
        opt_text = re.sub(r'Previous Year Questions\s*:.*$', '', opt_text, flags=re.IGNORECASE)
        opt_text = opt_text.strip()

        if opt_text:
            options[letter] = opt_text
    
    # Clean question text
    question_text = ' '.join(question_text.split())
    
    # Try to find answer (if provided)
    # Some PDFs have answers at the end or in separate section
    answer = None
    ans_match = re.search(r'(?:Ans(?:wer)?\.?\s*[:.]?\s*\(?([A-D])\)?)', content, re.IGNORECASE)
    if ans_match:
        answer = ans_match.group(1).upper()
    
    # Validate
    if len(question_text) > 10 and len(options) >= 2:
        return {
            "question_no": q_num,
            "question": question_text,
            "options": options,
            "answer": answer,
            "page": page_num
        }
    
    return None


def extract_all_questions(pdf_path, start_page=0, end_page=None):
    """Extract all questions from PDF"""
    
    all_questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        
        if end_page is None:
            end_page = total_pages - 1
        else:
            end_page = min(end_page - 1, total_pages - 1)
        
        start_page = max(0, start_page - 1)
        
        print(f"📄 Processing pages {start_page + 1} to {end_page + 1}...")
        
        for page_num in range(start_page, end_page + 1):
            if (page_num - start_page) % 10 == 0:
                print(f"   Page {page_num + 1}/{end_page + 1}...")
            
            page = pdf.pages[page_num]
            questions = extract_questions_from_page(page, page_num + 1)
            all_questions.extend(questions)
    
    # Remove duplicates
    unique_questions = []
    seen = set()
    for q in all_questions:
        key = (q['question_no'], q['question'][:50])
        if key not in seen:
            seen.add(key)
            unique_questions.append(q)
    
    return unique_questions


def main():
    parser = argparse.ArgumentParser(description='GATE Academy MCQ Parser')
    parser.add_argument('pdf', help='Path to PDF file')
    parser.add_argument('--start', '-s', type=int, default=1, help='Start page (default: 1)')
    parser.add_argument('--end', '-e', type=int, help='End page (default: all)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print("GATE Academy MCQ Parser")
    print(f"{'='*70}\n")
    
    # Extract questions
    questions = extract_all_questions(args.pdf, args.start, args.end)
    
    print(f"\n✅ Found {len(questions)} unique questions")
    
    # Statistics
    with_4_opts = sum(1 for q in questions if len(q['options']) == 4)
    with_ans = sum(1 for q in questions if q['answer'])
    
    print(f"   Questions with 4 options: {with_4_opts}/{len(questions)}")
    print(f"   Questions with answers: {with_ans}/{len(questions)}")
    
    # Save to JSON
    if not args.output:
        args.output = Path(args.pdf).stem + "_mcqs.json"
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {args.output}")
    
    # Show samples
    if questions:
        print(f"\n📌 Sample Questions:")
        print("="*70)
        for q in questions[:5]:
            print(f"\n[Page {q['page']}] Q{q['question_no']}: {q['question'][:80]}...")
            for k, v in q['options'].items():
                marker = " ✓" if k == q.get('answer') else ""
                print(f"  {k}) {v[:70]}{marker}")


if __name__ == "__main__":
    main()

