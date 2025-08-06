# Selenium Web Automation Tool (POC)

This is a simple Flask web application developed as a proof of concept (POC) to run Selenium scripts dynamically based on user input. It allows users to verify web elements such as dropdowns on any given web page by providing the URL and element locators. The results of the Selenium tests are displayed directly within the web app.

## Purpose

The tool is designed to run Selenium tests on the server side, enabling multiple users to simultaneously and independently verify web elements via the web interface. This concurrent usage capability was a key reason for developing this POC.

## Features

- Input any URL and Selenium element locators dynamically through the web interface
- Run Selenium scripts on-demand with user-provided inputs
- View test results instantly on the web page
- Supports multiple users running tests in parallel on the server
- currently supports login combination verification and dropdown verification (single and multiple/dependent dropdown that loads dynamically)

## Usage

1. Clone the repository
2. Install required dependencies from requirements.txt (`Flask`, `Selenium`, etc.)
3. Run the Flask app (app.py)
4. Access the web interface, enter the URL and locator values
5. Submit to run Selenium verification and view results

## Note

This repository is shared publicly to showcase the concept and implementation.
Use signup to create new user. For admin/login (admin dashboard - can add & delete users) use 'admin', 'adminpassword' as username, password.
---

Feel free to explore and reach out if you have any questions!
