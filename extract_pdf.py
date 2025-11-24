"""
Extract text from KIManual2025.pdf and save to knowledge base.
"""
import PyPDF2
from pathlib import Path

def extract_pdf_text(pdf_path: str, output_path: str):
    """Extract text from PDF and save to text file."""
    print(f"Extracting text from {pdf_path}...")
    
    # Open PDF
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        print(f"Found {len(pdf_reader.pages)} pages")
        
        # Extract text from all pages
        all_text = []
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text.strip():
                all_text.append(f"--- Page {i+1} ---\n{text}\n")
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i+1} pages...")
        
        # Combine all text
        full_text = "\n".join(all_text)
        
        # Save to output file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(full_text, encoding='utf-8')
        
        print(f"\n✓ Extracted {len(full_text)} characters")
        print(f"✓ Saved to {output_path}")
        
        return len(full_text)

if __name__ == "__main__":
    pdf_path = "KIManual2025.pdf"
    kb_path = "./kb/knowledge_base.txt"
    
    extract_pdf_text(pdf_path, kb_path)
