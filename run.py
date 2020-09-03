import sys
from scripts.arg_parser import parse_args
from scripts.tools import get_account, csv_writer
from scripts.cufflinx import Cufflinx
import traceback

def main():
    # main function that will execute the cufflinx scraper
    args = parse_args()
    if not args.search:
        sys.exit("[!] Enter search terms or pharse with -s option e.x. -s 'chris smith'")
    # varaibles
    driver_path = './driver/chromedriver.exe'
    login_url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    account = get_account()
    user_name = account[0]
    pass_word = account[1]
    # file_name = 'results.csv'
    # change this to whatever you want
    # search_query = "site:linkedin.com/in/ AND 'Data Scientist'
    # AND 'Washington D.C. Metro Area' AND 'Christopher Smith'"
    search_query = args.search
    if not search_query.startswith('site:linkedin.com/in/'):
        search_query = 'site:linkedin.com/in/ ' + search_query
    else:
        search_query = args.search
    print("Searching:", search_query)
    pages_to_be_scrapped = int(args.pages)
    filename = args.file_name
    cufflinx = Cufflinx(driver_path)
    cufflinx.linkedin_login(username=user_name,
                            password=pass_word,
                            url=login_url)
    try:
        accounts = cufflinx.google_search_results(pages_to_be_scrapped, search_query)
        results = cufflinx.scrape_profiles(accounts)
        csv_writer(filename, results)
        print('Done, check the results folder.')
    except IndexError:
        traceback.format_exc()


if __name__ == "__main__":
    main()
