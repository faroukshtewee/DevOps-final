import time
import os
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import shutil
from exercisesApp.utils.db_connection import get_db_connection
import tempfile

# python -m exercisesApp.Automation.generate_images_automation


# Set Path to Save Images Inside Project
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets the project root
SAVE_DIR = os.path.join(PROJECT_DIR, "image_outputs")
# Create the directory if it does not exist
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize WebDriver options
options = webdriver.ChromeOptions()
# we use these three lines whene run selenium inside container or remote server
# if i run it localy i can remove the --headless to see the chrome page for debugging
# and if i run it localy i can remove the --disable-dev-shm-usage to use the  shared memory  (/dev/shm) for faster performance
options.add_argument("--headless")  # Run in background (remove for debugging)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Create a temporary directory for the user data
user_data_dir = tempfile.mkdtemp()

# Set the user data directory to avoid conflicts
options.add_argument(f"--user-data-dir={user_data_dir}")

# Set Chrome download folder
prefs = {"download.default_directory": SAVE_DIR}  # Set Chrome download folder
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)
driver.get("https://raphaelai.org")

conn = get_db_connection('Automation')
cursor = conn.cursor()
cursor.execute("SELECT name_of_exercise FROM Exercise")
exercises = [row[0] for row in cursor.fetchall()]


for exercise in exercises:
    try:
        print(f"Processing: {exercise}")

        # Find the text input box and enter the exercise name
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="generator"]/div/div[1]/textarea'))
        )
        input_box.clear()
        input_box.send_keys(f'gym {exercise} man')
        input_box.send_keys(Keys.RETURN)

        # Click Generate Button
        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="generator"]/div/div[1]/div/button'))
        )
        generate_button.click()

        # Wait for Image to be Generated
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="generator"]/div/div[2]/div/img'))
        )

        # Click Download Button
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="generator"]/div/div[2]/div/button'))
        )
        download_button.click()

        time.sleep(5)
        downloaded_image = max(os.listdir(SAVE_DIR), key=lambda f: os.path.getctime(os.path.join(SAVE_DIR, f)))

        old_path = os.path.join(SAVE_DIR, downloaded_image)
        new_path = os.path.join(SAVE_DIR, f"{exercise}.png")
        shutil.move(old_path, new_path)

        print(f"Saved: {new_path}")

    except Exception as e:
        print(f"Error processing {exercise}: {e}")


cursor.close()
conn.close()
driver.quit()
