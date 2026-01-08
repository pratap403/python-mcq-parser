"""
Debug why Q5, Q6, Q7 are not being extracted
"""
import re

# This is the RIGHT COLUMN text from page 151
right_text = """Languages
4. Which of the following are computer
languages?
1. Cobra 2. Python
3. Squirrel 4. Java
Select the correct answer using the codes given
below.
(a) Only 1 and (b) Only 3 and
Only 1, 2 and 3 (d) All of the above (c)
69th BPSC (Pre) 2023
Ans. (d) : Computer language or programming language
is an artificial language which is designed in such a way
that it can express various computations required for
any work. Programming language is especially used
with computers. At present there are about 2500
programming languages in which Pascal, Basic Fortran,
C++, Java, JavaScript, Python, Lisp, Cobra, Squirrel,
etc. are prominent.
5. Which was one of the first operating systems to
be written in a high level programming
language, namely C?
(a) Solaris (b) Symbian
(c) Unix (d) Windows
UPASI 05.12.2021 Shift-I
Ans. (c) : Unix Operating system is written in C and
assembly language, its first version was released in
1971.
6. Which of the following statements is/are false?
(i) Compiler generates executable codes.
(ii) Assembler can be used to translate high
level language code into machine code.
(a) Neither (i) nor (ii) (b) Only (i)
(c) (i) and (ii) both (d) Only (ii)
Bihar PGT TRE 2.0, 15.12.2023
UPPCL Executive Assistant 23.11.2022, Shift-II
Ans. (d) : The compiler converts high-level language
into machine language and executes the entire code
program in one go.
An assembler is a kind of language processor. It is used
to translate the assembly language into machine
language.
7. Which of the following functions are performed
by a user interface?
(i) Accepting user input
(ii) Displaying output
(a) Both (i) and (ii) (b) Neither (i) and (ii)
(c) Only (ii) (d) Only (i)
UPPCL Executive Assistant 23.11.2022, Shift-II
YCT
151 / 592"""

# Split by question numbers (1-3 digits only)
parts = re.split(r'\n(\d{1,3})\.\s+', right_text)

print(f"Total parts: {len(parts)}")
print(f"\n{'='*70}")

for i in range(0, len(parts)):
    print(f"\nPart {i}: {parts[i][:100]}...")
    
print(f"\n{'='*70}")
print("ANALYZING EACH POTENTIAL QUESTION")
print(f"{'='*70}")

for i in range(1, len(parts), 2):
    if i + 1 >= len(parts):
        break
    
    qno = parts[i]
    content = parts[i + 1]
    
    print(f"\n--- Q{qno} ---")
    print(f"Content (first 200 chars): {content[:200]}")
    
    # Check for options
    has_options = re.search(r'\([a-d]\)', content, re.IGNORECASE)
    print(f"Has options: {bool(has_options)}")
    
    # Try inline pattern
    option_pattern_inline = r'\(([a-d])\)\s+([^()]+?)(?=\s*\([a-d]\)|$)'
    matches_inline = list(re.finditer(option_pattern_inline, content, re.IGNORECASE | re.DOTALL))
    print(f"Inline matches: {len(matches_inline)}")
    
    for m in matches_inline[:4]:
        print(f"  {m.group(1)}: {m.group(2)[:50]}...")

