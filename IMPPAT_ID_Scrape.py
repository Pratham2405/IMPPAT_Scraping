from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import csv
import time

# Setup Chrome driver
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)
driver.maximize_window()

# Output file
output_file = "imppat_druglike_ids.csv"

try:
    # Step 1: Navigate to the Advanced Search drug-like filter page
    driver.get("https://cb.imsc.res.in/imppat/advancedsearch/druglikefilter")
    print("Navigated to drug-like filter page")
    
    # Step 2: Set all filters according to screenshot
    # Wait for filter form to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select"))
    )
    
    # Set Lipinski RO5 violation to "Zero violation"
    lipinski_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='lipinski']"))
    lipinski_select.select_by_visible_text("Zero violation")
    
    # Set Ghose rule violation to "Zero violation"
    ghose_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='ghose']"))
    ghose_select.select_by_visible_text("Zero violation")
    
    # Set GSK 4/400 to "Good"
    gsk_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='gsk']"))
    gsk_select.select_by_visible_text("Good")
    
    # Set Pfizer 3/75 to "Good"
    pfizer_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='pfizer']"))
    pfizer_select.select_by_visible_text("Good")
    
    # Set Veber rule to "Good"
    veber_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='veber']"))
    veber_select.select_by_visible_text("Good")
    
    # Set Egan rule to "Good"
    egan_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='egan']"))
    egan_select.select_by_visible_text("Good")
    
    # Set QEDw to "is greater than" (leave text field empty as shown in screenshot)
    qedw_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='qedw_type']"))
    qedw_select.select_by_visible_text("is greater than")
    
    # Step 3: Click Search button
    search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Search']")
    search_button.click()
    print("Applied filters and submitted search")
    
    # Step 4: Wait for results table to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    print("Results table loaded")
    
    # Create CSV file and write header
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['IMPHY_ID'])
    
    # Initialize counter for total IDs
    total_ids = 0
    current_page = 1
    
    # Step 5: Process all pages
    while True:
        print(f"Processing page {current_page}")
        
        # Wait for table to be visible after page change
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Extract IMPHY IDs from the current page
        id_elements = driver.find_elements(By.CSS_SELECTOR, "table td a[href*='IMPHY']")
        
        # Extract text from each element
        page_ids = [element.text.strip() for element in id_elements if element.text.strip().startswith("IMPHY")]
        
        # Append to CSV
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for imphy_id in page_ids:
                writer.writerow([imphy_id])
        
        # Update total count
        total_ids += len(page_ids)
        print(f"Extracted {len(page_ids)} IMPHY IDs from page {current_page}")
        
        # Check for Next button
        next_buttons = driver.find_elements(By.LINK_TEXT, "Next")
        
        # If no Next button or it's disabled, we're on the last page
        if not next_buttons or 'disabled' in next_buttons[0].get_attribute('class'):
            break
        
        # Click Next button and wait for page transition
        next_buttons[0].click()
        current_page += 1
        time.sleep(2)  # Short delay for page loading
    
    print(f"Completed! Total: {total_ids} IMPHY IDs extracted to {output_file}")

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Close the browser
    driver.quit()
