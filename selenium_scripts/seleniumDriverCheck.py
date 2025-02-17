# selenium_script.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def selenium_driver_check():
    try:
        # Define Chrome options
        chrome_options = Options()
        # Add arguments to Chrome options
        # chrome_options.add_argument("--start-maximized")  # Opens the browser window in fullscreen mode
        chrome_options.add_argument("--headless")  # Uncomment to run Chrome in headless mode (without opening the browser window)

        # Initialize the Chrome WebDriver with ChromeDriverManager
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        # Open the webpage
        url = "https://example.com"  # Replace this with the URL of the webpage you want to open
        driver.get(url)
        time.sleep(5)

        # Check the title of the page to ensure it's the correct page
        if "Example Domain" in driver.title:
            result = {"status": "success", "message": "Driver check completed - Selenium Script ran successfully"}
        else:
            result = {"status": "failed", "message": "Unexpected page title"}

        # Close the webdriver
        driver.quit()
    except Exception as e:
        result = {"status": "error", "message": str(e)}
    
    return result
