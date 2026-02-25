"""
Phase 1: PDF Document Parser for Early Intervention AI
Extracts structured data from EI documents into JSON format.

Documents:
1. SCGC_Milestones_that_Matter_Most_1-24_Months_3-page.pdf
2. Support_Communication_Development_02.pdf
3. text.txt

Output:
- milestones_structured.json
- coaching_strategies_structured.json
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber

# Directory paths
DOCS_DIR = Path("docs")
OUTPUT_DIR = Path("parsed_output")
OUTPUT_DIR.mkdir(exist_ok=True)


class MilestoneParser:
    """Parse milestone PDF into structured JSON."""
    
    DOMAINS = [
        "Language",
        "Play",
        "Social Interaction",
        "Emotional Regulation",
        "Self-Directed Learning"
    ]
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.milestones = []
    
    def extract_age_range(self, text: str) -> Optional[tuple]:
        """
        Extract age range from text like '9-10 MONTHS' or '11-12 MONTHS'.
        Returns (age_min, age_max, age_range_text)
        """
        # Pattern: "9-10 MONTHS" or "11-12 MONTHS" or "1-2 MONTHS"
        pattern = r'(\d+)\s*-\s*(\d+)\s+MONTHS?'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            age_min = int(match.group(1))
            age_max = int(match.group(2))
            age_range_text = f"{age_min}-{age_max} months"
            return (age_min, age_max, age_range_text)
        
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common header/footer patterns
        text = re.sub(r'Milestones that Matter Most', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    def identify_domain(self, text: str) -> Optional[str]:
        """Identify domain from text."""
        text_upper = text.upper()
        for domain in self.DOMAINS:
            if domain.upper() in text_upper:
                return domain
        return None
    
    def extract_thread(self, text: str) -> Optional[str]:
        """
        Extract thread name like 'Gestures & Meanings' or 'Sounds & Words'.
        Usually appears before milestone text, often with special formatting.
        """
        # Common thread patterns
        thread_patterns = [
            r'([A-Z][a-z]+(?:\s+[&]\s+[A-Z][a-z]+)+)',  # "Gestures & Meanings"
            r'([A-Z][a-z]+\s+&\s+[A-Z][a-z]+)',
            r'(Sounds?\s+&\s+Words?)',
            r'(Play\s+Skills?)',
            r'(Social\s+Skills?)',
            r'(Emotional\s+Skills?)',
        ]
        
        for pattern in thread_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_milestone_section(self, text: str, page_num: int) -> List[Dict]:
        """Parse a section of text into milestone entries."""
        milestones = []
        lines = text.split('\n')
        
        current_age_range = None
        current_domain = None
        current_thread = None
        
        i = 0
        while i < len(lines):
            line = self.clean_text(lines[i])
            if not line:
                i += 1
                continue
            
            # Check for age range (e.g., "9-10 MONTHS" or "9-10\nMONTHS")
            age_info = self.extract_age_range(line)
            if age_info:
                current_age_range = age_info
                i += 1
                continue
            
            # Check if next line completes the age range
            if i + 1 < len(lines):
                combined = line + " " + self.clean_text(lines[i + 1])
                age_info = self.extract_age_range(combined)
                if age_info:
                    current_age_range = age_info
                    i += 2
                    continue
            
            # Check for domain keywords
            domain = self.identify_domain(line)
            if domain:
                current_domain = domain
                i += 1
                continue
            
            # Look for thread + milestone pattern
            # Format: "Thread Name I can do something."
            # The thread is usually bold and followed by milestone starting with "I"
            if 'I can' in line or 'I am' in line or 'I use' in line or 'I enjoy' in line or 'I notice' in line or 'I watch' in line:
                # Try to separate thread from milestone text
                # Thread usually comes before "I"
                parts = re.split(r'\s+(I\s+)', line, maxsplit=1)
                
                if len(parts) >= 3:
                    thread = parts[0].strip()
                    milestone_text = parts[1] + parts[2]
                    
                    # If thread looks valid (short, title case)
                    if len(thread) < 50 and thread[0].isupper():
                        current_thread = thread
                    else:
                        # Thread might be from previous line
                        milestone_text = line
                else:
                    milestone_text = line
                
                if current_age_range and current_domain:
                    milestone = {
                        "source": "Milestones that Matter Most",
                        "age_range": current_age_range[2],
                        "age_min": current_age_range[0],
                        "age_max": current_age_range[1],
                        "domain": current_domain,
                        "thread": current_thread or "General",
                        "milestone_text": milestone_text.strip(),
                        "page": page_num
                    }
                    milestones.append(milestone)
            else:
                # Line might be a thread name (before milestone)
                # Threads are usually short, title case, no ending period
                if (len(line) < 50 and line[0].isupper() and 
                    not line.endswith('.') and len(line.split()) <= 5):
                    current_thread = line
            
            i += 1
        
        return milestones
    
    def parse(self) -> List[Dict]:
        """Main parsing method."""
        print(f"Parsing milestone PDF: {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    page_milestones = self.parse_milestone_section(text, page_num)
                    self.milestones.extend(page_milestones)
        
        print(f"Extracted {len(self.milestones)} milestones")
        return self.milestones


def extract_two_column_text(page) -> str:
    """
    Extract text from a two-column PDF page by cropping left and right columns separately.
    This prevents pdfplumber from merging text across columns.
    
    Args:
        page: pdfplumber page object
    
    Returns:
        Combined text: left column + right column
    """
    # Get page dimensions
    width = page.width
    height = page.height
    
    # Split page vertically at midpoint
    midpoint = width / 2
    
    # Define crop boxes (x0, top, x1, bottom)
    left_box = (0, 0, midpoint, height)
    right_box = (midpoint, 0, width, height)
    
    # Extract text from each column
    left_text = page.crop(left_box).extract_text() or ""
    right_text = page.crop(right_box).extract_text() or ""
    
    # Combine: left column first, then right column
    return left_text + "\n\n" + right_text


class CoachingStrategyParser:
    """Parse coaching strategies PDF into structured JSON with layout-aware extraction."""
    
    LAYER_MARKERS = {
        "1st Layer": "Layer 1",
        "2nd Layer": "Layer 2",
        "3rd Layer": "Layer 3"
    }
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.strategies = []
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess PDF text to fix common issues.
        - Fix hyphenated line breaks
        - Remove headers/footers
        - Join wrapped lines
        """
        # Remove common headers/footers
        text = re.sub(r'How Parents Can Support', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Social Communication Development', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Support Communication Development', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'©.*?\d{4}', '', text)  # Remove copyright
        
        # Fix hyphenated words at line breaks (e.g., "develop-\nment" → "development")
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Join lines that are part of same sentence (not ending in period/question/exclamation)
        lines = text.split('\n')
        processed_lines = []
        buffer = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if buffer:
                    processed_lines.append(buffer)
                    buffer = ""
                continue
            
            # If buffer exists and current line doesn't start with capital, continue sentence
            if buffer and line and not line[0].isupper():
                buffer += " " + line
            # If buffer ends with sentence terminator, save it
            elif buffer and buffer[-1] in '.!?':
                processed_lines.append(buffer)
                buffer = line
            # Otherwise add to buffer
            else:
                if buffer:
                    buffer += " " + line
                else:
                    buffer = line
        
        if buffer:
            processed_lines.append(buffer)
        
        return '\n'.join(processed_lines)
    
    def extract_strategies_with_layers(self, text: str) -> List[Dict]:
        """
        Extract strategies using known titles from PDF structure analysis.
        This PDF has a complex two-column layout requiring specific handling.
        """
        strategies = []
        
        # Known strategy titles from PDF analysis (in order of appearance after column extraction)
        known_titles = [
            ("Find or create learning moments in your everyday activities", "Layer 1"),
            ("Offer your child a productive role and predictable steps", "Layer 1"),
            ("Use your position to your advantage", "Layer 1"),
            ("Talk about what your child is looking at", "Layer 1"),
            ("Encourage initiation", "Layer 2"),
            ("Balance your turns", "Layer 1"),  # Appears after Layer 2 marker but is Layer 1
            ("Make your messages clear", "Layer 1"),  # Appears after Layer 2 marker but is Layer 1
            ("Model gestures, words, and actions", "Layer 3"),
            ("Extend the activity and roles", "Layer 3"),
            ("Expect more as your child grows", "Layer 3"),
        ]
        
        # Find each title in the text and extract following content
        for title, layer in known_titles:
            # Find title position (case-insensitive, flexible matching)
            title_pattern = re.escape(title).replace('\\ ', '\\s+')
            match = re.search(title_pattern, text, re.IGNORECASE)
            
            if match:
                start_pos = match.end()
                
                # Find end position (next known title or end of text)
                end_pos = len(text)
                for next_title, _ in known_titles:
                    if next_title != title:
                        next_pattern = re.escape(next_title).replace('\\ ', '\\s+')
                        next_match = re.search(next_pattern, text[start_pos:], re.IGNORECASE)
                        if next_match and (start_pos + next_match.start()) < end_pos:
                            end_pos = start_pos + next_match.start()
                
                # Extract strategy text
                strategy_text = text[start_pos:end_pos].strip()
                
                # Clean the text: remove headers, footers, layer markers, copyright
                strategy_text = re.sub(r'Copyright.*?University.*?reserved.*?', '', strategy_text, flags=re.IGNORECASE | re.DOTALL)
                strategy_text = re.sub(r'Page\\s+\\d+\\s+of\\s+\\d+', '', strategy_text, flags=re.IGNORECASE)
                strategy_text = re.sub(r'\\.\\s+of\\s+\\d+', '', strategy_text)  # Remove ". of 2" fragments
                strategy_text = re.sub(r'\\d+(st|nd|rd)\\s+Layer:[^\\n]*', '', strategy_text, flags=re.IGNORECASE)
                strategy_text = re.sub(r'^[.\\s]+', '', strategy_text)  # Remove leading period/whitespace
                strategy_text = re.sub(r'[.\\s]+$', '.', strategy_text)  # Clean trailing whitespace
                strategy_text = re.sub(r'\\s+', ' ', strategy_text).strip()
                
                # Only add if we have substantial text
                if len(strategy_text) > 50:
                    strategies.append({
                        "source": "Support Communication Development",
                        "layer": layer,
                        "strategy_title": title,
                        "strategy_text": strategy_text,
                        "page": 1,  # Will update later
                        "domain_tag": "Social Communication"
                    })
        
        return strategies
        
        return strategies
    
    def parse(self) -> List[Dict]:
        """Main parsing method with layout-aware two-column extraction."""
        print(f"Parsing coaching strategies PDF: {self.pdf_path}")
        
        # Extract all text from PDF using two-column extraction
        all_text = ""
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Use two-column extraction for this document
                text = extract_two_column_text(page)
                if text:
                    all_text += "\n" + text
        
        # Preprocess entire document
        processed_text = self.preprocess_text(all_text)
        
        # Extract strategies with layer assignment
        self.strategies = self.extract_strategies_with_layers(processed_text)
        
        # Update page numbers based on content position
        with pdfplumber.open(self.pdf_path) as pdf:
            for strategy in self.strategies:
                # Simple heuristic: check title against each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = extract_two_column_text(page)
                    if strategy["strategy_title"] in page_text:
                        strategy["page"] = page_num
                        break
        
        print(f"Extracted {len(self.strategies)} strategies across multiple layers")
        return self.strategies


def parse_text_file(text_path: Path) -> List[Dict]:
    """Parse text file if it contains structured content."""
    print(f"Parsing text file: {text_path}")
    
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # If text file has structured content, parse it
    # For now, just return as a single entry
    return [{
        "source": "text.txt",
        "content": content,
        "type": "supplementary"
    }]


def validate_milestones(milestones: List[Dict]) -> List[str]:
    """Validate milestone data."""
    issues = []
    
    for i, milestone in enumerate(milestones):
        # Check required fields
        required = ["source", "age_range", "age_min", "age_max", "domain", "milestone_text"]
        for field in required:
            if field not in milestone or not milestone[field]:
                issues.append(f"Milestone {i}: Missing or empty field '{field}'")
        
        # Validate age range consistency
        if milestone.get('age_min') and milestone.get('age_max'):
            if milestone['age_min'] > milestone['age_max']:
                issues.append(f"Milestone {i}: age_min > age_max")
        
        # Check milestone text is not too short
        text = milestone.get('milestone_text', '')
        if len(text) < 10:
            issues.append(f"Milestone {i}: milestone_text too short")
    
    return issues


def validate_strategies(strategies: List[Dict]) -> List[str]:
    """Validate strategy data."""
    issues = []
    
    for i, strategy in enumerate(strategies):
        # Check required fields
        required = ["source", "layer", "strategy_title", "strategy_text"]
        for field in required:
            if field not in strategy or not strategy[field]:
                issues.append(f"Strategy {i}: Missing or empty field '{field}'")
        
        # Check strategy text is not too short
        text = strategy.get('strategy_text', '')
        if len(text) < 20:
            issues.append(f"Strategy {i}: strategy_text too short")
    
    return issues


def main():
    """Main execution function."""
    print("="*60)
    print("Phase 1: Document Parsing for EarlyInterventionAI")
    print("="*60)
    
    # Parse Milestones PDF
    milestone_pdf = DOCS_DIR / "SCGC_Milestones_that_Matter_Most_1-24_Months_3-page.pdf"
    if milestone_pdf.exists():
        parser = MilestoneParser(milestone_pdf)
        milestones = parser.parse()
        
        # Validate
        issues = validate_milestones(milestones)
        if issues:
            print(f"\nValidation issues found ({len(issues)}):")
            for issue in issues[:5]:  # Show first 5
                print(f"  - {issue}")
        
        # Save to JSON
        output_file = OUTPUT_DIR / "milestones_structured.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(milestones, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(milestones)} milestones to: {output_file}")
        
        # Print sample
        if milestones:
            print("\n" + "="*60)
            print("SAMPLE MILESTONE OUTPUT:")
            print("="*60)
            print(json.dumps(milestones[:3], indent=2))
    else:
        print(f"Milestone PDF not found: {milestone_pdf}")
    
    print("\n" + "="*60)
    
    # Parse Coaching Strategies PDF
    strategies_pdf = DOCS_DIR / "Support_Communication_Development_02.pdf"
    if strategies_pdf.exists():
        parser = CoachingStrategyParser(strategies_pdf)
        strategies = parser.parse()
        
        # Validate
        issues = validate_strategies(strategies)
        if issues:
            print(f"\nValidation issues found ({len(issues)}):")
            for issue in issues[:5]:  # Show first 5
                print(f"  - {issue}")
        
        # Save to CLEANED JSON file
        output_file = OUTPUT_DIR / "coaching_strategies_cleaned.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(strategies)} strategies to: {output_file}")
        
        # Print layer distribution
        layer_counts = {}
        for s in strategies:
            layer = s.get('layer', 'Unknown')
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        print(f"\nStrategies by Layer:")
        for layer, count in sorted(layer_counts.items()):
            print(f"   {layer}: {count} strategies")
        
        # Print sample (3 entries)
        if strategies:
            print("\n" + "="*60)
            print("SAMPLE STRATEGY OUTPUT (First 3):")
            print("="*60)
            print(json.dumps(strategies[:3], indent=2, ensure_ascii=False))
    else:
        print(f"Strategies PDF not found: {strategies_pdf}")
    
    print("\n" + "="*60)
    
    # Parse text file
    text_file = DOCS_DIR / "text.txt"
    if text_file.exists():
        text_data = parse_text_file(text_file)
        output_file = OUTPUT_DIR / "text_content.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved text content to: {output_file}")
    
    print("\n" + "="*60)
    print("Parsing complete! Check the 'parsed_output' directory for results.")
    print("="*60)


if __name__ == "__main__":
    main()
