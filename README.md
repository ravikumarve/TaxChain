<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/TaxChain-FinTech-6366F1?style=for-the-badge&logo=bitcoin&logoColor=white&labelColor=0F172A">
    <img alt="TaxChain" src="https://img.shields.io/badge/TaxChain-FinTech-6366F1?style=for-the-badge&logo=bitcoin&logoColor=white">
  </picture>
</p>

<p align="center">
  <strong>Multi-wallet, Multi-chain Crypto Tax & Portfolio P&L SaaS</strong><br>
  <em>Production-grade • 4 Cost Basis Methods • 8 Blockchains • DeFi Support • Global Tax Formats</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/github/v/release/ravikumarve/TaxChain?style=flat&label=version&color=6366F1" alt="Version"></a>
  <a href="#"><img src="https://img.shields.io/github/license/ravikumarve/TaxChain?style=flat&color=10B981" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.12+-2563EB?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/next.js-14-000000?style=flat&logo=next.js" alt="Next.js"></a>
  <a href="#"><img src="https://img.shields.io/badge/fastapi-0.104-009688?style=flat&logo=fastapi" alt="FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/status-production_ready-10B981?style=flat" alt="Status"></a>
</p>

---

## 📋 Overview

**TaxChain** calculates capital gains, cost basis, and generates professional tax reports across 8 blockchains. Supports portfolio tracking, DeFi positions, manual transaction editing, and 4 accounting methods. Built with financial-grade precision — `Decimal` everywhere, FIFO/LIFO/HIFO/Average Cost, full audit trail.

### What makes it different?
- **4 accounting methods** — FIFO, LIFO, HIFO, and Average Cost (switch anytime)
- **Portfolio dashboard** — Real-time P&L, allocation charts, top movers
- **In-memory ledger** — Manual transaction editor with CSV import & error reconciliation
- **Tax-loss harvesting** — Wash sale detection, loss optimization recommendations
- **DeFi support** — LP positions, lending, yield farming (Uniswap, AAVE, Curve)
- **India-first** — ITR Schedule VDA export (unique differentiator)
- **8 chains** — ETH, BNB, Polygon, Arbitrum, Optimism, Base, Solana, Bitcoin
- **Global tax formats** — US IRS 8949, UK HMRC, Australia ATO, India ITR VDA
- **Multi-currency** — USD, INR, EUR, GBP, AUD, SGD, CAD, JPY
- **No private keys ever** — Read-only wallet access

---

## 🗺️ Development Status

| Phase | Status | What's Included |
|-------|--------|----------------|
| **Phase 1 — Core Engine** | ✅ Complete | PostgreSQL schema, ORM models, FIFO tax calculator, 16+ test files |
| **Phase 2 — Backend API** | ✅ Complete | Auth, wallets, transactions, tax summary, CSV/PDF/ITR reports |
| **Phase 3 — Frontend** | ✅ Complete (v2) | Dark void theme, dashboard, wallet mgmt, tax/export/pricing/landing pages |
| **Phase 4 — Tax & Export** | ✅ Complete | CSV, PDF, ITR VDA, IRS 8949, HMRC, ATO, FIFO cost basis lot persistence |
| **Phase 5 — Payments** | ✅ Complete | Razorpay (India) + Lemon Squeezy (global), plan gates, webhooks |
| **Tier 1-3 — Hardening** | ✅ Complete | DB pooling, rate limiting, background jobs, structured logging, Sentry |
| **Sprint 6 — Portfolio Dashboard** | ✅ Complete | P&L tracking, allocation charts (chain/token), Recharts area chart, top movers |
| **Sprint 7 — In-Memory Ledger** | ✅ Complete | Manual tx CRUD, CSV import with preview, error reconciliation |
| **Sprint 8 — Accounting Methods** | ✅ Complete | FIFO, LIFO, HIFO, Average Cost — user-selectable with full recalc |
| **Sprint 9 — Tax-Loss Harvesting** | ✅ Complete | Wash sale detection (30-day rule), realized loss analysis, recommendations |
| **Sprint 10 — DeFi Support** | ✅ Complete | LP positions, lending/borrow, yield farm tracking, 6 new tx types |

---

## 🔗 Supported Blockchains

| Chain | Type | API | Native Token | Plan Access |
|-------|------|-----|-------------|-------------|
| **Ethereum** | EVM L1 | Etherscan | ETH | Free+ |
| **BNB Chain** | EVM L1 | BscScan | BNB | Starter+ |
| **Polygon** | EVM L1 | PolygonScan | MATIC | Starter+ |
| **Arbitrum** | EVM L2 | Arbiscan | ETH | Starter+ |
| **Optimism** | EVM L2 | Optimistic Etherscan | ETH | Pro |
| **Base** | EVM L2 | BaseScan | ETH | Pro |
| **Solana** | Non-EVM | Solscan | SOL | Pro |
| **Bitcoin** | UTXO | Blockstream | BTC | Pro |

---

## 📊 Accounting Methods

| Method | Description | Best For |
|--------|------------|----------|
| **FIFO** (Default) | First In, First Out — Oldest lots sold first | Most jurisdictions (US, UK, AU) |
| **LIFO** | Last In, First Out — Newest lots sold first | Higher cost basis → lower gains |
| **HIFO** | Highest Cost, First Out — Highest-cost lots sold first | Minimizing taxable gains |
| **Avg Cost** | Average Cost — Smooths cost across all lots | Simplicity (not accepted in all jurisdictions) |

Users can switch methods anytime via Settings. All 6 export formats respect the selected method.

---

## 📄 Tax Report Formats

| Format | Jurisdiction | Plan | Description |
|--------|-------------|------|-------------|
| **CSV** | Universal | Starter+ | Full transaction breakdown with gain/loss per event |
| **PDF** | Universal | Pro | Professional formatted report with methodology |
| **ITR Schedule VDA** | 🇮🇳 India | Pro | Official Indian tax filing format |
| **IRS Form 8949** | 🇺🇸 US | Starter+ | Short-term / long-term capital gains breakdown |
| **HMRC CGT** | 🇬🇧 UK | Starter+ | Capital gains in GBP with UK tax year (Apr 6–Apr 5) |
| **ATO Crypto** | 🇦🇺 Australia | Starter+ | Capital gains in AUD with CGT discount eligibility |

---

## 🧮 DeFi Transaction Types

| Type | Description | Tax Treatment |
|------|------------|---------------|
| `trade` | Token swap on DEX | Taxable (gain/loss realized) |
| `lp_deposit` | Liquidity pool deposit | Not taxable (trade for LP tokens) |
| `lp_withdraw` | Liquidity pool withdrawal | Taxable (LP tokens → underlying) |
| `borrow` | Borrowing assets (e.g. AAVE) | Not taxable (debt, not income) |
| `repay` | Repaying borrowed assets | Not taxable |
| `yield_farm` | Yield farming / vault deposit | Not taxable on deposit |
| `liquidation` | Liquidation event | Taxable |
| `staking` | Staking rewards | Taxable as income at FMV |
| `airdrop` | Free token distribution | Taxable as income at FMV |

**Supported Protocols:** Uniswap V2/V3, AAVE V2/V3, Compound, Curve, Lido, PancakeSwap, QuickSwap, Camelot, Velodrome, Aerodrome

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     TaxChain Backend (FastAPI)                         │
├──────────────┬──────────────┬───────────────┬───────────────────────┤
│  Auth        │  Wallets     │  Transactions │  Reports              │
│  /api/auth   │  /api/wallets│  /api/txs     │  /api/reports         │
├──────────────┼──────────────┼───────────────┼───────────────────────┤
│  Payments    │  Webhooks    │  Settings     │  Tax Loss Harvesting  │
│  /api/payments│  /api/wh    │  /api/settings│  /api/reports/tax-loss│
├──────────────┴──────────────┴───────────────┴───────────────────────┤
│  Core Services:                                                      │
│  ├── Tax Engine ─── 4 calculators: FIFO / LIFO / HIFO / Avg Cost    │
│  ├── DeFi Categorizer ─── Uniswap, AAVE, Curve, Lido protocol detection
│  ├── DeFi Position Tracker ─── LP, lending, yield farm aggregation   │
│  ├── Chain Sync ─── Etherscan/BscScan/PolygonScan/Arbiscan/etc.     │
│  ├── Price Engine ─── CoinGecko (cached, 10k entries)               │
│  └── Exchange Rate ─── open.er-api.com (live FX, 8 currencies)      │
├──────────────────────────────────────────────────────────────────────┤
│  Database: PostgreSQL / SQLite (SQLAlchemy 2.0 + Alembic migrations) │
│  └── 6 tables: users, wallets, transactions, cost_basis_lots,        │
│                tax_events, subscriptions                              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# Backend
cd backend
cp .env.example .env        # Edit with your API keys
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python create_tables.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# Frontend (separate terminal)
cd frontend
cp .env.example .env.local  # Edit NEXT_PUBLIC_API_URL if needed
npm install
npm run dev
```

---

## 💰 Pricing

| Plan | Price | Wallets | Chains | Exports | DeFi |
|------|-------|---------|--------|---------|------|
| **Free** | $0 | 1 | ETH | ❌ | ❌ |
| **Starter** | $9/mo (₹749) | 3 | ETH, BNB, Polygon, Arbitrum | CSV, IRS, HMRC, ATO | ❌ |
| **Pro** | $19/mo (₹1,599) | Unlimited | All 8 chains | All formats + ITR VDA | ✅ Full DeFi |

---

## 🛡️ Security

- **Read-only wallet access** — private keys never stored
- **JWT + bcrypt** — authenticated API with refresh tokens
- **Rate limited** — brute-force protection on auth (5/min), per-endpoint limits
- **Webhook signed** — HMAC-SHA256 verification for both payment providers
- **Input validated** — regex wallet validation per chain, XSS sanitization
- **SQL injection protected** — SQLAlchemy parameterized queries throughout

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic |
| **Frontend** | Next.js 14 (App Router), Tailwind CSS, Recharts, Axios |
| **Database** | PostgreSQL 15+ (production), SQLite (dev) |
| **Sync** | APScheduler (auto-sync every 6h) |
| **Accounting** | FIFO / LIFO / HIFO / Average Cost calculators |
| **Payments** | Razorpay (IN) + Lemon Squeezy (global) |
| **Prices** | CoinGecko (cached, 10k entries) |
| **FX Rates** | open.er-api.com (live, with fallback, 8 currencies) |
| **DeFi Protocols** | Uniswap V2/V3, AAVE, Compound, Curve, Lido, PancakeSwap, QuickSwap, Camelot, Velodrome, Aerodrome |
| **Monitoring** | Sentry, structured logging, request ID tracing |
| **Infra** | Render (API) + Vercel (frontend) + Supabase (DB) |

---

## 📫 Stay Updated

<p align="center">
  <a href="https://github.com/ravikumarve/TaxChain">GitHub</a> •
  <a href="https://github.com/ravikumarve/TaxChain/issues">Issues</a> •
  <a href="https://github.com/ravikumarve/TaxChain/discussions">Discussions</a>
</p>

<p align="center">
  <sub>Built by <a href="https://github.com/ravikumarve">Ravi</a> — crypto tax compliance, done right.</sub>
</p>

<p align="center">
  <a href="https://github.com/ravikumarve/TaxChain/stargazers">
    <img src="https://img.shields.io/github/stars/ravikumarve/TaxChain?style=social" alt="Stars">
  </a>
</p>
