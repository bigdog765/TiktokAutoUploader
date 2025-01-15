from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re

def extract_string_inside_quotes(text):
    # Regex to extract the string inside quotes
    pattern = r'"([^"]+)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # Return the content inside the quotes
    return None  # Return None if no match is found

# Configure Chrome options
options = Options()
#options.add_argument("--disable-gpu")  # Disable GPU acceleration
#options.add_argument("--headless")  # Run in headless mode (no GUI)

# Set up the driver with the absolute path to the ChromeDriver
chrome_driver_path = os.path.abspath("./webscrape/chromedriver-win64/chromedriver.exe")  # Replace with your chromedriver path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Load the website
driver.get("https://www.midjourney.com/explore?tab=hot")

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located(
    (By.XPATH, '//a[@class="block bg-cover bg-center w-full h-full bg-light-skeleton overflow-hidden dark:bg-dark-skeleton"]')))

# Extract image URLs (modify the XPath based on the page structure)
image_elements = driver.find_elements(
    By.XPATH, '//a[@class="block bg-cover bg-center w-full h-full bg-light-skeleton overflow-hidden dark:bg-dark-skeleton"]')

# Regex pattern
pattern = r'"[^"]*"\)\s*2x\)' # Extract the URL inside the background-image URL with 2x resolution

background_image_elements = [img.get_attribute("style").split(';')[1] for img in image_elements]
matches = [str(re.findall(pattern, elem)) for elem in background_image_elements]
# Print the extracted URLs
url_result = [extract_string_inside_quotes(match) for match in matches]
print(url_result)

# Quit the driver
driver.quit()