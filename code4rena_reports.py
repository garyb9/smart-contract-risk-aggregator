import time
import json
import logging
import requests
import pandas as pd
from copy import deepcopy
from typing import List
from bs4 import BeautifulSoup
from code4rena_definitions import *
from log_cfg import *
log = logging.getLogger(__name__)

class Code4renaReports():
    
    def __init__(self) -> None:
        self.cache_filename = 'code4rena_audit_reports.json'
        self.audit_reports = self.load_cache()
        self.reports_metadata = self.retrieve_report_metadata()
    
    def load_cache(self) -> List:
        try:
            reports = []
            with open(self.cache_filename, 'r') as f:
                reports = json.load(f)
            log.info('Cache found')
        except Exception as e:
            log.info('Cache not found')
        finally:
            return reports
            
    def cache_audit_reports(self) -> None:
        log.info('Writing to: %s', self.cache_filename)
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
                    'dates': dates.split(' — '),
                    'link': link
                })
        except Exception as e:
            log.exception('Error fetching reports list')
        finally:
            return reports_metadata
        
    def fill_missing_reports(self, refresh=False) -> List:    
        try:
            if refresh:
                missing_links = self.reports_metadata
            else:
                cached_links = [ar['link'] for ar in self.audit_reports]
                missing_links = [rm for rm in self.reports_metadata if rm['link'] not in cached_links]
            reports_count = len(missing_links)
            for idx, metadata in enumerate(missing_links):
                log.info('%s/%s: Fetching %s', idx+1, reports_count, metadata['project'])
                metadata['findings'] = self.parse_audit_report(metadata['link'])
                self.audit_reports.append(metadata)
        except Exception as e:
            log.exception('Error running reports scraper')
        finally:
            self.cache_audit_reports()
            return self.audit_reports
        
    def parse_audit_report(self, link:str) -> None:
        try:
            findings = {
                'high-risk': [],
                'medium-risk': [],
                'low-risk-non-critical': [],
                'informational': [],
                'gas-optimization':[],
            }
            if MAIN_URL not in link:
                log.info('Skipping %s', link)
                return findings
            reports_page = requests.get(link)
            if reports_page.status_code != 200:
                raise Exception(f"Error fetching page {link}, status code: {reports_page.status_code}")
            page = reports_page.text
            soup = BeautifulSoup(page, "html.parser")
            contents_main_div = soup.find("div", {"class": "report-toc"})
            links_in_page = [li['href'] for li in contents_main_div.find_all('a', href=True)]
            for lip in links_in_page:
                if lip.startswith('#h-'):
                    findings['high-risk'].append(lip[6:].replace('-', ' '))
                if lip.startswith('#m-'):
                    findings['medium-risk'].append(lip[6:].replace('-', ' '))
                if lip.startswith(('#l-', '#n-')):
                    findings['low-risk-non-critical'].append(lip[6:].replace('-', ' '))
                if lip.startswith('#info-'):
                    findings['informational'].append(lip[9:].replace('-', ' '))
                if lip.startswith('#g-'):
                    findings['gas-optimization'].append(lip[6:].replace('-', ' '))
        except Exception as e:
            log.exception('Error running reports parser for %s', link)
        finally:
            return findings

if __name__ == "__main__":
    c4 = Code4renaReports()
    audit_reports = c4.fill_missing_reports()
