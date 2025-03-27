# 🔍 Logo-Grouper (Veridion Challenge)

**Logo-Grouper** is a Python tool built to extract and group visually similar logos from a large list of domains. It uses perceptual hashing and graph-based clustering to efficiently match logos that look alike, even when they differ in size, color, or compression.

Designed to work at scale, Logo-Grouper extracts logos using multiple fallback methods, validates them for quality, hashes them using `pHash`, and clusters similar ones using a similarity graph.

---

## 🔑 How It Works

Logo-Grouper processes each domain in three key steps: logo retrieval, perceptual hashing, and similarity-based grouping using a graph structure.

### 1. Logo Retrieval (Multi-Level Fallback)

To maximize accuracy and coverage, logos are extracted using multiple prioritized sources:

- **HTML `<link rel="icon">`** – Parses the homepage to find explicitly declared favicons.
- **Clearbit API** – Attempts to fetch a high-quality logo for the domain.
- **DuckDuckGo Icon API** – Grabs lightweight, cached icons.
- **Fallback to `/favicon.ico`** – Standard browser location.

Each image is validated:

- Minimum size of 32x32 pixels  
- Basic visual complexity (avoiding blank, transparent, or uniform icons)  
- Converted to RGB/RGBA for consistent processing  

If none of the sources provide a high-quality logo, the system falls back to the first available image.

### 2. Perceptual Hashing

Each valid image is converted into a 64-bit perceptual hash using `imagehash.phash()`. This type of hash:

- Encodes the visual structure of an image  
- Is robust to scaling, compression, and minor color changes  
- Allows fast, meaningful comparisons using Hamming distance  

### 3. Similarity-Based Grouping

- The system computes Hamming distance between all logo hashes.  
- Two domains are considered similar if their hash distance ≤ **threshold** (default: `10`).  
- These similarities are represented in an undirected graph, where:  
  - **Nodes** = domains  
  - **Edges** = visual similarity  
- The **connected components** of the graph form final logo groups.

The result is a list of clusters, each containing domains that share visually similar branding.

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
