import React from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { ArrowLeft, Users, Target, Percent, Calendar } from 'lucide-react';
import { groupsApi } from '@/lib/api';
import toast from 'react-hot-toast';

interface CreateGroupFormData {
  name: string;
  description: string;
  target_amount: string;
  interest_rate: string;
  duration_months: number;
}

export default function CreateGroupPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateGroupFormData>();

  const onSubmit = async (data: CreateGroupFormData) => {
    try {
      await groupsApi.createGroup({
        name: data.name,
        description: data.description,
        target_amount: data.target_amount,
        interest_rate: (parseFloat(data.interest_rate) / 100).toFixed(4),
        duration_months: data.duration_months,
      });
      toast.success('Group created successfully!');
      router.push('/groups');
    } catch (error: any) {
      const message = error.response?.data?.message || 'Failed to create group';
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
            <h1 className="text-xl font-bold text-gray-900">Create New Group</h1>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Group Name */}
            <div>
              <label htmlFor="name" className="form-label">
                Group Name *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Users className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="name"
                  type="text"
                  {...register('name', {
                    required: 'Group name is required',
                    minLength: {
                      value: 3,
                      message: 'Name must be at least 3 characters',
                    },
                  })}
                  className="form-input pl-10"
                  placeholder="e.g., Tech Startup Fund"
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-danger-600">
                  {errors.name.message}
                </p>
              )}
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="form-label">
                Description
              </label>
              <textarea
                id="description"
                {...register('description')}
                rows={3}
                className="form-input"
                placeholder="Describe the purpose and goals of this investment group..."
              />
            </div>

            {/* Target Amount */}
            <div>
              <label htmlFor="target_amount" className="form-label">
                Target Amount ($) *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Target className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="target_amount"
                  type="number"
                  step="0.01"
                  min="100"
                  {...register('target_amount', {
                    required: 'Target amount is required',
                    min: {
                      value: 100,
                      message: 'Minimum target amount is $100',
                    },
                  })}
                  className="form-input pl-10"
                  placeholder="10000"
                />
              </div>
              {errors.target_amount && (
                <p className="mt-1 text-sm text-danger-600">
                  {errors.target_amount.message}
                </p>
              )}
            </div>

            {/* Interest Rate */}
            <div>
              <label htmlFor="interest_rate" className="form-label">
                Expected Annual Return (%) *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Percent className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="interest_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  {...register('interest_rate', {
                    required: 'Interest rate is required',
                    min: {
                      value: 0,
                      message: 'Interest rate must be positive',
                    },
                    max: {
                      value: 100,
                      message: 'Interest rate cannot exceed 100%',
                    },
                  })}
                  className="form-input pl-10"
                  placeholder="8"
                />
              </div>
              {errors.interest_rate && (
                <p className="mt-1 text-sm text-danger-600">
                  {errors.interest_rate.message}
                </p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                This is the expected annual return rate for the investment.
              </p>
            </div>

            {/* Duration */}
            <div>
              <label htmlFor="duration_months" className="form-label">
                Duration (Months) *
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Calendar className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="duration_months"
                  type="number"
                  min="1"
                  max="120"
                  {...register('duration_months', {
                    required: 'Duration is required',
                    min: {
                      value: 1,
                      message: 'Minimum duration is 1 month',
                    },
                    max: {
                      value: 120,
                      message: 'Maximum duration is 120 months',
                    },
                  })}
                  className="form-input pl-10"
                  placeholder="12"
                />
              </div>
              {errors.duration_months && (
                <p className="mt-1 text-sm text-danger-600">
                  {errors.duration_months.message}
                </p>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-end space-x-4 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary"
              >
                {isSubmitting ? 'Creating...' : 'Create Group'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
