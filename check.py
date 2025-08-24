import pandas as pd

truth_df = pd.read_csv("Aadhar autofulfill.csv")
ocr_df = pd.read_csv("output/extracted_data.csv")

print("Truth CSV columns:", truth_df.columns.tolist())
print("OCR CSV columns:", ocr_df.columns.tolist())
