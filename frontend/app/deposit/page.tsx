import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, CreditCard, CheckCircle, DollarSign } from 'lucide-react';
import { walletApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';

const PRESET_AMOUNTS = [50, 100, 250, 500, 1000];

export default function DepositPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [amount, setAmount] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleDeposit = async () => {
    const depositAmount = parseFloat(amount);
    
    if (!amount || depositAmount < 10) {
      toast.error('Minimum deposit amount is $10');
      return;
    }

    try {
      setIsProcessing(true);
      await walletApi.deposit(depositAmount);
      setIsSuccess(true);
      toast.success(`Successfully deposited ${formatCurrency(depositAmount)}`);
    } catch (error: any) {
      const message = error.response?.data?.message || 'Deposit failed';
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm p-8 text-center max-w-md w-full">
          <div className="h-16 w-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-8 w-8 text-success-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Deposit Successful!
          </h2>
          <p className="text-gray-600 mb-6">
            You have successfully deposited {formatCurrency(parseFloat(amount))} to your wallet.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => router.push('/dashboard')}
              className="btn-primary w-full"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => {
                setIsSuccess(false);
                setAmount('');
              }}
              className="btn-secondary w-full"
            >
              Make Another Deposit
            </button>
          </div>
        </div>
      </div>
    );
  }

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
            <h1 className="text-xl font-bold text-gray-900">Deposit Funds</h1>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Deposit Form */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Enter Amount
            </h2>
            
            <div className="mb-6">
              <label className="form-label">Amount ($)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="form-input pl-10 text-2xl font-bold"
                  placeholder="0.00"
                  min="10"
                  step="0.01"
                />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Minimum deposit: $10.00
              </p>
            </div>

            {/* Preset Amounts */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              {PRESET_AMOUNTS.map((preset) => (
                <button
                  key={preset}
                  onClick={() => setAmount(preset.toString())}
                  className={`py-2 px-4 rounded-lg border text-sm font-medium transition-colors ${
                    amount === preset.toString()
                      ? 'border-primary-600 bg-primary-50 text-primary-700'
                      : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  ${preset}
                </button>
              ))}
            </div>

            <button
              onClick={handleDeposit}
              disabled={isProcessing || !amount}
              className="btn-primary w-full"
            >
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <CreditCard className="h-5 w-5 mr-2" />
                  Deposit {amount ? formatCurrency(parseFloat(amount)) : ''}
                </>
              )}
            </button>
          </div>

          {/* Info Card */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Current Balance
              </h3>
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(user?.wallet?.balance || 0)}
              </p>
            </div>

            <div className="bg-primary-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-primary-900 mb-2">
                How Deposits Work
              </h3>
              <ul className="space-y-2 text-sm text-primary-800">
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  Deposits are processed instantly
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  No fees on deposits
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  Funds are available immediately for contributions
                </li>
                <li className="flex items-start">
                  <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  Secure and encrypted transactions
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
