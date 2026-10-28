from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://bilet.tcdd.gov.tr/")
    
    time.sleep(5)
    
    with open("tcdd_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    driver.quit()
    print("HTML kaydedildi.")

if __name__ == "__main__":
    debug()
