---
name: supply-chain-threat-intel
description: Multi-agent LLM guidance for investigating software supply chain attacks via web browsing with consensus verification
version: 2.0.0
metadata:
  hermes:
    tags: [supply-chain, security, threat-intel, multi-agent, llm-guided-investigation]
    multi_agent:
      enabled: true
      default_agents: 4
      orchestration: automatic
---

# Supply Chain Attack Investigator — Multi-Agents

## Purpose

This skill uses a multi-agent pipeline to investigate software supply chain attacks. Multiple agents work in parallel to discover incidents, aggregate findings, and apply consensus filtering for high-confidence results.

## How It Works

```
User Query
    ↓
┌─────────────────────────────────────────┐
│  COORDINATOR (Auto-Spawns 4 Parallel Agents)  │
│  - Loads prompts/*.md                   │
│  - Reads config/consensus_settings.yml   │
│  - Spawns N agents (default 4)           │
│  - Aggregates all responses              │
│  - Computes consensus percentages        │
│  - Applies confidence thresholds         │
│  - Presents filtered, graded report     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  N INDEPENDENT AGENTS (Each: 5+ sources)│
│  Agent 1: GitHub + Socket.dev + focused terms  │
│  Agent 2: CISA + Snyk + broad terms               │
│  Agent 3: News aggregators + sharp terms         │
│  Agent 4: Vendor blogs + timeframe buffer        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  AGGREGATOR / CONSENSUS ENGINE          │
│  - Normalizes to common formats         │
│  - De-duplicates by CVE/GHSA/package    │
│  - Scores findings: 0-100% consensus    │
│  - Detects conflicts (agents disagree)  │
│  - Applies confidence thresholds        │
│  - Filters low-confidence items         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  FINAL OUTPUT (Confidence-Graded)       │
│  ✅ HIGH CONFIDENCE (80-100% consensus) │
│  ⚠️  MEDIUM CONFIDENCE (60-79%)        │
│  🔍 SUSPECTED (40-59%)                  │
│  ⚠️  CONFLICTIC (agents disagree)       │
│  ❌ EXCLUDED (<40% - appendix)         │
└─────────────────────────────────────────┘
```

## Auto-Spawning Behavior

When this skill is loaded, the COORDINATOR automatically:

1. **Reads** the user query (e.g., "npm crypto attacks last 6 months")
2. **Loads** prompts from `/prompts/coordinator.md` and `config/consensus_settings.yml`
3. **Spawns** 4 parallel agents using `delegate_task(role="leaf")`
4. **Injects** `prompts/agent.md` into each agent context (investigation goal, 5 sources to check)
5. **Waits** for all agents to return JSON findings
6. **Loads** `prompts/aggregator.md` to:
   - Normalize and de-duplicate findings
   - Compute consensus percentages (agents found / total agents)
   - Apply confidence boosts (GitHub/CISA get +20%)
   - Detect conflicts (agents disagree on severity/versions/time)
7. **Applies** thresholds:
   - HIGH: 80-100% consensus (4/4 agents)
   - MEDIUM: 60-79% consensus (3/4 agents)
   - SUSPECTED: 40-59% with strong source
   - EXCLUDED: <40% or single-agent
8. **Presents** final report using `prompts/output_template.md`

## File Structure

```
supply-chain-threat-intel/
├── SKILL.md                           # Main LLM guidance
├── prompts/
│   ├── coordinator.md                 # Orchestration script (loads first)
│   ├── agent.md                       # Individual agent task template
│   ├── aggregator.md                  # Consensus engine rules
│   ├── investigation_plan.md          # Step-by-step methodology
│   ├── source_checklist.md            # Where to search, query patterns
│   ├── ioc_extraction.md              # What IOCs to extract
│   ├── verification_guide.md          # How to validate claims across sources
│   └── output_template.md             # Final report structure
├── config/
│   ├── consensus_settings.yml         # Thresholds, agent count, boosts
│   └── ecosystem_priorities.yml       # What to prioritize for crypto/web3/etc.
└── research/                          # Reference for LLM knowledge
    ├── sources.md                     # Source reference list
    ├── patterns.md                    # Attack patterns
    └── case_studies.md                # Example investigations
```

## Configuration

`config/consensus_settings.yml`:
```yaml
default_agent_count: 4
high_confidence: 80      # HIGH: 80-100% consensus
medium_confidence: 60    # MEDIUM: 60-79%
suspected: 40            # SUSPECTED: 40-59% with strong source
exclude: 40              # EXCLUDED: <40% or single-agent

confidence_boost:
  github_advisory: +20%  # Primary source adds confidence
  cisa_kev: +20%
  vendor_blog: +15%
  security_blog: +10%
  news_aggregator: +5%
```

`config/ecosystem_priorities.yml`:
```yaml
npm:
  priority_sources:
    - GitHub Advisory
    - CISA KEV
    - Socket.dev
    - Snyk
  high_risk_packages:
    - "*wallet*"
    - "*defi*"
    - "*crypto*"
    - "*web3*"
```

## Prompts Loaded by Agents

Each independent agent loads ALL prompts:
1. **investigation_plan.md** — Multi-source search methodology
2. **source_checklist.md** — 5+ TIER-1/TIER-2 sources
3. **ioc_extraction.md** — Crypto wallets, C2 domains, Telegram, GitHub repos
4. **verification_guide.md** — CVE/GHSA validation, source diversity
5. **agent.md** — Task template (returns JSON findings)

 Agents vary in approach:
- Different sources (GitHub vs Snyk vs news)
- Different search terms (exact vs broad)
- Different timeframes (exact ± buffer)

## Multi-Agent Consensus Scoring

For each incident (CVE/GHSA/package):
```yaml
finding_id: "CVE-2025-59144"
consensus_pct: (agents_found / total_agents) * 100

# Confidence boosts applied if primary source exists
boosted_consensus_pct = consensus_pct + source_boost

confidence_level:
  - HIGH: boosted_consensus_pct >= 80
  - MEDIUM: 60-79%
  - SUSPECTED: 40-59% AND (GitHub Advisory OR CISA KEV OR Vendor Blog)
  - EXCLUDED: <40% OR single-agent finding
```

## Conflict Handling

Conflicts (agents disagree on severity > 1 CVSS point, versions, time in wild > 2 hours) are NEVER auto-resolved:
- Both/all claims listed with source citations
- Flagged as `⚠️ CONFLICTIC INFORMATION`
- Recommended action: Requery deeper

## Output Format

Each incident uses `prompts/output_template.md`:
- Multi-Agent Consensus header (X/Y agents)
- Confidence grade (HIGH/MEDIUM/SUSPECTED)
- Quick overview (package, CVE, ecosystem, CVSS, attack vector)
- Attack mechanics (compromise → payload → impact)
- IOCs (wallet addresses, C2, Telegram, GitHub repos, code samples)
- Impact (downloads, dependents, downstream ecosystem)
- Sources (primary first, then corroborating)
- Attribution (campaign, actor, tactics) — if known

Report sections:
- HIGH CONFIDENCE incidents first
- MEDIUM CONFIDENCE next
- SUSPECTED (needs manual verification)
- CONFLICTIC (agents disagree)
- Appendix: Excluded findings

## Quick Start

**Load this skill** when you ask any of:
- "Supply chain attacks for [ecosystem] [timeframe]"
- "Compromised packages affecting [domain]"
- "Investigate [CVE/GHSA] supply chain incident"
- "Recent npm/crypto/defi attacks"

The skill auto-spawns agents, collects findings, and returns a consensus-filtered report.

## Backward Compatibility

For simple yes/no questions, coordinator uses single agent:
```
"Is package X compromised?"
→ 1 agent quick check
→ Returns yes/no with source citation
```

---

**This skill is auto-orchestrated via `delegate_task` with multi-agent consensus filtering.**
