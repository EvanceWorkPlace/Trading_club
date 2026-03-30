import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownRight,
  Filter,
  Download,
  Search,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Transaction } from '@/types';
import { transactionsApi } from '@/lib/api';
import {
  formatCurrency,
  formatDate,
  formatRelativeTime,
  getStatusColor,
} from '@/lib/utils';
import toast from 'react-hot-toast';

export default function TransactionsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    filterTransactions();
  }, [searchQuery, typeFilter, transactions]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [transactionsRes, summaryRes] = await Promise.all([
        transactionsApi.getTransactions(),
        transactionsApi.getSummary(),
      ]);
      setTransactions(transactionsRes.data.results || transactionsRes.data);
      setFilteredTransactions(transactionsRes.data.results || transactionsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      toast.error('Failed to load transactions');
    } finally {
      setIsLoading(false);
    }
  };

  const filterTransactions = () => {
    let filtered = transactions;

    if (searchQuery) {
      filtered = filtered.filter(
        (t) =>
          t.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.reference_number.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (typeFilter !== 'ALL') {
      filtered = filtered.filter((t) => t.transaction_type === typeFilter);
    }

    setFilteredTransactions(filtered);
  };

  const getTransactionIcon = (type: string) => {
    const isCredit = type === 'DEPOSIT' || type === 'PROFIT' || type === 'REFUND';
    return isCredit ? (
      <ArrowUpRight className="h-5 w-5 text-success-600" />
    ) : (
      <ArrowDownRight className="h-5 w-5 text-danger-600" />
    );
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/dashboard')}
                className="h-10 w-10 bg-primary-600 rounded-xl flex items-center justify-center"
              >
                <span className="text-white font-bold">IC</span>
              </button>
              <h1 className="text-xl font-bold text-gray-900">Transactions</h1>
            </div>
            <button
              onClick={() => toast.info('Export feature coming soon!')}
              className="btn-secondary"
            >
              <Download className="h-5 w-5 mr-2" />
              Export
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-sm p-4">
              <p className="text-sm text-gray-600">Total Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {summary.total_transactions}
              </p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4">
              <p className="text-sm text-gray-600">Total Credits</p>
              <p className="text-2xl font-bold text-success-600">
                {formatCurrency(summary.total_credits)}
              </p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4">
              <p className="text-sm text-gray-600">Total Debits</p>
              <p className="text-2xl font-bold text-danger-600">
                {formatCurrency(summary.total_debits)}
              </p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4">
              <p className="text-sm text-gray-600">Net Flow</p>
              <p
                className={`text-2xl font-bold ${
                  parseFloat(summary.net_flow) >= 0
                    ? 'text-success-600'
                    : 'text-danger-600'
                }`}
              >
                {formatCurrency(summary.net_flow)}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search transactions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input pl-10"
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-5 w-5 text-gray-400" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="form-input py-2"
                >
                  <option value="ALL">All Types</option>
                  <option value="DEPOSIT">Deposits</option>
                  <option value="CONTRIBUTION">Contributions</option>
                  <option value="PROFIT">Profits</option>
                  <option value="WITHDRAWAL">Withdrawals</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Transactions List */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {filteredTransactions.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-gray-500">No transactions found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Transaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reference
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTransactions.map((transaction) => (
                    <tr
                      key={transaction.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div
                            className={`h-8 w-8 rounded-full flex items-center justify-center mr-3 ${
                              transaction.transaction_type === 'DEPOSIT' ||
                              transaction.transaction_type === 'PROFIT'
                                ? 'bg-success-100'
                                : 'bg-danger-100'
                            }`}
                          >
                            {getTransactionIcon(transaction.transaction_type)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {transaction.transaction_type_display}
                            </p>
                            <p className="text-sm text-gray-500">
                              {transaction.description}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className="text-sm text-gray-600">
                          {transaction.reference_number}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className="text-sm text-gray-600">
                          {formatDate(transaction.created_at)}
                        </p>
                        <p className="text-xs text-gray-400">
                          {formatRelativeTime(transaction.created_at)}
                        </p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`badge ${getStatusColor(
                            transaction.status
                          )}`}
                        >
                          {transaction.status_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
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
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
