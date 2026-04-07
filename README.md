# TaxChain - Multi-Wallet Crypto Tax & Portfolio SaaS

![TaxChain Logo](https://img.shields.io/badge/TaxChain-FinTech-blue)
![Version](https://img.shields.io/badge/version-0.1.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/Next.js-14.0+-black)

TaxChain is a production-grade crypto tax and portfolio P&L SaaS that helps users calculate capital gains, cost basis, and generate tax reports across multiple wallets and chains.

## 🚀 Key Features

- **Multi-Chain Support**: ETH, BNB, Polygon, Solana
- **Automated Tax Calculation**: FIFO cost basis methodology
- **Real-time Portfolio Tracking**: Live P&L with historical charts
- **Tax Report Generation**: CSV, PDF, and India ITR Schedule VDA exports
- **Secure & Private**: Read-only wallet access, no private keys stored
- **Global Payments**: Razorpay (India) + Lemon Squeezy (global)

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with Alembic migrations
- **Auth**: JWT tokens with bcrypt
- **Background Jobs**: APScheduler

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts
- **Tables**: TanStack Table
- **State**: Zustand + React Query

### External APIs
- **Blockchain**: Etherscan, BscScan, PolygonScan, Solscan
- **Prices**: CoinGecko API
- **Payments**: Razorpay, Lemon Squeezy

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/taxchain.git
cd taxchain
```

2. Set up Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd ../frontend
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API URL
```

3. Start the development server:
```bash
npm run dev
```

## 🗄️ Database Schema

The application uses PostgreSQL with the following core tables:

- `users` - User accounts and subscription plans
- `wallets` - Connected blockchain addresses (read-only)
- `transactions` - Raw blockchain transactions
- `cost_basis_lots` - FIFO inventory tracking
- `tax_events` - Calculated gains/losses
- `subscriptions` - Payment subscriptions

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### Wallets
- `GET /api/wallets` - List user wallets
- `POST /api/wallets` - Add new wallet
- `DELETE /api/wallets/{id}` - Remove wallet
- `POST /api/wallets/{id}/sync` - Manual sync

### Transactions & Tax
- `GET /api/transactions` - Paginated transaction list
- `GET /api/tax/summary` - Tax summary by financial year
- `POST /api/reports/csv` - Generate CSV report
- `POST /api/reports/itr` - India ITR Schedule VDA export

## 💰 Pricing Plans

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 1 wallet, ETH only, no export |
| Starter | $9/month | 3 wallets, 3 chains, CSV export |
| Pro | $19/month | Unlimited wallets, all features |

## 🚢 Deployment

### Backend (Render)
```bash
git push render main
```

### Frontend (Vercel)
```bash
npm run build
npm run start
```

### Database (Supabase)
- Free tier: 500MB storage
- Automatic backups
- Managed PostgreSQL

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

- Never store private keys or seed phrases
- All wallet access is read-only
- Rate limiting on all API endpoints
- Input validation on all user inputs
- Regular security audits

## 📞 Support

- Documentation: [GitHub Wiki](https://github.com/yourusername/taxchain/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/taxchain/issues)
- Email: support@taxchain.app

## 🙏 Acknowledgments

- Built with ❤️ by Ravi
- Inspired by the need for affordable crypto tax solutions in global markets
- Special thanks to the FastAPI and Next.js communities

---

**TaxChain** - Making crypto taxes simple and accessible for everyone.