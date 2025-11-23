# Search Engine Implementation - CS600 Project

## Project Overview

This project implements a simplified search engine based on Section 23.6 of the textbook, designed to index and search HTML documents from a small website. The implementation uses **inverted indexing** as the core data structure and **TF-IDF (Term Frequency-Inverse Document Frequency)** for ranking search results.

### Author
**Ankit Dhandharia**  
Course: CS600  
Project: Search Engine Implementation

---

## Key Features

✅ **Inverted Index**: Efficient term-to-document mapping  
✅ **NLTK Stopwords**: Comprehensive English stopword filtering  
✅ **TF-IDF Ranking**: Relevance-based result ranking  
✅ **Hyperlink Extraction**: Web crawler component  
✅ **Boundary Condition Handling**: Robust error handling  
✅ **Interactive & Test Modes**: Dual operation modes

---

## Algorithms and Data Structures

### 1. Inverted Index

**Description**: An inverted index is the fundamental data structure used in search engines. It maps each term (word) to the set of documents that contain it.

**Data Structure**: `defaultdict(set)`
- **Key**: Term (string)
- **Value**: Set of document filenames containing the term

**Example**:
```python
{
    "security": {"index.html", "network_security.html", "cloud_security.html"},
    "encryption": {"cryptography.html", "cloud_security.html"},
    "malware": {"malware_analysis.html", "incident_response.html"}
}
```

**Algorithm**:
1. For each HTML document:
   - Parse HTML and extract text content
   - Tokenize text into individual words
   - Filter out stopwords and single characters
   - For each remaining term:
     - Add the document to that term's set in the inverted index

**Time Complexity**: O(D × T) where D = number of documents, T = average terms per document  
**Space Complexity**: O(V × D) where V = vocabulary size

**Benefits**:
- O(1) lookup to find documents containing a term
- Efficient for AND queries (set intersection)
- Scalable for large document collections

### 2. TF-IDF Ranking Algorithm

**Description**: TF-IDF measures how important a term is to a document in a collection. It combines term frequency (how often a term appears in a document) with inverse document frequency (how rare the term is across all documents).

**Formula**:
```
TF-IDF(term, document) = TF(term, document) × IDF(term)

Where:
TF(term, document) = (count of term in document) / (total terms in document)
IDF(term) = log(total documents / documents containing term)
```

**Implementation**:
```python
def calculate_tf_idf(self, term, document):
    # Term Frequency (normalized)
    term_count = self.term_frequency[term][document]
    doc_length = self.document_lengths[document]
    tf = term_count / doc_length if doc_length > 0 else 0
    
    # Inverse Document Frequency
    total_docs = len(self.documents)
    docs_with_term = self.document_frequency[term]
    idf = math.log(total_docs / docs_with_term) if docs_with_term > 0 else 0
    
    # TF-IDF Score
    return tf * idf
```

**Ranking Process**:
1. Find all documents containing ALL query terms (AND semantics)
2. For each matching document:
   - Calculate TF-IDF score for each query term
   - Sum the scores across all query terms
3. Sort documents by total score (highest first)

**Benefits**:
- Gives higher scores to documents where query terms are frequent
- Penalizes common terms that appear in many documents
- Rewards rare, specific terms that are more discriminative
- Better than simple term frequency counting

### 3. Additional Data Structures

**Term Frequency**: `defaultdict(Counter)`
- Maps each term to a Counter of {document: frequency}
- Used in TF-IDF calculation
- Example: `{"security": {"doc1.html": 5, "doc2.html": 3}}`

**Document Frequency**: `Counter`
- Counts how many documents contain each term
- Used for IDF calculation
- Example: `{"security": 4, "encryption": 2}`

**Document Lengths**: `dict`
- Maps each document to its total number of terms (after filtering)
- Used for normalizing term frequency
- Example: `{"index.html": 97, "cryptography.html": 260}`

**Hyperlinks**: `defaultdict(set)`
- Maps each document to the set of URLs it links to
- Supports web crawler functionality
- Example: `{"index.html": {"cybersecurity_fundamentals.html", "cloud_security.html"}}`

---

## Approach and Implementation

### Phase 1: Document Parsing
1. Read HTML files from the `webpages/` directory
2. Use BeautifulSoup to parse HTML and extract text
3. Extract hyperlinks (anchor tags) for web crawler component
4. Tokenize text using regex: `\b\w+\b`
5. Convert all tokens to lowercase for case-insensitive matching

### Phase 2: Filtering
1. Remove **stopwords** using NLTK's English stopwords corpus
   - Stopwords: common words like "the", "and", "is", "are", etc.
   - These words appear frequently but provide little semantic value
2. Remove single-character tokens
3. Keep only alphanumeric words

### Phase 3: Indexing
1. Count term occurrences in each document (term frequency)
2. Update inverted index: add document to each term's set
3. Update document frequency: count documents containing each term
4. Store document length for normalization

### Phase 4: Searching
1. Parse and filter the search query (same as documents)
2. Find documents containing ALL query terms (AND semantics)
   - Use set intersection on inverted index entries
3. Calculate TF-IDF scores for matching documents
4. Rank results by total TF-IDF score (descending)
5. Display results with URLs and scores

### Boundary Condition Handling
- **Empty query**: Detect and prompt user for input
- **Stopwords-only query**: Notify user and request specific terms
- **Non-existent terms**: Report terms not found in any document
- **No matching documents**: Clear message when no results found
- **File errors**: Handle missing files and parsing errors gracefully

---

## Dependencies

The project requires the following Python libraries:

```bash
pip install beautifulsoup4 nltk
```

- **BeautifulSoup4**: HTML parsing and text extraction
- **NLTK**: Natural Language Toolkit for comprehensive stopwords

---

## Project Structure

```
Project/
├── search_engine.py           # Main search engine implementation
├── webpages/                  # Directory containing HTML documents
│   ├── input.txt              # URL mapping file (filename URL)
│   ├── index.html             # Homepage with navigation
│   ├── cybersecurity_fundamentals.html
│   ├── cloud_security.html
│   ├── cryptography.html
│   ├── network_security.html
│   ├── malware_analysis.html
│   ├── incident_response.html
│   └── ethical_hacking.html
├── output.txt                 # Test output with boundary conditions
└── README.md                  # This file
```

---

## Sample Web Pages

The project includes **8 HTML pages** on cybersecurity topics:

1. **index.html**: Homepage with navigation to all topics
2. **cybersecurity_fundamentals.html**: Core security principles (CIA triad)
3. **cloud_security.html**: Cloud service models and security challenges
4. **cryptography.html**: Encryption, hashing, digital signatures
5. **network_security.html**: Firewalls, IDS/IPS, network attacks
6. **malware_analysis.html**: Malware types and analysis techniques
7. **incident_response.html**: IR lifecycle and best practices
8. **ethical_hacking.html**: Penetration testing methodologies

Each page contains:
- Rich, relevant content (300-500 words)
- **Hyperlinks** to related pages (web crawler aspect)
- Proper HTML structure for parsing

---

## Usage Instructions

### Interactive Mode

Run the search engine in interactive mode to enter queries manually:

```bash
python search_engine.py
```

**Features**:
- Enter search queries and see ranked results
- Type `stats` to view search engine statistics
- Type `exit` or `quit` to exit

**Example Session**:
```
🔍 Mini Search Engine - Interactive Mode
Type 'exit' or 'quit' to exit
Type 'stats' to see statistics

Enter search query: cloud security

Search terms (after filtering): ['cloud', 'security']
  'cloud' → found in 2 documents
  'security' → found in 6 documents

Found 2 matching document(s)
1. cloud_security.html
   Relevance Score (TF-IDF): 0.123456
   URL: https://www.coursera.org/articles/cybersecurity-analyst-skills
   Links: 7 outgoing hyperlink(s)

2. index.html
   Relevance Score (TF-IDF): 0.045678
   URL: https://cybersecurity-hub.example.com/
   Links: 7 outgoing hyperlink(s)
```

### Test Mode

Run predefined test queries and save output to `output.txt`:

```bash
python search_engine.py --test
```

**Test Cases**:
- Empty query
- Stopwords-only query
- Non-existent term
- Single-term queries
- Multi-term queries (AND semantics)
- Complex multi-word queries

The output demonstrates:
- Boundary condition handling
- Ranking algorithm effectiveness
- Proper error messages

---

## Input File Format

The `webpages/input.txt` file maps filenames to URLs:

```
filename URL

// Example:
index.html https://cybersecurity-hub.example.com/
cybersecurity_fundamentals.html https://www.securitymagazine.com/articles/101473-the-fundamentals-of-cybersecurity-in-the-age-of-ai
cloud_security.html https://www.coursera.org/articles/cybersecurity-analyst-skills
cryptography.html https://cybersecurity-hub.example.com/cryptography
network_security.html https://www.malwarebytes.com/cybersecurity
malware_analysis.html https://www.coursera.org/articles/cybersecurity-analyst-skills
incident_response.html https://www.linkedin.com/pulse/fundamentals-cybersecurity-comprehensive-guide-beginners-mytectra-l8eoc/
ethical_hacking.html https://www.purdueglobal.edu/blog/information-technology/ethical-hacker/
```

---

## Testing Strategy

### Boundary Conditions Tested

1. **Empty Query**
   - Input: `""`
   - Expected: Error message requesting search terms
   
2. **Stopwords-Only Query**
   - Input: `"the and is are"`
   - Expected: Message indicating only stopwords, request specific terms
   
3. **Non-Existent Term**
   - Input: `"xyzabc123notfound"`
   - Expected: Message indicating term not found in any document
   
4. **Single Term Positive Match**
   - Input: `"security"`, `"encryption"`, `"malware"`
   - Expected: Ranked list of matching documents
   
5. **Multi-Term AND Query**
   - Input: `"cloud security"`, `"network attack"`, `"encryption cryptography"`
   - Expected: Only documents containing ALL terms, ranked by TF-IDF
   
6. **Complex Query**
   - Input: `"security threats protection"`
   - Expected: Documents with all three terms, demonstrating ranking

### Verification Process

1. Run `python search_engine.py --test`
2. Review `output.txt` for all test cases
3. Verify boundary conditions are handled correctly
4. Confirm TF-IDF ranking produces sensible results
5. Check that hyperlinks are extracted from all pages

---

## Algorithm Analysis

### Search Query Performance

**Preprocessing**: O(Q) where Q = query length
- Tokenize and filter query terms

**Document Retrieval**: O(T) where T = number of query terms
- For each term, lookup in inverted index: O(1)
- Set intersection of document sets: O(D) where D = avg docs per term

**Ranking**: O(M × T) where M = matching documents
- Calculate TF-IDF for each term in each matching document

**Sorting**: O(M log M)
- Sort matching documents by score

**Total**: O(Q + T + D + M×T + M log M)

For typical queries (few terms, few matches), this is very efficient.

### Space Complexity

**Inverted Index**: O(V × D_avg)
- V = vocabulary size
- D_avg = average documents per term

**Term Frequency**: O(V × D_avg)

**Total**: O(V × D) where D = total documents

This is acceptable for small to medium collections. For large scale, additional optimization techniques like compression and sharding would be needed.

---

## Improvements Over Basic Implementation

1. **NLTK Stopwords**: More comprehensive (179 words) vs hardcoded (~25 words)
2. **TF-IDF Ranking**: Better relevance scoring vs simple term frequency
3. **Hyperlink Extraction**: Supports web crawler functionality
4. **Better Documentation**: Extensive comments and docstrings
5. **Error Handling**: Robust boundary condition handling
6. **Statistics Display**: Useful insights into indexed data
7. **Dual Modes**: Interactive for exploration, test for automated validation

---

## Limitations and Future Enhancements

### Current Limitations
- AND-only queries (no OR or NOT operators)
- No phrase search (e.g., "cloud computing")
- No stemming or lemmatization (e.g., "encrypt" vs "encryption")
- Limited to local HTML files (no actual web crawling)

### Possible Enhancements
- Add query operators (OR, NOT, phrase search)
- Implement Porter Stemmer for word normalization
- Add caching for faster repeated queries
- Implement actual web crawler to fetch pages
- Support for proximity search (terms near each other)
- Add search suggestions and auto-complete
- Build web interface for easier interaction

---

## References

- Course Textbook: Section 23.6 - Search Engine
- NLTK Documentation: https://www.nltk.org/
- BeautifulSoup Documentation: https://www.crummy.com/software/BeautifulSoup/
- TF-IDF Algorithm: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- Inverted Index: https://en.wikipedia.org/wiki/Inverted_index

---

## Conclusion

This search engine implementation demonstrates core information retrieval concepts including inverted indexing, stopword filtering, and TF-IDF ranking. The system efficiently searches a small collection of cybersecurity-related web pages, handling various query types and boundary conditions robustly.

The use of well-established data structures (sets, dictionaries, counters) from Python's standard library ensures both efficiency and code clarity. NLTK integration provides industrial-strength stopword filtering, while TF-IDF ranking produces relevance scores that align with user expectations.

---

**For questions or issues, please contact: ankitdhandharia21@gmail.com**
