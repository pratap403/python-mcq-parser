"""
Count how many questions are actually in pages 151-161
"""
import pdfplumber
import re

PDF_PATH = "C:\\Users\\Akshaypratap\\Desktop\\pdf\\files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"

def count_questions_on_page(page_num):
    """Count questions on a specific page"""
    
    with pdfplumber.open(PDF_PATH) as pdf:
        page = pdf.pages[page_num]
        text = page.extract_text()
        
        # Find all question numbers
        # Pattern: number followed by dot at start of line or after newline
        question_pattern = r'(?:^|\n)(\d+)\.\s+'
        matches = re.findall(question_pattern, text)
        
        return matches

def main():
    print(f"\n{'='*70}")
    print("Question Count Analysis: Pages 151-161")
    print(f"{'='*70}\n")
    
    total_questions = []
    
    for page_num in range(150, 161):  # Pages 151-161 (0-indexed)
        questions = count_questions_on_page(page_num)
        
        if questions:
            print(f"Page {page_num + 1}: Found {len(questions)} question numbers")
            print(f"  Question numbers: {', '.join(questions[:20])}")
            if len(questions) > 20:
                print(f"  ... and {len(questions) - 20} more")
            print()
            
            total_questions.extend(questions)
    
    print(f"{'='*70}")
    print(f"TOTAL: {len(total_questions)} question numbers found across all pages")
    print(f"{'='*70}\n")
    
    # Show unique question numbers
    unique_qnos = sorted(set(int(q) for q in total_questions))
    print(f"Unique question numbers: {len(unique_qnos)}")
    print(f"Range: Q{min(unique_qnos)} to Q{max(unique_qnos)}")
    
    # Show first 30
    print(f"\nFirst 30 unique question numbers:")
    print(', '.join(str(q) for q in unique_qnos[:30]))

if __name__ == "__main__":
    main()

