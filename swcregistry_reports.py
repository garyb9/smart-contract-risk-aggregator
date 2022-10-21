import time
import json
import logging
import requests
import pandas as pd
from copy import deepcopy
from typing import List
from bs4 import BeautifulSoup
from swcregistry_definitions import *
from log_cfg import *
log = logging.getLogger(__name__)

class SwcregistryReports():

    def __init__(self) -> None:
        self.cache_filename = 'swcregistry_reports.json'
        self.audit_reports = self.load_cache()
        self.registry_metadata = self.retrieve_registry_metadata()

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

    def retrieve_registry_metadata(self) -> List:
        registry_metadata = []
        try:
            registry_page = requests.get(MAIN_URL)
            log.info('fetching registry links')
            if registry_page.status_code != 200:
                raise Exception(f"Error fetching page: {registry_page.status_code}")
            page = registry_page.text
            soup = BeautifulSoup(page, 'html.parser')
            registry_main_table = soup.find('tbody')
            registry_item_list = list(registry_main_table.children)
            for registry_item in registry_item_list:
                id_name = registry_item.find('a', href=True).text
                link = registry_item.find('a', href=True)['href']
                title = registry_item.find('p').text
                relationship = registry_item.find('p').findNext('p').text
                relationship_link = registry_item.find('a', href=True).findNext('a', href=True)['href']
                registry_metadata.append({
                    'ID': id_name,
                    'title': title,
                    'link': MAIN_URL + link,
                    'relationship': relationship,
                    'relationship link': relationship_link
            })
        except Exception as e:
            log.exception('Error fetching list')
        finally:
            return registry_metadata

    def fill_missing_reports(self, refresh=False) -> List:
        try:
            if refresh:
                missing_links = self.registry_metadata
            else:
                cached_links = [ar['link'] for ar in self.audit_reports]
                missing_links = [rm for rm in self.registry_metadata if rm['link'] not in cached_links]
            reports_count = len(missing_links)
            for idx, metadata in enumerate(missing_links):
                log.info('%s/%s: Fetching %s', idx+1, reports_count, metadata['ID'])
                metadata['findings'] = self.parse_audit_report(metadata['link'])
                self.audit_reports.append(metadata)
        except Exception as e:
            log.exception('Error running parser')
        finally:
            self.cache_audit_reports()
            return self.audit_reports

    def parse_audit_report(self, link:str) -> None:
        try:
            findings = {
                'relationships': [],
                'description': [],
                'remediation': [],
                'references': [],
                'references-links': [],
            }
            if MAIN_URL not in link:
                log.info('Skipping %s', link)
                return findings
            reports_page = requests.get(link)
            if reports_page.status_code !=200:
                raise Exception(f'Error fetching page {link}, status code: {reports_page.status_code}')
            page = reports_page.text
            soup = BeautifulSoup(page, 'html.parser')
            reports_main_div = soup.find('article')
            headers_in_page  = reports_main_div.find_all('h2')
            for header in headers_in_page:
                if header.text=='Description':
                    description = header.find_next_sibling('p').text
                    findings['description'].append(description) 
                if header.text=='Remediation':
                    remediation = header.find_next_sibling('p').text
                    findings['remediation'].append(remediation) 
                if header.text=='References':
                    references = header.find_next_sibling()
                    for li in references.find_all('li'):
                        name = li.find('a', href=True).text
                        findings['references'].append(name) 
                        link = li.find('a', href=True)['href']
                        findings['references-links'].append(link) 
                
        except Exception as e:
            log.exception('Error running parser for %s', link)
        finally:
            return findings

if __name__ == "__main__":
    swc = SwcregistryReports()
    reports = swc.fill_missing_reports()