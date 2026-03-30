// User Types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number?: string;
  avatar?: string;
  is_email_verified: boolean;
  date_joined: string;
  wallet: Wallet;
}

export interface Wallet {
  id: string;
  balance: string;
  total_deposited: string;
  total_contributed: string;
  total_earned: string;
  created_at: string;
  updated_at: string;
}

// Group Types
export interface InvestmentGroup {
  id: string;
  name: string;
  description: string;
  created_by: User;
  target_amount: string;
  current_amount: string;
  interest_rate: string;
  duration_months: number;
  total_profit: string;
  status: 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  progress_percentage: number;
  days_remaining: number | null;
  is_fully_funded: boolean;
  start_date: string | null;
  end_date: string | null;
  member_count: number;
  memberships?: GroupMembership[];
  created_at: string;
  updated_at: string;
}

export interface GroupMembership {
  id: string;
  user: User;
  role: 'ADMIN' | 'MEMBER';
  is_active: boolean;
  total_contributed: string;
  profit_share: string;
  contribution_percentage: number;
  joined_at: string;
}

export interface GroupInvitation {
  id: string;
  group: string;
  group_name: string;
  invited_by: User;
  email: string;
  status: 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED';
  expires_at: string;
  created_at: string;
}

// Investment Types
export interface Contribution {
  id: string;
  group: string;
  group_name: string;
  user: string;
  user_name: string;
  amount: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface ProfitDistribution {
  id: string;
  user: string;
  user_name: string;
  contribution_amount: string;
  contribution_percentage: string;
  profit_share: string;
  total_payout: string;
  created_at: string;
}

export interface InvestmentSimulation {
  id: string;
  principal_amount: string;
  interest_rate: string;
  duration_months: number;
  projected_amount: string;
  total_interest: string;
  created_at: string;
}

// Transaction Types
export interface Transaction {
  id: string;
  transaction_type: 'DEPOSIT' | 'WITHDRAWAL' | 'CONTRIBUTION' | 'PROFIT' | 'REFUND' | 'TRANSFER';
  transaction_type_display: string;
  amount: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  status_display: string;
  description: string;
  reference_number: string;
  group_id?: string;
  contribution_id?: string;
  created_at: string;
  completed_at?: string;
}

// Dashboard Types
export interface DashboardStats {
  wallet_balance: string;
  total_deposited: string;
  total_contributed: string;
  total_earned: string;
  active_groups: number;
  completed_groups: number;
  roi_percentage: number;
}

export interface PortfolioSummary {
  wallet: {
    balance: string;
    total_deposited: string;
    total_contributed: string;
    total_earned: string;
  };
  groups: {
    active: number;
    pending: number;
    completed: number;
    total: number;
  };
  contributions: {
    total_amount: string;
  };
  roi: {
    total_contributed: number;
    total_earned: number;
    net_profit: number;
    roi_percentage: number;
  };
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  message: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
