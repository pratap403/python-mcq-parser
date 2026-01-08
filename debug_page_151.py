"""
Debug page 151 to see the actual text structure
"""
import pdfplumber
import re

PDF_PATH = "C:\\Users\\Akshaypratap\\Desktop\\pdf\\files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"

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
            if abs(y - current_y) > 3:  # 3 points tolerance
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

def main():
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[150]  # Page 151 (0-indexed)
        
        left_text, right_text = extract_column_text(page)
        
        print(f"\n{'='*70}")
        print("LEFT COLUMN - Page 151")
        print(f"{'='*70}\n")
        print(left_text[:2000])  # First 2000 chars
        
        print(f"\n\n{'='*70}")
        print("RIGHT COLUMN - Page 151")
        print(f"{'='*70}\n")
        print(right_text[:2000])  # First 2000 chars
        
        # Count question patterns
        print(f"\n\n{'='*70}")
        print("FULL RIGHT COLUMN TEXT")
        print(f"{'='*70}\n")
        print(right_text)

if __name__ == "__main__":
    main()

