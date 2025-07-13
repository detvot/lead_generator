import argparse
import logging
import os
from src.scraper import AlternativeScraper
from src.output import save_leads_to_csv

# Setup logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description=\'Lead Generator: Scrape leads based on keywords.\')
    parser.add_argument(\'--keyword\', type=str, required=True, help=\'Keyword to search for (e.g., \'web design\', \'marketing\').\')
    parser.add_argument(\'--max_sites\', type=int, default=10, help=\'Maximum number of sites to scrape for leads. Default is 10.\')
    parser.add_argument(\'--output_dir\', type=str, default=\'./data\', help=\'Directory to save the output CSV file. Default is ./data.\')

    args = parser.parse_args()

    scraper = AlternativeScraper()
    leads = scraper.scrape_leads_for_keyword(args.keyword, args.max_sites)

    if leads:
        output_file = os.path.join(args.output_dir, f\'{args.keyword.replace(\' \', \'_\')}_leads.csv\')
        save_leads_to_csv(leads, output_file)
        logger.info(f\'Successfully saved {len(leads)} leads to {output_file}\')
    else:
        logger.info(f\'No leads found for keyword: {args.keyword}\')

if __name__ == \'__main__\':
    main()


