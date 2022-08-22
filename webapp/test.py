from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import threading
from collections import deque
import sys

class Scraper(threading.Thread):
    def run(self):
        global urls
        global is_processing
        global options
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, 10)
        driver.get('https://quizlet.com/login')
        driver.find_element(By.ID, 'username').send_keys(os.getenv('QUIZLET_USER'))
        driver.find_element(By.ID, 'password').send_keys(os.getenv('QUIZLET_PASS'))
        driver.find_element(By.ID, 'password').send_keys(Keys.ENTER)
        wait.until(EC.url_changes('https://quizlet.com/login'))
        while True:
            lock_con.acquire()
            print(f'url queue is {urls}')
            if len(urls) == 0:
                lock_con_2.acquire()
                is_processing = False
                driver.quit()
                lock_con_2.release()
                lock_con.release()
                break
            url = urls.popleft()
            lock_con.release()
            print(f'"{url}" is proccessing.')
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            elements = soup.find_all('span', class_='TermText')
            words = {}
            for i in range(0, len(elements), 2):
                words[elements[i].text] = elements[i+1].text
            print(words)

def url_add(url):
    global urls
    global is_processing
    lock_con.acquire()
    urls.append(url)
    print(f'"{url}" is added.')
    lock_con.release()
    lock_con_2.acquire()
    if not is_processing:
        Scraper().start()
        is_processing = True
    lock_con_2.release()

urls = deque()
is_processing = False
lock_con = threading.Condition()
lock_con_2 = threading.Condition()

options = webdriver.FirefoxOptions()
options.add_argument('--headless')

url_add('https://quizlet.com/jp/710467932/%E3%82%AE%E3%83%AA%E3%82%B7%E3%83%A3%E6%96%87%E5%AD%97-flash-cards/')
url_add('https://quizlet.com/jp/712164442/stock-4500-19772029-flash-cards/')
url_add('https://quizlet.com/_bs05fo?x=1jqt&i=3bkz3f')
url_add('https://quizlet.com/_br3hv4?x=1jqt&i=3bkz3f')