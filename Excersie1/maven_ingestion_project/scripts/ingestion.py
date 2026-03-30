import logging
import pandas as pd
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime

# 1. Setup Base Directories (Relative to the script location)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LANDING_DIR = DATA_DIR / "landing"
EXTRACTED_DIR = DATA_DIR / "extracted"
RAW_DIR = DATA_DIR / "raw"
LOGS_DIR = DATA_DIR / "logs"

# 2. Create required folders
for folder in [EXTRACTED_DIR, RAW_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# 3. Configure Logging
logging.basicConfig(
    filename=LOGS_DIR / "ingestion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_ingestion():
    try:
        # 4. Extract ZIP
        zip_path = LANDING_DIR / "Maven+Fuzzy+Factory.zip"
        if not zip_path.exists():
            logging.error(f"ZIP file not found at {zip_path}")
            print(f"Error: ZIP file not found.")
            return

        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(EXTRACTED_DIR)
        logging.info("ZIP extracted successfully")

        # 5. Identify CSVs
        csv_files = list(EXTRACTED_DIR.glob("*.csv"))
        if not csv_files:
            logging.warning("No CSV files found in extraction zone.")
            return

        ingestion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = []

        # 6. Process Files (The Core Loop)
        for file_path in csv_files:
            df = pd.read_csv(file_path)

            # Add Audit Metadata
            df["source_file"] = file_path.name
            df["ingestion_time"] = ingestion_time

            # Write to Raw Zone
            output_file = RAW_DIR / f"raw_{file_path.name}"
            df.to_csv(output_file, index=False)

            # Track Summary
            summary.append({
                "table_name": file_path.stem,
                "rows_ingested": len(df),
                "columns_ingested": len(df.columns),
                "raw_output_file": output_file.name
            })
            logging.info(f"Ingested {file_path.name} with {len(df)} rows")

        # 7. Generate Summary Report
        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(RAW_DIR / "raw_ingestion_summary.csv", index=False)
        
        print("--- Ingestion Summary ---")
        print(summary_df)
        logging.info("Ingestion workflow completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    run_ingestion()