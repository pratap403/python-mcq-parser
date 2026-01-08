import pdfplumber
import re
import json
import sys

class AdaptiveMCQParser:
    """Adaptive parser that handles different PDF formats"""
    
    def __init__(self, pdf_path, output_json="mcqs_output.json"):
        self.pdf_path = pdf_path
        self.output_json = output_json
        self.config = self.detect_format()
    
    def detect_format(self):
        """Auto-detect PDF format and return configuration"""
        print("🔍 Detecting PDF format...")
        
        config = {
            'has_columns': False,
            'option_pattern': r'\(([a-dA-D])\)\s*',
            'question_pattern': r'^(\d+)\.\s+',
            'has_answer_sheet': False,
            'is_bilingual': False
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            
            # Detect columns
            words = page.extract_words()
            if words:
                mid_x = page.width / 2
                left_count = sum(1 for w in words if w['x0'] < mid_x)
                right_count = sum(1 for w in words if w['x0'] >= mid_x)
                
                if left_count > 50 and right_count > 50:
                    config['has_columns'] = True
                    print("   ✓ Multi-column layout detected")
                else:
                    print("   ✓ Single-column layout detected")
            
            # Detect option style
            if re.search(r'\([a-dA-D]\)', text):
                config['option_pattern'] = r'\(([a-dA-D])\)\s*'
                print("   ✓ Option style: (a) (b) (c) (d)")
            elif re.search(r'^[a-dA-D]\)', text, re.MULTILINE):
                config['option_pattern'] = r'^([a-dA-D])\)\s*'
                print("   ✓ Option style: a) b) c) d)")
            elif re.search(r'^[a-dA-D]\.', text, re.MULTILINE):
                config['option_pattern'] = r'^([a-dA-D])\.\s*'
                print("   ✓ Option style: a. b. c. d.")
            
            # Check for answer sheet
            full_text = '\n'.join(p.extract_text() for p in pdf.pages)
            if re.search(r'ANSWER[-\s]*SHEET|ANSWER[-\s]*KEY', full_text, re.IGNORECASE):
                config['has_answer_sheet'] = True
                print("   ✓ Answer sheet found")
            
            # Check bilingual
            if any(ord(c) > 127 for c in text):
                config['is_bilingual'] = True
                print("   ✓ Bilingual content detected")
        
        return config
    
    def extract_text(self):
        """Extract text based on detected format"""
        if self.config['has_columns']:
            return self._extract_columns()
        else:
            return self._extract_simple()
    
    def _extract_simple(self):
        """Simple single-column extraction"""
        with pdfplumber.open(self.pdf_path) as pdf:
            texts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text and not re.search(r'ANSWER[-\s]*SHEET', text, re.IGNORECASE):
                    texts.append(text)
            return '\n\n'.join(texts)
    
    def _extract_columns(self):
        """Multi-column extraction"""
        all_text = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                width = page.width
                height = page.height
                mid = width / 2
                
                # Left column
                left_bbox = (0, 0, mid - 20, height)
                left_text = page.crop(left_bbox).extract_text()
                
                # Right column
                right_bbox = (mid + 20, 0, width, height)
                right_text = page.crop(right_bbox).extract_text()
                
                if left_text and "ANSWER" not in left_text:
                    all_text.append(left_text)
                if right_text and "ANSWER" not in right_text:
                    all_text.append(right_text)
        
        return '\n\n'.join(all_text)
    
    def parse_mcqs(self, text):
        """Parse MCQs using detected patterns"""
        blocks = text.split('\n\n') if self.config['has_columns'] else [text]
        mcqs = []
        
        for block in blocks:
            lines = block.split('\n')
            
            # Find question starts
            question_starts = []
            for i, line in enumerate(lines):
                if re.match(self.config['question_pattern'], line.strip()):
                    question_starts.append(i)
            
            # Parse each question
            for idx in range(len(question_starts)):
                start = question_starts[idx]
                end = question_starts[idx + 1] if idx + 1 < len(question_starts) else len(lines)
                
                question_lines = lines[start:end]
                parsed = self._parse_question(question_lines)
                
                if parsed:
                    mcqs.append(parsed)
        
        return mcqs

    def _parse_question(self, lines):
        """Parse a single question from lines"""
        if not lines:
            return None

        first_line = lines[0].strip()
        qmatch = re.match(self.config['question_pattern'], first_line)

        if not qmatch:
            return None

        qno = int(qmatch.group(1))
        question_parts = [first_line.split('.', 1)[1].strip()]
        options = {}

        # Process remaining lines
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Check if line has options
            has_options = re.search(self.config['option_pattern'], line)

            if has_options:
                # Extract options
                pattern = self.config['option_pattern'] + r'([^()]+?)(?=\s*' + self.config['option_pattern'] + r'|$)'
                for match in re.finditer(pattern, line):
                    key = match.group(1).upper()
                    value = match.group(2).strip() if len(match.groups()) > 1 else match.group(0).split(')', 1)[-1].strip()
                    if value and key not in options:
                        options[key] = value
            else:
                # Part of question
                question_parts.append(line)

        if len(options) >= 2:
            return {
                "question_no": qno,
                "question": ' '.join(question_parts),
                "options": options,
                "answer": None
            }

        return None

    def extract_answers(self):
        """Extract answers from answer sheet"""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and re.search(r'ANSWER[-\s]*SHEET|ANSWER[-\s]*KEY', text, re.IGNORECASE):
                    parts = re.split(r'ANSWER[-\s]*(?:SHEET|KEY)', text, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        answer_text = parts[1]
                        answers = {}
                        for m in re.finditer(r'(\d+)\.\s*\(([a-dA-D*])\)', answer_text):
                            answers[int(m.group(1))] = m.group(2).upper()
                        return answers
        return {}

    def parse(self):
        """Main parsing method"""
        print(f"\n📄 Parsing: {self.pdf_path}")

        # Extract text
        print("📝 Extracting text...")
        text = self.extract_text()

        # Parse questions
        print("🔍 Parsing questions...")
        mcqs = self.parse_mcqs(text)
        print(f"   Found {len(mcqs)} questions")

        # Extract answers
        if self.config['has_answer_sheet']:
            print("📋 Extracting answers...")
            answers = self.extract_answers()
            print(f"   Found {len(answers)} answers")

            # Attach answers
            for q in mcqs:
                if q["question_no"] in answers:
                    q["answer"] = answers[q["question_no"]]

        # Sort by question number
        mcqs = sorted(mcqs, key=lambda x: x["question_no"])

        # Save
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(mcqs, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Saved {len(mcqs)} questions to {self.output_json}")

        # Show sample
        if mcqs:
            print(f"\n📌 Sample Question:")
            q = mcqs[0]
            print(f"   Q{q['question_no']}: {q['question'][:60]}...")
            print(f"   Options: {list(q['options'].keys())}")
            print(f"   Answer: {q.get('answer', 'N/A')}")

        return mcqs

def main():
    if len(sys.argv) < 2:
        print("Usage: python mcq-parser-adaptive.py <pdf_path> [output.json]")
        print("\nUsing default PDF...")
        pdf_path = "C:\\Users\\Akshaypratap\\Desktop\\pdf\\files\\YCT_Computer_Chapterwise_Solved_Papers_English_M_250906_083412.pdf"
        output = "mcqs_adaptive_alias.json"
    else:
        pdf_path = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else "mcqs_adaptive.json"

    parser = AdaptiveMCQParser(pdf_path, output)
    parser.parse()

if __name__ == "__main__":
    main()

