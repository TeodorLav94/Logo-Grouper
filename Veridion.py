import pandas as pd           # citire fisier .parquet si prelucrare date tabelare
import imagehash              # pentru generarea hash-urilor din imagini
import requests               # cereri HTTP pentru descarcare logo-uri
from PIL import Image         # lucrul cu imagini (deschidere, afisare)
from io import BytesIO        # transformare bytes in imagine
from tqdm import tqdm         # bara de progres in bucla
import networkx as nx         # pentru grafuri și grupare

# Incarc domeniile din fisierul parquet
def load_domains(parquet_file):
    df = pd.read_parquet(parquet_file)
    df['domain'] = df['domain'].astype(str).str.strip()
    return df['domain'].dropna().unique().tolist()

# Folosesc Clearbit, apoi DuckDuckGo si favicon ca fallback
def get_logo(domain):
    sources = [
        f"https://logo.clearbit.com/{domain}",
        f"https://icons.duckduckgo.com/ip3/{domain}.ico", 
        f"https://{domain}/favicon.ico",
    ]
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in sources:
        try:
            response = requests.get(url, headers=headers, timeout=2)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if img.mode == "P" and "transparency" in img.info:
                    return img.convert("RGBA")
                else:
                    return img.convert("RGB")
        except Exception:
            continue
    return None

# Folosesc perceptual hash pentru a face hash la imagine
def hash_logo(image):
    return imagehash.phash(image)

# Compare hashes (Hamming distance)
def hamming_distance(hash1, hash2):
    return hash1 - hash2

# Construiesc graf de similaritate
def build_similarity_graph(domain_hashes, threshold=5):
    G = nx.Graph()
    domains = list(domain_hashes.keys())

    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            d1, d2 = domains[i], domains[j]
            h1, h2 = domain_hashes[d1], domain_hashes[d2]
            if hamming_distance(h1, h2) <= threshold:
                G.add_edge(d1, d2)

    for domain in domains:
        G.add_node(domain)  

    return G

# Main
def main():
    parquet_file = "logos.snappy.parquet"
    domains = load_domains(parquet_file)

    domain_hashes = {}
    failed = []

    print("Downloading and hashing logos...")
    preview_limit = 1
    for i, domain in enumerate(tqdm(domains)):
        logo = get_logo(domain)
        if logo:
            try:
                domain_hashes[domain] = hash_logo(logo)
                if i < preview_limit:
                    logo.show(title=domain)
            except Exception:
                    failed.append(domain)
        else:
            failed.append(domain)

    print(f"\nSuccessfully hashed: {len(domain_hashes)} / {len(domains)}")
    print(f"Failed domains: {len(failed)}")

    # Cluster logouri folosind un graf de similaritate
    G = build_similarity_graph(domain_hashes, threshold=10)
    clusters = list(nx.connected_components(G))

    # Salvez rezultatele
    output = [list(group) for group in clusters]
    pd.DataFrame({'cluster_id': range(len(output)), 'domains': output}).to_json("logo_clusters.json", orient="records", indent=2)

    print(f"\n Clustering complete! {len(clusters)} groups saved to logo_clusters.json")

if __name__ == "__main__":
    main() 