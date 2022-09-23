import os
import logging
from code4rena_reports import *

if __name__ == "__main__":
    audit_reports = scrape_reports()
    risks = parse_audit_reports(audit_reports)
    