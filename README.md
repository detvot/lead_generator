# Lead Generator

This is a Python-based lead generation tool that scrapes websites for contact information (emails, phone numbers, company names, and addresses) based on keywords.

## Features

-   **Keyword-based Search:** Scrapes websites related to a given keyword using DuckDuckGo.
-   **Industry-specific Websites:** Leverages predefined lists of websites for various industries to broaden the search.
-   **Contact Information Extraction:** Extracts emails, phone numbers, company names, and addresses from scraped web pages.
-   **Contact Page Discovery:** Intelligently searches for common contact or \"about us\" pages if initial information is not found on the homepage.
-   **Anti-blocking Measures:** Employs techniques like random user agents and delays to avoid being blocked.
-   **CSV Output:** Saves generated leads into a clean CSV file for easy import into spreadsheets.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/lead_generator.git
    cd lead_generator
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the `main.py` script with your desired keyword and optional parameters:

```bash
python main.py --keyword \"web design\" --max_sites 20 --output_dir ./data
```

### Arguments:

-   `--keyword` (required): The keyword to search for (e.g., \"web design\", \"marketing\").
-   `--max_sites` (optional): Maximum number of sites to scrape for leads. Default is 10.
-   `--output_dir` (optional): Directory to save the output CSV file. Default is `./data`.

## Output

The generated leads will be saved in a CSV file named `[keyword]_leads.csv` (e.g., `web_design_leads.csv`) in the specified output directory.

## Contributing

Feel free to fork this repository, open issues, or submit pull requests.

