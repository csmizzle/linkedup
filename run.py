from scripts.arg_parser import parse_args
from scripts.tools import df_to_csv
from scripts.accounts import get_account
from scripts.cufflinx import Cufflinx
import traceback


def main():
    # main function that will execute the cufflinx scraper
    args = parse_args()
    # variables
    driver_path = './driver/chromedriver.exe'
    account = get_account()
    user_name = account[0]
    pass_word = account[1]
    filename = args.file_name
    # Company Search
    if args.company != '':
        # noinspection PyBroadException
        try:
            cufflinx = Cufflinx(driver_path)
            cufflinx.linkedin_login(username=user_name,
                                    password=pass_word)
            company = args.company
            cufflinx.company_search(company)
            employee_links = cufflinx.get_employees()
            # results = cufflinx.scrape_profiles(employee_links)
            # df_to_csv(filename, results)
        except Exception:
            traceback.print_exc()
    # Google Search
    elif args.search != '':
        search_query = args.search
        if not search_query.startswith('site:linkedin.com/in/'):
            search_query = 'site:linkedin.com/in/ ' + search_query
        else:
            search_query = args.search
        print("[!] Searching:", search_query)
        pages = int(args.pages)
        try:
            cufflinx = Cufflinx(driver_path)
            cufflinx.linkedin_login(username=user_name,
                                    password=pass_word)
            cufflinx.google_search(search_query)
            accounts = cufflinx.collect_search_results(pages)
            results = cufflinx.scrape_profiles(accounts)
            df_to_csv(filename, results)
            print('[!] Done, check the results folder.')
        except IndexError:
            traceback.print_exc()
    else:
        print('[*] Error: need to specify search ...')


if __name__ == "__main__":
    main()
