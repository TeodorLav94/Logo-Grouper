import pandas as pd           # citire fisier .parquet si prelucrare date tabelare
import requests               # cereri HTTP pentru descarcare logo-uri
from PIL import Image         # lucrul cu imagini (deschidere, afisare)
from io import BytesIO        # transformare bytes in imagine
from tqdm import tqdm         # bara de progres in bucla

# Incarc domeniile din fisierul parquet
def load_domains(parquet_file):
    df = pd.read_parquet(parquet_file)
    df['domain'] = df['domain'].astype(str).str.strip()
    return df['domain'].dropna().unique().tolist()

# Folosesc Clearbit
def get_logo(domain):
    url = f"https://logo.clearbit.com/{domain}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception:
        pass
    return None

def main():
    parquet_file = "logos.snappy.parquet"
    domains = load_domains(parquet_file)

    success = []
    failed = []
    preview_limit = 5

    print("Downloading logos...")

    for i, domain in enumerate(tqdm(domains)):
        logo = get_logo(domain)
        if logo:
            success.append(domain)
            if i < preview_limit:
                logo.show(title=domain)
        else:
            failed.append(domain)

    print("\n=== Logo Download Summary ===")
    print(f"Success: {len(success)} domains")
    print(f"Failed : {len(failed)} domains")
    print(f"Success list (first 5): {success[:5]}")
    print(f"Failed list  (first 5): {failed[:5]}")

if __name__ == "__main__":
    main()
