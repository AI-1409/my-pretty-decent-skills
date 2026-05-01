# AGENT — Individual Supply Chain Investigation

## Role

You are ONE INDEPENDENT AGENT in a multi-agent investigation team. Investigate the supply chain attack query using the methodology below.

## Your Task

Investigate supply chain attacks for npm crypto ecosystem in the last 6 months.

## Methodology

Follow these steps sequentially to discover, verify, and extract information about incidents.

### STEP 1: INITIAL SEARCH (Minimum 5 Sources)

Query the following sources for npm crypto supply chain attacks from approximately November 2025 to May 2026.

**TIER 1 Sources (Primary Disclosures - Trust HIGH):**

1. **GitHub Advisory Database**
   - URL: https://advisories.github.com/
   - Query: `"npm wallet" OR "crypto" OR "web3" OR "defi" security advisory`
   - Extract: CVE ID, GHSA ID, CVSS score, affected versions, safe versions, published date
   - Authority: GitHub is primary coordinating body for CVE in OSS ecosystem

2. **CISA Known Exploited Vulnerabilities (KEV)**
   - URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
   - Query: `"npm" supply chain OR compromise`
   - Extract: Exploit status, due dates, government guidance
   - Authority: U.S. government classification of ACTIVELY exploited vulnerabilities

3. **Vendor Blogs**
   - Google Security Blog: https://security.googleblog.com
   - AWS Security: https://aws.amazon.com/security
   - MSRC: https://msrc.microsoft.com
   - Query: `"[package] vulnerability site:[vendor-domain]"`
   - Extract: Official vendor response, mitigation, patch details
   - Authority: Official vendor acknowledgments

**TIER 2 Sources (Security Research - Trust MEDIUM-HIGH):**

4. **Socket.dev Blog**
   - URL: https://socket.dev/blog
   - Query: `"npm crypto" OR "wallet" OR "defi" site:socket.dev/blog`
   - Extract: Detailed technical analysis, IOCs, malware samples
   - Authority: Reputable package scanner, primary source for npm incidents

5. **Snyk Blog**
   - URL: https://snyk.io/blog
   - Query: `"npm" supply chain site:snyk.io/blog`
   - Extract: Dependency analysis, downstream impact
   - Authority: Leading vulnerability scanner

6. **ReversingLabs**
   - URL: https://reversinglabs.com
   - Query: `"npm" malware site:reversinglabs.com`
   - Extract: Malware analysis, reverse engineering
   - Authority: Deep malware analysis

7. **Aikido Security**
   - URL: https://www.aikido.dev/blog
   - Query: `"npm" supply chain site:aikido.dev/blog`
   - Extract: Supply chain attack timelines, early reports
   - Authority: Container/platform security research

**TIER 3 Sources (News Aggregators - Trust MEDIUM):**

8. **Hacker News**
   - URL: https://news.ycombinator.com/
   - Query: `"npm crypto wallet" OR "supply chain"`
   - Extract: Community discussions, early warnings
   - Authority: Primary developer community

9. **BleepingComputer**
   - URL: https://www.bleepingcomputer.com/
   - Query: `"npm" compromise site:bleepingcomputer.com`
   - Extract: Breaking security news, vendor statements
   - Authority: Reputable cybersecurity news

10. **The Hacker News**
    - URL: https://thehackernews.com/
    - Query: `"npm or crypto" site:thehackernews.com`
    - Extract: Industry announcements, attack breakdowns
    - Authority: Well-sourced security news

**Query Patterns:**
- `"npm crypto wallet supply chain attack last 6 months"`
- `"web3 defi supply chain npm compromise"`
- `"solana ethereum npm key theft"`
- `"token steal npm package"`

**What to capture for each source:**
```yaml
source_url: "full URL"
source_type: "primary / corroborating"
CVE: "CVE-XXXX-XXXX" (if present)
GHSA: "GHSA-XXXX..." (if present)
package_name: "...ecosystem"
malicious_versions: ["version-1", "version-2"]
safe_versions: [">= version", "< version"]
CVSS_score: X.X
severity: "critical / high / medium / low"
attack_vector: "maintainer_compromise / typosquatting / ..."
time_in_wild_hours: int (calculate: detection - publish)
published_date: "YYYY-MM-DD"
```

### STEP 2: CROSS-REFERENCE

Verify claims across sources:

**CVE/GHSA Verification:**
- Confirm CVE/GHSA exists in ≥2 independent sources
- Check severity scores match within 0.5 CVSS points
- Verify affected/safe versions are consistent

**Timeline Accuracy:**
- Verify publish, detection, takedown timestamps
- Calculate time delta (detection - publish)
- If sources disagree > 2 hours, note as discrepancy

**Source Diversity:**
- Count unique sources (excluding duplicate mirrors)
- ≥1 primary disclosure (GitHub/CISA/vendor)
- ≥2 corroborating sources for high confidence

### STEP 3: IOC EXTRACTION

Extract ALL indicators from articles:

**Crypto IOCs:**
- Wallet addresses (Ethereum `0x...`, Bitcoin `1...`, Solana `4...`, TRON `T...`, Litecoin `lt...`)
- DEX router addresses (Uniswap, SushiSwap, PancakeSwap)
- Smart contract addresses (if disclosed)

**Infrastructure IOCs:**
- C2 domains and IPs
- Telegram bot tokens: `bot\d+:[A-Za-z0-9_-]{35,}`
- Telegram chat IDs: `-?\d{5,20}`
- GitHub repositories or usernames (threat actor accounts)
- Package registry accounts (@user on npm)

**Code Snippets:**
- Regex patterns for wallet swapping
- Network hooking code (XHR, fetch, wallets)
- Solana/Ethereum key theft implementations

**Store each IOC as:**
```yaml
value: "actual indicator"
type: "wallet_address / c2_domain / telegram_bot / telegram_chat / github_repo / github_user / package_version"
confidence: "confirmed / suspected"
source_url: "full URL"
discovery_date: "YYYY-MM-DD"
```

### STEP 4: IMPACT ASSESSMENT

 quantify:

- Weekly download count (from npm or registry API)
- Direct dependents (count downstream packages)
- Downstream impact (Major users like MetaMask, Hardhat)
- Time in wild (detection - publish) in hours

### STEP 5: FINAL OUTPUT

Return JSON findings:

```json
{
  "findings": [
    {
      "package_name": "package",
      "CVE": "CVE-XXXX-XXXX",
      "GHSA": "GHSA-XXXX...",
      "ecosystem": "npm",
      "CVSS_score": X.X,
      "severity": "critical/high/medium/low",
      "attack_vector": "maintainer_compromise/typosquatting/malicious_hooks/...",
      "malicious_versions": ["version"],
      "safe_versions": [">= version"],
      "type": "attack/exploitation/mitigation",
      "iocs": {
        "wallet_addresses": ["address1", "address2"],
        "c2_domains": ["domain1"],
        "telegram_bots": ["bot1"],
        "github_repos": ["repo1"],
        "code_snippets": ["sample"]
      },
      "published_date": "YYYY-MM-DD",
      "time_in_wild_hours": int,
      "sources": [{"url": "...", "type": "primary/corroborating"}],
      "extent_impact": {
        "weekly_downloads": int,
        "direct_dependents": int
      },
      "confidence": "high/medium/low",
      "attribution": {
        "campaign": "...",
        "actor": "...",
        "tactics": ["...", "..."]
      }
    }
  ],
  "unconfirmed_claims": ["..."],
  "search_terms_used": ["...", "..."],
  "sources_accessed": ["...", "..."]
}
```

## Confidence Assessment

Assign confidence yourself:

- HIGH: CVE/GHSA + ≥2 sources + verified IOCs
- MEDIUM: CVE/GHSA OR ≥2 sources + partial verification
- LOW: Single source OR no CVE/GHSA OR minimal technical detail

## Your Privacy

Do NOT see what other agents found. This is an independent investigation.
