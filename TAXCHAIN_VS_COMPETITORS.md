# TaxChain — Competitive Strategy & Build Plan
> Last updated: 2026-06-20
> Source: Web research on Koinly, CoinLedger, CoinTracker, ZenLedger, CoinTracking

---

## Market Position

| Metric | TaxChain | Koinly | CoinLedger | CoinTracker |
|---|---|---|---|---|
| Pricing (annual) | $0–$228/yr ($19/mo) | $49–$279/yr | $49–$199/yr | $59–$599/yr |
| Chains | 8 | 170+ | 250+ | 500+ |
| Countries | 4 tax formats | 20+ countries | 40+ countries | 5 countries |
| Tax methods | FIFO only | FIFO/LIFO/HIFO/Avg | FIFO/LIFO/HIFO | FIFO/LIFO/HIFO |
| Portfolio tracker | ❌ Basic cards | ✅ Full dashboard | ✅ Full dashboard | ✅ Full dashboard |
| DeFi/NFT | ❌ | ✅ Limited | ✅ Full | ✅ Limited |
| CSV import | ❌ | ✅ | ✅ | ✅ |
| Mobile app | ❌ | ✅ | ✅ | ✅ |
| **India ITR VDA** | ✅ **Unique** | ❌ | ❌ | ❌ |
| **8 fiat currencies** | ✅ **Unique** | ❌ | ❌ | ❌ |

---

## Build Plan (Priority Order)

### Sprint 6 — Portfolio Dashboard Overhaul (2 days)
Transform `/dashboard` from basic cards into a real portfolio hub.

```
/dashboard
├── Total portfolio value (USD + local currency)
├── Allocation pie chart (by chain / by token) — Recharts
├── P&L line chart (portfolio value over time)
├── Unrealized gain/loss card
├── Recent transactions feed (last 10)
└── Top movers: gainers / losers widgets
```

### Sprint 7 — In-Memory Ledger + Transaction Editor (3 days)
Allow users to manually manage their transaction data, not just sync from chain APIs.

```
New: /dashboard/ledger
├── In-memory transaction table
│   ├── Add transaction manually (date, type, token, qty, price, chain)
│   ├── Edit any field inline (reclassify type, fix price, update quantity)
│   ├── Delete transactions
│   └── Bulk select → delete / re-tag / re-classify
│
├── CSV Import
│   ├── Upload CSV → preview parsed rows in-memory
│   ├── Column mapping UI (drag-to-match columns)
│   ├── Validate before commit (flag missing prices, unknown tokens)
│   └── Commit to database
│
├── Error Reconciliation
│   ├── Auto-detect: missing price_usd, unknown token_symbol, unclassified tx_type
│   ├── Side-by-side: raw API data vs parsed transaction
│   ├── "Fix all missing prices" bulk action
│   └── Before-you-file status checklist
│
└── Unsaved changes indicator
    ├── "You have N unsafe transactions" banner
    └── Auto-save draft to localStorage (crash recovery)
```

> **Why this matters:** No competitor lets users easily fix wrongly categorized transactions. This is the #1 complaint about Koinly/CoinTracker (Reddit confirms). Building a clean in-memory editor is a trust differentiator.

### Sprint 8 — More Accounting Methods (2-3 days)
```
Backend: /api/user/settings
├── Selected cost basis method: FIFO | LIFO | HIFO | AVG_COST
├── TaxEngine factory — instantiate calculator by method
└── Recalculate on method change (background job for large portfolios)

Frontend: /dashboard/settings
├── Radio/select for cost basis method
├── "Preview impact" — show what-if gain/loss with each method
└── Warning: changing method may affect previous filings
```

### Sprint 9 — Tax-Loss Harvesting (1 day)
```
/r eports/tax-loss-harvesting
├── Scan all holdings with unrealized losses
├── Rank by loss amount → "sell candidate" list
├── "Sell $X to offset $Y in gains" calculator
├── Wash sale rule check (30-day window, US only)
└── Export as PDF report
```

### Sprint 10 — DeFi Transaction Support (3-5 days)
```
Backend: /app/services/categoriser.py
├── Add DeFi protocol detection (Uniswap V2/V3, Aave, Curve, Balancer)
├── Liquidity pool: add liquidity → split into two token buys
├── Liquidity pool: remove → sell LP tokens for underlying assets
├── Lending: deposit → transfer_out; withdraw → transfer_in + interest
├── Yield farming: reward claims → airdrop/income tx type
└── Flash loans: detect + zero-out (no tax event)

Frontend: /dashboard/defi
├── Protocol breakdown (value per protocol)
├── DeFi transaction log with protocol icons
└── Unrecognized protocol → flag for user review
```

### Sprint 11 — PWA + Mobile (1 week)
```
/frontend/ (Next.js PWA)
├── next.config.js → PWA config (service worker, manifest)
├── Install prompt component ("Add to Home Screen")
├── Touch-friendly: larger tap targets, swipe gestures on tables
├── Pull-to-refresh on transaction/tax pages
├── Bottom navigation bar (mobile) vs sidebar (desktop)
└── Offline-capable: cached dashboard, pending edits in localStorage
```

### Sprint 12 — More Chains + Pricing Update (2 days)
```
New chains (EVM pattern, 1 day each):
├── Avalanche (C-chain) → snowtrace.io API
├── Fantom → ftmscan.com API
├── zkSync Era → explorers.zksync.io API
├── Cronos → cronoscan.com API

Pricing revision:
├── Free:    $0     — 1 wallet, ETH only, no exports
├── Starter: $49/yr — 3 wallets, 4 chains, CSV + IRS/HMRC/ATO
├── Pro:     $99/yr — unlimited wallets, 12 chains, all exports + ITR
└── Lifetime: $149 one-time (AppSumo launch)
```

---

## Strategic Moat (What Only TaxChain Does)

| Feature | Competitors | TaxChain |
|---|---|---|
| **India ITR Schedule VDA** | ❌ None | ✅ Built, pro-only |
| **Multi-fiat (INR, EUR, GBP, AUD, SGD, CAD, JPY)** | ❌ USD-only or 1-2 | ✅ 8 currencies |
| **Modern stack (FastAPI + Next.js)** | ❌ Legacy PHP/Ruby | ✅ Fast, cheap infra |
| **Dark void theme** | ❌ Boring TurboTax clones | ✅ Premium fintech feel |
| **In-memory ledger editing** | ❌ Read-only imports | ✅ Planned — edit before commit |

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| CoinGecko rate limits (30/min free) | Price lookups fail | 10k LRU cache + DB price table + manual price input |
| Etherscan API limits | Wallet sync stalls | Queue syncs, process overnight via APScheduler |
| India crypto tax rules change | ITR format outdated | Modular report generator, update via config |
| DeFi protocol changes | Categorizer breaks | Protocol-specific tests + "flag unknown" fallback |
| Users compare price vs Koinly | $19/mo looks expensive | Switch to annual $49–$99/yr pricing before launch |
