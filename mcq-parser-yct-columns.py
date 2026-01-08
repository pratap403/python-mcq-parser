"""
YCT PDF Parser - CORRECT Column-Based Approach
Uses word positions to properly separate left and right columns
"""
import pdfplumber
import re
import json

PDF_PATH = "D:\\pdf_files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"
OUTPUT_JSON = "mcqs_yct_columns.json"

def extract_column_text(page):
    """Extract text from left and right columns separately using word positions"""
    
    words = page.extract_words()
    if not words:
        return "", ""
    
    # Determine column boundary (middle of page)
    page_width = page.width
    column_boundary = page_width / 2
    
    # Separate words into left and right columns
    left_words = []
    right_words = []
    
    for word in words:
        x = word['x0']
        y = word['top']
        text = word['text']
        
        if x < column_boundary:
            left_words.append((y, x, text))
        else:
            right_words.append((y, x, text))
    
    # Sort by y-position (top to bottom), then x-position (left to right)
    left_words.sort(key=lambda w: (w[0], w[1]))
    right_words.sort(key=lambda w: (w[0], w[1]))
    
    # Reconstruct text with line breaks
    def words_to_text(words):
        if not words:
            return ""
        
        lines = []
        current_line = []
        current_y = words[0][0]
        
        for y, x, text in words:
            # If y-position changed significantly, start new line
            if abs(y - current_y) > 3:  # 3 points tolerance for better line detection
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y
            else:
                current_line.append(text)
        
        # Add last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    left_text = words_to_text(left_words)
    right_text = words_to_text(right_words)
    
    return left_text, right_text

def parse_column_questions(text, page_num):
    """Parse questions from a single column of text"""

    questions = []

    # Split by question numbers (e.g., "112.", "113.")
    # Only match 1-3 digit numbers to avoid years like 1971
    parts = re.split(r'\n(\d{1,3})\.\s+', text)

    i = 1
    while i < len(parts):
        if i + 1 >= len(parts):
            break

        qno = int(parts[i])
        content = parts[i + 1]

        # Skip if question number is unreasonably high (likely not a question)
        if qno > 500:
            i += 2
            continue

        # Check if content has options pattern
        has_options = re.search(r'\([a-d]\)', content, re.IGNORECASE)

        # If no options found, this might be part of previous question (numbered list)
        # Try to merge with next parts until we find options
        if not has_options and i + 3 < len(parts):
            merged_content = content
            j = i + 2
            while j < len(parts) and j < i + 10:  # Look ahead max 5 parts
                if j + 1 < len(parts):
                    next_num = int(parts[j]) if parts[j].isdigit() else 0

                    # Only merge if next number is small (likely a list item like "1. Cobra")
                    if next_num <= 10:
                        merged_content += f"\n{parts[j]}. {parts[j + 1]}"

                        # Check if merged content now has options
                        if re.search(r'\([a-d]\)', merged_content, re.IGNORECASE):
                            # Found options! Use merged content
                            content = merged_content
                            has_options = True
                            i = j  # Will be incremented by 2 at end of loop
                            break
                    else:
                        break  # Stop merging if we hit a real question number (> 10)
                j += 2

        if not has_options:
            i += 2
            continue

        # Parse this question
        parsed = parse_single_question(qno, content, page_num)
        if parsed:
            questions.append(parsed)

        i += 2

    return questions

def parse_single_question(qno, content, page_num):
    """Parse a single question with vertical or inline options"""

    # Find answer first and truncate content
    ans_match = re.search(r'\nAns\.?\s*[:.]?\s*\(([a-d])\)', content, re.IGNORECASE)
    answer = None
    if ans_match:
        answer = ans_match.group(1).upper()
        # Cut content at answer to avoid explanation
        content = content[:ans_match.start()]

    # Try Method 1: Vertical options (each on new line)
    option_pattern_vertical = r'\n\(([a-d])\)\s+'
    parts_vertical = re.split(option_pattern_vertical, content, flags=re.IGNORECASE)

    # Try Method 2: Inline options (all on same/few lines)
    # Find all (a), (b), (c), (d) patterns - but not (i), (ii), etc.
    # Match option letter followed by text until next option or end
    option_pattern_inline = r'\(([a-d])\)\s+(.+?)(?=\s*\([a-d]\)\s+|\nAns|\n\d+\.\s|$)'
    matches_inline = list(re.finditer(option_pattern_inline, content, re.IGNORECASE | re.DOTALL))

    # Decide which method to use
    use_vertical = len(parts_vertical) >= 5  # At least 2 options
    use_inline = len(matches_inline) >= 3  # At least 3 options

    options = {}
    question_text = ""

    if use_vertical and len(parts_vertical) >= len(matches_inline) * 2:
        # Use vertical parsing
        question_text = parts_vertical[0].strip()

        # Extract options - parts are: [question, 'a', option_a_text, 'b', option_b_text, ...]
        for i in range(1, len(parts_vertical), 2):
            if i + 1 < len(parts_vertical):
                key = parts_vertical[i].upper()
                value = parts_vertical[i + 1].strip()

                # Stop at next option or end
                next_option = re.search(r'\n\(([a-d])\)', value, re.IGNORECASE)
                if next_option:
                    value = value[:next_option.start()].strip()

                # Clean option
                value = clean_text(value)

                if len(value) > 0 and len(value) < 500:
                    options[key] = value

    elif use_inline:
        # Use inline parsing
        # Find where first option starts
        first_match = matches_inline[0]
        question_text = content[:first_match.start()].strip()

        # Extract options
        for match in matches_inline:
            key = match.group(1).upper()
            value = match.group(2).strip()

            # Clean option
            value = clean_text(value)

            if len(value) > 0 and len(value) < 500:
                options[key] = value

    else:
        return None

    # Clean question text
    question_text = clean_text(question_text)
    
    # Validate
    if len(question_text) > 15 and len(options) >= 3:
        return {
            "question_no": qno,
            "question": question_text,
            "options": options,
            "answer": answer,
            "page": page_num
        }
    
    return None

def clean_text(text):
    """Clean text - remove exam codes and extra info"""
    # Remove exam source codes (e.g., "UPPCL Executive Assistant 23.11.2022, Shift-II")
    text = re.sub(r'[A-Z]{2,}[\sA-Za-z\.,\-:()]+\d{2}[-./]\d{2}[-./]\d{4}[,\s]*Shift[-\s]*[IVX]+', '', text)
    text = re.sub(r'[A-Z]{2,}[\sA-Za-z\.,\-:()]+\d{2}[-./]\d{2}[-./]\d{4}', '', text)
    text = re.sub(r'[A-Z]{2,}[\sA-Za-z\.,\-:()]+\d{4}', '', text)
    text = re.sub(r',?\s*Shift[-\s]*[IVX]+', '', text)
    text = re.sub(r'Stage\s+Ist', '', text)

    # Remove YCT page numbers (e.g., "YCT 151 / 592")
    text = re.sub(r'YCT\s+\d+\s*/\s*\d+', '', text)

    # Remove Bihar PGT TRE patterns
    text = re.sub(r'Bihar\s+PGT\s+TRE\s+[\d.]+,?\s*\d{2}[-./]\d{2}[-./]\d{4}', '', text)

    # Remove BPSC patterns
    text = re.sub(r'\d+[a-z]*\s+BPSC\s*\([^)]+\)\s*\d{4}', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text.strip()

def extract_all_questions(pdf_path, start_page=10, num_pages=30):
    """Extract questions from PDF using column-based approach"""
    
    print(f"📄 Extracting from pages {start_page+1} to {start_page+num_pages}...")
    print(f"   Using column-based extraction...\n")
    
    all_questions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        end_page = min(len(pdf.pages), start_page + num_pages)
        
        for page_num in range(start_page, end_page):
            if page_num % 5 == 0:
                print(f"   Page {page_num+1}/{end_page}...")
            
            page = pdf.pages[page_num]
            
            # Extract left and right columns separately
            left_text, right_text = extract_column_text(page)
            
            # Parse questions from each column
            left_questions = parse_column_questions(left_text, page_num + 1)
            right_questions = parse_column_questions(right_text, page_num + 1)
            
            all_questions.extend(left_questions)
            all_questions.extend(right_questions)
    
    return all_questions

def main():
    print(f"\n{'='*70}")
    print("YCT PDF Parser - Column-Based Extraction")
    print(f"{'='*70}\n")
    
    # Extract questions from pages 172 to 200
    questions = extract_all_questions(PDF_PATH, start_page=171, num_pages=29)
    
    print(f"\n✅ Found {len(questions)} questions")
    
    # Remove duplicates
    unique = {}
    for q in questions:
        key = (q['question_no'], q['question'][:30])
        if key not in unique or len(q['options']) > len(unique[key]['options']):
            unique[key] = q
    
    questions = list(unique.values())
    questions.sort(key=lambda x: (x['page'], x['question_no']))
    
    print(f"   {len(questions)} unique questions")
    
    # Save
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved to {OUTPUT_JSON}")
    
    # Statistics
    with_4_opts = sum(1 for q in questions if len(q['options']) == 4)
    with_answer = sum(1 for q in questions if q['answer'])
    
    print(f"\n📊 Statistics:")
    print(f"   Questions with 4 options: {with_4_opts}/{len(questions)}")
    print(f"   Questions with answers: {with_answer}/{len(questions)}")
    
    # Show samples
    print(f"\n📌 Sample Questions:")
    print(f"{'='*70}\n")
    
    for q in questions[:5]:
        print(f"[Page {q['page']}] Q{q['question_no']}: {q['question']}")
        for k, v in sorted(q['options'].items()):
            print(f"  {k}) {v}")
        print(f"  ✓ Answer: {q.get('answer', 'N/A')}\n")

if __name__ == "__main__":
    main()

