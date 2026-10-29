import os
import io
import zipfile
import requests
import pandas as pd
from features import extract_features_from_url

def get_benign_urls(limit=3000):
    print(f"[1/4] Fetching {limit} benign domains from Tranco...")
    try:
        url = "https://tranco-list.eu/top-1m.csv.zip"
        r = requests.get(url, timeout=20)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df = pd.read_csv(f, header=None, names=['rank', 'domain'], nrows=limit)
        return ['https://' + d for d in df['domain'].tolist()]
    except Exception as e:
        print(f"Warning: Live Tranco fetch failed ({e}). Generating fallback benign samples...")
        fallbacks = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'github.com',
                     'wikipedia.org', 'cloudflare.com', 'reddit.com', 'linkedin.com', 'netflix.com']
        return [f"https://{d}/path/{i}" for i in range(limit // len(fallbacks) + 1) for d in fallbacks][:limit]

def get_phishing_urls(limit=3000):
    print(f"[2/4] Fetching {limit} phishing URLs from live feeds...")
    urls = []
    # Primary: Phishunt community feed
    try:
        r = requests.get("https://phishunt.io/feed/feed.txt", timeout=15)
        for line in r.text.splitlines():
            line = line.strip()
            if line.startswith(('http://', 'https://')):
                urls.append(line)
            if len(urls) >= limit:
                break
    except Exception as e:
        print(f"Phishunt feed notice: {e}")

    # Secondary: OpenPhish community feed
    if len(urls) < limit:
        try:
            r = requests.get("https://openphish.com/feed.txt", timeout=15)
            for line in r.text.splitlines():
                line = line.strip()
                if line.startswith(('http://', 'https://')):
                    urls.append(line)
                if len(urls) >= limit:
                    break
        except Exception as e:
            print(f"OpenPhish feed notice: {e}")

    # Fallback generator if network blocks both feeds
    if len(urls) < limit:
        print(f"Live feeds yielded {len(urls)} samples. Generating synthetic variations to reach {limit}...")
        templates = [
            "http://verify-paypal-account-login-{}.com/update",
            "http://192.168.1.{}/banking/secure-auth/login.html",
            "https://netflix-billing-update-{}.xyz/account",
            "http://appleid-security-verification-alert-{}.top/signin"
        ]
        needed = limit - len(urls)
        for i in range(needed):
            tpl = templates[i % len(templates)]
            urls.append(tpl.format(i))

    return urls[:limit]

def main():
    SAMPLE_SIZE = 3000  # 3k benign + 3k phishing = 6k balanced rows
    os.makedirs("data", exist_ok=True)

    benign = get_benign_urls(limit=SAMPLE_SIZE)
    phishing = get_phishing_urls(limit=SAMPLE_SIZE)

    print(f"[3/4] Extracting features for {len(benign)} benign URLs...")
    records = []
    for u in benign:
        row = extract_features_from_url(u)
        row['label'] = 0  # 0 = Benign
        records.append(row)

    print(f"[4/4] Extracting features for {len(phishing)} phishing URLs...")
    for u in phishing:
        row = extract_features_from_url(u)
        row['label'] = 1  # 1 = Phishing
        records.append(row)

    df = pd.DataFrame(records)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    output_path = os.path.join("data", "dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"\n[DONE] Successfully generated {output_path} with shape {df.shape}!")

if __name__ == "__main__":
    main()