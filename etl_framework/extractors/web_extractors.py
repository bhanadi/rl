"""
Web-based data extractors.
"""
import json
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from ..core.base import Extractor
from ..core.exceptions import ExtractionError


class APIExtractor(Extractor):
    """Extract data from REST APIs."""
    
    def __init__(self, name: str, base_url: str, endpoint: str, 
                 method: str = "GET", headers: Optional[Dict] = None,
                 params: Optional[Dict] = None, data: Optional[Dict] = None,
                 auth: Optional[Dict] = None, timeout: int = 30):
        super().__init__(name)
        self.base_url = base_url.rstrip('/')
        self.endpoint = endpoint.lstrip('/')
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}
        self.data = data
        self.auth = auth
        self.timeout = timeout
        
    def validate_config(self) -> bool:
        """Validate API extractor configuration."""
        if not self.base_url:
            raise ExtractionError("Base URL is required")
        if not self.endpoint:
            raise ExtractionError("API endpoint is required")
        return True
        
    def extract(self) -> Any:
        """Extract data from REST API."""
        self.validate_config()
        
        try:
            import requests
        except ImportError:
            raise ExtractionError("requests package is required for API extraction")
        
        try:
            url = urljoin(f"{self.base_url}/", self.endpoint)
            
            # Set up authentication
            auth = None
            if self.auth:
                auth_type = self.auth.get('type', '').lower()
                if auth_type == 'basic':
                    auth = (self.auth['username'], self.auth['password'])
                elif auth_type == 'bearer':
                    self.headers['Authorization'] = f"Bearer {self.auth['token']}"
                elif auth_type == 'api_key':
                    key_location = self.auth.get('location', 'header').lower()
                    key_name = self.auth.get('key_name', 'api_key')
                    if key_location == 'header':
                        self.headers[key_name] = self.auth['api_key']
                    elif key_location == 'query':
                        self.params[key_name] = self.auth['api_key']
            
            # Make API request
            response = requests.request(
                method=self.method,
                url=url,
                headers=self.headers,
                params=self.params,
                json=self.data if self.method in ['POST', 'PUT', 'PATCH'] else None,
                auth=auth,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Try to parse as JSON, fall back to text
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
                
        except Exception as e:
            raise ExtractionError(f"Failed to extract from API {url}: {str(e)}")


class WebScrapingExtractor(Extractor):
    """Extract data from web pages using web scraping."""
    
    def __init__(self, name: str, url: str, selectors: Dict[str, str],
                 headers: Optional[Dict] = None, delay: float = 1.0,
                 max_pages: int = 1, pagination_selector: Optional[str] = None):
        super().__init__(name)
        self.url = url
        self.selectors = selectors
        self.headers = headers or {'User-Agent': 'ETL-Framework-Bot/1.0'}
        self.delay = delay
        self.max_pages = max_pages
        self.pagination_selector = pagination_selector
        
    def validate_config(self) -> bool:
        """Validate web scraping extractor configuration."""
        if not self.url:
            raise ExtractionError("URL is required")
        if not self.selectors:
            raise ExtractionError("CSS selectors are required")
        return True
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract data from web pages."""
        self.validate_config()
        
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise ExtractionError("requests and beautifulsoup4 packages are required for web scraping")
        
        all_data = []
        current_url = self.url
        pages_scraped = 0
        
        while current_url and pages_scraped < self.max_pages:
            try:
                # Add delay to be respectful
                if pages_scraped > 0:
                    time.sleep(self.delay)
                
                response = requests.get(current_url, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_data = self._extract_from_page(soup)
                all_data.extend(page_data)
                
                # Check for next page
                current_url = None
                if self.pagination_selector and pages_scraped < self.max_pages - 1:
                    next_link = soup.select_one(self.pagination_selector)
                    if next_link:
                        href = next_link.get('href')
                        if href:
                            current_url = urljoin(self.url, href)
                
                pages_scraped += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to scrape page {current_url}: {str(e)}")
                break
        
        return all_data
    
    def _extract_from_page(self, soup) -> List[Dict[str, Any]]:
        """Extract data from a single page."""
        # Find the container elements (assume the first selector defines the item container)
        container_selector = list(self.selectors.keys())[0]
        containers = soup.select(self.selectors[container_selector])
        
        if not containers:
            return []
        
        results = []
        for container in containers:
            item = {}
            for field_name, selector in self.selectors.items():
                if field_name == container_selector:
                    continue
                
                elements = container.select(selector)
                if elements:
                    if len(elements) == 1:
                        item[field_name] = self._extract_text(elements[0])
                    else:
                        item[field_name] = [self._extract_text(el) for el in elements]
                else:
                    item[field_name] = None
            
            if item:  # Only add if we extracted some data
                results.append(item)
        
        return results
    
    def _extract_text(self, element) -> str:
        """Extract text from a BeautifulSoup element."""
        # Check for common attributes first
        for attr in ['data-text', 'title', 'alt']:
            if element.get(attr):
                return element[attr].strip()
        
        # Check for href in links
        if element.name == 'a' and element.get('href'):
            return element['href']
        
        # Check for src in images
        if element.name == 'img' and element.get('src'):
            return element['src']
        
        # Default to text content
        return element.get_text(strip=True)


class FTPExtractor(Extractor):
    """Extract files from FTP servers."""
    
    def __init__(self, name: str, host: str, username: str, password: str,
                 remote_path: str, file_pattern: str = "*",
                 port: int = 21, passive: bool = True):
        super().__init__(name)
        self.host = host
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.file_pattern = file_pattern
        self.port = port
        self.passive = passive
        
    def validate_config(self) -> bool:
        """Validate FTP extractor configuration."""
        if not all([self.host, self.username, self.password]):
            raise ExtractionError("Host, username, and password are required for FTP")
        return True
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract file list from FTP server."""
        self.validate_config()
        
        try:
            import ftplib
            import fnmatch
        except ImportError:
            raise ExtractionError("ftplib is required for FTP extraction")
        
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(self.host, self.port)
                ftp.login(self.username, self.password)
                
                if self.passive:
                    ftp.set_pasv(True)
                
                ftp.cwd(self.remote_path)
                
                # Get file list
                files = []
                ftp.retrlines('LIST', files.append)
                
                result = []
                for file_line in files:
                    parts = file_line.split()
                    if len(parts) >= 9:
                        filename = ' '.join(parts[8:])
                        if fnmatch.fnmatch(filename, self.file_pattern):
                            result.append({
                                'filename': filename,
                                'size': parts[4] if len(parts) > 4 else None,
                                'modified': ' '.join(parts[5:8]) if len(parts) > 7 else None,
                                'path': f"{self.remote_path}/{filename}",
                                'full_line': file_line
                            })
                
                return result
                
        except Exception as e:
            raise ExtractionError(f"Failed to extract from FTP {self.host}: {str(e)}")