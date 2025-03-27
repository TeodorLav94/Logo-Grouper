# 🔍 Logo-Grouper (Veridion Challenge)

**Logo-Grouper** is a Python tool built to extract and group visually similar logos from a large list of domains. It uses perceptual hashing and graph-based clustering to efficiently match logos that look alike, even when they differ in size, color, or compression.

Designed to work at scale, Logo-Grouper extracts logos using multiple fallback methods, validates them for quality, hashes them using `pHash`, and clusters similar ones using a similarity graph.

---

## 🔑 How It Works

### Logo Retrieval

For each domain, the tool attempts to extract the most relevant logo using a layered fallback approach:

1. Parses the homepage's HTML to extract `<link rel="icon">`
2. Queries Clearbit’s logo API
3. Fetches icons from DuckDuckGo
4. Falls back to the default `/favicon.ico` location

Each downloaded image is validated (minimum size and visual complexity). If no meaningful logo is found, the first available fallback is used.

### Logo Hashing and Grouping

- Each logo is converted to a perceptual hash using `imagehash.phash()`
- All pairs of hashes are compared using Hamming distance  
- If the distance ≤ **threshold** (default: `10`), the logos are considered visually similar
- Similar logos are grouped using connected components in a graph

---

## 🧪 Example Run

- Domains processed: **3,416**
- Logos successfully extracted: **3,338** (97.71%)
- Logos failed: **78**
- Groups formed: **1,286**
- Processing time: ~1 minute (32 threads)

---

## 📄 Output

- logo_groups.json: List of grouped domains with similar logos

---

## 🔧 Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`:
  - `imagehash`, `Pillow`, `requests`, `bs4`, `networkx`, `tqdm`, `pandas`

Install with:

```bash
pip install -r requirements.txt
