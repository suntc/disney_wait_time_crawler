import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from pathlib import PurePath, Path

def setup_driver():
    url = "http://www15.plala.or.jp/gcap/disney/realtime.htm"
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)
    driver.get(url)
    
    return driver

def get_para_date(para):
    para_date = int(para.split('(')[1].split(',')[0])
    return para_date

def get_function_paras(driver):
    ## start from current page
    MIN_DATE = 20111101

    def handle_one_page():
        para_list = []
        ## BOX, BOXA are class names used by the calendar div
        ele_BOX = driver.find_elements(By.CLASS_NAME, "BOX")
        ele_BOXA = driver.find_elements(By.CLASS_NAME, "BOXA")
        cell_count = len(ele_BOX) + len(ele_BOXA)
        ## cal0 ~ calXX are ID used by calendar's div
        for i in range(cell_count):
            cid = 'cal' + str(i)
            try:
                element = driver.find_element(By.ID, cid)
                para = element.get_attribute('onclick')
                para_list.append(para)
            except Exception as e:
                print(e)
        return para_list

    all_paras = []
    button = driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='前月']")))
    try:
        while True:
            para_list = handle_one_page()
            min_para = para_list[0]
            min_para_date = int(min_para.split('(')[1].split(',')[0])
            print(para_list)
            all_paras = all_paras + para_list[::-1]
            if min_para_date <= MIN_DATE:
                break
            button.click()
            button = driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='前月']")))
        ## output to file
        with open("function_paras.json", 'w') as outfile:
            json.dump(all_paras, outfile)
            outfile.close()

    except Exception as e:
        print(e)

            
            
def get_tables_html_by_page(driver):
    MAX_DATE = 20180228
    MIN_DATE = 20111101

    def handle_one_page():
        para_list = []
        ## BOX, BOXA are class names used by the calendar div
        ele_BOX = driver.find_elements(By.CLASS_NAME, "BOX")
        ele_BOXA = driver.find_elements(By.CLASS_NAME, "BOXA")
        cell_count = len(ele_BOX) + len(ele_BOXA)
        ## cal0 ~ calXX are ID used by calendar's div
        for i in range(cell_count):
            cid = 'cal' + str(i)
            try:
                element = driver.find_element(By.ID, cid)
                para = element.get_attribute('onclick')
                para_list.append(para)
            except Exception as e:
                print(e)
        return para_list
    
    all_paras = []
    button = driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='前月']")))
    html_dict = {}
    try:
        while True:
            para_list = handle_one_page()
            min_para = para_list[0]
            min_para_date = int(min_para.split('(')[1].split(',')[0])

            for para in para_list:
                para_date = get_para_date(para)
                if para_date > MAX_DATE or para_date < MIN_DATE:
                    continue
                if para_date in html_dict:
                    continue
                driver.execute_script(para)
                ## arbitrarily pick one element to test whether is has been loaded
                locator = (By.CLASS_NAME, "BUSY0")
                driver.wait.until(EC.presence_of_element_located(locator))
                # time.sleep(1)
                table = driver.find_element(By.ID, "boxG")
                innerhtm = table.get_attribute("innerHTML")
                htm = '<div id="boxG">' + innerhtm + '</div>'
                html_dict.setdefault(para_date, htm)
                print(htm)
                ## output to file
                fp = Path('tables')
                if not fp.exists():
                    fp.mkdir()
                p = PurePath('tables', str(para_date) + ".html")
                with open(str(p), 'w') as outfile:
                    outfile.write(htm)
                    outfile.close()
            if min_para_date <= MIN_DATE:
                break
            button.click()
            button = driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='前月']")))

    except Exception as e:
        print(e)


def get_tables_html(driver, paras):
    ## BOXG is the class name of the outer container of the table we intersted in
    MAX_DATE = 20180228
    MIN_DATE = 20111101
    button = driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='前月']")))
    html_dict = {}
    for para in paras:
        para_date = get_para_date(para)
        if para_date > MAX_DATE or para_date < MIN_DATE:
            continue
        if para_date in html_dict:
            continue
        driver.execute_script(para)
        ## arbitrarily pick one element to test whether is has been loaded
        locator = (By.CLASS_NAME, "BUSY0")
        driver.wait.until(EC.presence_of_element_located(locator))
        # time.sleep(1)
        table = driver.find_element(By.ID, "boxG")
        innerhtm = table.get_attribute("innerHTML")
        htm = '<div id="boxG">' + innerhtm + '</div>'
        html_dict.setdefault(para_date, htm)
        print(htm)


def main():
    driver = setup_driver()
    # get_function_paras(driver)
    with open("function_paras.json", 'r') as infile:
        all_paras = json.load(infile)
        infile.close()
    get_tables_html_by_page(driver)

if __name__ == '__main__':
    main()