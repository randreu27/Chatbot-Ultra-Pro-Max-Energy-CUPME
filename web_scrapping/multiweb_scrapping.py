import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import PyPDF2
from typing import List, Dict, Any, Optional, Union, Tuple
from io import BytesIO
import ast
import json

class CustomHTMLParser:
    def __init__(self, documents: Optional[List[Dict[str, str]]] = [], no_pdfs: Optional[List] = []) -> None:

        self.documents = documents
        self.visited = set()
        self.pdfs = []
        if no_pdfs == []:
            self.no_pdfs = ['_CV_', '-pt-','-CN-', '-HU-', '-NO-', '-VI-', '-ES-', '-ZH-', '-CZ-', '-DE-', '-FR-', '-IT-', '-de-', '-fr-', '-it-']
        else:
            self.no_pdfs = no_pdfs

    def scrape_recursive(self, url: str, domain: str) -> None:
        """ Recursively scrape a webpage and its links. """
        # Check if the URL has already been visited or if it doesn't start with the domain
        
        if url in self.visited or not url.startswith(domain) or "/global" not in url:
            return
        self.visited.add(url)

        try:
            res = requests.get(url, timeout=10)
            content_type = res.headers.get('Content-Type', '')

            if 'text/html' in content_type:
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                self.documents.append({"url": url, "text": text})
                #print(f"Scraping HTML: {url}")

                # Search links in other pages and PDFs
                for link in soup.find_all('a', href=True):
                    link_url = link['href']
                    
                    # Keep the PDFs
                    if 'pdf' in link_url:
                        if all(elem not in link_url for elem in self.no_pdfs):
                            self.pdfs.append(link_url)
                            
                    # Check for links that start with /global
                    if '/global' in link_url:
                        if '#' in link_url:
                            unique_url = link_url.split('#')[0]
                        else:
                            unique_url = link_url
                        href = urljoin(url, unique_url)
                        self.scrape_recursive(href, domain)
                
        except Exception as e:
            print(f"Error in {url}: {e}")

    def extract_pdf_text(self, pdf_url:str) -> str:
        """ Extract text from a PDF file. """
        try:
            res = requests.get(pdf_url, timeout=10)
            reader = PyPDF2.PdfReader(BytesIO(res.content))
            #print(f"Scraping PDF: {pdf_url}")
            return "\n".join([page.extract_text() or '' for page in reader.pages])
        except Exception as e:
            print(f"Error {pdf_url}")
        
    def save_documents(self, documents) -> None:
        """ Save the scraped documents as text files. And save the URLs in a JSON file. """

        file_url_pairs = {}
        
        # Create directory if it doesn't exist
        if not os.path.exists("./product-offerings"):
            os.makedirs("./product-offerings")

        # Save each document as a text file
        for i in range(len(documents)): 
            if documents[i]['text'] != '' and documents[i]['text'] != None:
                name = str(i) + '.txt'
                file_url_pairs[name] = documents[i]['url']
                text = documents[i]['text'] 
                with open(f"product-offerings\\{name}", "w", encoding="utf-8") as f:
                    f.write(text)
        
        # Save the dictionary as a JSON file
        with open("file_url_pairs.json", "w", encoding="utf-8") as json_file:
            json.dump(file_url_pairs, json_file, indent=4)    


def main(start_urls: List[str] , domain: str) -> None:
    parser = CustomHTMLParser()
    for url in start_urls:
        parser.scrape_recursive(url, domain)
    print(len(parser.pdfs))
    for pdf_url in parser.pdfs:
        pdf_text = parser.extract_pdf_text(pdf_url)
        parser.documents.append({"url": pdf_url, "text": pdf_text})      

    parser.save_documents(parser.documents)
    return parser
