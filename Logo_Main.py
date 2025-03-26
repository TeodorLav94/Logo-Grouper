import pandas as pd                 # citire fisier .parquet si manipulare tabelara
from tqdm import tqdm               # afisare progres in bucle lungi
import networkx as nx               # lucrul cu grafuri pentru grupare pe baza similaritatii
from concurrent.futures import ThreadPoolExecutor, as_completed  # paralelizare cu thread-uri
import warnings                     # ignorare avertismente PIL
from Logo_Utils import get_logo, hash_logo, hamming_distance  # functii custom pentru extragere si procesare logo-uri

warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# Incarc domeniile din fisierul parquet
def load_domains(parquet_file):
    df = pd.read_parquet(parquet_file)
    df['domain'] = df['domain'].astype(str).str.strip()
    return df['domain'].dropna().unique().tolist()

# Construiesc graf de similaritate
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

# Procesez un singur domain: iau logo-ul, fac hash
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

# Main
def main():
    parquet_file = "logos.snappy.parquet"
    domains = load_domains(parquet_file)

    domain_hashes = {}
    failed = []

    # modific preview_limit pentru a dechide primele n logo-uri, pentru verificare
    preview_limit = 0

    # threshold controleaza cat de similare trebuie sa fie doua logo-uri (distanta Hamming)
    # valori mai mici = grupuri mai stricte, valori mai mari = grupuri mai permisive 
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

    # Grupez logo-urile folosind un graf de similaritate
    G = build_similarity_graph(domain_hashes, threshold)
    groups = list(nx.connected_components(G))

    # Salvez rezultatele
    output = [list(group) for group in groups]
    pd.DataFrame({'group_id': range(len(output)), 'domains': output}).to_json("logo_groups.json", orient="records", indent=2)

    print(f"\n\u2705 Grouping complete! {len(groups)} groups saved to logo_groups.json")

if __name__ == "__main__":
    main()
