import pandas as pd                 # read .parquet file and manipulate tabular data
from tqdm import tqdm               # show progress bar for long loops
import networkx as nx               # work with graphs for grouping by similarity
from concurrent.futures import ThreadPoolExecutor, as_completed  # multithreading
import warnings                     # suppress PIL warnings
from Logo_Utils import get_logo, hash_logo, hamming_distance  # custom functions for logo extraction and processing

warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# Load domains from a .parquet file
def load_domains(parquet_file):
    df = pd.read_parquet(parquet_file)
    df['domain'] = df['domain'].astype(str).str.strip()
    return df['domain'].dropna().unique().tolist()

# Build similarity graph based on perceptual hash distance
def build_similarity_graph(domain_hashes, threshold):
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

# Process a single domain: fetch logo and compute hash
def process_domain(domain, preview=False):
    logo = get_logo(domain)
    if logo:
        try:
            h = hash_logo(logo)
            if preview:
                logo.show(title=domain)
            return domain, h
        except Exception:
            return domain, None
    return domain, None

# Main function
def main():
    parquet_file = "logos.snappy.parquet"
    domains = load_domains(parquet_file)

    domain_hashes = {}
    failed = []

    # Set preview_limit to display the first n logos for visual check
    preview_limit = 0

    # threshold controls how similar two logos must be (based on Hamming distance)
    # lower values = stricter groups, higher values = more permissive
    threshold = 10

    print("Downloading and hashing logos...")

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [
            executor.submit(process_domain, domain, i < preview_limit)
            for i, domain in enumerate(domains)
        ]
        for f in tqdm(as_completed(futures), total=len(futures)):
            domain, hash_result = f.result()
            if hash_result:
                domain_hashes[domain] = hash_result
            else:
                failed.append(domain)

    print(f"\nSuccessfully hashed: {len(domain_hashes)} / {len(domains)}")
    print(f"Failed domains: {len(failed)}")

    # Group logos using a similarity graph
    G = build_similarity_graph(domain_hashes, threshold)
    groups = list(nx.connected_components(G))

    # Save output
    output = [list(group) for group in groups]
    pd.DataFrame({'group_id': range(len(output)), 'domains': output}).to_json("logo_groups.json", orient="records", indent=2)

    print(f"\n✅ Grouping complete! {len(groups)} groups saved to logo_groups.json")

if __name__ == "__main__":
    main()
