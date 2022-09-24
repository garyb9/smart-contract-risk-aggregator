from importlib.metadata import metadata
import json
import logging
import requests
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from code4rena_definitions import *
from log_cfg import *
log = logging.getLogger(__name__)

class Code4renaReports():
    
    def __init__(self, full_refresh=False) -> None:
        self.cache_filename = 'code4rena_audit_reports.json'
        self.audit_reports = self.load_cache()
        self.reports_metadata = self.retrieve_report_metadata()
        self.fill_missing_reports(refresh=full_refresh)
    
    def load_cache(self) -> List:
        try:
            with open(self.cache_filename, 'r') as f:
                self.audit_reports = json.load(f)
            log.info('Cache found')
        except Exception as e:
            log.info('Cache not found')
        finally:
            return []
            
    def cache_audit_reports(self) -> None:
        with open(self.cache_filename, 'w') as f:
            json.dump(self.audit_reports, f, indent=4)
    
    def retrieve_report_metadata(self) ->  List:
        reports_metadata = []
        try:
            reports_page = requests.get(REPORTS_URL)
            log.info('Fetching report links')
            if reports_page.status_code != 200:
                raise Exception(f"Error fetching page: {reports_page.status_code}")
            page = reports_page.text
            soup = BeautifulSoup(page, "html.parser")
            reports_main_div = soup.find("div", {"class": "wrapper-report"})
            reports_div_list = list(reports_main_div.children)
            for report_div in reports_div_list:
                project = report_div.find('h4').text
                dates = report_div.find('p').text
                link = report_div.find('a', href=True)['href']
                if link.startswith('/reports'):
                    link = MAIN_URL + link[1:]
                reports_metadata.append({
                    'project': project,
                    'dates': dates,
                    'link': link
                })
        except Exception as e:
            log.exception('Error fetching reports list')
        finally:
            return reports_metadata
    
    def identify_missing_reports(self) -> None:
        cached_links = set([ar['link'] for ar in self.audit_reports])
        report_links = set([ar['link'] for ar in self.reports_metadata])
        missing = report_links.difference(cached_links)
        1==1
        
    def fill_missing_reports(self, refresh=False) -> List:    
        # TODO: add full refresh functionallity
        try:
            self.identify_missing_reports()
            reports_count = len(self.reports_metadata)
            for idx, metadata in enumerate(self.reports_metadata):
                log.info('%s/%s: Fetching %s', idx+1, reports_count, metadata['project'])
                reports_page = requests.get(metadata['link']) # get link
                if reports_page.status_code != 200:
                    raise Exception(f"Error fetching page: {reports_page.status_code}")
                # self.audit_reports[idx]['page'] = reports_page.text
        except Exception as e:
            log.exception('Error running reports scraper')
        finally:
            self.cache_audit_reports()
            return self.audit_reports
        
    def parse_audit_reports(self, audit_reports:list) -> None:
        try:
            findings = findings_template.copy() # init 
            for idx, report in enumerate(audit_reports):
                log.info('%s/%s: Fetching %s', idx+1, len(audit_reports), report['project'])
                reports_page = requests.get(report['link'])
                if reports_page.status_code != 200:
                    raise Exception(f"Error fetching page: {reports_page.status_code}")
                page = reports_page.text
                soup = BeautifulSoup(page, "html.parser")
                contents_main_div = soup.find("div", {"class": "report-toc"})
                links_in_page = [(li.string, report['link'] + li['href']) for li in contents_main_div.find_all('a', href=True)]
                for lip in links_in_page:
                    # TODO: consider using regex in the future?
                    # if lip[0].startswith('H-'):
                    1==1
                1==1
            1==1
        except Exception as e:
            log.exception('Error running reports parser')
            return []

if __name__ == "__main__":
    c4 = Code4renaReports()
    audit_reports = c4.fill_missing_reports()

exit(0)