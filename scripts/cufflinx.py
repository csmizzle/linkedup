from time import sleep
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from .tools import connect_driver, flatten, clean_text
from tqdm import tqdm
import traceback


class Cufflinx:
    """
    LinkedIn Scraper that uses account name and password to
    collect data based on a google boolean search
    TODO: Add targeted searching for analysts
    TODO: Breaks on search "'Computer Vision' AND 'China' AND 'Tshinghua'", "Can't find good results"
    """
    def __init__(self, path: str):
        # driver path for Chrome agent
        self.driver = connect_driver(path)

    def linkedin_login(self, username: str, password: str):

        # login url
        url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'

        print('[!] Logging into Linkedin...')
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
        # trying to bypass both unsupported browser and phone number checking web pages
        if 'https://www.linkedin.com/check/add-phone' in current_url:
            print('Asking for phone number...')
            skip_button = self.driver.find_element_by_xpath('//div[@class="secondary-action"]')
            skip_button.click()
            print('[!] Skipped that...')
            print('[!] Ready to search!')
        elif current_url == 'https://www.linkedin.com/error_pages/unsupported-browser.html':
            print('[!] Unsupported Browser ... going to continue anyways')
            try:
                allow = self.driver.find_element_by_xpath('//a[@href="https://www.linkedin.com/?allowUnsupportedBrowser=true"]')
                allow_link = allow.get_attribute("href")
                self.driver.get(allow_link)
            except NoSuchElementException:
                continue_click = self.driver.find_element_by_css_selector('[title="continue anyway"]')
                continue_click.click()
        print('Ready to search!')
        sleep(10)

    def google_search(self, search: str):
        # search Google for the given search terms
        print('[!] Google Search ...')
        search = str(search)
        self.driver.get('https://www.google.com')
        search_query = self.driver.find_element_by_name('q')
        search_query.send_keys(search)
        search_query.send_keys(u'\ue007')

    @staticmethod
    def collect_linkedin_accounts(elements):
        linkedin_accounts = [e.get_attribute("href") for e in elements
                             if str(e.get_attribute("href")).startswith("https://www.linkedin.com/in/")]
        return linkedin_accounts

    def bottom_of_page(self):
        # get size of page prior to scrolling
        len_prior = self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        # scroll to execute any java page extension
        self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(0.5)
        # get len after possibly generating more of the page
        len_after = self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if len_after != len_prior:
            # recursively call function if lengths are different; allows for all employees to be presented
            self.bottom_of_page()
        else:
            print('[!] Bottom of page reached ...')

    def company_search(self, company_name: str):
        # click on search bar
        search_bar = self.driver.find_element_by_xpath('//*[@placeholder="Search"]')
        search_bar.click()
        # send company into search box and search
        print('[!] Searching for', company_name)
        search_bar.send_keys(company_name)
        search_bar.send_keys(u'\ue007')
        sleep(2)
        # clicks on first company returned
        self.driver.find_element_by_class_name('search-result__title').click()

    def get_employees(self) -> list:
        # clicks on the employees card
        company_cards = self.driver.find_elements_by_class_name('t-14')
        print('[!] Getting employees ...')
        sleep(5)
        print(company_cards)
        employee_card = [c for c in company_cards if 'people' in str(c.get_attribute('href'))]
        print(employee_card)
        employee_card.click()
        # scroll to the bottom of the page and render
        self.bottom_of_page()
        # find employee links
        employee_links = self.driver.find_elements_by_xpath('//*[@data-control-name="people_profile_card_name_link"]')
        # collect hrefs from links
        employee_hrefs = [e.get_attribute('href') for e in employee_links]
        return employee_hrefs

    def collect_search_results(self, pages: int) -> list:
        # get href links
        list_of_links = []
        # collects links from each google page per the -p flag in the parser arguments
        for p in range(pages):
            elements = self.driver.find_elements_by_xpath('//*[@id="rso"]/div/div/div/a')
            links = self.collect_linkedin_accounts(elements)
            list_of_links.append(links)
            if pages > 1:
                self.driver.find_element_by_id('pnnext').click()
        list_of_links = flatten(list_of_links)
        # no duplicates in list using set
        return list(set(list_of_links))

    def profile_data_grabber(self, url: str) -> dict:
        """
        TODO: More data to be collected ... positions, years, skills
        :param url:
        :return:
        """
        print('[!] Scraping', str(url), '...')
        self.driver.get(url)
        current_link = self.driver.current_url
        sleep(5)
        element = self.driver.find_element_by_id("oc-background-section")
        actions = ActionChains(self.driver)
        try:
            more_exp = self.driver.find_element_by_class_name('pv-experience-section__see-more')
            actions.move_to_element(more_exp).perform()
            print('[!] Showing all exp...')
            more_exp.find_element_by_class_name('pv-profile-section__see-more-inline').click()
            sleep(2)
        except NoSuchElementException:
            print('[!] No extra exp to show...')
            pass
        actions.move_to_element(element).perform()
        print('[!] Rendering Java for', url, '...')
        sleep(5)
        soup = BeautifulSoup(self.driver.page_source, features="lxml")

        try:
            # added clean_text, names often have index? numbers next to them in the html
            name = clean_text(soup.find('title').text.split('|')[0].strip())
        except IndexError:
            name = 'No data'
        try:
            company = soup.findAll("span", {
                "class": "text-align-left ml2 t-14 t-black t-bold full-width "
                         "lt-line-clamp lt-line-clamp--multi-line ember-view"})[0].text.strip()
        except IndexError:
            company = 'No data'
        try:
            job = soup.findAll("h2", {"class": "mt1 t-18 t-black t-normal break-words"})[0].text.strip()
        except IndexError:
            job = 'No data'
        try:
            experience = [e.text.strip() for e in
                          soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
            if len(experience) == 0:
                self.driver.execute_script("window.scrollTo(0, 500)")
                print('Looking for exp...')
                sleep(3)
                experience = [e.text.strip() for e in
                              soup.findAll("p", {"class": "pv-entity__secondary-title t-14 t-black t-normal"})]
        except IndexError:
            experience = ['No data']
        try:
            education = [c.text.strip() for c in
                         soup.findAll('h3', {"class": "pv-entity__school-name t-16 t-black t-bold"})]
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
        try:
            skills = [s.text.strip() for s in
                      soup.findAll("span", {"class": "pv-skill-category-entity__name-text t-16 t-black t-bold"})]
        except NoSuchElementException:
            skills = "No data"
        except IndexError:
            skills = "No data"
        # data returned in dict() format
        entry = {
            'name': name,
            'company': company,
            'job': job,
            'experience': experience,
            'education': education,
            'fos': fos,
            'loc': loc,
            'skills': skills,
            'current_link': current_link
        }
        return entry

    def scrape_profiles(self, list_of_links: list) -> list:
        """
        :param list_of_links:
        :return:
        """
        print('[!] Scraping profiles ...')
        results = []
        for url in tqdm(list_of_links):
            try:
                entry = self.profile_data_grabber(url)
                results.append(entry)
            except Exception:
                # passing so we won't lose data if error hits
                traceback.print_exc()
                pass
        self.driver.close()

        return results
