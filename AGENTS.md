# AGENTS.md — TaxChain
# Multi-wallet, Multi-chain Crypto Tax & P&L SaaS
# Runtime Constitution for OpenCode + DeepSeek V3.1
# Sensei: Claude | Builder: Ravi | Stack: Next.js + FastAPI + PostgreSQL

### 2026-04-22 15:45 - Phase 5: Payments & Deployment Completed
**Agent:** orchestrator
**Summary:** Completed Phase 5 - Payments, Landing Page & Deployment
- ✅ Backend payment service with Razorpay & Lemon Squeezy integration
- ✅ Backend payments router with order creation and subscription management
- ✅ Backend webhooks router for payment confirmation
- ✅ Frontend pricing page with Free/Starter/Pro tiers
- ✅ Frontend payment checkout components (UpgradeModal, PlanBadge)
- ✅ Marketing landing page with hero, features, pricing, FAQ sections
- ✅ Plan gates and upgrade prompts integrated in dashboard
- ✅ Production deployment configurations (Vercel, Render, Supabase)
- ✅ Comprehensive testing guide and automated test script
- ✅ Updated requirements.txt with payment dependencies

**Key Features Implemented:**
- Dual payment provider support (Razorpay for India, Lemon Squeezy for global)
- Plan-based feature gates with real-time validation
- Subscription management with automatic plan upgrades
- Webhook signature verification for security
- Responsive pricing page with FAQ section
- Professional landing page with conversion optimization
- Production-ready deployment configurations
- End-to-end payment flow testing

**Files Created:**
- backend/app/services/payment_service.py (comprehensive payment logic)
- backend/app/routers/payments.py (payment endpoints)
- backend/app/routers/webhooks.py (webhook handlers)
- frontend/app/pricing/page.tsx (pricing page)
- frontend/app/page.tsx (landing page)
- frontend/components/payments/UpgradeModal.tsx (upgrade modal)
- frontend/components/payments/PlanBadge.tsx (plan badge component)
- DEPLOYMENT.md (deployment guide)
- TESTING.md (testing guide)
- test_payment_flow.py (automated test script)
- vercel.json, render.yaml (deployment configs)

**Next Steps:**
1. Set up Razorpay and Lemon Squeezy accounts
2. Configure payment provider plans and webhooks
3. Deploy to production (Vercel + Render + Supabase)
4. Run end-to-end tests in production environment
5. Monitor payment flows and optimize conversion

---

### 2026-04-16 14:30 - Phase 4: Tax & Export Completed
**Agent:** orchestrator
**Summary:** Completed Phase 4 - Tax & Export functionality
- ✅ Backend reports router fully functional with CSV, PDF, and ITR exports
- ✅ PDF report generation using ReportLab with professional formatting
- ✅ India ITR Schedule VDA export format (Pro-only feature)
- ✅ Frontend tax summary page with financial year selector
- ✅ Frontend reports page with export functionality and plan gates
- ✅ Created wallets and transactions pages for complete navigation
- ✅ Updated dashboard layout with proper navigation links
- ✅ Added missing dependencies (aiosqlite, slowapi) to requirements.txt
- ✅ All export functionality tested and verified

**Key Features Implemented:**
- Tax summary with total gain/loss, short-term/long-term breakdown
- Token-level breakdown with transaction counts
- CSV export with comprehensive transaction data
- PDF export with professional formatting and methodology explanation
- ITR Schedule VDA export for Indian tax filing (Pro only)
- Plan-based feature gates (Free/Starter/Pro)
- Financial year selector with 5-year history
- Responsive design with proper error handling

---

### 2026-04-12 02:30 - Wallet Management System Completed
**Agent:** orchestrator
**Summary:** Completed Phase 3 frontend wallet management implementation
- Enhanced WalletList component with real-time sync status and loading states
- Improved AddWalletModal with client-side validation and blockchain-specific error handling
- Added visual feedback for sync operations and form validation
- Backend validation and plan limit enforcement already fully functional

---

## 0. READ THIS FIRST — AGENT PRIME DIRECTIVE

You are building TaxChain: a production-grade crypto tax and portfolio P&L SaaS.
This is a FINANCIAL product. Users trust it with their wallet data and tax calculations.
Every decision — code, UI, UX, copy — must reinforce TRUST, ACCURACY, and CLARITY.

When in doubt, ask: "Would a stressed crypto holder trust this with their taxes?"
If no → rebuild it.
If yes → ship it.

---

## 1. PROJECT OVERVIEW

**Product:** TaxChain
**Category:** Fintech / Crypto Tax SaaS
**Target Users:** Retail crypto holders globally, with a strong India-first angle
**Core Pain:** Calculating capital gains, cost basis, and generating tax reports across multiple wallets and chains is a nightmare. No affordable tool does it cleanly for non-US markets.
**Monetisation:** Monthly SaaS subscription via Razorpay (India) + Lemon Squeezy (global)
**Distribution:** Direct landing page → Gumroad/AppSumo for lifetime deal later
**India Angle:** ITR Schedule VDA export is a unique differentiator — no competitor does this cleanly

---

## 2. TECH STACK — NON-NEGOTIABLE

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (NOT SQLite — financial multi-user data requires it)
- **ORM:** SQLAlchemy with Alembic for migrations
- **Background Jobs:** APScheduler (wallet sync, price fetching)
- **Auth:** JWT tokens (python-jose), bcrypt for passwords
- **Environment:** python-dotenv, pydantic-settings

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **UI Components:** shadcn/ui
- **Styling:** Tailwind CSS
- **Charts:** Recharts (P&L graphs, portfolio breakdown)
- **Tables:** TanStack Table (transaction history — must handle 1000s of rows)
- **State:** Zustand for global state, React Query for server state
- **Forms:** React Hook Form + Zod validation

### External APIs (all free tier at launch)
- **Etherscan API** — ETH transaction history (free, 5 req/sec)
- **BscScan API** — BNB Chain transactions (free)
- **PolygonScan API** — Polygon transactions (free)
- **Solscan API** — Solana transactions (free tier)
- **CoinGecko API** — Historical + current prices (free, 30 calls/min)
- **No paid APIs until 500+ active users**

### Infrastructure
- **Backend:** Render (free tier → $7/month when ready)
- **Frontend:** Vercel (free tier)
- **Database:** Supabase PostgreSQL (free tier = 500MB, enough for launch)
- **File Storage:** Supabase Storage (for exported PDF/CSV reports)

### Payments
- **India:** Razorpay subscriptions
- **Global:** Lemon Squeezy (merchant of record — no Stripe approval needed)

---

## 3. REPOSITORY STRUCTURE

```
taxchain/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Settings via pydantic-settings
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── wallet.py
│   │   │   ├── transaction.py
│   │   │   └── subscription.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── wallets.py
│   │   │   ├── transactions.py
│   │   │   ├── reports.py
│   │   │   └── webhooks.py          # Razorpay + Lemon Squeezy
│   │   ├── services/
│   │   │   ├── chain_sync.py        # Fetches tx from Etherscan etc.
│   │   │   ├── price_engine.py      # CoinGecko historical prices
│   │   │   ├── tax_engine.py        # FIFO cost basis calculator — CORE
│   │   │   ├── report_generator.py  # CSV + PDF export
│   │   │   └── categoriser.py       # trade/transfer/staking/airdrop
│   │   └── utils/
│   │       ├── auth.py              # JWT helpers
│   │       └── rate_limiter.py      # API call throttling
│   ├── alembic/                     # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx             # Portfolio overview
│   │   │   ├── wallets/page.tsx     # Wallet management
│   │   │   ├── transactions/page.tsx
│   │   │   ├── tax/page.tsx         # Tax summary + year selector
│   │   │   └── reports/page.tsx     # Export centre
│   │   ├── (marketing)/
│   │   │   ├── page.tsx             # Landing page
│   │   │   └── pricing/page.tsx
│   │   └── api/                     # Next.js API routes (webhooks only)
│   ├── components/
│   │   ├── ui/                      # shadcn components
│   │   ├── dashboard/
│   │   │   ├── PortfolioCard.tsx
│   │   │   ├── PnlChart.tsx
│   │   │   ├── TransactionTable.tsx
│   │   │   ├── ChainBadge.tsx
│   │   │   └── TaxSummaryCard.tsx
│   │   ├── wallets/
│   │   │   └── AddWalletModal.tsx
│   │   └── reports/
│   │       └── ExportPanel.tsx
│   ├── lib/
│   │   ├── api.ts                   # Axios instance + interceptors
│   │   └── utils.ts
│   ├── store/
│   │   └── useAppStore.ts           # Zustand store
│   └── types/
│       └── index.ts                 # Shared TypeScript types
│
├── AGENTS.md                        # This file
└── docker-compose.yml               # Local dev (postgres)
```

---

## 4. DATABASE SCHEMA — BUILD THIS FIRST

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',        -- free | starter | pro
    country VARCHAR(10) DEFAULT 'IN',
    financial_year_start VARCHAR(5) DEFAULT '04-01', -- India: Apr 1
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Wallets (read-only addresses — NEVER store private keys)
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    address VARCHAR(255) NOT NULL,
    chain VARCHAR(20) NOT NULL,             -- eth | bnb | polygon | sol
    label VARCHAR(100),
    last_synced_at TIMESTAMP,
    tx_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Raw transactions from chain
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID REFERENCES wallets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tx_hash VARCHAR(255) NOT NULL,
    chain VARCHAR(20) NOT NULL,
    tx_type VARCHAR(30) NOT NULL,           -- trade | transfer_in | transfer_out | staking | airdrop | nft_sale | fee
    token_symbol VARCHAR(50),
    token_address VARCHAR(255),
    quantity DECIMAL(36, 18) NOT NULL,      -- 18 decimals for crypto
    price_usd DECIMAL(20, 8),              -- price at time of tx
    value_usd DECIMAL(20, 8),              -- quantity * price
    fee_usd DECIMAL(20, 8),
    timestamp TIMESTAMP NOT NULL,
    raw_data JSONB,                         -- full API response for audit
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tx_hash, chain)
);

-- Computed cost basis per token per user (FIFO)
CREATE TABLE cost_basis_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_symbol VARCHAR(50) NOT NULL,
    chain VARCHAR(20) NOT NULL,
    quantity_remaining DECIMAL(36, 18) NOT NULL,
    cost_per_unit_usd DECIMAL(20, 8) NOT NULL,
    acquired_at TIMESTAMP NOT NULL,
    source_tx_id UUID REFERENCES transactions(id)
);

-- Tax events (realised gains/losses)
CREATE TABLE tax_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_symbol VARCHAR(50) NOT NULL,
    quantity DECIMAL(36, 18) NOT NULL,
    proceeds_usd DECIMAL(20, 8) NOT NULL,
    cost_basis_usd DECIMAL(20, 8) NOT NULL,
    gain_loss_usd DECIMAL(20, 8) NOT NULL,  -- proceeds - cost_basis
    is_short_term BOOLEAN,                   -- holding < 1 year
    sale_tx_id UUID REFERENCES transactions(id),
    acquired_at TIMESTAMP,
    disposed_at TIMESTAMP NOT NULL,
    financial_year VARCHAR(10)               -- e.g. "2024-25"
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,          -- razorpay | lemonsqueezy
    provider_sub_id VARCHAR(255),
    plan VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,            -- active | cancelled | expired
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. CORE ENGINE — TAX CALCULATOR (FIFO)

This is the most critical service. Get this right before anything else.

```python
# backend/app/services/tax_engine.py

"""
FIFO Cost Basis Calculator
Rules:
- First In First Out (FIFO) — default for most jurisdictions
- Each buy creates a "lot" with quantity + cost per unit
- Each sell consumes oldest lots first
- Gain/Loss = proceeds - cost_basis
- Short-term: held < 365 days
- India-specific: 30% flat tax on all crypto gains (no short/long distinction)
"""

from decimal import Decimal
from datetime import datetime
from collections import deque
from typing import List
from app.models.transaction import Transaction
from app.models.tax_event import TaxEvent

def calculate_fifo(
    user_id: str,
    token_symbol: str,
    transactions: List[Transaction]
) -> List[TaxEvent]:
    """
    Process transactions chronologically.
    Buys → add to lot queue.
    Sells → consume from front of queue, calculate gain/loss.
    """
    lots = deque()  # (quantity, cost_per_unit, acquired_at)
    tax_events = []

    for tx in sorted(transactions, key=lambda t: t.timestamp):
        if tx.tx_type in ('transfer_in', 'airdrop', 'staking'):
            # Treat as buy at market price
            lots.append({
                'quantity': tx.quantity,
                'cost_per_unit': tx.price_usd or Decimal('0'),
                'acquired_at': tx.timestamp
            })

        elif tx.tx_type in ('transfer_out', 'trade'):
            quantity_to_sell = tx.quantity
            proceeds_per_unit = tx.price_usd or Decimal('0')
            total_cost_basis = Decimal('0')
            total_proceeds = quantity_to_sell * proceeds_per_unit

            while quantity_to_sell > 0 and lots:
                lot = lots[0]
                if lot['quantity'] <= quantity_to_sell:
                    # Consume entire lot
                    total_cost_basis += lot['quantity'] * lot['cost_per_unit']
                    quantity_to_sell -= lot['quantity']
                    lots.popleft()
                else:
                    # Partial lot
                    total_cost_basis += quantity_to_sell * lot['cost_per_unit']
                    lot['quantity'] -= quantity_to_sell
                    quantity_to_sell = Decimal('0')

            tax_events.append(TaxEvent(
                user_id=user_id,
                token_symbol=token_symbol,
                quantity=tx.quantity,
                proceeds_usd=total_proceeds,
                cost_basis_usd=total_cost_basis,
                gain_loss_usd=total_proceeds - total_cost_basis,
                is_short_term=(tx.timestamp - lots[0]['acquired_at']).days < 365 if lots else True,
                disposed_at=tx.timestamp,
                sale_tx_id=tx.id
            ))

    return tax_events
```

**Agent rule:** Never modify FIFO logic without writing a test first. Tax calculation bugs = user trust destroyed permanently.

---

## 6. API INTEGRATION LAYER

### Etherscan (ETH, and pattern for BscScan/PolygonScan)

```python
# backend/app/services/chain_sync.py

import httpx
import asyncio
from app.config import settings

CHAIN_CONFIGS = {
    'eth': {
        'base_url': 'https://api.etherscan.io/api',
        'api_key': settings.ETHERSCAN_API_KEY,
    },
    'bnb': {
        'base_url': 'https://api.bscscan.com/api',
        'api_key': settings.BSCSCAN_API_KEY,
    },
    'polygon': {
        'base_url': 'https://api.polygonscan.com/api',
        'api_key': settings.POLYGONSCAN_API_KEY,
    }
}

async def fetch_transactions(address: str, chain: str) -> list:
    config = CHAIN_CONFIGS[chain]
    async with httpx.AsyncClient() as client:
        # Normal transactions
        resp = await client.get(config['base_url'], params={
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'asc',
            'apikey': config['api_key']
        })
        txs = resp.json().get('result', [])

        # ERC-20 token transfers
        resp2 = await client.get(config['base_url'], params={
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'sort': 'asc',
            'apikey': config['api_key']
        })
        token_txs = resp2.json().get('result', [])

        await asyncio.sleep(0.2)  # Rate limit: 5 req/sec
        return txs + token_txs
```

### CoinGecko Price Lookup

```python
# backend/app/services/price_engine.py

import httpx
from datetime import datetime
from functools import lru_cache

COINGECKO_IDS = {
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'MATIC': 'matic-network',
    'SOL': 'solana',
    'BTC': 'bitcoin',
    'USDT': 'tether',
    'USDC': 'usd-coin',
}

@lru_cache(maxsize=10000)  # Cache price lookups aggressively
async def get_historical_price(token_symbol: str, date: datetime) -> float:
    coin_id = COINGECKO_IDS.get(token_symbol.upper())
    if not coin_id:
        return 0.0  # Unknown token — return 0, flag for user review

    date_str = date.strftime('%d-%m-%Y')  # CoinGecko format
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/history'

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={'date': date_str, 'localization': 'false'})
        data = resp.json()
        return data.get('market_data', {}).get('current_price', {}).get('usd', 0.0)
```

---

## 7. API ENDPOINTS

### Auth
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
```

### Wallets
```
GET    /api/wallets              # List user's wallets
POST   /api/wallets              # Add wallet (address + chain)
DELETE /api/wallets/{id}         # Remove wallet
POST   /api/wallets/{id}/sync    # Trigger manual sync
GET    /api/wallets/{id}/status  # Sync status + tx count
```

### Transactions
```
GET /api/transactions            # Paginated list (filter by chain, type, date)
GET /api/transactions/summary    # Aggregated stats
```

### Tax & Reports
```
GET  /api/tax/summary            # Total gains/losses by financial year
GET  /api/tax/events             # All tax events (paginated)
POST /api/reports/csv            # Generate + return CSV download URL
POST /api/reports/pdf            # Generate + return PDF download URL
POST /api/reports/itr            # India-specific ITR Schedule VDA format
```

### Payments
```
POST /api/payments/create-order   # Razorpay order
POST /api/webhooks/razorpay       # Payment confirmation
POST /api/webhooks/lemonsqueezy   # Global payment confirmation
```

---

## 8. FRONTEND DESIGN CONSTITUTION — TAXCHAIN

**Tone:** Trusted fintech. Clean, calm, data-dense. Not cold — warm but professional.
**Reference:** Notion meets Zerion. Dark sidebar, white content area.
**NOT:** Brutalist, playful, maximalist. This is a tax product.

### Color System

```css
:root {
  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8F9FA;
  --bg-sidebar: #0F172A;       /* Dark navy sidebar */
  --bg-card: #FFFFFF;

  /* Text */
  --text-primary: #0F172A;
  --text-secondary: #64748B;
  --text-muted: #94A3B8;
  --text-sidebar: #E2E8F0;

  /* Brand */
  --brand: #6366F1;            /* Indigo — trust, technology */
  --brand-light: #EEF2FF;

  /* Financial */
  --gain: #10B981;             /* Green — profit */
  --gain-bg: #ECFDF5;
  --loss: #EF4444;             /* Red — loss */
  --loss-bg: #FEF2F2;
  --neutral: #64748B;

  /* Chains */
  --eth: #627EEA;
  --bnb: #F3BA2F;
  --polygon: #8247E5;
  --sol: #9945FF;

  /* Borders */
  --border: #E2E8F0;
  --border-strong: #CBD5E1;
}
```

### Typography

```css
/* Import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --font-ui: 'Plus Jakarta Sans', sans-serif;     /* All UI text */
  --font-data: 'JetBrains Mono', monospace;       /* Numbers, addresses, hashes */
}

/* Scale */
.text-display   { font-size: 36px; font-weight: 700; }
.text-heading   { font-size: 24px; font-weight: 600; }
.text-subhead   { font-size: 18px; font-weight: 600; }
.text-body      { font-size: 14px; font-weight: 400; line-height: 1.6; }
.text-small     { font-size: 12px; font-weight: 500; }
.text-mono      { font-family: var(--font-data); font-size: 13px; }
```

### Component Rules

**Wallet address display:**
Always truncate: `0x1234...5678`. Full address on hover/copy. Monospace font always.

**P&L values:**
Green + up arrow for gains. Red + down arrow for losses. Monospace. Never hide the sign.

**Numbers:**
Always use `toLocaleString()` with 2 decimal places for USD. Crypto amounts: up to 8 decimal places.

**Chain badges:**
Small colored dot + chain name. Use `--eth`, `--bnb`, `--polygon`, `--sol` colors.

**Tables:**
Striped rows (#F8F9FA alternate). Sticky header. Sortable columns. Pagination at 50 rows.
Never truncate amounts in tables — horizontal scroll if needed.

**Cards:**
`border: 1px solid var(--border)`, `border-radius: 12px`, `padding: 24px`.
Subtle shadow: `box-shadow: 0 1px 3px rgba(0,0,0,0.06)`.

**Buttons:**
Primary: `background: var(--brand)`, white text, `border-radius: 8px`.
Danger: `background: var(--loss)`.
No brutalist styling. No 0px border-radius. Trust-first always.

**Loading states:**
Skeleton loaders (not spinners) for data tables. Pulse animation acceptable.

### Layout

```
┌─────────────────────────────────────────────────┐
│  SIDEBAR (240px, dark navy)                      │
│  ┌─────────────────────────────────────────────┐ │
│  │ TaxChain logo                               │ │
│  │ ─────────                                   │ │
│  │ Dashboard                                   │ │
│  │ Wallets                                     │ │
│  │ Transactions                                │ │
│  │ Tax Report                                  │ │
│  │ Export                                      │ │
│  │ ─────────                                   │ │
│  │ Settings                                    │ │
│  │ [Plan badge]                                │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  MAIN CONTENT (flex-1, white)                     │
│  ┌─────────────────────────────────────────────┐ │
│  │ Top bar: Page title + Year selector + Export│ │
│  │ ─────────────────────────────────────────── │ │
│  │ Content area                                │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 9. PLAN LIMITS & FEATURE GATES

```python
PLAN_LIMITS = {
    'free': {
        'wallets': 1,
        'chains': ['eth'],
        'tx_history_years': 1,
        'export_csv': False,
        'export_pdf': False,
        'export_itr': False,
    },
    'starter': {
        'wallets': 3,
        'chains': ['eth', 'bnb', 'polygon'],
        'tx_history_years': 3,
        'export_csv': True,
        'export_pdf': False,
        'export_itr': False,
    },
    'pro': {
        'wallets': 999,
        'chains': ['eth', 'bnb', 'polygon', 'sol'],
        'tx_history_years': 10,
        'export_csv': True,
        'export_pdf': True,
        'export_itr': True,      # India ITR VDA — PRO ONLY
    }
}
```

Free tier converts when users see their P&L but hit the export paywall.
That is the designed conversion moment. Build it deliberately — show the numbers, blur/lock the export button.

---

## 10. MVP BUILD ORDER — FOLLOW THIS EXACTLY

### Phase 1 — Core Engine (Days 1–5)
- [ ] PostgreSQL schema + Alembic migrations
- [ ] Etherscan API wrapper (ETH only)
- [ ] CoinGecko price lookup with caching
- [ ] Transaction categoriser (trade/transfer/staking)
- [ ] FIFO tax calculator
- [ ] Unit tests for tax calculator (minimum 10 test cases)

### Phase 2 — Backend API (Days 6–10)
- [ ] FastAPI app structure
- [ ] Auth endpoints (register/login/JWT)
- [ ] Wallet CRUD endpoints
- [ ] Transaction sync endpoint + APScheduler job
- [ ] Tax summary endpoint
- [ ] CSV export endpoint

### Phase 3 — Frontend Dashboard (Days 11–17)
- [ ] Next.js setup + shadcn/ui + Tailwind
- [ ] Auth pages (login/signup)
- [ ] Dashboard layout (sidebar + main)
- [ ] Portfolio overview card (total value, total gain/loss)
- [ ] P&L chart (Recharts — 30d/90d/1y/all)
- [ ] Transaction table (TanStack Table, paginated)
- [ ] Add wallet modal + sync status

### Phase 4 — Tax & Export (Days 18–21)
- [ ] Tax summary page (by financial year, by token)
- [ ] CSV download
- [ ] PDF report (use ReportLab on backend)
- [ ] India ITR VDA format (pro only)

### Phase 5 — Payments & Launch (Days 22–25)
- [ ] Razorpay subscription integration
- [ ] Lemon Squeezy integration
- [ ] Plan gates in frontend (show, don't hide — blur + upgrade prompt)
- [ ] Landing page + pricing page
- [ ] Deploy: Vercel + Render + Supabase

---

## 11. AGENT TASK ASSIGNMENTS

When using Ghost Agency agents, assign as follows:

| Task | Agent |
|---|---|
| Backend API, DB schema, chain integrations | Build squad |
| FIFO calculator, price engine | Build squad — flag for QA review |
| Frontend components, dashboard UI | Build squad with TAXCHAIN frontend constitution |
| Landing page, pricing page | Build squad + Copywriter agent |
| CSV/PDF report formatting | Build squad |
| Test cases for tax calculator | QA agent |
| API rate limit handling, error recovery | Build squad |
| Razorpay/Lemon Squeezy webhooks | Build squad |
| SEO meta tags, structured data | SEO agent |

---

## 12. AGENT RULES — ALWAYS / ASK / NEVER

### ✅ ALWAYS DO
- Use `Decimal` not `float` for all financial calculations — float precision errors in money = catastrophe
- Validate wallet addresses before accepting them (regex per chain)
- Store raw API responses in `raw_data JSONB` — always keep audit trail
- Rate-limit all external API calls (Etherscan: 200ms delay, CoinGecko: 2s delay)
- Return paginated responses for any list endpoint (default 50, max 200)
- Write the backend first, frontend second, always
- Cache price lookups — CoinGecko rate limits will kill you otherwise
- Show P&L in user's local currency equivalent AND USD

### ⚠️ ASK BEFORE
- Adding a new blockchain (new chain = new API integration = new test suite needed)
- Changing the FIFO calculation method
- Modifying the database schema after Phase 1 is complete
- Adding any paid external API
- Changing the subscription plan limits

### 🚫 NEVER DO
- Store private keys or seed phrases — EVER, under any circumstance
- Use `float` for financial calculations — use `Decimal` always
- Skip input validation on wallet addresses
- Make synchronous external API calls in request handlers — use background jobs
- Expose raw database errors to the frontend
- Delete transaction history without explicit user confirmation
- Hardcode API keys — always use environment variables
- Round crypto amounts before calculation — only round for display

---

## 13. ENVIRONMENT VARIABLES

```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@host:5432/taxchain
SECRET_KEY=your-jwt-secret-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Chain APIs
ETHERSCAN_API_KEY=
BSCSCAN_API_KEY=
POLYGONSCAN_API_KEY=
SOLSCAN_API_KEY=

# Payments
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
LEMONSQUEEZY_API_KEY=
LEMONSQUEEZY_WEBHOOK_SECRET=

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=
NEXT_PUBLIC_LEMONSQUEEZY_STORE_ID=
```

---

## 14. KNOWN RISKS & MITIGATIONS

| Risk | Mitigation |
|---|---|
| CoinGecko rate limits (30/min free) | Cache aggressively with lru_cache + DB price cache table |
| Etherscan API limits | Queue wallet syncs, process overnight via APScheduler |
| Wrong FIFO calculation | 10+ unit tests before Phase 2. QA agent review mandatory |
| Token not in CoinGecko | Flag as "price unknown", show quantity, let user input price manually |
| User connects exchange wallet (1000s of txs) | Background job, progress indicator, email when done |
| PostgreSQL costs | Supabase free tier = 500MB, enough for 1000+ users at launch |

---

## 15. LAUNCH CHECKLIST

- [ ] Tax calculator passes all test cases
- [ ] Wallet addresses never stored with private keys
- [ ] Privacy policy mentions read-only wallet access
- [ ] Rate limiting on all auth endpoints (prevent brute force)
- [ ] CORS configured for production domain only
- [ ] All API keys in environment variables, not in code
- [ ] CSV export works end-to-end
- [ ] Razorpay test mode → live mode switch tested
- [ ] Free tier limits enforced on backend (not just frontend)
- [ ] Landing page live with pricing
- [ ] Error monitoring (Sentry free tier)

---

## 16. PRICING — FINAL

| Plan | Price | Limits |
|---|---|---|
| Free | $0 | 1 wallet, ETH only, current FY, no export |
| Starter | $9/month | 3 wallets, 3 chains, 3 years history, CSV export |
| Pro | $19/month | Unlimited wallets, all chains, full history, CSV + PDF + ITR export |
| Lifetime (AppSumo later) | $79 once | Pro features, limited quantity |

---

*This file is the single source of truth for TaxChain.*
*All agents read this before any task. No exceptions.*
*When instructions conflict, this file wins.*

— Sensei approved. Build brutal. Ship clean.
