/**
 * Calculates Shannon entropy of an input string.
 * Uses Math.log2 to match Python's math.log2 exactly.
 */
export function calculateShannonEntropy(text) {
  if (!text || text.length === 0) return 0.0;
  
  const charCounts = {};
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    charCounts[char] = (charCounts[char] || 0) + 1;
  }

  let entropy = 0.0;
  const len = text.length;
  for (const char in charCounts) {
    const p = charCounts[char] / len;
    entropy -= p * Math.log2(p);
  }

  return parseFloat(entropy.toFixed(4));
}

/**
 * Extracts 16 numerical features from a raw URL string.
 * Order must match Python's features.py verbatim:
 * [url_len, host_len, path_len, count_dot, count_hyphen, count_at, 
 *  count_question, count_equal, count_slash, count_percent, is_ip, 
 *  subdomain_depth, has_keyword, is_https, hostname_entropy, url_entropy]
 */
export function extractFeaturesFromUrl(rawUrl) {
  const cleanUrl = rawUrl.trim();
  let urlObj;
  
  try {
    urlObj = new URL(cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') 
      ? cleanUrl 
      : 'http://' + cleanUrl
    );
  } catch (e) {
    // Fallback for malformed URLs
    urlObj = {
      hostname: '',
      pathname: '',
      search: '',
      protocol: 'http:'
    };
  }

  const hostname = (urlObj.hostname || '').toLowerCase();
  const path = urlObj.pathname || '';
  const query = urlObj.search ? urlObj.search.substring(1) : '';

  // 1. Length metrics
  const urlLen = cleanUrl.length;
  const hostLen = hostname.length;
  const pathLen = path.length;

  // 2. Character counts
  const countDot = (cleanUrl.match(/\./g) || []).length;
  const countHyphen = (hostname.match(/-/g) || []).length;
  const countAt = (cleanUrl.match(/@/g) || []).length;
  const countQuestion = (cleanUrl.match(/\?/g) || []).length;
  const countEqual = (cleanUrl.match(/=/g) || []).length;
  const countSlash = (cleanUrl.match(/\//g) || []).length;
  const countPercent = (cleanUrl.match(/%/g) || []).length;

  // 3. Structural metrics
  const hostClean = hostname.split(':')[0];
  const isIp = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(hostClean) ? 1.0 : 0.0;

  // Subdomain depth calculation (mirrors tldextract logic)
  const parts = hostClean.split('.');
  let subdomainDepth = 0.0;
  if (parts.length > 2 && !isIp) {
    // If parts are [sub2, sub1, domain, tld], depth is parts.length - 2
    subdomainDepth = parts.length - 2;
  }

  const suspiciousKeywords = ['login', 'verify', 'update', 'banking', 'secure', 'signin', 'account', 'admin'];
  const targetCheck = (path + query).toLowerCase();
  const hasKeyword = suspiciousKeywords.some(kw => targetCheck.includes(kw)) ? 1.0 : 0.0;

  const isHttps = urlObj.protocol === 'https:' ? 1.0 : 0.0;

  // 4. Entropy metrics
  const hostnameEntropy = calculateShannonEntropy(hostname);
  const urlEntropy = calculateShannonEntropy(cleanUrl);

  // Return as a Float32Array matching the shape expected by ONNX (16 features)
  return new Float32Array([
    urlLen,
    hostLen,
    pathLen,
    countDot,
    countHyphen,
    countAt,
    countQuestion,
    countEqual,
    countSlash,
    countPercent,
    isIp,
    subdomainDepth,
    hasKeyword,
    isHttps,
    hostnameEntropy,
    urlEntropy
  ]);
}