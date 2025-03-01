from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import os
import re
import requests
import random
import threading
import secrets
import time
import tempfile

threads = []
success_ctr = 0
amount_of_images = 5
image_index = amount_of_images

def extract_string_inside_quotes(text):
    # Regex to extract the string inside quotes
    pattern = r'"([^"]+)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # Return the content inside the quotes
    return None  # Return None if no match is found
API_KEY = '618478fe-a490-4bd3-9112-8bdcb94377d2'

def get_scrapeops_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

def download_image(url, all_urls):
    global success_ctr
    # Extract only the file name from the URL
    file_name = url.split("/")[-1]  # Get the last part of the URL

    random_prefix = secrets.token_hex(4)
    save_path = os.path.join("./ImagesDirPath", random_prefix + file_name)  # Save directly in ImagesDirPath

    # Ensure the ImagesDirPath directory exists
    os.makedirs("./ImagesDirPath", exist_ok=True)

    url = get_scrapeops_url(url)
    user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    ]
    headers={'User-Agent': random.choice(user_agents_list)}
    response = requests.request("GET", url, headers=headers)

    print('Status code:', response.status_code)
    # Check if the request was successful
    if response.status_code == 200:
        # Write the image data to a file
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):  # Write in chunks
                file.write(chunk)
        print(f"Image downloaded and saved to {save_path}")
        success_ctr+=1
    else:
        print(f"Failed to download image. Status code: {response.status_code} {response.reason} {response.text}")
        # retry image download with a new image url
        print('Retrying a new image.')
        retry_image_download(all_urls)

def retry_image_download(all_urls):
    global image_index
    image_index +=1
    download_image(all_urls[image_index],all_urls)

def execute(in_docker=False):
    print('Webscraping started...')
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    #chrome_options.add_argument('--headless') # prevents DevToolsActivePort file doesn't exist error?
    chrome_options.add_argument('--disable-dev-shm-usage')
    if in_docker:
        # Explicitly point to a linux chromedriver executable
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        chrome_driver_path = os.path.abspath("./webscrape/chromedriver-win64/chromedriver.exe")  # Replace with your chromedriver path
        print(chrome_driver_path)
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    # Load the website
    driver.get("https://www.midjourney.com/explore?tab=hot")

    # Print the page source to verify the element is present
    #print(driver.page_source) # recaptcha will be present in the page source if ran in headless mode

    # Increase the wait time
    wait = WebDriverWait(driver, 10)

    try:
        print("Waiting for the element to be located")
        wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//a[@class="block bg-cover bg-center w-full h-full bg-light-skeleton overflow-hidden dark:bg-dark-skeleton"]')))
        print("Element found")
    except Exception as e:
        print("Element not found")
        raise e
    # Extract image URLs (modify the XPath based on the page structure)
    image_elements = driver.find_elements(
        By.XPATH, '//a[@class="block bg-cover bg-center w-full h-full bg-light-skeleton overflow-hidden dark:bg-dark-skeleton"]')

    url_result1 = extract_url_data(image_elements)

    # scroll down a few pages for more images
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    body.send_keys(Keys.PAGE_DOWN)
    body.send_keys(Keys.PAGE_DOWN)
    body.send_keys(Keys.PAGE_DOWN)
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)
    
    image_elements_scrolled = driver.find_elements(
        By.XPATH, '//a[@class="block bg-cover bg-center w-full h-full bg-light-skeleton overflow-hidden dark:bg-dark-skeleton"]')
    #print(f"Found {len(image_elements)} images before scrolling.")
    print(f"Found {len(image_elements_scrolled)} images after scrolling down")

    url_result2 = extract_url_data(image_elements_scrolled)
    url_result = url_result1 + url_result2
    random.shuffle(url_result)

    for url in url_result[:amount_of_images]:
        thr = threading.Thread(target=download_image, args=(url,url_result,))
        thr.start()
        threads.append(thr)
        time.sleep(2)
    [t.join() for t in threads]
    # Quit the driver
    driver.quit()

def extract_url_data(image_elements):
    desired_images = []
    for el in image_elements:
        # Option 1: If the element itself has size information (for background images or divs)
        size = el.size
        height = size['height']
        if height == 550: # aspect ratio of 9:16
            desired_images.append(el)

    print(f"Found {len(desired_images)} images with the desired aspect ratio")
    # Regex pattern
    pattern = r'"[^"]*"\)\s*2x\)' # Extract the URL inside the background-image URL with 2x resolution

    background_image_elements = [img.get_attribute("style").split(';')[1] for img in desired_images]
    matches = [str(re.findall(pattern, elem)) for elem in background_image_elements]
    # Print the extracted URLs
    url_result = [extract_string_inside_quotes(match) for match in matches]
    return url_result