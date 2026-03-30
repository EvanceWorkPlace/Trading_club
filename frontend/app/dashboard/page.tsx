import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Wallet,
  TrendingUp,
  Users,
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Activity,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardStats, PortfolioSummary, Transaction, InvestmentGroup } from '@/types';
import { analyticsApi, transactionsApi, groupsApi } from '@/lib/api';
import { formatCurrency, formatPercentage, formatRelativeTime, getStatusColor } from '@/lib/utils';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444'];

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [myGroups, setMyGroups] = useState<InvestmentGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
    }
  }, [isAuthenticated]);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const [statsRes, portfolioRes, transactionsRes, groupsRes] = await Promise.all([
        analyticsApi.getPortfolioSummary(),
        analyticsApi.getPortfolioSummary(),
        transactionsApi.getRecent(5),
        groupsApi.getMyGroups(),
      ]);

      setPortfolio(portfolioRes.data);
      setRecentTransactions(transactionsRes.data);
      setMyGroups(groupsRes.data.slice(0, 3));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  // Prepare chart data
  const walletData = portfolio
    ? [
        { name: 'Balance', value: parseFloat(portfolio.wallet.balance) },
        { name: 'Contributed', value: parseFloat(portfolio.wallet.total_contributed) },
        { name: 'Earned', value: parseFloat(portfolio.wallet.total_earned) },
      ]
    : [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold">IC</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.first_name}
              </span>
              <button
                onClick={() => router.push('/profile')}
                className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-700 font-medium"
              >
                {user?.first_name?.[0]}
                {user?.last_name?.[0]}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Wallet Balance */}
          <div className="bg-white rounded-xl shadow-sm p-6 card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Wallet Balance</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatCurrency(portfolio?.wallet.balance || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <Wallet className="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-success-600 flex items-center">
                <ArrowUpRight className="h-4 w-4 mr-1" />
                Available
              </span>
            </div>
          </div>

          {/* Total Contributed */}
          <div className="bg-white rounded-xl shadow-sm p-6 card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Contributed</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatCurrency(portfolio?.wallet.total_contributed || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-warning-100 rounded-lg flex items-center justify-center">
                <PiggyBank className="h-6 w-6 text-warning-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-600">
                Across {portfolio?.groups.total || 0} groups
              </span>
            </div>
          </div>

          {/* Total Earned */}
          <div className="bg-white rounded-xl shadow-sm p-6 card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Earned</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatCurrency(portfolio?.wallet.total_earned || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-success-100 rounded-lg flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-success-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-success-600 flex items-center">
                <ArrowUpRight className="h-4 w-4 mr-1" />
                Profit share
              </span>
            </div>
          </div>

          {/* ROI */}
          <div className="bg-white rounded-xl shadow-sm p-6 card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">ROI</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatPercentage(portfolio?.roi.roi_percentage || 0)}
                </p>
              </div>
              <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-gray-600">
                Net: {formatCurrency(portfolio?.roi.net_profit || 0)}
              </span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Portfolio Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Portfolio Overview
              </h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={walletData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {walletData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center space-x-6 mt-4">
                {walletData.map((item, index) => (
                  <div key={item.name} className="flex items-center">
                    <div
                      className="h-3 w-3 rounded-full mr-2"
                      style={{ backgroundColor: COLORS[index] }}
                    />
                    <span className="text-sm text-gray-600">{item.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* My Groups */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">My Groups</h2>
                <button
                  onClick={() => router.push('/groups')}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all
                </button>
              </div>
              <div className="space-y-4">
                {myGroups.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    You haven't joined any groups yet.
                  </p>
                ) : (
                  myGroups.map((group) => (
                    <div
                      key={group.id}
                      onClick={() => router.push(`/groups/${group.id}`)}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                    >
                      <div>
                        <h3 className="font-medium text-gray-900">{group.name}</h3>
                        <p className="text-sm text-gray-500">
                          {formatCurrency(group.current_amount)} of{' '}
                          {formatCurrency(group.target_amount)}
                        </p>
                      </div>
                      <div className="text-right">
                        <span
                          className={`badge ${getStatusColor(group.status)}`}
                        >
                          {group.status}
                        </span>
                        <p className="text-sm text-gray-500 mt-1">
                          {group.progress_percentage.toFixed(1)}% funded
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Actions
              </h2>
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/deposit')}
                  className="w-full btn-success"
                >
                  <DollarSign className="h-5 w-5 mr-2" />
                  Deposit Funds
                </button>
                <button
                  onClick={() => router.push('/groups/create')}
                  className="w-full btn-primary"
                >
                  <Users className="h-5 w-5 mr-2" />
                  Create Group
                </button>
                <button
                  onClick={() => router.push('/groups/discover')}
                  className="w-full btn-secondary"
                >
                  <Activity className="h-5 w-5 mr-2" />
                  Discover Groups
                </button>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Recent Transactions
                </h2>
                <button
                  onClick={() => router.push('/transactions')}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all
                </button>
              </div>
              <div className="space-y-3">
                {recentTransactions.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    No transactions yet.
                  </p>
                ) : (
                  recentTransactions.map((transaction) => (
                    <div
                      key={transaction.id}
                      className="flex items-center justify-between py-2"
                    >
                      <div className="flex items-center">
                        <div
                          className={`h-8 w-8 rounded-full flex items-center justify-center mr-3 ${
                            transaction.transaction_type === 'DEPOSIT' ||
                            transaction.transaction_type === 'PROFIT'
                              ? 'bg-success-100'
                              : 'bg-danger-100'
                          }`}
                        >
                          {transaction.transaction_type === 'DEPOSIT' ||
                          transaction.transaction_type === 'PROFIT' ? (
                            <ArrowUpRight className="h-4 w-4 text-success-600" />
                          ) : (
                            <ArrowDownRight className="h-4 w-4 text-danger-600" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {transaction.transaction_type_display}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatRelativeTime(transaction.created_at)}
                          </p>
                        </div>
                      </div>
                      <span
                        className={`text-sm font-medium ${
                          transaction.transaction_type === 'DEPOSIT' ||
                          transaction.transaction_type === 'PROFIT'
                            ? 'text-success-600'
                            : 'text-danger-600'
                        }`}
                      >
                        {transaction.transaction_type === 'DEPOSIT' ||
                        transaction.transaction_type === 'PROFIT'
                          ? '+'
                          : '-'}
                        {formatCurrency(transaction.amount)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Group Stats */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Group Statistics
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Active Groups</span>
                  <span className="font-semibold text-gray-900">
                    {portfolio?.groups.active || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Pending Groups</span>
                  <span className="font-semibold text-gray-900">
                    {portfolio?.groups.pending || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Completed</span>
                  <span className="font-semibold text-gray-900">
                    {portfolio?.groups.completed || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
