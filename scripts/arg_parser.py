import argparse
import time


def parse_args():
    # arguments that can be used to tailor searches and depth of searches
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search',
                        help='Enter Google boolean search e.x. "site:linkedin.com/in/ '
                             'AND *single quote*Data Scientist*single quote* AND *single quote*Washington D.C. '
                             'Metro Area*single quote* AND *single quote*Christopher Smith*single quote*"')
    parser.add_argument('-p', '--pages',
                        default=1, help='Enter number of pages to be searched')
    parser.add_argument('-f', '--file_name',
                        default='linked_in_scrape'+str(time.strftime('%Y%m%d-%H%M')), help='Enter filename '
                                                                                           'for .csv output')

    return parser.parse_args()