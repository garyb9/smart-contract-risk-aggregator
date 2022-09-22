import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from definitions import *

def scrape_reports() -> list:
    try:
        reports_page = requests.get(REPORTS_URL)
        if reports_page.status_code != 200:
            raise Exception(f"Error fetching page: {reports_page.status_code}")
        page = reports_page.text
        soup = BeautifulSoup(page, "html.parser")
        audit_reports = []
        reports_main_div = soup.find("div", {"class": "wrapper-report"})
        reports_div_list = list(reports_main_div.children)
        for report_div in reports_div_list:
            project = report_div.find('h4').text
            link = report_div.find('a', href=True)['href']
            if link.startswith('/reports'):
                link = MAIN_URL + link[1:]
            audit_reports.append({
                'project': project,
                'link': link
            })
        return audit_reports
    except Exception as e:
        logging.exception('Error running reports scraper')
        return []

def parse_audit_reports(audit_reports:list) -> None:
    try:
        for report in audit_reports:
            reports_page = requests.get(report['link'])
            if reports_page.status_code != 200:
                raise Exception(f"Error fetching page: {reports_page.status_code}")
            page = reports_page.text
            soup = BeautifulSoup(page, "html.parser")
            contents_main_div = soup.find("div", {"class": "report-toc"})
            links_in_page = [(li.string, report['link'] + li['href']) for li in contents_main_div.find_all('a', href=True)]
            1==1
    except Exception as e:
        logging.exception('Error running reports parser')
        return []
