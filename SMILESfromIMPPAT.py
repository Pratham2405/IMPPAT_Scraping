from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv
import time
import os

os.makedirs("drive-download-20250104T145431Z-001", exist_ok=True)  # Add this before file creation
OUTPUT_CSV = "drive-download-20250104T145431Z-001/imppat_smiles.csv"
# Configuration
INPUT_CSV = "imppat_druglike_ids.csv"

BASE_URL = "https://cb.imsc.res.in/imppat/phytochemical-detailedpage/"

# Setup Chrome driver (headless)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

try:
    # Read IMPHY IDs from CSV using Pandas
    df = pd.read_csv(INPUT_CSV)
    imphy_ids = df['IMPHY_ID'].tolist()

    # Prepare output CSV file
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['IMPHY_ID', 'SMILES'])

        # Iterate through each IMPHY ID to extract SMILES
        for idx, imphy_id in enumerate(imphy_ids):
            url = f"{BASE_URL}{imphy_id}"
            driver.get(url)
            print(f"Processing {idx+1}/{len(imphy_ids)}: {imphy_id}")

            try:
                # Wait explicitly for the SMILES element to load using robust XPath selector
                smiles_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//strong[contains(text(), 'SMILES:')]/following-sibling::text[1]")
                    )
                )
                smiles_code = smiles_element.text.strip()
                print(f"Extracted SMILES: {smiles_code}")

            except Exception as e:
                print(f"Could not find SMILES for {imphy_id}: {str(e)}")
                smiles_code = "Not Found"

            # Write IMPHY ID and SMILES code to CSV
            writer.writerow([imphy_id, smiles_code])

            # Polite delay between requests
            time.sleep(1)

    print(f"\nAll SMILES codes extracted successfully to {OUTPUT_CSV}")

except Exception as e:
    print(f"Critical error: {str(e)}")

finally:
    driver.quit()
