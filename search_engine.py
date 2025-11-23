# Search Engine Implementation - CS600 Project
# Based on textbook Section 23.6

import os
import re
import sys
import math
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from urllib.parse import urljoin

# Import NLTK for stopwords
try:
    import nltk
    from nltk.corpus import stopwords
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    STOPWORDS = set(stopwords.words('english'))
except ImportError:
    # Fallback stopwords if NLTK not available
    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
        "in", "on", "at", "to", "for", "with", "by", "about", "like",
        "from", "of", "as", "this", "that", "these", "those", "it", "its",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "should", "could", "may", "might", "must", "can"
    }


class SearchEngine:
    """
    Search engine using inverted index and TF-IDF ranking.
    Uses NLTK stopwords and extracts hyperlinks from pages.
    """
    
    def __init__(self, webpages_dir="webpages"):
        self.webpages_dir = webpages_dir
        
        # Inverted index: maps terms to documents
        self.inverted_index = defaultdict(set)
        self.term_frequency = defaultdict(Counter)
        self.document_frequency = Counter()
        self.document_lengths = {}
        
        # Hyperlinks for web crawler
        self.hyperlinks = defaultdict(set)
        
        self.stopwords = STOPWORDS
        self.documents = []
        self.document_urls = {}
        
        self._load_url_mapping()
    
    def _load_url_mapping(self):
        # Load URL mappings from input.txt
        input_file = os.path.join(self.webpages_dir, "input.txt")
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("//"):
                        parts = line.split(" ", 1)  # Split at first space
                        if len(parts) == 2:
                            filename, url = parts
                            self.document_urls[filename] = url
            
            print(f"✓ Loaded {len(self.document_urls)} URL mappings from input.txt")
        except FileNotFoundError:
            print(f"⚠ Warning: {input_file} not found. URLs will not be displayed.")
        except Exception as e:
            print(f"⚠ Error loading URL mapping: {e}")
    
    def _extract_hyperlinks(self, soup, base_url=""):
        # Extract all hyperlinks from HTML
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if base_url:
                full_url = urljoin(base_url, href)
            else:
                full_url = href
            links.add(full_url)
        return links
    
    def parse_document(self, filename):
        # Parse HTML file and update indexes
        filepath = os.path.join(self.webpages_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            
            soup = BeautifulSoup(content, "html.parser")
            
            # Extract hyperlinks
            base_url = self.document_urls.get(filename, "")
            links = self._extract_hyperlinks(soup, base_url)
            self.hyperlinks[filename] = links
            
            # Extract and tokenize text
            text = soup.get_text()
            tokens = re.findall(r'\b\w+\b', text.lower())
            
            # Filter stopwords and single chars
            filtered_tokens = [
                token for token in tokens
                if token not in self.stopwords and len(token) > 1
            ]
            
            term_counts = Counter(filtered_tokens)
            self.document_lengths[filename] = len(filtered_tokens)
            
            # Update indexes
            for term, count in term_counts.items():
                self.inverted_index[term].add(filename)
                self.term_frequency[term][filename] = count
                self.document_frequency[term] += 1
            
            print(f"✓ Indexed: {filename} ({len(term_counts)} unique terms, {len(links)} links)")
            return True
            
        except FileNotFoundError:
            print(f"✗ Error: File not found - {filepath}")
            return False
        except Exception as e:
            print(f"✗ Error parsing {filename}: {e}")
            return False
    
    def build_index(self):
        # Build inverted index from all HTML files
        print(f"\n{'='*60}")
        print(f"Building Inverted Index from '{self.webpages_dir}'...")
        print(f"{'='*60}\n")
        
        self.documents = []
        
        if not os.path.exists(self.webpages_dir):
            print(f"✗ Error: Directory '{self.webpages_dir}' not found!")
            return
        
        html_files = [
            f for f in os.listdir(self.webpages_dir)
            if f.endswith((".html", ".htm"))
        ]
        
        if not html_files:
            print(f"✗ Warning: No HTML files found in '{self.webpages_dir}'")
            return
        
        for filename in sorted(html_files):
            if self.parse_document(filename):
                self.documents.append(filename)
        
        print(f"\n{'='*60}")
        print(f"Indexing Complete!")
        print(f"{'='*60}")
        print(f"Documents indexed: {len(self.documents)}")
        print(f"Unique terms: {len(self.inverted_index)}")
        print(f"Total hyperlinks: {sum(len(links) for links in self.hyperlinks.values())}")
        print(f"{'='*60}\n")
    
    def calculate_tf_idf(self, term, document):
        # Calculate TF-IDF score
        # TF = term_count / total_terms, IDF = log(total_docs / docs_with_term)
        term_count = self.term_frequency[term][document]
        doc_length = self.document_lengths[document]
        tf = term_count / doc_length if doc_length > 0 else 0
        
        total_docs = len(self.documents)
        docs_with_term = self.document_frequency[term]
        idf = math.log(total_docs / docs_with_term) if docs_with_term > 0 else 0
        
        return tf * idf
    
    def search(self, query):
        # Search for documents with ALL query terms (AND logic)
        if not query.strip():
            print("⚠ Empty query. Please enter some search terms.")
            return []
        
        query_terms = re.findall(r'\b\w+\b', query.lower())
        filtered_terms = [
            term for term in query_terms
            if term not in self.stopwords and len(term) > 1
        ]
        
        if not filtered_terms:
            print("⚠ Query contains only stopwords. Please use more specific terms.")
            return []
        
        print(f"\nSearch terms (after filtering): {filtered_terms}")
        
        # Find docs with ALL terms using set intersection
        matching_docs = None
        
        for term in filtered_terms:
            if term in self.inverted_index:
                if matching_docs is None:
                    matching_docs = self.inverted_index[term].copy()
                else:
                    matching_docs &= self.inverted_index[term]
                print(f"  '{term}' → found in {len(self.inverted_index[term])} documents")
            else:
                print(f"  '{term}' → NOT FOUND in any document")
                return []
        
        if not matching_docs:
            print("\n✗ No documents found matching all query terms.")
            return []
        
        # Rank by TF-IDF scores
        ranked_results = []
        for doc in matching_docs:
            score = sum(
                self.calculate_tf_idf(term, doc)
                for term in filtered_terms
                if term in self.inverted_index
            )
            ranked_results.append((doc, score))
        
        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results
    
    def display_results(self, results):
        # Display search results
        if not results:
            print("\nNo results to display.")
            return
        
        print(f"\n{'='*60}")
        print(f"✓ Found {len(results)} matching document(s)")
        print(f"{'='*60}\n")
        
        for i, (doc, score) in enumerate(results, 1):
            # Get URL from mapping or use a default message
            url = self.document_urls.get(doc, "URL not available")
            
            print(f"{i}. {doc}")
            print(f"   Relevance Score (TF-IDF): {score:.6f}")
            print(f"   URL: {url}")
            
            # Show linked pages if available
            if doc in self.hyperlinks and self.hyperlinks[doc]:
                num_links = len(self.hyperlinks[doc])
                print(f"   Links: {num_links} outgoing hyperlink(s)")
            
            print()  # Blank line between results
        
        print(f"{'='*60}\n")
    
    def display_statistics(self):
        """Display search engine statistics."""
        print(f"\n{'='*60}")
        print("Search Engine Statistics")
        print(f"{'='*60}")
        print(f"Total Documents: {len(self.documents)}")
        print(f"Vocabulary Size: {len(self.inverted_index)} unique terms")
        print(f"Total Hyperlinks: {sum(len(links) for links in self.hyperlinks.values())}")
        
        # Find most common terms
        term_doc_counts = [(term, len(docs)) for term, docs in self.inverted_index.items()]
        term_doc_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 10 Most Common Terms:")
        for i, (term, count) in enumerate(term_doc_counts[:10], 1):
            print(f"  {i}. '{term}' appears in {count} document(s)")
        
        print(f"{'='*60}\n")
    
    def run_interactive(self):
        # Interactive mode - run queries
        self.build_index()
        self.display_statistics()
        
        print("🔍 Mini Search Engine - Interactive Mode")
        print("Type 'exit' or 'quit' to quit")
        print("Type 'stats' to see statistics\n")
        
        while True:
            try:
                query = input("Enter search query: ").strip()
                
                if query.lower() in ['exit', 'quit']:
                    print("\n👋 Exiting search engine. Goodbye!")
                    break
                
                if query.lower() == 'stats':
                    self.display_statistics()
                    continue
                
                # Perform search and display results
                results = self.search(query)
                self.display_results(results)
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting search engine. Goodbye!")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}\n")


def run_tests(engine):
    # Run test queries
    test_queries = [
        "",  # empty
        "the and is are",  # stopwords only
        "xyzabc123notfound",  # non-existent
        "security",
        "encryption",
        "malware",
        "cloud",
        "cloud security",
        "network attack",
        "encryption cryptography",
        "malware detection",
        "incident response",
        "security threats protection",
        "firewall intrusion detection",
        "cybersecurity best practices"
    ]
    
    print("\n" + "="*60)
    print("Running Automated Test Suite")
    print("="*60 + "\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*60}")
        print(f"TEST CASE {i}: Query = '{query}'")
        print(f"{'─'*60}")
        
        results = engine.search(query)
        engine.display_results(results)


def main():
    # Main function - run in test or interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n🧪 Running in TEST mode...")
        print("Output will be saved to output.txt\n")
        
        engine = SearchEngine()
        engine.build_index()
        
        output_file = "output.txt"
        original_stdout = sys.stdout
        
        with open(output_file, 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print("="*60)
            print("SEARCH ENGINE - TEST OUTPUT")
            print("="*60)
            print(f"Total Documents Indexed: {len(engine.documents)}")
            print(f"Vocabulary Size: {len(engine.inverted_index)} unique terms")
            print("="*60 + "\n")
            
            run_tests(engine)
            
            print("\n" + "="*60)
            print("END OF TEST OUTPUT")
            print("="*60)
        
        sys.stdout = original_stdout
        print(f"✓ Test output saved to {output_file}")
        
    else:
        engine = SearchEngine()
        engine.run_interactive()


if __name__ == "__main__":
    main()
