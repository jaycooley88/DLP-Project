# DLP Scanner: OCR + PII Detection Workflow (SBAR)

##  Situation

A manual security audit of a network share drive revealed over 3000 .pdf's and image files of scanned patient records. The records were located in a folder belonging to a hospital unit that had been closed years ago, apparently used as a staging location to upload into Epic, the proper electronic health record system. The files were accessible to multiple users who were not affiliated with the unit, let alone the hospital.

##  Background

These files originate from legacy document storage, intake forms, and medical paperwork. Most are either image-based PDFs or direct scans (JPEG, PNG). They lack a text layer, making them unsearchable and unanalyzable via standard compliance tools. There are several different forms and layouts, making manual review further impractical. 

With these constraints in mind, this project integrates two open-source tools:

- EasyOCR — for text extraction from images and PDFs
- Microsoft Presidio — for detecting sensitive information in text

The system is designed to be local, open-source based, auditable, and expandable.

##  Assessment

A Python-based workflow was developed and tested to:

- Perform OCR on PDFs and images (JPEG, PNG)
- Generate machine-readable `.txt` files
- Analyze the extracted text using Microsoft Presidio for high-priority PII
- Output a timestamped summary report and per-file matches
- Rank entity detections by severity (SSN, Name, Phone, Location, Date)

The solution runs successfully on Windows with GPU acceleration (optional via t/f toggle, CUDA toolkit support needed) and supports automated batch processing of thousands of documents with minimal configuration.

### Features

- Batch OCR processing of PDFs and image files
- PII/PHI detection with customizable severity rules
- Automatically generates summary reports and per-file text output
- GPU support with EasyOCR (optional)

### Folder Structure

```
G:/DLP project/
├── discovered pdf/            # Place PDFs and images here
├── OCR results/               # Output folder for OCR'd .txt files
│   └── presidio scan results/ # Presidio results with timestamped reports
```

### How to Run

1. Install required packages:

   
    pip install easyocr pdf2image pillow presidio-analyzer
    
    Install Poppler for Windows (https://github.com/oschwartz10612/poppler-windows/releases) and add the `/bin` folder to your system PATH

3. Adjust file paths in `DLP-project.py` if needed

4. Run the script:

    
    DLP-project.py
  

5. OCR `.txt` files will be saved in `OCR results/`, and a timestamped Presidio scan report will be placed in `OCR results/presidio scan results/`.

### Sample Output

```
Presidio Analysis Results
==============================
File: sample_page_1.txt
  - Entity: SSN                  | Confidence: 0.95 | Match: 293-45-6789
  - Entity: PERSON               | Confidence: 0.87 | Match: John A. Doe

Total files scanned: 12
Files with PII detected: 4
Entity type counts (by severity):
  - US_SSN: 3
  - PERSON: 4
  - PHONE_NUMBER: 2
```

## R — Recommendation

Deploy this script as a first-stage triage tool for:

- Auditing scanned document repositories
- Feeding compliant document management systems
- Supporting downstream redaction or reporting workflows

### Future Enhancements

While the tool works perfectly for its intended use, it can be further refined if the need arises. As a fan of the pareto principle, this work will be deferred until such a time where they can be better incorporated with other projects

- Dashboard results view to trend instances of PII/PHI being uploaded to insecure locations
- PII redaction/sanitization
- Exporting structured results (CSV/JSON)
- Tracking user/permissions for individual education remediation
- Integrating with document management systems or SIEM
- Adding custom entity types for domain-specific use
 
---
