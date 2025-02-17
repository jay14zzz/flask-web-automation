from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from webdriver_manager.chrome import ChromeDriverManager

import time

def dropdown1_check(url, element_id):
    status = "success"
    message = ""
    dropdown_options = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--start-maximized")
    
    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        return {"status": "error", "message": f"error initializing driver: {str(e)}", "options": dropdown_options}

    try:
        # Open the URL
        driver.get(url)
        time.sleep(3)
    except Exception as e:
        driver.quit()
        return {"status": "error", "message": f"error opening URL: {str(e)}", "options": dropdown_options}

    try:
        # Find the dropdown element by its ID
        dropdown = Select(driver.find_element(By.ID, element_id))
    except Exception as e:
        driver.quit()
        return {"status": "error", "message": f"error finding element: {str(e)}", "options": dropdown_options}

    try:
        # Get all options from the dropdown
        dropdown_options = [option.text for option in dropdown.options]
    except Exception as e:
        driver.quit()
        return {"status": "error", "message": f"error retrieving options: {str(e)}", "options": dropdown_options}

    driver.quit()
    return {"status": status, "message": message, "options": dropdown_options}