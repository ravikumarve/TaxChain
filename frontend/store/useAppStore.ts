import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  plan: 'free' | 'starter' | 'pro'
  country: string
  financial_year_start: string
}

interface Wallet {
  id: string
  address: string
  chain: 'eth' | 'bnb' | 'polygon' | 'sol'
  label?: string
  last_synced_at?: string
  tx_count: number
}

interface AppState {
  // Auth state
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  
  // Data state
  wallets: Wallet[]
  transactions: any[]
  portfolioValue: number
  totalGainLoss: number
  
  // UI state
  isLoading: boolean
  error: string | null
  
  // Actions
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  clearAuth: () => void
  setWallets: (wallets: Wallet[]) => void
  addWallet: (wallet: Wallet) => void
  removeWallet: (id: string) => void
  setTransactions: (transactions: any[]) => void
  setPortfolioData: (value: number, gainLoss: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      wallets: [],
      transactions: [],
      portfolioValue: 0,
      totalGainLoss: 0,
      isLoading: false,
      error: null,

      // Actions
      setAuth: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          error: null,
        }),

      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          wallets: [],
          transactions: [],
        }),

      setWallets: (wallets) => set({ wallets }),

      addWallet: (wallet) =>
        set((state) => ({
          wallets: [...state.wallets, wallet],
        })),

      removeWallet: (id) =>
        set((state) => ({
          wallets: state.wallets.filter((wallet) => wallet.id !== id),
        })),

      setTransactions: (transactions) => set({ transactions }),

      setPortfolioData: (value, gainLoss) =>
        set({ portfolioValue: value, totalGainLoss: gainLoss }),

      setLoading: (loading) => set({ isLoading: loading }),

      setError: (error) => set({ error }),
    }),
    {
      name: 'taxchain-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)