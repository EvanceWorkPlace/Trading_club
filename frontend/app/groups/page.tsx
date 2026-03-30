import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Plus,
  Search,
  Filter,
  Users,
  TrendingUp,
  Calendar,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { InvestmentGroup } from '@/types';
import { groupsApi } from '@/lib/api';
import { formatCurrency, formatPercentage, getStatusColor } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function GroupsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [groups, setGroups] = useState<InvestmentGroup[]>([]);
  const [filteredGroups, setFilteredGroups] = useState<InvestmentGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchGroups();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    filterGroups();
  }, [searchQuery, statusFilter, groups]);

  const fetchGroups = async () => {
    try {
      setIsLoading(true);
      const response = await groupsApi.getMyGroups();
      setGroups(response.data);
      setFilteredGroups(response.data);
    } catch (error) {
      toast.error('Failed to load groups');
    } finally {
      setIsLoading(false);
    }
  };

  const filterGroups = () => {
    let filtered = groups;

    if (searchQuery) {
      filtered = filtered.filter(
        (group) =>
          group.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          group.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'ALL') {
      filtered = filtered.filter((group) => group.status === statusFilter);
    }

    setFilteredGroups(filtered);
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
              <h1 className="text-xl font-bold text-gray-900">My Groups</h1>
            </div>
            <button
              onClick={() => router.push('/groups/create')}
              className="btn-primary"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Group
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search groups..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input pl-10"
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-5 w-5 text-gray-400" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="form-input py-2"
                >
                  <option value="ALL">All Status</option>
                  <option value="PENDING">Pending</option>
                  <option value="ACTIVE">Active</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-sm text-gray-600">Total Groups</p>
            <p className="text-2xl font-bold text-gray-900">{groups.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-sm text-gray-600">Active</p>
            <p className="text-2xl font-bold text-success-600">
              {groups.filter((g) => g.status === 'ACTIVE').length}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-sm text-gray-600">Pending</p>
            <p className="text-2xl font-bold text-warning-600">
              {groups.filter((g) => g.status === 'PENDING').length}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-sm text-gray-600">Completed</p>
            <p className="text-2xl font-bold text-primary-600">
              {groups.filter((g) => g.status === 'COMPLETED').length}
            </p>
          </div>
        </div>

        {/* Groups Grid */}
        {filteredGroups.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No groups found
            </h3>
            <p className="text-gray-500 mb-4">
              {searchQuery || statusFilter !== 'ALL'
                ? 'Try adjusting your filters'
                : "You haven't joined any groups yet"}
            </p>
            <button
              onClick={() => router.push('/groups/discover')}
              className="btn-primary"
            >
              Discover Groups
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGroups.map((group) => (
              <div
                key={group.id}
                onClick={() => router.push(`/groups/${group.id}`)}
                className="bg-white rounded-xl shadow-sm p-6 card-hover cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {group.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {group.description || 'No description'}
                    </p>
                  </div>
                  <span className={`badge ${getStatusColor(group.status)}`}>
                    {group.status}
                  </span>
                </div>

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium text-gray-900">
                      {group.progress_percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-600 rounded-full transition-all"
                      style={{ width: `${group.progress_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center text-sm">
                    <TrendingUp className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">
                      {formatCurrency(group.current_amount)}
                    </span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Users className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-gray-600">
                      {group.member_count} members
                    </span>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {group.days_remaining !== null
                      ? `${group.days_remaining} days left`
                      : 'Not started'}
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
