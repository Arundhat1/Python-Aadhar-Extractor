import pandas as pd
from fuzzywuzzy import fuzz

# Paths to your files
ground_truth_path = "Aadhar autofulfill.csv"   # change to your actual ground truth file path
extracted_path = "output/extracted_data.csv"  # path to your OCR output CSV
mismatch_output_path = "output/mismatches.csv"

# Load CSV files
ground_df = pd.read_csv(ground_truth_path)
extracted_df = pd.read_csv(extracted_path)

# Normalize column names (lowercase, no spaces)
ground_df.columns = [c.strip().lower() for c in ground_df.columns]
extracted_df.columns = [c.strip().lower() for c in extracted_df.columns]

# These are the fields we want to compare
fields_to_compare = ["name", "dob", "aadhaar", "gender"]

# Ensure both have filename for matching
if "filename" not in ground_df.columns or "filename" not in extracted_df.columns:
    raise ValueError("Both CSVs must have a 'filename' column for matching.")

# Merge dataframes on filename
merged_df = pd.merge(ground_df, extracted_df, on="filename", suffixes=("_gt", "_ext"))

total_counts = {field: 0 for field in fields_to_compare}
correct_counts = {field: 0 for field in fields_to_compare}

mismatches = []

# Compare each field
for _, row in merged_df.iterrows():
    for field in fields_to_compare:
        gt_col = field + "_gt"
        ext_col = field + "_ext"

        gt_val = str(row[gt_col]).strip() if pd.notna(row[gt_col]) else ""
        ext_val = str(row[ext_col]).strip() if pd.notna(row[ext_col]) else ""

        if gt_val != "":
            total_counts[field] += 1
            # Use exact match here — can switch to fuzz if you want partial matches
            if gt_val.lower() == ext_val.lower():
                correct_counts[field] += 1
            else:
                mismatches.append({
                    "filename": row["filename"],
                    field + " (extracted)": ext_val,
                    field + " (expected)": gt_val
                })

# Save mismatches
mismatch_df = pd.DataFrame(mismatches)
mismatch_df.to_csv(mismatch_output_path, index=False)

# Print field-wise accuracy
print("=== Field-wise Accuracy ===")
for field in fields_to_compare:
    accuracy = (correct_counts[field] / total_counts[field] * 100) if total_counts[field] > 0 else 0
    print(f"{field:<8}: {accuracy:.2f}%")

# Print overall accuracy
overall_correct = sum(correct_counts.values())
overall_total = sum(total_counts.values())
overall_accuracy = (overall_correct / overall_total * 100) if overall_total > 0 else 0
print(f"\nOverall Accuracy: {overall_accuracy:.2f}%")
print(f"[!] Mismatches saved to {mismatch_output_path}")
