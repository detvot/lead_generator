import csv
import logging

logger = logging.getLogger(__name__)

def save_leads_to_csv(leads, filename):
    if not leads:
        logger.info(\"No leads to save.\")
        return

    # Define CSV headers
    fieldnames = [\"keyword\", \"company_name\", \"website\", \"email\", \"phone_number\", \"address\", \"source_url\"]

    try:
        with open(filename, \"w\", newline=\"\", encoding=\"utf-8\") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)
        logger.info(f\"Leads successfully saved to {filename}\")
    except IOError as e:
        logger.error(f\"Error saving leads to CSV file {filename}: {e}\")


