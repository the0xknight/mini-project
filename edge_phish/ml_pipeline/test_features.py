from features import extract_features_from_url

test_cases = [
    "https://www.google.com",
    "http://192.168.1.1/admin/login.php?update=true",
    "https://paypal.com.verify-account-security-alert.xyz/signin",
    "https://github.com/torvalds/linux"
]

print("=== Running Phase 1 Feature Extractor Test ===")
for url in test_cases:
    feats = extract_features_from_url(url)
    print(f"\nURL: {url}")
    print(f" -> Feature Count: {len(feats)}")
    print(f" -> Host Entropy:  {feats['hostname_entropy']}")
    print(f" -> Is IP Address: {feats['is_ip']}")
    print(f" -> Has Keyword:   {feats['has_keyword']}")
    
    assert len(feats) == 16, f"Expected 16 features, got {len(feats)}"
    assert all(isinstance(v, float) for v in feats.values()), "All features must be float."

print("\n[SUCCESS] Feature extractor passed all checks!")