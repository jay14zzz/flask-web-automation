from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager


import time
import pandas as pd
import requests
# import easyocr
import traceback
from datetime import datetime
import uuid
import os

# Define a function to perform the login test
def perform_login_test(driver, url, login_value, pass_value):
    try:
        driver.get(url)
        time.sleep(1)

        # Select language (if required)
        try:
            english_radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='english']")
            english_radio_button.click()
        except Exception as e:
            pass
            
        username_input = driver.find_element(By.NAME, "registration_no")
        username_input.clear()
        username_input.send_keys(login_value)

        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(pass_value)

        # Captcha handling
        flag = 0
        cap_ctr = 1
        # while flag == 0:
        #     captcha_input = driver.find_element(By.NAME, "txtCode")
        #     img_element = driver.find_element(By.ID, "image")
        #     image_url = img_element.get_attribute("src")
        #     # Generate a unique filename using UUID
        #     image_filename = f'captcha_image_{uuid.uuid4()}.jpg'
        #     response = requests.get(image_url)
        #     with open(image_filename, 'wb') as f:
        #         f.write(response.content)
        #     reader = easyocr.Reader(['en'], gpu=False)
        #     results = reader.readtext(image_filename)
        #     detected_text = results[0][1].lower().replace(" ", "")
        #     captcha_input.send_keys(detected_text)
        #     os.remove(image_filename)
        #     driver.find_element(By.TAG_NAME, 'h4').click()
        #     time.sleep(1)
        #
        #     error_label = driver.find_element(By.CLASS_NAME, "error")
        #     if error_label.is_displayed():
        #         flag = 0
        #         driver.find_element(By.LINK_TEXT, "here").click()
        #         cap_ctr += 1
        #         time.sleep(3)
        #     else:
        #         flag = 1

        login_btn = driver.find_element(By.XPATH, "//input[@value='Login' and @class='btn blue_button5 right']")
        login_btn.click()
        time.sleep(3)

        
        try:
            invalid_label=driver.find_element(By.XPATH,"//label[contains(@class, 'js-invalid')]")
            if invalid_label.is_displayed():
                return cap_ctr, "failed -- Invaild Data"
            unknown_invalid_label=driver.find_element(By.XPATH,"//label[contains(@class, 'error')]")
            if unknown_invalid_label.is_displayed():
                return cap_ctr, "failed -- Invaild Data - UNK error "
        except:
            pass
        return cap_ctr, "success"
    except Exception as e:
        traceback.print_exc()
        return 'NaN', "failed -- unexpected error while executing"
    
def test_login_combinations(url, file_path, login_columns, password_columns, dob_format, test_case):
    
    # data_frame = pd.read_excel(filepath)
    if file_path.endswith('.csv'):
        # Read CSV file using pandas
        data_frame = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        # Read Excel file using pandas
        data_frame = pd.read_excel(file_path)
    else:
        # return "Unsupported file format"
        return {"status": "failed", "message": "Failed to read file"}
        
    # Store the test results    
    test_result = []

    if test_case =="limited":
        # len_of_df = len(data_frame)
        len_of_df = data_frame.shape[0]
        if len_of_df > 10:
            data_frame = data_frame[:3]
        elif len_of_df >=2:
            data_frame = data_frame.head(2)
        elif len_of_df == 0:
            return {"status": "failed", "message": "Failed to read file (insufficient data)"}

    
    # Iterate through each row and each combination of login and password fields
    for index, row in data_frame.iterrows():
        for login_col in login_columns:
            for pass_col in password_columns:
                login_value = row[login_col]
                pass_value = row[pass_col]
    
                # print(pass_value,type(pass_value))
    
                try:
                    # pass_value = pd.to_datetime(pass_value, dayfirst=True).strftime('%d-%m-%y')
                    # dob format conversion logic/ code changed. since the above line converts even mobile no to dob format without error

                    # Attempt to parse the value as a date with day-first format
                    c_value = str(pass_value)
                    c_value = c_value.replace('/', '-')
                    parsed_date = datetime.strptime(c_value, '%d-%m-%Y') # Y - 4y format; y - 2y format;
                    # If successful, format date as dd-mm-yy
                    pass_value = parsed_date.strftime('%d-%m-%y')
                    if dob_format == 'yyyy':
                        pass_value = parsed_date.strftime('%d-%m-%Y')
                except ValueError:
                    # pass
                    try:
                        # pass_value = pd.to_datetime(pass_value, dayfirst=True).strftime('%d-%m-%y')
                        # dob format conversion logic/ code changed. since the above line converts even mobile no to dob format without error

                        # Attempt to parse the value as a date with day-first format
                        c_value = str(pass_value)
                        c_value = c_value.replace('/', '-')
                        parsed_date = datetime.strptime(c_value, '%d-%m-%y')
                        # If successful, format date as dd-mm-yy
                        pass_value = parsed_date.strftime('%d-%m-%y')
                        if dob_format == 'yyyy':
                            pass_value = parsed_date.strftime('%d-%m-%Y')
                    except ValueError:
                        pass

                # print(pass_value,type(pass_value))
    
                # Initialize the Chrome WebDriver
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                # chrome_options.add_argument("--start-maximized")
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
                
                cap_ctr, status = perform_login_test(driver, url, login_value, pass_value)
                test_result.append(f"Test case {index + 1} : {login_value} and {pass_value} - {status}. Captcha try count: {cap_ctr}")
    
                driver.quit()
                
    # return test_result
    return {"status": "success", "results": test_result}


# # Debug statements for running login script
# # Read data from the Excel file
# file_path = r'C:\Users\017927\Documents\Projects\May 24\Call Letter\bobfojan24_oecla_may24\Sample_DATA (1).csv'
# url = "https://regqc.sifyitest.com/bobfojan24/oecla_may24/login.php?appid=78fc7136fcc5e0413bd46958952aee9b"
# # Define the login and password field combinations
# login_columns = ['RegistrationNo', 'Rollno']  # Add your actual column names for Rollno and Registration_No
# password_columns = ['Password', 'Birthdate']  # Add your actual column names for Password and DOB


# app = test_login_combinations(url, file_path, login_columns, password_columns)