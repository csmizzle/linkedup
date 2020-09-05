from time import sleep
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from .tools import connect_driver, flatten
from tqdm import tqdm


class Cufflinx:
    """
    LinkedIn Scraper that uses account name and password to
    collect data based on a google boolean search
    TODO: Add targeted searching for analysts
    TODO: Breaks on search "'Computer Vision' AND 'China' AND 'Tshinghua'", "Can't find good results"
    """
    def __init__(self, path: str):
        # driver path for Chrome agent
        if path:
            self.driver = connect_driver(path)
        else:
            self.driver = connect_driver('../driver/chromedriver.exe')

    def linkedin_login(self, username: str, password: str, url: str):

        print('Logging into Linkedin...')
        username = str(username)
        password = str(password)
        # username
        self.driver.get(url)
        username_box = self.driver.find_element_by_xpath('//div[@class="form__input--floating"]')
        type_username = username_box.find_element_by_id('username')
        type_username.click()
        type_username.send_keys(username)
        sleep(0.5)

        # password
        password_box = self.driver.find_element_by_xpath('//div[@class="form__input--floating"][2]')
        type_password = password_box.find_element_by_id('password')
        type_password.click()
        type_password.send_keys(password)
        sleep(0.5)

        # hit enter
        button = self.driver.find_element_by_xpath('//div[@class="login__form_action_container "]')
        button.click()

        current_url = self.driver.current_url
        if 'https://www.linkedin.com/check/add-phone' in current_url:
            print('Asking for phone number...')
            skip_button = self.driver.find_element_by_xpath('//div[@class="secondary-action"]')
            skip_button.click()
            print('Skipped that...')
            print('Ready to search!')
        elif current_url == 'https://www.linkedin.com/error_pages/unsupported-browser.html':
            print('Unsupported Browser ... going to continue anyways')
            try:
                allow = self.driver.find_element_by_xpath('//a[@href="https://www.linkedin.com/?allowUnsupportedBrowser=true"]')
                allow_link = allow.get_attribute("href")
                self.driver.get(allow_link)
            except NoSuchElementException:
                continue_click = self.driver.find_element_by_css_selector('[title="continue anyway"]')
                continue_click.click()
            print('Ready to search!')
        else:
            print('Ready to search!')
        sleep(10)

    def google_search_results(self, page_num: int, search: str) -> list:

        # search Google for the given search terms
        print('Google Search ...')
        search = str(search)
        self.driver.get('https://www.google.com')
        search_query = self.driver.find_element_by_name('q')
        search_query.send_keys(search)
        search_query.send_keys(u'\ue007')
        sleep(3)
        # get href links
        pages = page_num
        list_of_links = []
        # collects links from each google page per the -p flag in the parser arguments

        for p in range(pages):
            next_page = self.driver.find_elements_by_id('pnnext')
            if len(next_page) > 1:
                next_page = self.driver.find_elements_by_id('pnnext')[1]
            else:
                next_page = self.driver.find_elements_by_id('pnnext')[0]
            elems = self.driver.find_elements_by_xpath("//a[@href]")
            links = [x.get_attribute("href") for x in elems
                     if str(x.get_attribute("href")).startswith("https://www.linkedin.com/in/")]
            list_of_links.append(links)
            sleep(3)
            next_page.click()
        list_of_links = flatten(list_of_links)
        # no duplicates in list using set
        return list(set(list_of_links))

    def scrape_profiles(self, list_of_links: list) -> list:
        """
        TODO: More data to be collected ... positions, years, skills
        :param list_of_links:
        :return:
        """
        print('Scraping profiles ...')
        results = []
        # this is where the magic happens ...
        for url in tqdm(list_of_links):
            print('Scraping', str(url), '...')
            self.driver.get(url)
            current_link = self.driver.current_url
            sleep(5)
            element = self.driver.find_element_by_id("oc-background-section")
            actions = ActionChains(self.driver)
            try:
                more_exp = self.driver.find_element_by_class_name('pv-experience-section__see-more')
                actions.move_to_element(more_exp).perform()
                print('Showing all exp...')
                more_exp.find_element_by_class_name('pv-profile-section__see-more-inline').click()
                sleep(2)
            except NoSuchElementException:
                print('No extra exp to show...')
                pass
            actions.move_to_element(element).perform()
            print('Rendering Java for', url, '...')
            sleep(5)
            soup = BeautifulSoup(self.driver.page_source, features="lxml")
            try:
                name = soup.find('title').text.split('|')[0].strip()
            except IndexError:
                name = 'No data'
            try:
                company = soup.findAll("span", {"class": "text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view"})[0].text.strip()
            except IndexError:
                company = 'No data'
            try:
                job = soup.findAll("h2", {"class": "mt1 t-18 t-black t-normal break-words"})[0].text.strip()
            except IndexError:
                job = 'No data'
            try:
                experience = [e.text.strip() for e in soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
                if len(experience) == 0:
                    self.driver.execute_script("window.scrollTo(0, 500)")
                    print('Looking for exp...')
                    sleep(3)
                    experience = [e.text.strip() for e in soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
            except IndexError:
                experience = ['No data']
            try:
                education = [c.text.strip() for c in soup.findAll('h3', {"class": "pv-entity__school-name t-16 t-black t-bold"})]
            except IndexError:
                education = ["No data"]
            try:
                fos = [f.text.strip() for f in soup.findAll('span', {"class": "pv-entity__comma-item"})]
            except IndexError:
                fos = ['No data']
            try:
                loc = soup.findAll("li", {"class": "t-16 t-black t-normal inline-block"})[0].text.strip()
            except IndexError:
                loc = 'No data'
            entry = [name, company, job, experience, education, fos, loc, current_link]
            results.append(entry)

        self.driver.close()

        return results
