import sys
from scripts.arg_parser import parse_args
from scripts.tools import df_to_csv
from scripts.accounts import get_account
from scripts.cufflinx import Cufflinx
import traceback


def main():
    # main function that will execute the cufflinx scraper
    args = parse_args()
    if not args.search:
        sys.exit("[!] Enter search terms or pharse with -s option e.x. -s 'chris smith'")
    # variables
    driver_path = './driver/chromedriver.exe'
    account = get_account()
    user_name = account[0]
    pass_word = account[1]
    # file_name = 'results.csv'
    # change this to whatever you want
    # ex. search_query = "site:linkedin.com/in/ AND 'Data Scientist'
    # AND 'Washington D.C. Metro Area' AND 'Christopher Smith'"
    search_query = args.search
    if not search_query.startswith('site:linkedin.com/in/'):
        search_query = 'site:linkedin.com/in/ ' + search_query
    else:
        search_query = args.search
    print("Searching:", search_query)
    pages = int(args.pages)
    filename = args.file_name
    cufflinx = Cufflinx(driver_path)
    cufflinx.linkedin_login(username=user_name,
                            password=pass_word)
    try:
        cufflinx.google_search(search_query)
        accounts = cufflinx.collect_search_results(pages)
        results = cufflinx.scrape_profiles(accounts)
        # csv_writer(filename, results)
        df_to_csv(filename, results)
        print('Done, check the results folder.')
    except IndexError:
        traceback.format_exc()


if __name__ == "__main__":
    main()
