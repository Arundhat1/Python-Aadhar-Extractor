# Aadhaar Info Extractor (OCR + Regex)

Extracts key information (Name, DOB, Gender, Aadhaar Number) from Aadhaar card images using **OpenCV**, **pytesseract**, and **regex**.

## 🚀 Features
- Works on JPG/PNG Aadhaar card scans
- Outputs CSV with filename, name, DOB, gender, Aadhaar
- Basic preprocessing for digit-heavy fields
- Fallback Aadhaar extraction from bottom crop

## 📂 Project Structure
AadhaarOCR/
│── main.py
│── requirements.txt
│── README.md
│── samples/ (put Aadhaar images here)

## ⚡ Usage
1. Install requirements:
   ```bash
   pip install -r requirements.txt

Also install Tesseract OCR
 and make sure it’s in PATH.

Run the script:

python main.py


By default, it processes images in the samples/ folder and saves results to output.csv.

📝 Example Output
filename	name	dob	gender	aadhaar
a001.jpg	Rahul Sharma	12/04/1998	Male	123412341234
🔍 Limitations

Works best on clear scanned images (not blurred or tilted)

Name extraction can miss if OCR fails

Aadhaar may be missed if number is broken into lines

📌 Tech Used

Python, OpenCV, pytesseract, pandas
