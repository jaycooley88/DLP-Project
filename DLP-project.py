import os
from pathlib import Path
from datetime import datetime
from collections import Counter
from pdf2image import convert_from_path
from PIL import Image
import easyocr
from presidio_analyzer import AnalyzerEngine

# === CONFIG ===
PDF_FOLDER = Path("G:/DLP project/discovered pdf")
OUTPUT_FOLDER = Path("G:/DLP project/OCR results")
TEMP_IMAGE_FOLDER = OUTPUT_FOLDER / "temp_images"
LANGUAGES = ['en']
OCR_MIN_CONFIDENCE = 0.3
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# === INIT ===
reader = easyocr.Reader(LANGUAGES, gpu=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
TEMP_IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

# === STEP 1: OCR PDFs ===
for pdf_file in PDF_FOLDER.glob("*.pdf"):
    print(f"\nProcessing PDF: {pdf_file.name}")
    images = convert_from_path(str(pdf_file), dpi=300, output_folder=str(TEMP_IMAGE_FOLDER))

    for page_num, image in enumerate(images, start=1):
        image_path = TEMP_IMAGE_FOLDER / f"{pdf_file.stem}_page_{page_num}.png"
        image.save(image_path, 'PNG')

        results = reader.readtext(str(image_path))
        text_blocks = [text for _, text, conf in results if conf >= OCR_MIN_CONFIDENCE]
        full_text = '\n'.join(text_blocks)

        output_file = OUTPUT_FOLDER / f"{pdf_file.stem}_page_{page_num}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)

# === STEP 2: OCR Image Files ===
for ext in IMAGE_EXTENSIONS:
    for image_file in PDF_FOLDER.glob(f"*{ext}"):
        print(f"\nProcessing Image: {image_file.name}")

        results = reader.readtext(str(image_file))
        text_blocks = [text for _, text, conf in results if conf >= OCR_MIN_CONFIDENCE]
        full_text = '\n'.join(text_blocks)

        output_file = OUTPUT_FOLDER / f"{image_file.stem}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)

print("\nOCR phase complete. Beginning Presidio scan...")

# === STEP 3: Presidio Analysis ===
input_dir = str(OUTPUT_FOLDER)
output_dir = os.path.join(input_dir, "presidio scan results")
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime("%m%d%y")
output_file = os.path.join(output_dir, f"presidio_results_{timestamp}.txt")

analyzer = AnalyzerEngine()

total_files = 0
files_with_pii = 0
entity_counter = Counter()

severity_order = [
    "US_SSN",
    "PERSON",
    "PHONE_NUMBER",
    "LOCATION",
    "DATE_TIME"
]

with open(output_file, "w", encoding="utf-8") as out:
    out.write("Presidio Analysis Results\n")
    out.write("=" * 60 + "\n")

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt"):
            total_files += 1
            file_path = os.path.join(input_dir, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            results = analyzer.analyze(
                text=text,
                entities=[],
                language='en',
                score_threshold=0.3
            )

            if results:
                files_with_pii += 1
                out.write(f"\nFile: {filename}\n")
                for result in results:
                    entity_counter[result.entity_type] += 1
                    match_text = text[result.start:result.end].replace("\n", " ")
                    out.write(
                        f"  - Entity: {result.entity_type:<20} "
                        f"| Confidence: {result.score:.2f} "
                        f"| Match: {match_text}\n"
                    )

    # Summary section
    sorted_entities = sorted(
        entity_counter.items(),
        key=lambda x: severity_order.index(x[0]) if x[0] in severity_order else len(severity_order)
    )

    out.write("\n" + "=" * 60 + "\n")
    out.write(f"Total files scanned: {total_files}\n")
    out.write(f"Files with PII detected: {files_with_pii}\n")
    out.write("Entity type counts (by severity):\n")
    for entity, count in sorted_entities:
        out.write(f"  - {entity}: {count}\n")

print(f"\nPresidio scan complete. Results saved to: {output_file}")
