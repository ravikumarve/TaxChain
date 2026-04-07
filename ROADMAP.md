# TaxChain Implementation Roadmap

## Project Overview

**Product:** TaxChain — Multi-wallet, Multi-chain Crypto Tax & P&L SaaS
**Timeline:** 25-day MVP development cycle
**Strategy:** India-first crypto tax solution with global expansion capabilities
**Target Users:** Retail crypto holders globally, with strong India market focus
**Core Differentiation:** ITR Schedule VDA export for Indian tax compliance

## Phase-by-Phase Implementation

### Phase 1 — Core Engine (Days 1–5)
```markdown
- [ ] PostgreSQL schema + Alembic migrations
- [ ] Etherscan API wrapper (ETH only)
- [ ] CoinGecko price lookup with caching
- [ ] Transaction categorizer (trade/transfer/staking)
- [ ] FIFO tax calculator
- [ ] Unit tests for tax calculator (minimum 10 test cases)
```

### Phase 2 — Backend API (Days 6–10)
```markdown
- [ ] FastAPI app structure
- [ ] Auth endpoints (register/login/JWT)
- [ ] Wallet CRUD endpoints
- [ ] Transaction sync endpoint + APScheduler job
- [ ] Tax summary endpoint
- [ ] CSV export endpoint
```

### Phase 3 — Frontend Dashboard (Days 11–17)
```markdown
- [ ] Next.js setup + shadcn/ui + Tailwind
- [ ] Auth pages (login/signup)
- [ ] Dashboard layout (sidebar + main)
- [ ] Portfolio overview card (total value, total gain/loss)
- [ ] P&L chart (Recharts — 30d/90d/1y/all)
- [ ] Transaction table (TanStack Table, paginated)
- [ ] Add wallet modal + sync status
```

### Phase 4 — Tax & Export (Days 18–21)
```markdown
- [ ] Tax summary page (by financial year, by token)
- [ ] CSV download
- [ ] PDF report (use ReportLab on backend)
- [ ] India ITR VDA format (pro only)
```

### Phase 5 — Payments & Launch (Days 22–25)
```markdown
- [ ] Razorpay subscription integration
- [ ] Lemon Squeezy integration
- [ ] Plan gates in frontend (show, don't hide — blur + upgrade prompt)
- [ ] Landing page + pricing page
- [ ] Deploy: Vercel + Render + Supabase
```

## Critical Path Dependencies

| Dependency | Phase | Criticality |
|------------|-------|-------------|
| FIFO Tax Calculator | Phase 1 | High — Core functionality |
| Etherscan API Integration | Phase 1 | High — Data acquisition |
| CoinGecko Price Engine | Phase 1 | High — Valuation accuracy |
| PostgreSQL Schema | Phase 1 | High — Data integrity |
| JWT Authentication | Phase 2 | Medium — User security |
| Transaction Categorization | Phase 2 | Medium — Data quality |
| Frontend Dashboard | Phase 3 | Medium — User experience |
| Payment Integration | Phase 5 | Medium — Monetization |

## Risk Mitigation Table

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| CoinGecko rate limits | High | High | LRU caching + DB price cache table |
| Etherscan API limits | High | Medium | Queue wallet syncs, overnight processing |
| FIFO calculation errors | Critical | Low | 10+ unit tests, QA agent review |
| Unknown token pricing | Medium | Medium | Flag for manual review, user input |
| High transaction volumes | Medium | Low | Background jobs, progress indicators |
| Database costs | Low | Low | Supabase free tier (500MB) |
| Payment integration failures | Medium | Low | Test mode validation, fallback options |

## Success Metrics

### Phase 1 Completion
- ✅ Tax calculator passes all test cases
- ✅ Wallet addresses never stored with private keys
- ✅ Privacy policy mentions read-only wallet access

### Phase 2 Completion
- ✅ Rate limiting on all auth endpoints
- ✅ CORS configured for production domain only
- ✅ All API keys in environment variables

### Phase 3 Completion
- ✅ Dashboard loads within 3 seconds
- ✅ Transaction table handles 1000+ rows
- ✅ Mobile-responsive design

### Phase 4 Completion
- ✅ CSV export works end-to-end
- ✅ PDF generation functional
- ✅ ITR VDA format validated

### Phase 5 Completion
- ✅ Razorpay test → live mode tested
- ✅ Free tier limits enforced on backend
- ✅ Landing page live with pricing
- ✅ Error monitoring (Sentry) configured

## Monetization Strategy

### Pricing Tiers
```markdown
| Plan | Price | Wallets | Chains | Export | History |
|------|-------|---------|--------|--------|---------|
| Free | $0 | 1 | ETH only | None | Current FY |
| Starter | $9/month | 3 | ETH, BNB, Polygon | CSV | 3 years |
| Pro | $19/month | Unlimited | All chains | CSV+PDF+ITR | Full history |
| Lifetime* | $79 once | Pro features | All chains | All exports | Full history |

*AppSumo offering post-launch
```

### Conversion Strategy
- Free tier shows P&L but blocks exports (designed conversion moment)
- Starter tier targets casual traders
- Pro tier targets serious investors and Indian tax filers
- Lifetime deal for early adopters via AppSumo

### Payment Providers
- **India:** Razorpay subscriptions
- **Global:** Lemon Squeezy (merchant of record)

## One Thing Today

**Day 1 Priority:** Build the PostgreSQL schema and FIFO tax calculator with comprehensive test cases.

**Critical First Steps:**
1. Set up PostgreSQL database with proper schema
2. Implement Decimal-based financial calculations
3. Write FIFO algorithm with 10+ test cases
4. Validate against known crypto tax scenarios

**Why this first?** The tax calculation engine is the core of TaxChain. Getting this right builds user trust and prevents catastrophic financial errors. Everything else depends on accurate tax calculations.

---

*This roadmap is based on the implementation plan from AGENTS.md. Last updated: April 7, 2026.*