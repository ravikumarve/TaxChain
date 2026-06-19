// User types
export interface User {
  id: string
  email: string
  plan: 'free' | 'starter' | 'pro'
  country: string
  financial_year_start: string
  created_at: string
  updated_at: string
}

// Wallet types
export interface Wallet {
  id: string
  user_id: string
  address: string
  chain: 'eth' | 'bnb' | 'polygon' | 'sol'
  label?: string
  last_synced_at?: string
  tx_count: number
  created_at: string
}

// Transaction types
export interface Transaction {
  id: string
  wallet_id: string
  user_id: string
  tx_hash: string
  chain: 'eth' | 'bnb' | 'polygon' | 'sol'
  tx_type: 'trade' | 'transfer_in' | 'transfer_out' | 'staking' | 'airdrop' | 'nft_sale' | 'fee'
  token_symbol?: string
  token_address?: string
  quantity: number
  price_usd?: number
  value_usd?: number
  fee_usd?: number
  timestamp: string
  raw_data?: any
  created_at: string
}

// Tax event types
export interface TaxEvent {
  id: string
  user_id: string
  token_symbol: string
  quantity: number
  proceeds_usd: number
  cost_basis_usd: number
  gain_loss_usd: number
  is_short_term: boolean
  sale_tx_id: string
  acquired_at?: string
  disposed_at: string
  financial_year: string
}

// API response types
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  country?: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

// Dashboard types
export interface PortfolioSummary {
  total_value: number
  total_gain_loss: number
  wallet_count: number
  transaction_count: number
}

export interface TaxSummary {
  financial_year: string
  total_gain_loss_usd: number
  short_term_gain_loss_usd: number
  long_term_gain_loss_usd: number
  token_breakdown: Array<{
    token_symbol: string
    total_gain_loss_usd: number
    short_term_gain_loss_usd: number
    long_term_gain_loss_usd: number
    transaction_count: number
    tax_event_count: number
  }>
  transaction_count: number
  tax_event_count: number
  date_range: {
    start_date: string
    end_date: string
  }
}

// Form types
export interface AddWalletForm {
  address: string
  chain: 'eth' | 'bnb' | 'polygon' | 'sol'
  label?: string
}

// Chart data types
export interface ChartDataPoint {
  date: string
  value: number
}

export interface PnLData {
  date: string
  gain_loss: number
  cumulative: number
}