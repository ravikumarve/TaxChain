# TaxChain Startup Guide

## 🚀 Quick Start

### Option 1: Using Startup Scripts (Recommended)

#### Start Backend
```bash
cd backend
./start_server.sh
```

#### Start Frontend
```bash
cd frontend  
./start_frontend.sh
```

### Option 2: Manual Startup

#### Start Backend
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Start Frontend
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📱 Available Pages

- **Landing**: http://localhost:3000/
- **Login**: http://localhost:3000/auth/login
- **Signup**: http://localhost:3000/auth/signup
- **Dashboard**: http://localhost:3000/dashboard
- **Wallets**: http://localhost:3000/dashboard/wallets
- **Transactions**: http://localhost:3000/dashboard/transactions
- **Tax Summary**: http://localhost:3000/dashboard/tax
- **Reports**: http://localhost:3000/dashboard/reports

## 🔧 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'slowapi'`
**Solution**: Make sure you're using the virtual environment:
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Problem**: Port 8000 already in use
**Solution**: Kill the process or use a different port:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Frontend Issues

**Problem**: Port 3000 already in use
**Solution**: Kill the process or use different port:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

**Problem**: Module not found errors
**Solution**: Install dependencies:
```bash
cd frontend
npm install
```

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/
```

### Test API Endpoints
```bash
# View API docs
# Open http://localhost:8000/docs in browser

# Test specific endpoint (requires auth)
curl http://localhost:8000/api/tax/summary
```

### Test Frontend
```bash
# Open http://localhost:3000 in browser
# Navigate through all pages
# Test authentication flow
# Test export functionality
```

## 📝 Environment Setup

### Backend (.env)
```bash
DATABASE_URL=sqlite+aiosqlite:///./taxchain.db
SECRET_KEY=your-jwt-secret-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛑 Stopping Servers

### Stop Backend
Press `Ctrl+C` in the backend terminal

### Stop Frontend  
Press `Ctrl+C` in the frontend terminal

### Force Stop All
```bash
# Kill all processes on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

## 🎯 Phase 4 Testing Checklist

- [ ] User can sign up and login
- [ ] Dashboard loads correctly
- [ ] Navigation works between all pages
- [ ] Wallet management functions
- [ ] Tax summary displays correctly
- [ ] Financial year selector works
- [ ] CSV export downloads
- [ ] PDF export downloads
- [ ] ITR export shows plan gate
- [ ] Plan restrictions work
- [ ] Responsive design looks good

## 📞 Support

If you encounter issues:
1. Check the terminal logs for error messages
2. Verify both servers are running
3. Check environment variables are set correctly
4. Ensure dependencies are installed
5. Try clearing browser cache and restarting