import os
import glob
import subprocess
from pathlib import Path

# Use the same data directory as other scripts
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def process_excel_file(excel_file):
    """Process a single Excel file by running the email extractor."""
    print(f"\n📊 Processing: {excel_file}")
    
    print(f"📨 Running email extraction for {excel_file}...")
    try:
        # Run without capturing output to see real-time progress
        result = subprocess.run(
            ['python3', 'new_email_ext.py', '--excel', excel_file],
            check=True
        )
        if result.returncode != 0:
            print(f"❌ Process exited with code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed processing {excel_file}. Return code: {e.returncode}")
        if e.output:
            print("Error output:", e.output.decode())
    except FileNotFoundError:
        print("❌ Error: Could not find python or new_email_ext.py. Make sure both exist in the current directory.")
    except Exception as e:
        print(f"❌ Unexpected error processing {excel_file}:", str(e))

def main():
    # Find all Excel files in the data directory that don't end with _updated.xlsx
    excel_files = [
        f for f in glob.glob(os.path.join(DATA_DIR, "*.xlsx"))
        if not f.endswith("_updated.xlsx")
    ]
    # check there's no _update for each file
    for excel_file in excel_files:
        if os.path.exists(excel_file.replace(".xlsx", "_updated.xlsx")):
            excel_files.remove(excel_file)
    
    print(excel_files)
    if not excel_files:
        print("❌ No Excel files found in the data directory!")
        return
    
    print(f"🔍 Found {len(excel_files)} Excel files to process")
    
    # Process each Excel file
    for i, excel_file in enumerate(excel_files, 1):
        print(f"\n[{i}/{len(excel_files)}] Processing file: {os.path.basename(excel_file)}")
        process_excel_file(excel_file)
    
    print("\n✅ Batch processing complete!")
    print(f"📊 Processed {len(excel_files)} files")

if __name__ == "__main__":
    main() 