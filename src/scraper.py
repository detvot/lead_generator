import requests
import time
import random
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, quote
import logging

logger = logging.getLogger(__name__)

class AlternativeScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        
        self.base_headers = {
            \'Accept\': \'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\',
            \'Accept-Language\': \'en-US,en;q=0.5\',
            \'Accept-Encoding\': \'gzip, deflate\',
            \'Connection\': \'keep-alive\',
            \'Upgrade-Insecure-Requests\': \'1\',
            \'DNT\': \'1\',
        }
        
        self.industry_websites = {
            \'web design\': [
                \'https://www.awwwards.com\',
                \'https://dribbble.com\',
                \'https://www.behance.net\',
                \'https://www.smashingmagazine.com\',
                \'https://www.webdesignerdepot.com\'
            ],
            \'marketing\': [
                \'https://www.hubspot.com\',
                \'https://blog.hootsuite.com\',
                \'https://www.socialmediaexaminer.com\',
                \'https://contentmarketinginstitute.com\',
                \'https://blog.marketo.com\'
            ],
            \'software\': [
                \'https://github.com\',
                \'https://stackoverflow.com\',
                \'https://dev.to\',
                \'https://www.producthunt.com\',
                \'https://techcrunch.com\'
            ],
            \'consulting\': [
                \'https://www.mckinsey.com\',
                \'https://www.bcg.com\',
                \'https://www2.deloitte.com\',
                \'https://www.pwc.com\',
                \'https://www.accenture.com\'
            ]
        }
        
    def get_random_headers(self):
        headers = self.base_headers.copy()
        headers[\'User-Agent\'] = self.ua.random
        return headers
    
    def random_delay(self, min_delay=2, max_delay=5):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def make_request(self, url, retries=3):
        for attempt in range(retries):
            try:
                headers = self.get_random_headers()
                
                if attempt > 0:
                    self.random_delay(5, 10)
                else:
                    self.random_delay()
                
                response = self.session.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    logger.warning(f\"Rate limited on {url}, waiting longer...\")
                    time.sleep(random.uniform(15, 30))
                    continue
                elif response.status_code in [403, 404]:
                    logger.warning(f\"Access denied or not found: {url}\")
                    return None
                else:
                    logger.warning(f\"Unexpected status code {response.status_code} for {url}\")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f\"Request failed for {url}: {str(e)}\")
                if attempt == retries - 1:
                    return None
                    
        return None
    
    def search_duckduckgo(self, keyword, num_results=10):
        search_url = f\"https://html.duckduckgo.com/html/?q={quote(keyword)}\"
        
        response = self.make_request(search_url)
        if not response:
            logger.error(f\"Failed to search DuckDuckGo for keyword: {keyword}\")
            return []
        
        soup = BeautifulSoup(response.content, \'html.parser\')
        
        urls = []
        for link in soup.find_all(\'a\', class_=\'result__a\'):
            href = link.get(\'href\')
            if href and href.startswith(\'http\') and \'duckduckgo.com\' not in href:
                urls.append(href)
        
        return urls[:num_results]
    
    def get_industry_websites(self, keyword):
        keyword_lower = keyword.lower()
        websites = []
        
        for industry, urls in self.industry_websites.items():
            if industry in keyword_lower:
                websites.extend(urls)
        
        if not websites:
            for urls in self.industry_websites.values():
                websites.extend(urls[:2])
        
        return websites
    
    def extract_contact_info(self, soup, url):
        contact_info = {
            \'emails\': set(),
            \'phones\': set(),
            \'company_name\': \'\',
            \'address\': \'\'
        }
        
        text = soup.get_text()
        email_pattern = r\'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b\'
        emails = re.findall(email_pattern, text)
        business_emails = [email for email in emails if not any(x in email.lower() for x in [\'noreply\', \'no-reply\', \'donotreply\', \'example.com\', \'test.com\'])]
        contact_info[\'emails\'].update(business_emails)
        
        phone_patterns = [
            r\'\\+?1?[-.\\s]?\\(?[0-9]{3}\\)?[-.\\s]?[0-9]{3}[-.\\s]?[0-9]{4}\',
            r\'\\+?[0-9]{1,3}[-.\\s]?[0-9]{3,4}[-.\\s]?[0-9]{3,4}[-.\\s]?[0-9]{3,4}\',
            r\'\\([0-9]{3}\\)[-.\\s]?[0-9]{3}[-.\\s]?[0-9]{4}\'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            contact_info[\'phones\'].update(phones)
        
        title = soup.find(\'title\')
        if title:
            title_text = title.get_text().strip()
            for suffix in [\' - Home\', \' | Home\', \' - Official Site\', \' | Official Site\']:
                title_text = title_text.replace(suffix, \'\')
            contact_info[\'company_name\'] = title_text[:100]
        
        if not contact_info[\'company_name\']:
            h1 = soup.find(\'h1\')
            if h1:
                contact_info[\'company_name\'] = h1.get_text().strip()[:100]
        
        address_selectors = [
            \'[class*=\"address\"]\',
            \'[class*=\"location\"]\',
            \'[class*=\"contact\"]\',
            \'address\'
        ]
        
        for selector in address_selectors:
            address_elem = soup.select_one(selector)
            if address_elem:
                address_text = address_elem.get_text().strip()
                if len(address_text) > 10 and len(address_text) < 200:
                    contact_info[\'address\'] = address_text
                    break
        
        return contact_info
    
    def find_contact_pages(self, base_url):
        contact_paths = [
            \'/contact\',
            \'/contact-us\',
            \'/about\',
            \'/about-us\',
            \'/team\',
            \'/company\',
            \'/contact.html\',
            \'/about.html\'
        ]
        
        contact_urls = []
        for path in contact_paths:
            contact_url = urljoin(base_url, path)
            contact_urls.append(contact_url)
        
        return contact_urls
    
    def scrape_leads_for_keyword(self, keyword, max_sites=10):
        logger.info(f\"Starting enhanced lead scraping for keyword: {keyword}\")
        
        urls = []
        
        try:
            ddg_urls = self.search_duckduckgo(keyword, max_sites // 2)
            urls.extend(ddg_urls)
            logger.info(f\"Found {len(ddg_urls)} URLs from DuckDuckGo\")
        except Exception as e:
            logger.error(f\"DuckDuckGo search failed: {e}\")
        
        industry_urls = self.get_industry_websites(keyword)
        urls.extend(industry_urls[:max_sites // 2])
        logger.info(f\"Added {len(industry_urls[:max_sites // 2])} industry-specific URLs\")
        
        urls = list(set(urls))[:max_sites]
        logger.info(f\"Total {len(urls)} unique URLs to scrape\")
        
        leads = []
        
        for url in urls:
            try:
                logger.info(f\"Scraping: {url}\")
                
                response = self.make_request(url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, \'html.parser\')
                contact_info = self.extract_contact_info(soup, url)
                
                if not contact_info[\'emails\'] and not contact_info[\'phones\']:
                    contact_urls = self.find_contact_pages(url)
                    for contact_url in contact_urls[:2]:
                        try:
                            contact_response = self.make_request(contact_url)
                            if contact_response:
                                contact_soup = BeautifulSoup(contact_response.content, \'html.parser\')
                                contact_page_info = self.extract_contact_info(contact_soup, contact_url)
                                
                                contact_info[\'emails\'].update(contact_page_info[\'emails\'])
                                contact_info[\'phones\'].update(contact_page_info[\'phones\'])
                                if not contact_info[\'address\'] and contact_page_info[\'address\']:
                                    contact_info[\'address\'] = contact_page_info[\'address\']
                                
                                if contact_info[\'emails\'] or contact_info[\'phones\']:
                                    break
                        except Exception as e:
                            logger.error(f\"Error scraping contact page {contact_url}: {e}\")
                            continue
                
                if contact_info[\'emails\']:
                    for email in contact_info[\'emails\']:
                        lead = {
                            \'keyword\': keyword,
                            \'company_name\': contact_info[\'company_name\'][:255] if contact_info[\'company_name\'] else \'\',
                            \'website\': url,
                            \'email\': email,
                            \'phone_number\': list(contact_info[\'phones\'])[0][:50] if contact_info[\'phones\'] else \'\',
                            \'address\': contact_info[\'address\'][:500] if contact_info[\'address\'] else \'\',
                            \'source_url\': url
                        }
                        leads.append(lead)
                
                elif contact_info[\'company_name\'] or contact_info[\'phones\']:
                    lead = {
                        \'keyword\': keyword,
                        \'company_name\': contact_info[\'company_name\'][:255] if contact_info[\'company_name\'] else \'\',
                        \'website\': url,
                        \'email\': \'\',
                        \'phone_number\': list(contact_info[\'phones\'])[0][:50] if contact_info[\'phones\'] else \'\',
                        \'address\': contact_info[\'address\'][:500] if contact_info[\'address\'] else \'\',
                        \'source_url\': url
                    }
                    leads.append(lead)
                    
            except Exception as e:
                logger.error(f\"Error scraping {url}: {str(e)}\")
                continue
        
        logger.info(f\"Completed enhanced scraping for keyword \'{keyword}\'. Found {len(leads)} leads.\")
        return leads


