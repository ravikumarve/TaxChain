# TaxChain Frontend Redesign Blueprint

**Source design:** `TaxChain.html` (root directory, 674 lines, standalone HTML)
**Target:** Next.js 14 App Router frontend at `frontend/app/`
**Author:** Analyzed from TaxChain.html by orchestrator
**Date:** 2026-06-19

---

## 1. Design Language — Complete Thematic Shift

| Aspect | Current Frontend | Target (TaxChain.html) |
|---|---|---|
| **Theme** | Light/white (`#FFFFFF` bg) | **Dark void** (`#010204` bg) |
| **Vibe** | Generic SaaS (blue/white) | Institutional fintech (dark/indigo) |
| **Typography** | Basic sans-serif | Plus Jakarta Sans (UI) + JetBrains Mono (data) |
| **Glassmorphism** | None | `backdrop-filter: blur(30px)` with glass panels |
| **Animations** | None | **3D isometric data stream** (Canvas2D, not Three.js) |
| **Grid** | Standard cards | **Bento grid** (12-column fractional spans 4/6/8) |
| **Chains displayed** | 4 (eth/bnb/polygon/sol) | **8 chains** with badges |
| **Export formats** | Only ITR mentioned | **4 formats**: ITR VDA, IRS 8949, HMRC, ATO |
| **Security cues** | Generic "bank-level" | Specific: HMAC-SHA256 webhooks, 5/min auth rate limit, SQLAlchemy SQLi defense |
| **Footer** | Basic 4-col | 4-col with Platform/Developers/Company sections + systems status indicator |

---

## 2. Design Token System (CSS Custom Properties → Tailwind)

The HTML defines the following dark palette. These must become the new `tailwind.config.js`:

```css
/* Source tokens from TaxChain.html */
--bg-void: #010204;              /* Page background — darkest */
--bg-surface: #070913;           /* Card/section surface */
--bg-panel: #0d1120;             /* Panel backgrounds */
--bg-glass: rgba(13, 17, 32, 0.5); /* Glassmorphism base */
--border-dim: rgba(255,255,255,0.05);
--border-glow: rgba(99,102,241,0.2);
--indigo: #6366F1;               /* Primary brand — indigo */
--indigo-dim: rgba(99,102,241,0.1);
--emerald: #10B981;              /* Gains/success */
--emerald-dim: rgba(16,185,129,0.1);
--slate: #94a3b8;                /* Muted text */
--text-main: #ffffff;
--text-muted: #94a3b8;
--text-faint: #475569;
--font-ui: 'Plus Jakarta Sans', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Tailwind Config Additions

```js
// frontend/tailwind.config.js — add to existing config
colors: {
  brand: {
    DEFAULT: '#6366F1',
    light: '#EEF2FF',
    dim: 'rgba(99,102,241,0.1)',
  },
  gain: {
    DEFAULT: '#10B981',
    bg: '#ECFDF5',
    dim: 'rgba(16,185,129,0.1)',
  },
  loss: {
    DEFAULT: '#EF4444',
    bg: '#FEF2F2',
  },
  void: '#010204',
  surface: '#070913',
  panel: '#0d1120',
  glass: 'rgba(13,17,32,0.5)',
  'border-dim': 'rgba(255,255,255,0.05)',
  'border-glow': 'rgba(99,102,241,0.2)',
  'text-muted': '#94a3b8',
  'text-faint': '#475569',
  chains: {
    eth: '#627EEA',
    bnb: '#F3BA2F',
    polygon: '#8247E5',
    sol: '#9945FF',
    arbitrum: '#28A0F0',
    optimism: '#FF0420',
    base: '#0052FF',
    btc: '#F7931A',
  },
}
```

### Key CSS Patterns to Replicate

```css
/* Glassmorphism panel */
.glass-pane {
  background: var(--bg-glass);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid var(--border-dim);
  border-radius: 16px;
}

/* Text gradient */
.text-gradient {
  background: linear-gradient(180deg, #fff 0%, #64748b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Dot matrix background */
.dot-matrix {
  background-image: radial-gradient(rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: radial-gradient(circle at 50% 40%, black 10%, transparent 80%);
}

/* Ambient core glow */
.ambient-core {
  background: radial-gradient(ellipse at center, rgba(99,102,241,0.08), transparent 70%);
  filter: blur(80px);
}

/* Bento node hover */
.bento-node:hover {
  border-color: var(--border-glow);
  transform: translateY(-4px);
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
}

/* Bento node gradient overlay */
.bento-node::after {
  background: radial-gradient(circle at top right, rgba(99,102,241,0.1), transparent 50%);
  opacity: 0;
  transition: opacity 0.4s;
}
.bento-node:hover::after { opacity: 1; }
```

---

## 3. Section-by-Section Component Map

### 3a. Background Layer

| Component | File | Type | Description |
|---|---|---|---|
| `LedgerCanvas` | `components/landing/LedgerCanvas.tsx` | Client (`'use client'`) | Canvas2D isometric data stream. 15×25 block cylinder, dot connections, mouse-responsive tilt. Raw Canvas2D (NOT Three.js). 375 nodes, `requestAnimationFrame` loop. |
| `DotMatrix` | `components/landing/DotMatrix.tsx` | Server | CSS `radial-gradient` dot grid overlay, fixed position, full viewport. Mask radial gradient for fade at edges. |

**Performance note:** Reduce `numCols`/`numRows` by 50% on mobile (`window.innerWidth < 768`). Canvas-only — estimated 20-30fps on Latitude 3460, acceptable for background.

### 3b. Navigation

| Component | File | Type |
|---|---|---|
| `Navbar` | `components/landing/Navbar.tsx` | Client |

**Structure:**
```
Logo: [indigo wireframe block] TaxChain
Links: COMPLIANCE | INFRASTRUCTURE | PRICING (mono uppercase)
Actions: [GitHub] [Connect Wallet]
Mobile: nav-links hidden, burger menu
```

**States:** Scrolled → add `bg-void/80` backdrop-blur to nav. Default → transparent.

### 3c. Hero Section

| Component | File | Type |
|---|---|---|
| `HeroSection` | `components/landing/HeroSection.tsx` | Server (wraps client children) |
| `WalletCard` | `components/landing/WalletCard.tsx` | Client — hover parallax |
| `TaxTerminal` | `components/landing/TaxTerminal.tsx` | Client — hover parallax |

**Layout:** 2-column grid `1fr 1.1fr`, 85vh min-height.

**Left column:**
- Badge: emerald dot + "Multi-wallet, Multi-chain SaaS" (mono, uppercase)
- Headline: "Institutional-grade crypto tax engine." with `text-gradient`
- Subtitle: max-width 540px, muted, weight 300
- CTAs: "Generate Report" (primary btn), "View Supported Chains" (outline btn)

**Right column (dual viewport):**
- `WalletCard` (left): glass pane, 280px, rotated -3deg. Shows 3 wallet items with chain-colored icons (E, B, P) and "Synced" status.
- `TaxTerminal` (right): glass pane, 460px, rotated +2deg. Terminal-style log with timestamps, SYNC/ENGINE/MATCH/PRICING/SUCCESS lines.

**Hover:** Both cards `rotate(0)` + `translateY(-10px)` + border glow. Smooth CSS transition `0.6s cubic-bezier(0.16, 1, 0.3, 1)`.

### 3d. Bento Matrix — Compliance Section

| Component | File | Type |
|---|---|---|
| `BentoMatrix` | `components/landing/BentoMatrix.tsx` | Server (container) |
| `BentoNode` | `components/landing/BentoNode.tsx` | Server |

**Grid layout (12 columns):**
```
┌──────────────────────────────────────┬──────────────────┐
│ 01 // GLOBAL JURISDICTIONS (span-8)  │ 02 // METHODOLOGY│
│ Official Tax Formats                 │ Strict FIFO      │
│                                      │ (span-4)         │
├──────────────────────────┬───────────┴──────────────────┤
│ 03 // PRICING ORACLE     │ 04 // ZERO COMPROMISE       │
│ Multi-Currency Resolution│ Read-Only Security          │
│ (span-6)                 │ (span-6)                    │
└──────────────────────────┴─────────────────────────────┘
```

**Props for `BentoNode`:**
```tsx
interface BentoNodeProps {
  span: 4 | 6 | 8 | 12
  index: string    // e.g. "01"
  label: string    // e.g. "GLOBAL JURISDICTIONS"
  title: string
  children: React.ReactNode
}
```

### 3e. Architecture Section

| Component | File | Type |
|---|---|---|
| `ArchitectureSection` | `components/landing/ArchitectureSection.tsx` | Server |

**Layout:** 2-column `1fr 1.2fr`.

**Left column:**
- Headline: "Production-ready infrastructure."
- Subtitle: Sync across multiple block explorers, background scheduler, non-blocking.
- Chain badges: 8 badges — Ethereum, BNB Chain, Polygon, Arbitrum, Optimism, Base, Solana, Bitcoin.
- Tech stack card (dark surface, indigo border glow):
  - Frontend: Next.js 14 + Tailwind
  - Backend: FastAPI (Python 3.12+)
  - Database: PostgreSQL 15+
  - Background: APScheduler
  - Payments: Lemon Squeezy + Razorpay
  - Oracles: CoinGecko + open.er-api

**Right column (`FormatBlock`):**
- `Export Engines` heading (mono)
- Universal Exports section: CSV Master (Starter+), PDF Summary (Pro)
- Jurisdictional Formats section: India ITR (Pro), US IRS 8949 (Starter+), UK HMRC (Starter+), Australia ATO (Starter+)
- Each format: emerald code name + description + tier badge
- System Hardening section: green checkmark list of security measures

### 3f. Pricing Matrix

| Component | File | Type |
|---|---|---|
| `PricingSection` | `components/landing/PricingSection.tsx` | Server |
| `PricingCard` | `components/landing/PricingCard.tsx` | Server |

**3-column grid**, cards have hover lift + glow.

| | Free | Starter | Pro |
|---|---|---|---|
| Price | $0 | $9/mo | $19/mo |
| Volume | TRIAL ACCESS | EVM ESSENTIALS | INSTITUTIONAL ACCESS |
| Wallets | 1 | 3 | Unlimited |
| Chains | ETH only | ETH, BNB, Polygon, Arbitrum | All 8 |
| CSV | ✗ | ✓ | ✓ |
| PDF | ✗ | ✗ | ✓ |
| ITR VDA | ✗ | ✗ | ✓ |
| IRS/HMRC/ATO | ✗ | ✓ | ✓ |
| CTA | Create Account | Select Starter | Select Pro |
| Pro card | — | — | "MOST POPULAR" banner at top |

### 3g. Footer

| Component | File | Type |
|---|---|---|
| `Footer` | `components/landing/Footer.tsx` | Server |

**Columns:** Brand (logo + description, 2fr) | Platform (3 links) | Developers (3 links) | Company (3 links)

**Footer bottom bar:**
```
© 2026 TAXCHAIN. CRYPTO TAX COMPLIANCE, DONE RIGHT.    ● SYSTEMS OPERATIONAL
```

---

## 4. Complete Component Inventory

```
frontend/components/landing/
├── LedgerCanvas.tsx            # Canvas2D isometric data stream
├── DotMatrix.tsx               # CSS dot-grid background overlay
├── Navbar.tsx                  # Navigation with mobile hamburger
├── HeroSection.tsx             # Hero + dual viewport
├── WalletCard.tsx              # Left glass card with 3 wallet items
├── TaxTerminal.tsx             # Right glass card with FIFO terminal log
├── BentoMatrix.tsx             # 12-col bento grid container
├── BentoNode.tsx               # Individual bento grid item
├── ArchitectureSection.tsx     # Left info + right format block layout
├── ChainBadge.tsx              # Single chain badge (8 chains)
├── TechStackCard.tsx           # Dark card with stack list
├── FormatBlock.tsx             # Export engines + hardening details
├── PricingSection.tsx          # 3-column pricing matrix
├── PricingCard.tsx             # Individual pricing plan card
└── Footer.tsx                  # 4-column footer
```

**Total: 15 new components**

---

## 5. Dashboard Pages — Darkening Pass

The existing dashboard structure is sound. Each page needs a dark theme pass:

| Page | Action |
|---|---|
| `app/page.tsx` | **Replace entirely** with new landing page composing all `components/landing/*` |
| `app/pricing/page.tsx` | Refactor to use `PricingSection.tsx` component |
| `app/auth/login/page.tsx` | Keep — apply dark theme CSS variables |
| `app/auth/signup/page.tsx` | Keep — apply dark theme CSS variables |
| `app/dashboard/layout.tsx` | Keep sidebar layout — darken to `--bg-void: #010204`, sidebar `--bg-panel: #0d1120` |
| `app/dashboard/page.tsx` | Keep cards — darken to `--bg-surface: #070913`, text to `--text-main: #fff` |
| `app/dashboard/wallets/page.tsx` | Keep — darken |
| `app/dashboard/transactions/page.tsx` | Keep — darken table rows |
| `app/dashboard/tax/page.tsx` | Keep — darken |
| `app/dashboard/reports/page.tsx` | Keep — darken |

### Component-Level Darkening

| Component | Change |
|---|---|
| `PortfolioCard.tsx` | `bg-white` → `bg-surface`, `text-gray-900` → `text-main`, `text-gray-600` → `text-muted` |
| `ChainBadge.tsx` | Extend to 8 chains (add arbitrum, optimism, base, btc) |
| `AddWalletModal.tsx` | Dark modal overlay, dark form fields |
| `WalletList.tsx` | Dark table/cards, chain badges updated |
| `UpgradeModal.tsx` | Dark theme pass |

---

## 6. Mobile Responsiveness

| Breakpoint | Behavior |
|---|---|
| **≤1024px** | Hero/Architecture grid → 1 column. Dual viewport stacked vertically. Bento matrix → flex column. Footer → 2 columns. |
| **≤768px** | Nav stacked, nav-links hidden (burger menu). Hero font reduced. Glass cards full-width (no rotation transform). Footer → 1 column. Canvas nodes halved. |

### Fluid Typography
```css
.hero h1 { font-size: clamp(3.5rem, 5.5vw, 5rem); }
```

---

## 7. Implementation Order

```
Phase 1 — Foundation (~1 session)
├── tailwind.config.js → add dark tokens
├── globals.css → replace :root with dark void palette
├── layout.tsx → already correct (Plus Jakarta Sans + JetBrains Mono)
├── DotMatrix.tsx + LedgerCanvas.tsx (background layer)

Phase 2 — Landing Page Components (~2 sessions)
├── Navbar.tsx
├── HeroSection.tsx + WalletCard.tsx + TaxTerminal.tsx
├── BentoMatrix.tsx + BentoNode.tsx
├── ArchitectureSection.tsx + ChainBadge.tsx + TechStackCard.tsx + FormatBlock.tsx
├── PricingSection.tsx + PricingCard.tsx
├── Footer.tsx
├── app/page.tsx → compose all landing components

Phase 3 — Dashboard Darkening (~1 session)
├── app/dashboard/layout.tsx → dark sidebar
├── All dashboard pages → dark CSS pass
├── ChainBadge.tsx → 8 chains
├── auth pages → dark theme pass

Phase 4 — Polish (~1 session)
├── Mobile responsive verification
├── Canvas performance tuning (node count throttle)
├── Animation timing tweaks
└── Build verification (next build)
```

---

## 8. Key Technical Notes

- **Canvas animation is raw Canvas2D** (not Three.js) — no dependency required
- **No icon library needed** — the HTML uses text-only (E, B, P), monospace, and CSS shapes
- **All landing components are stateless** — zero backend integration required
- Animations use CSS `cubic-bezier(0.16, 1, 0.3, 1)` — the "power curve" for smooth deceleration
- The existing `Plus_Jakarta_Sans` and `JetBrains_Mono` font imports in `layout.tsx` are already correct
- `globals.css` :root variables from AGENTS.md (light theme) must be replaced with dark void palette from TaxChain.html

---

*This blueprint is the single source of truth for the frontend redesign. All build decisions trace back to TaxChain.html.*
