from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time 
import re
import os 
import shutil
import argparse
from loguru import logger
from utils import retriever
from utils import pdf
from utils import storeData

logger.add("logfile.log", rotation="500 MB", retention="12 days", compression="zip")

def extract_info(input_string):
    pattern = r"^(.*?) - (\d+) - (.*)$"
    match = re.search(pattern, input_string)
    if match:
        company_name = match.group(1)
        number = match.group(2)
        title = match.group(3)
        return company_name, number, title
    else:
        return None, None, None
    
def getCompanyInfo(driver, bse_id : str):
    driver.get(f"https://www.screener.in/company/{bse_id}/")
    print('screener.in loaded successfully')
    bse_link = driver.find_element(By.XPATH, '//*[@id="top"]/div[3]/div[1]/div[2]/a[2]').get_attribute('href')
    driver.get(bse_link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="deribody"]/div[4]/div/div[2]/div/div/table/tbody[1]/tr[12]/td[3]')))
    net_profit = driver.find_element(By.XPATH, '//*[@id="res"]/div/div/table/tbody[2]/tr[1]/td[4]').text
    revenue = driver.find_element(By.XPATH, '//*[@id="res"]/div/div/table/tbody[1]/tr[1]/td[4]').text
    sales = driver.find_element(By.XPATH, '//*[@id="deribody"]/div[4]/div/div[2]/div/div/table/tbody[1]/tr[12]/td[3]').text
    # driver.quit()
    return net_profit, revenue, sales

def scraper(scrape_time):
    logger.info(f"Scraping at {datetime.now()}")
    print(f"Scraping at : {scrape_time}")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')  
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    WEBPAGE = "https://www.bseindia.com/corporates/ann.html"
    
    reports = []
    driver.get(WEBPAGE)
    time.sleep(2)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="lblann"]/table/tbody/tr[4]/td/table')))
    table_Xpath = '//*[@id="lblann"]/table/tbody/tr[4]/td'
    number_of_rows = len(driver.find_elements(By.XPATH, '//*[@id="lblann"]/table/tbody/tr[4]/td/table')) + 1
    latest_received_time = scrape_time
    
    for row in range(1, number_of_rows):
        try:
            received_time_str = driver.find_element(By.XPATH, table_Xpath + f'/table[{row}]/tbody/tr[3]/td/b[1]').text
            date_object = datetime.strptime(received_time_str, "%d-%m-%Y %H:%M:%S")
            received_time = date_object.time()

            if received_time <= scrape_time:
                continue
            title = driver.find_element(By.XPATH, value=table_Xpath + f'/table[{row}]/tbody/tr[1]/td[1]/span').text
            company, bse_id, subject = extract_info(title)
            update_type = driver.find_element(By.XPATH, f'//*[@id="lblann"]/table/tbody/tr[4]/td/table[{row}]/tbody/tr[1]/td[2]').text
            if update_type and update_type in ['Company Update', 'Result']:
                result_pattern = ['year', 'unaudited', 'financial results', 'ended', 'end']
                pattern1 = r"\b(?:Award_of_Order|Receipt_of_Order)\b"
                pattern2 = r"\b(?:year|Year) (?:ended|Ended)Un-Audited|Unaudited|Audited|Financial Results\b"
                match1 = re.findall(pattern1, title, re.IGNORECASE)
                match2 = re.findall(pattern2, title, re.IGNORECASE)
                if not match1 and not match2:
                    logger.debug("No pattern match found")
                    continue
            else:
                continue

            pdf_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@id="lblann"]/table/tbody/tr[4]/td/table[{row}]/tbody/tr[1]/td[4]/a'))
            ).get_attribute('href')

            logger.info(f"Title : {title}")
            
            net_profit, revenue, sales = getCompanyInfo(driver2, bse_id=str(bse_id))
            time.sleep(1)
            filepath = pdf.downloadFile(pdf_link)
            reports.append({
                "company": company,
                "subject": subject,
                "link": pdf_link,
                "received_time": received_time,
                "category" : update_type, 
                "filepath" : filepath, 
                "Sales" : sales, 
                "Net Profit" : net_profit, 
                "Revenue" : revenue
            })
            if received_time > latest_received_time:
                latest_received_time = received_time

        except Exception as e:
            print(f'Exception ', e)

    logger.success('Scraped Successfully')
    driver.quit()
    driver2.quit()
    return reports, latest_received_time

def process_reports(reports):
    if os.path.exists("files"):
        for report in reports:
            print(report)
            filepath = report['filepath']
            if report['category'] == 'Result': 
                prompt = "Give Standalone total income/revenue, profit before and after tax of the company. Use proper symbol for representing currency."
            else: 
                prompt = f"Give me the order amount the company {report['company']} received and by whom, the date at which the order was given and also the time period by which the order has to be executed."
            response = retriever.get_information(filepath, prompt, report['category'])
            print(response, end='\n\n')
            if report['category'] != "Result" :
                storeData.writeIntoFile(report, response)
            # sendSMS.sendSMSNotification(['+917042690376'], f"{report['company'].upper()}\n{response}")
        shutil.rmtree('files')
    return


def main():
    parser = argparse.ArgumentParser(description='Set scrape time for the scraper.')
    parser.add_argument('--scrape_time', type=str, required=True, help='Scrape time in HH:MM:SS format')
    args = parser.parse_args()

    scrape_time_str = args.scrape_time
    scrape_time = datetime.strptime(scrape_time_str, '%H:%M:%S').time()

    while True:
        reports, latest_received_time = scraper(scrape_time)
        if reports:
            process_reports(reports)
        scrape_time = latest_received_time
        time.sleep(180)

if __name__ == "__main__":
    main()
