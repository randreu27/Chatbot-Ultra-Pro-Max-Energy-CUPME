import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import PyPDF2
from typing import List, Dict, Any, Optional, Union, Tuple
from io import BytesIO
import ast

class CustomHTMLParser:
    def __init__(self, documents: Optional[List[Dict[str, str]]] = None) -> None:
        if documents is None:
            self.documents = []
        self.documents = documents
        self.visited = set()
        self.pdfs = []

    def scrape_recursive(self, url: str, domain: str) -> None:
        if url in self.visited or not url.startswith(domain):
            return
        self.visited.add(url)

        try:
            res = requests.get(url, timeout=10)
            content_type = res.headers.get('Content-Type', '')

            if 'text/html' in content_type:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                self.documents.append({"url": url, "text": text})
                print(f"Scraping HTML: {url}")

                # Search links in other pages and PDFs
                for link in soup.find_all('a', href=True):
                    link_url = link['href']
                    if 'pdf' in link_url and "_CV_" not in link_url:
                        if link_url not in self.pdfs:
                            self.pdfs.append(link_url)
                    if '/global' in link_url:
                        if '#' in link_url:
                            unique_url = link_url.split('#')[0]
                        else:
                            unique_url = link_url
                    href = urljoin(url, unique_url)
                    self.scrape_recursive(href, domain)

        except Exception as e:
            print(f"Error in {url}: {e}")

    def extract_pdf_text(self, pdf_bytes: bytes) -> str:
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            return "\n".join([page.extract_text() or '' for page in reader.pages])
        except Exception as e:
            print(f"Error en {pdf_bytes}: {e}")
    
    def save_documents(self) -> None:
        for i in self.documents: 
            name = i['url'][30:-5] + '.txt' 
            name = name.replace('/', '___')
            name = name.replace('?', '---')
            text = i['text']
            try: 
                with open(f"ALL_pages\\{name}", "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception as e:
                print(f"Error creating the file {name}.txt: {e}")


def main(start_urls: List[str] , domain: str) -> None:
    parser = CustomHTMLParser()
    for url in start_urls:
        parser.scrape_recursive(url, domain)
    
    for pdf_url in parser.pdfs:
        try:
            res = requests.get(pdf_url, timeout=10)
            if res.status_code == 200:
                pdf_text = parser.extract_pdf_text(res.content)
                parser.documents.append({"url": pdf_url, "text": pdf_text})
                print(f"Scraping PDF: {pdf_url}")
        except Exception as e:
            print(f"Error in {pdf_url}: {e}")

    parser.save_documents()

    



