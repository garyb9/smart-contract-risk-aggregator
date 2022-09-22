import os
import logging
from reports import *


if __name__ == "__main__":
    audit_reports = scrape_reports()
    risks = parse_audit_reports(audit_reports)
    