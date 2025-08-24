# main.py — targeted Aadhaar extraction + improved parsing
import os
import re
import cv2
import pytesseract
import pandas as pd
import numpy as np
from pytesseract import Output

# ---------- CONFIG ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

IMAGE_FOLDER = "aadhar"                  # input folder
OUTPUT_CSV = "output/extracted_data.csv"  # output path
os.makedirs("output", exist_ok=True)

# Patterns
DOB_PATTERN = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
AADHAAR_TOKEN_PATTERN = re.compile(r"\d+")  # tokens that contain digits
AADHAAR_FULL = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")

# Junk words not to treat as name
JUNK_WORDS = {"government of india", "govt of india", "govemment of india", "govarnmanl ofindia",
              "goverment of india", "dob", "date of birth", "name"}

# ---------- UTILITIES ----------
def clean_line(line: str) -> str:
    if not isinstance(line, str):
        return ""
    return re.sub(r'\s+', ' ', line).strip()

def preprocess_for_digits(img):
    """Preprocess crop for best digit OCR: grayscale, resize, blur, adaptive threshold."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # upscale for better OCR on small text
    h, w = gray.shape
    scale = 2 if max(h, w) < 200 else 1
    if scale != 1:
        gray = cv2.resize(gray, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
    # denoise
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    # adaptive threshold
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 15, 6)
    # morphological opening to remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    return th

def tesseract_digits_and_confidence(img):
    """
    Run tesseract on an image crop with digit whitelist and return
    (digits_string, mean_confidence). If no digits found, return ("", 0.0).
    """
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
    data = pytesseract.image_to_data(img, config=config, output_type=Output.DICT)
    texts = []
    confs = []
    n = len(data['text'])
    for i in range(n):
        txt = data['text'][i].strip()
        conf = int(data['conf'][i]) if data['conf'][i] != '-1' else -1
        if txt != "" and re.fullmatch(r"[0-9]+", txt):
            texts.append(txt)
            if conf >= 0:
                confs.append(conf)
    if not texts:
        # fallback: try to extract digits from full OCR text
        ocr_full = pytesseract.image_to_string(img, config=config)
        digits = re.sub(r"\D", "", ocr_full)
        return digits, (sum(confs)/len(confs) if confs else 0.0)
    joined = "".join(texts)
    mean_conf = (sum(confs) / len(confs)) if confs else 0.0
    return joined, mean_conf

# ---------- CANDIDATE DISCOVERY ----------
def find_aadhaar_candidates_from_data(data):
    """
    data: pytesseract.image_to_data output (dict with keys including 'text','left','top','width','height','line_num')
    Returns list of candidates: dicts with 'digits' (raw), 'bbox' (x1,y1,x2,y2), 'words_idx' (indices)
    """
    candidates = []
    n = len(data['text'])
    # Group by line_num
    for i in range(n):
        line_num = data['line_num'][i]
        # collect all indices with same line_num
    # Build mapping from line number to indices
    line_map = {}
    for i in range(n):
        ln = data['line_num'][i]
        line_map.setdefault(ln, []).append(i)
    for ln, idxs in line_map.items():
        # join consecutive digit-containing tokens
        i = 0
        while i < len(idxs):
            idx = idxs[i]
            txt = clean_line(data['text'][idx])
            if AADHAAR_TOKEN_PATTERN.search(txt):
                # start a sequence
                seq_idxs = [idx]
                j = i+1
                while j < len(idxs):
                    nxt = idxs[j]
                    nxt_txt = clean_line(data['text'][nxt])
                    # allow tokens that contain digits or look like groups
                    if AADHAAR_TOKEN_PATTERN.search(nxt_txt):
                        seq_idxs.append(nxt)
                        j += 1
                    else:
                        break
                # form candidate digits
                digit_str = "".join(re.sub(r"\D", "", clean_line(data['text'][k])) for k in seq_idxs)
                if len(digit_str) >= 12:  # candidate
                    # compute bbox covering seq
                    lefts = [data['left'][k] for k in seq_idxs]
                    tops = [data['top'][k] for k in seq_idxs]
                    rights = [data['left'][k] + data['width'][k] for k in seq_idxs]
                    bottoms = [data['top'][k] + data['height'][k] for k in seq_idxs]
                    x1, y1, x2, y2 = min(lefts), min(tops), max(rights), max(bottoms)
                    candidates.append({
                        'digits': digit_str,
                        'bbox': (x1, y1, x2, y2),
                        'indices': seq_idxs
                    })
                i = j
            else:
                i += 1
    return candidates

# ---------- MAIN IMAGE PROCESS ----------
def extract_fields_for_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    h, w = img.shape[:2]

    # Full OCR to get words+positions
    full_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    n = len(full_data['text'])

    # Collect lines in order
    line_map = {}
    for i in range(n):
        ln = full_data['line_num'][i]
        line_map.setdefault(ln, []).append(i)

    ordered_lines = []
    for ln in sorted(line_map.keys()):
        texts = [clean_line(full_data['text'][i]) for i in line_map[ln] if clean_line(full_data['text'][i])]
        if texts:
            ordered_lines.append(" ".join(texts))

    ordered_lines = [l for l in ordered_lines if l.strip()]

    # --- DOB detection ---
    dob, dob_line_idx = "", None
    for idx, line in enumerate(ordered_lines):
        m = DOB_PATTERN.search(line)
        if m:
            dob, dob_line_idx = m.group(), idx
            break

    # --- Name detection ---
    name = ""
    if dob_line_idx is not None:
        for j in range(dob_line_idx - 1, -1, -1):
            cand = ordered_lines[j].strip()
            if cand.lower() in JUNK_WORDS or re.search(r"\d", cand):
                continue
            if len(cand.split()) >= 2:
                name = cand
                break
    if not name:
        for line in ordered_lines:
            if line.lower() in JUNK_WORDS: continue
            if len(line.split()) >= 2 and not re.search(r"\d", line):
                name = line
                break

    # --- Gender detection ---
    gender = ""
    if dob_line_idx is not None:
        for j in range(dob_line_idx + 1, min(dob_line_idx + 3, len(ordered_lines))):
            low = ordered_lines[j].lower()
            if "male" in low: gender = "Male"; break
            if "female" in low: gender = "Female"; break
            if len(ordered_lines[j].strip()) == 4: gender = "Male"; break
            if len(ordered_lines[j].strip()) == 6: gender = "Female"; break
    if not gender:
        for line in ordered_lines:
            low = line.lower()
            if "male" in low: gender = "Male"; break
            if "female" in low: gender = "Female"; break

    # --- Aadhaar detection ---
    candidates = find_aadhaar_candidates_from_data(full_data)
    best_aadhaar, best_conf = "", -1.0
    for cand in candidates:
        x1, y1, x2, y2 = cand["bbox"]
        pad_x = int((x2 - x1) * 0.25) + 5
        pad_y = int((y2 - y1) * 0.4) + 5
        sx, sy = max(0, x1 - pad_x), max(0, y1 - pad_y)
        ex, ey = min(w, x2 + pad_x), min(h, y2 + pad_y)
        crop = img[sy:ey, sx:ex]
        if crop.size == 0: continue
        proc = preprocess_for_digits(crop)
        digits, conf = tesseract_digits_and_confidence(proc)
        digits = re.sub(r"\D", "", digits)
        if len(digits) == 12 and conf > best_conf:
            best_conf, best_aadhaar = conf, digits

    if not best_aadhaar:
        bottom_crop = img[int(h*0.65):h, 0:w]
        proc = preprocess_for_digits(bottom_crop)
        digits, _ = tesseract_digits_and_confidence(proc)
        m = re.search(r"(\d{12})", digits)
        if m: best_aadhaar = m.group(1)

    if best_aadhaar and len(best_aadhaar) != 12:
        best_aadhaar = ""

    return {
        "filename": os.path.basename(image_path),
        "name": name or "",
        "dob": dob or "",
        "aadhaar": best_aadhaar or "",
        "gender": gender or ""
    }

def process_all():
    rows = []
    files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    for fname in files:
        path = os.path.join(IMAGE_FOLDER, fname)
        print(f"[+] Processing {fname}")
        r = extract_fields_for_image(path)
        rows.append(r)
    # Save as strings to avoid pandas turning into floats
    df = pd.DataFrame(rows, columns=["filename","name","dob","aadhaar","gender"], dtype=str)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[✅] Saved {len(rows)} records to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_all()
