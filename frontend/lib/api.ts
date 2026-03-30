import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && originalRequest) {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  
  register: (data: {
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    password_confirm: string;
    phone_number?: string;
  }) => api.post('/auth/register/', data),
  
  googleAuth: (accessToken: string) =>
    api.post('/auth/google/', { access_token: accessToken }),
  
  refreshToken: (refreshToken: string) =>
    api.post('/auth/refresh/', { refresh: refreshToken }),
  
  getProfile: () => api.get('/auth/profile/'),
  
  updateProfile: (data: Partial<{
    first_name: string;
    last_name: string;
    phone_number: string;
  }>) => api.patch('/auth/profile/update/', data),
  
  changePassword: (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => api.post('/auth/password/change/', data),
  
  getDashboard: () => api.get('/auth/dashboard/'),
};

// Wallet API
export const walletApi = {
  getWallet: () => api.get('/auth/wallet/'),
  
  deposit: (amount: number) =>
    api.post('/auth/wallet/deposit/', { amount }),
};

// Groups API
export const groupsApi = {
  getGroups: () => api.get('/groups/'),
  
  getGroup: (id: string) => api.get(`/groups/${id}/`),
  
  createGroup: (data: {
    name: string;
    description: string;
    target_amount: string;
    interest_rate: string;
    duration_months: number;
  }) => api.post('/groups/', data),
  
  updateGroup: (id: string, data: Partial<{
    name: string;
    description: string;
  }>) => api.patch(`/groups/${id}/`, data),
  
  joinGroup: (id: string, invitationToken?: string) =>
    api.post(`/groups/${id}/join/`, { invitation_token: invitationToken }),
  
  leaveGroup: (id: string) => api.post(`/groups/${id}/leave/`),
  
  inviteMember: (id: string, email: string) =>
    api.post(`/groups/${id}/invite/`, { email }),
  
  getMembers: (id: string) => api.get(`/groups/${id}/members/`),
  
  getMyGroups: () => api.get('/groups/my_groups/'),
  
  discoverGroups: () => api.get('/groups/discover/'),
};

// Invitations API
export const invitationsApi = {
  getInvitations: () => api.get('/groups/invitations/'),
  
  acceptInvitation: (id: string) =>
    api.post(`/groups/invitations/${id}/accept/`),
  
  declineInvitation: (id: string) =>
    api.post(`/groups/invitations/${id}/decline/`),
};

// Contributions API
export const contributionsApi = {
  getContributions: () => api.get('/investments/contributions/'),
  
  getGroupContributions: (groupId: string) =>
    api.get(`/investments/contributions/group_contributions/?group=${groupId}`),
  
  createContribution: (data: {
    group: string;
    amount: string;
    notes?: string;
  }) => api.post('/investments/contributions/', data),
  
  getMyContributions: () =>
    api.get('/investments/contributions/my_contributions/'),
};

// Profit API
export const profitApi = {
  getMyDistributions: () =>
    api.get('/investments/profits/my_distributions/'),
  
  getGroupDistributions: (groupId: string) =>
    api.get(`/investments/profits/group_distributions/?group=${groupId}`),
};

// Simulation API
export const simulationApi = {
  calculate: (data: {
    principal_amount: string;
    interest_rate: string;
    duration_months: number;
    calculation_method: 'simple' | 'compound';
  }) => api.post('/investments/simulations/calculate/', data),
  
  getMySimulations: () =>
    api.get('/investments/simulations/my_simulations/'),
  
  saveSimulation: (data: {
    principal_amount: string;
    interest_rate: string;
    duration_months: number;
  }) => api.post('/investments/simulations/', data),
};

// Analytics API
export const analyticsApi = {
  getROI: () => api.get('/investments/analytics/roi/'),
  
  getGroupAnalytics: () =>
    api.get('/investments/analytics/group_analytics/'),
  
  getPortfolioSummary: () =>
    api.get('/investments/analytics/portfolio_summary/'),
};

// Transactions API
export const transactionsApi = {
  getTransactions: (params?: {
    type?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }) => api.get('/transactions/history/', { params }),
  
  getSummary: () => api.get('/transactions/summary/'),
  
  getRecent: (limit?: number) =>
    api.get('/transactions/recent/', { params: { limit } }),
  
  getByType: () => api.get('/transactions/by_type/'),
  
  getMonthlyBreakdown: () =>
    api.get('/transactions/stats/monthly_breakdown/'),
  
  getDashboardCards: () =>
    api.get('/transactions/stats/dashboard_cards/'),
};

export default api;
