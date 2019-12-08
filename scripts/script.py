from selenium import webdriver
from time import sleep
import csv
from bs4 import BeautifulSoup
import argparse
import random
from selenium.webdriver.chrome.options import Options
import sys
import time
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search', help='Enter Google boolean search e.x. "site:linkedin.com/in/ AND *single quote*Data Scientist*single quote* AND *single quote*Washington D.C. Metro Area*single quote* AND *single quote*Christopher Smith*single quote*"')
    parser.add_argument('-p', '--pages', default=1, help='Enter number of pages to be searched')
    parser.add_argument('-f', '--file_name', default='linked_in_scrape'+str(time.strftime('%Y%m%d-%H%M')), help='Enter filename for .csv output')

    return parser.parse_args()

def get_ua():

    ua_list = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
               "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
               "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
               "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
               "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
               "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
               "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"]
    ua = random.choice(ua_list)

    return ua

def get_account():
    
    account_list = [
        # to add more account, just make a new list within this list
        # ['account_example', 'password_example'],
        ['',''],

    ]
    account = random.choice(account_list)

    return(account)

def connect_driver(path):

    useragent = get_ua()
    options = Options()
    options.add_argument(f'user-agent={useragent}')
    driver = webdriver.Chrome(path, chrome_options=options)
    #driver = webdriver.Chrome(path)

    return driver

def linkedin_login(driver,username,password,url):

    print('Logging into Linkedin...')
    username = str(username)
    password = str(password)
    # username
    driver.get(url)
    username_box = driver.find_element_by_xpath('//div[@class="form__input--floating"]')
    type_username = username_box.find_element_by_id('username')
    type_username.click()
    type_username.send_keys(username)
    sleep(0.5)

    # password
    password_box = driver.find_element_by_xpath('//div[@class="form__input--floating"][2]')
    type_password = password_box.find_element_by_id('password')
    type_password.click()
    type_password.send_keys(password)
    sleep(0.5)

    # hit enter
    button = driver.find_element_by_xpath('//div[@class="login__form_action_container "]')
    button.click()

    current_url = driver.current_url
    if 'https://www.linkedin.com/check/add-phone' in current_url:
        print('Asking for phone number...')
        skip_button = driver.find_element_by_xpath('//div[@class="secondary-action"]')
        skip_button.click()
        print('Skipped that...')
        print('Ready to search!')
    elif current_url == 'https://www.linkedin.com/error_pages/unsupported-browser.html':
        print('Unsupported Browser ... going to continue anyways')
        allow = driver.find_element_by_xpath('//a[@href="https://www.linkedin.com/?allowUnsupportedBrowser=true"]')
        allow_link = allow.get_attribute("href")
        driver.get(allow_link)
        print('Ready to search!')
    else:
        print('Ready to search!')
    sleep(10)

def google_search_results(driver, page_num, search):

    print('Google Search...')
    search = str(search)
    driver.get('https://www.google.com')
    search_query = driver.find_element_by_name('q')
    search_query.send_keys(search)
    search_query.send_keys(u'\ue007')
    sleep(3)
    # get href links
    pages = page_num
    list_of_lists = []
    for p in range(pages):
        next_page = driver.find_elements_by_class_name('pn')
        if len(next_page) > 1:
            next_page = driver.find_elements_by_class_name('pn')[1]
        else:
            next_page = driver.find_elements_by_class_name('pn')[0]
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            links = elem.get_attribute("href")
        links = [x.get_attribute("href") for x in elems]
        list_of_lists.append(links)
        sleep(3)
        next_page.click()

    clean_links = []
    for l in list_of_lists:
        for x in l:
            x = str(x)
            if x.startswith('https://www.linkedin.com/in/'):
                clean_links.append(x)
    print('Scraping profiles...')

    results = []
    for url in clean_links:
        print('Scraping', url,'...')
        driver.get(url)
        current_link = driver.current_url
        sleep(5)
        element = driver.find_element_by_id("oc-background-section")
        actions = ActionChains(driver)
        try:
            more_exp = driver.find_element_by_class_name('pv-experience-section__see-more')
            actions.move_to_element(more_exp).perform()
            print('Showing all exp...')
            more_exp.find_element_by_class_name('pv-profile-section__see-more-inline').click()
            sleep(2)
        except NoSuchElementException:
            print('No extra exp to show...')
            pass
        actions.move_to_element(element).perform()
        print('Rendering Java for', url,'...')
        sleep(5)
        soup=BeautifulSoup(driver.page_source,features="lxml")
        try:
            name = soup.find('title').text.split('|')[0].strip()
        except IndexError:
            name = 'No data'
        try:
            company = soup.findAll("span", {"class": "text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view"})[0].text.strip()
        except IndexError:
            company = 'No data'
        try:
            job = soup.findAll("h2", {"class": "mt1 t-18 t-black t-normal"})[0].text.strip()
        except IndexError:
            job = 'No data'
        try:
            experience =  [e.text for e in soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
            if len(experience) == 0:
                driver.execute_script("window.scrollTo(0, 500)")
                print('Looking for exp...')
                sleep(3)
                experience =  [e.text for e in soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
        except IndexError:
            experience = ['No data']
        try:
            education = [c.text for c in soup.findAll('h3', {"class": "pv-entity__school-name t-16 t-black t-bold"})]
        except IndexError:
            education = ["No data"]
        try:
            fos = [f.text for f in soup.findAll('span', {"class": "pv-entity__comma-item"})]
        except IndexError:
            fos = ['No data']
        try:
            loc = soup.findAll("li", {"class": "t-16 t-black t-normal inline-block"})[0].text.strip()
        except IndexError:
            loc = 'No data'

        entry = [name, company, job, experience, education, fos, loc, current_link]
        results.append(entry)
    driver.close()

    return(results)

def csv_writer(file_name, results_list_of_lists):
    # point this at your results fold, be sure to use forward slashes
    with open('./results/'+file_name+'.csv','w', errors='ignore', newline="") as f:
        w = csv.writer(f)
        w.writerows(results_list_of_lists)

def main():

    sys.path.append('./enviroment/env/Lib')
    print('Enviroment loaded...')
    print(sys.executable)
    args = parse_args()
    if not args.search:
        sys.exit("[!] Enter search terms or pharse with -s option e.x. -s 'chris smith'")
    #varaibles
    driver_path = './driver/final_driver/chromedriver_win32/chromedriver.exe'
    login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    account = get_account()
    user_name = account[0]
    pass_word = account[1]
    # file_name = 'results.csv'
    # change this to wahtever you want
    # search_query = "site:linkedin.com/in/ AND 'Data Scientist' AND 'Washington D.C. Metro Area' AND 'Christopher Smith'"
    search_query = args.search
    if not search_query.startswith('site:linkedin.com/in/'):
        search_query = 'site:linkedin.com/in/ ' + search_query
    else:
        search_query = args.search
    print("Searching:", search_query)
    pages_to_be_scrapped = int(args.pages)
    filename = args.file_name
    crawler = connect_driver(driver_path)
    linkedin_login(crawler,user_name,pass_word,login_url)
    results = google_search_results(crawler, pages_to_be_scrapped, search_query)
    csv_writer(filename, results)
    print('Done, check the results folder.')

if __name__ == "__main__":
    main()