"""
Debug why questions 2, 4, 5, 6, 7 are not being extracted
"""
import pdfplumber
import re

PDF_PATH = "C:\\Users\\Akshaypratap\\Desktop\\pdf\\files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"

def extract_column_text(page):
    """Extract text from left and right columns separately"""
    words = page.extract_words()
    if not words:
        return "", ""
    
    page_width = page.width
    column_boundary = page_width / 2
    
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
    
    left_words.sort(key=lambda w: (w[0], w[1]))
    right_words.sort(key=lambda w: (w[0], w[1]))
    
    def words_to_text(words):
        if not words:
            return ""
        
        lines = []
        current_line = []
        current_y = words[0][0]
        
        for y, x, text in words:
            if abs(y - current_y) > 3:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y
            else:
                current_line.append(text)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    left_text = words_to_text(left_words)
    right_text = words_to_text(right_words)
    
    return left_text, right_text

def analyze_question_extraction(text, column_name):
    """Analyze why questions are not being extracted"""
    
    print(f"\n{'='*70}")
    print(f"{column_name} - Question Extraction Analysis")
    print(f"{'='*70}\n")
    
    # Split by question numbers
    parts = re.split(r'\n(\d+)\.\s+', text)
    
    print(f"Total parts after split: {len(parts)}")
    print(f"Number of potential questions: {(len(parts) - 1) // 2}\n")
    
    for i in range(1, min(len(parts), 15), 2):  # Check first 7 questions
        if i + 1 >= len(parts):
            break
        
        qno = parts[i]
        content = parts[i + 1]
        
        # Check for options
        has_options = re.search(r'\([a-d]\)', content, re.IGNORECASE)
        option_matches = re.findall(r'\n\(([a-d])\)', content, re.IGNORECASE)
        
        # Check for answer
        has_answer = re.search(r'\nAns\.?\s*[:.]?\s*\(([a-d])\)', content, re.IGNORECASE)
        
        print(f"Q{qno}:")
        print(f"  Has options pattern: {bool(has_options)}")
        print(f"  Option markers found: {len(option_matches)} - {option_matches}")
        print(f"  Has answer: {bool(has_answer)}")
        print(f"  Content length: {len(content)} chars")
        print(f"  First 150 chars: {content[:150].replace(chr(10), ' ')}")
        print()

def main():
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[150]  # Page 151
        
        left_text, right_text = extract_column_text(page)
        
        analyze_question_extraction(left_text, "LEFT COLUMN")
        analyze_question_extraction(right_text, "RIGHT COLUMN")

if __name__ == "__main__":
    main()

