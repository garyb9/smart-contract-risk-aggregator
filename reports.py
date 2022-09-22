import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from definitions import *

def scrape_reports():
    try:
        reports_page = requests.get(REPORTS_URL)
        if reports_page.status_code != 200:
            raise Exception(f"Error fetching page: {reports_page.status_code}")
        page = reports_page.text
        soup = BeautifulSoup(page, "html.parser")
        audit_reports = []
        reports_main_div = soup.find_all("div", {"class": "wrapper-report"})
        reports_div_list = list(reports_main_div[0].children)
        for report_div in reports_div_list:
            project = report_div.find('h4').text
            link = report_div.find('a', href=True)['href']
            audit_reports.append({
                'project': project,
                'link': link
            })
        return audit_reports
    except Exception as e:
        logging.exception('Error running reports scraper')
        return []