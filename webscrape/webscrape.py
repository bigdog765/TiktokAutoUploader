from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configure Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode (no GUI)

# Set up the driver
service = Service("path/to/chromedriver")  # Replace with your chromedriver path
driver = webdriver.Chrome(service=service, options=options)

# Load the website
driver.get("https://www.midjourney.com/explore")

# Extract image URLs (modify the XPath based on the page structure)
image_elements = driver.find_elements(By.XPATH, "//img[@src]")  # Adjust selector if needed
image_urls = [img.get_attribute("src") for img in image_elements]

# Print the extracted URLs
print(image_urls)

# Quit the driver
driver.quit()
