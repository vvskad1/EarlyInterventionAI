# Phase 1: Document Parsing for EarlyInterventionAI

## Overview

This phase focuses on **extracting structured data** from Early Intervention PDF documents and converting them into clean JSON format suitable for later RAG (Retrieval-Augmented Generation) integration.

**No embeddings or RAG implementation in this phase** - only parsing and structured output.

## Documents to Parse

Located in `docs/` directory:

1. **SCGC_Milestones_that_Matter_Most_1-24_Months_3-page.pdf**
   - Developmental milestones organized by age ranges (1-24 months)
   - Structured by domains: Language, Play, Social Interaction, Emotional Regulation, Self-Directed Learning

2. **Support_Communication_Development_02.pdf**
   - Coaching strategies for supporting communication development
   - Organized in 3 layers: Create learning moments, Make it fun, Model & expand

3. **text.txt**
   - Supplementary text content

## Installation

Install required dependencies:

```bash
pip install pdfplumber>=0.10.0
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the parsing script:

```bash
python parse_documents.py
```

This will:
1. Parse all PDFs in the `docs/` directory
2. Extract structured data
3. Validate the output
4. Save JSON files to `parsed_output/` directory
5. Print sample outputs to console

## Output Files

The script generates the following JSON files in `parsed_output/`:

### 1. `milestones_structured.json`

Each milestone entry contains:

```json
{
  "source": "Milestones that Matter Most",
  "age_range": "9-10 months",
  "age_min": 9,
  "age_max": 10,
  "domain": "Language",
  "thread": "Sounds & Words",
  "milestone_text": "I can use my voice to make different sounds to let you know how I feel.",
  "page": 2
}
```

**Fields:**
- `source`: Document source name
- `age_range`: Age range as text (e.g., "9-10 months")
- `age_min`: Minimum age in months (integer)
- `age_max`: Maximum age in months (integer)
- `domain`: Developmental domain
- `thread`: Specific thread/category within domain
- `milestone_text`: The actual milestone description
- `page`: Page number in source PDF

### 2. `coaching_strategies_structured.json`

Each strategy entry contains:

```json
{
  "source": "Support Communication Development",
  "layer": "Layer 2",
  "strategy_title": "Encourage initiation",
  "strategy_text": "Wait for the child to initiate communication before responding. Create opportunities for the child to make the first move.",
  "page": 2,
  "domain_tag": "Social Communication"
}
```

**Fields:**
- `source`: Document source name
- `layer`: Strategy layer (Layer 1, 2, or 3)
- `strategy_title`: Brief strategy title
- `strategy_text`: Full strategy description
- `page`: Page number in source PDF
- `domain_tag`: Domain classification

### 3. `text_content.json`

Structured content from text files.

## Parsing Logic

### Milestone Parser (`MilestoneParser`)

**Step 1: Age Range Detection**
- Uses regex to identify age ranges like "9-10 MONTHS"
- Extracts numeric values for `age_min` and `age_max`
- Pattern: `(\d+)\s*-\s*(\d+)\s+MONTHS?`

**Step 2: Domain Identification**
- Scans text for domain keywords: Language, Play, Social Interaction, etc.
- Maintains current domain context while parsing

**Step 3: Thread Extraction**
- Identifies sub-categories like "Gestures & Meanings", "Sounds & Words"
- Uses pattern matching for common thread formats

**Step 4: Milestone Extraction**
- Identifies milestone statements (typically starting with "I")
- Associates each milestone with current age range, domain, and thread
- Cleans whitespace and removes headers/footers

**Step 5: Validation**
- Ensures all required fields are present
- Validates age_min <= age_max
- Checks milestone text length (min 10 characters)

### Coaching Strategy Parser (`CoachingStrategyParser`)

**Step 1: Layer Detection**
- Identifies which layer (1, 2, or 3) based on keywords
- Layer 1: "Create a learning moment"
- Layer 2: "Make it fun and keep it going"
- Layer 3: "Model, expand, & keep moving"

**Step 2: Strategy Block Extraction**
- Detects strategy titles (usually short, title case, no ending period)
- Groups subsequent text as strategy description
- Handles bullet points and formatting

**Step 3: Text Cleaning**
- Normalizes whitespace
- Removes repetitive headers/footers
- Consolidates multi-line text

**Step 4: Validation**
- Ensures all required fields are present
- Validates strategy text length (min 20 characters)

## Text Cleaning Functions

Both parsers use common cleaning utilities:

1. **Whitespace Normalization**
   - Converts multiple spaces to single space
   - Removes leading/trailing whitespace

2. **Header/Footer Removal**
   - Removes document titles that repeat on each page
   - Removes page numbers

3. **Line Break Handling**
   - Preserves meaningful line breaks
   - Joins continuation lines appropriately

## Data Validation

The script includes validation for:

- **Required Fields**: All mandatory fields must be present
- **Field Values**: Fields must not be empty
- **Age Range Logic**: age_min must be ≤ age_max
- **Text Length**: Milestone and strategy text must meet minimum lengths
- **Domain Consistency**: No milestone should mix multiple age ranges

Validation issues are reported to console but don't block output generation.

## Example Output

### Sample Milestone

```json
{
  "source": "Milestones that Matter Most",
  "age_range": "11-12 months",
  "age_min": 11,
  "age_max": 12,
  "domain": "Language",
  "thread": "Gestures & Meanings",
  "milestone_text": "I can point to things I want or find interesting.",
  "page": 2
}
```

### Sample Strategy

```json
{
  "source": "Support Communication Development",
  "layer": "Layer 1",
  "strategy_title": "Create Communication Opportunities",
  "strategy_text": "Set up situations where the child needs to communicate to get what they want. For example, put desired toys in clear containers the child cannot open independently.",
  "page": 1,
  "domain_tag": "Social Communication"
}
```

## Next Steps (Phase 2)

After structured JSON is created:
1. Generate embeddings for each entry
2. Store in vector database (ChromaDB)
3. Implement RAG retrieval system
4. Integrate with chatbot interface

## Troubleshooting

**Issue: "pdfplumber not found"**
```bash
pip install pdfplumber
```

**Issue: "Permission denied on PDF"**
- Ensure PDFs are not open in another application
- Check file permissions

**Issue: "No milestones extracted"**
- Verify PDF format matches expected structure
- Check console output for parsing errors
- PDFs may need manual inspection if format is unusual

## File Structure

```
EarlyInterventionAI-main/
├── parse_documents.py          # Main parsing script
├── docs/                       # Input PDFs
│   ├── SCGC_Milestones_that_Matter_Most_1-24_Months_3-page.pdf
│   ├── Support_Communication_Development_02.pdf
│   └── text.txt
├── parsed_output/              # Generated JSON files
│   ├── milestones_structured.json
│   ├── coaching_strategies_structured.json
│   └── text_content.json
└── PARSING_README.md           # This file
```

## Notes

- **No AI/LLM used in parsing**: Pure regex and rule-based extraction
- **Deterministic output**: Same input always produces same output
- **Human review recommended**: Validate a sample of parsed data before using in production
- **Extensible**: Easy to add parsers for additional document types
