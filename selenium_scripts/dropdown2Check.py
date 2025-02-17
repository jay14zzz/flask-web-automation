from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

import time

def dropdown2_check(url,id1,id2):

    status = "success"
    dropdownlst1 = []
    dropdownlst2 = []
    # driver = None
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--start-maximized")

    try:
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        return {"status": "error", "message": f"error initializing driver: {str(e)}", "options1": dropdownlst1, "options2": dropdownlst2}

    try:
        driver.get(url)
        time.sleep(3)
    except Exception as e:
        return {"status": "error", "message": f"error navigating to URL: {str(e)}", "options1": dropdownlst1, "options2": dropdownlst2}

    try:
        # Find the dropdown element by its ID
        dropdown1 = Select(driver.find_element(By.ID, id1))
    except Exception as e:
        return {"status": "error", "message": f"error finding element 1: {str(e)}", "options1": dropdownlst1, "options2": dropdownlst2}

    try:
        # Find the dropdown element by its ID
        dropdown2 = Select(driver.find_element(By.ID, id2))
    except Exception as e:
        return {"status": "error","message": f"error finding element 2: {str(e)}", "options1": dropdownlst1, "options2": dropdownlst2}


    # # Find the dropdown element by its ID
    # dropdown1 = Select(driver.find_element(By.ID,"selstateapplied"))
    # dropdown2 = Select(driver.find_element(By.ID,"selexamcentre"))

    try:
        dropdownlst1 = []
        dropdownlst2 = []
        
        # Iterate through each option and select it
        for option1 in dropdown1.options:
            # Get the text of the option
            option1_text = option1.text
            # Select the option by visible text
            dropdown1.select_by_visible_text(option1_text)
            try:
                alert = driver.switch_to.alert
                alert.accept()  # Accept the alert (click "OK")
            except NoAlertPresentException:
                pass  # No alert is present, do nothing
                    
            # Optional: Perform actions after selecting each option
            # Example: Print selected option text
            # print(f"Selected option for dropdown1: {option1_text}")
            dropdownlst1.append(option1_text)
            
            # Optional: Add a delay (for demonstration purposes)
            # driver.implicitly_wait(1)  # Wait for 1 second
        
            time.sleep(1)
            
            dropdown2 = driver.find_element(By.ID,id2)
            temp_lst = []
            if (dropdown2.is_enabled()==False):
                temp_lst.append("Select (disabled)")
                dropdownlst2.append(temp_lst)
                continue
            dropdown2 = Select(driver.find_element(By.ID,id2))
            for option2 in dropdown2.options:
                # Get the text of the option
                option2_text = option2.text
                # Select the option by visible text
                # dropdown2.select_by_visible_text(option2_text)
                
                # Optional: Perform actions after selecting each option
                # Example: Print selected option text
                # print(f"Selected option for dropdown2    : {option2_text}")
                # time.sleep(1)
                temp_lst.append(option2_text)
            if (temp_lst[0]=='Select' and len(temp_lst)>1):
                temp_lst.pop(0)
            dropdownlst2.append(temp_lst)
    except Exception as e:
        driver.quit()
        return {"status": "error", "message": f"retrieving options: {str(e)}", "options1": dropdownlst1, "options2": dropdownlst2}

    # dropdown_options_1 = dropdownlst1
    # dropdown_options_2 = dropdownlst2
    dropdownlst1.pop(0)
    dropdownlst2.pop(0)

    driver.quit()
    return {"status": status, "options1": dropdownlst1, "options2": dropdownlst2}

    