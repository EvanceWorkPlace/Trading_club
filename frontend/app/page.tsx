'use client';

import React from 'react';
import Link from 'next/link';
import {
  Users,
  TrendingUp,
  Shield,
  Wallet,
  ArrowRight,
  CheckCircle,
  BarChart3,
  PiggyBank,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="h-10 w-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">IC</span>
              </div>
              <span className="text-xl font-bold text-gray-900">InvestClub</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="btn-primary"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-50 via-white to-primary-100 py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Invest Together,{' '}
                <span className="text-primary-600">Grow Together</span>
              </h1>
              <p className="mt-6 text-xl text-gray-600 leading-relaxed">
                Join collaborative investment groups, pool your funds with others,
                and achieve your financial goals faster through collective investing.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-4">
                <Link href="/register" className="btn-primary text-lg px-8 py-3">
                  Start Investing
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link href="/login" className="btn-secondary text-lg px-8 py-3">
                  Sign In
                </Link>
              </div>
              <div className="mt-8 flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                  <span>No fees</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                  <span>Secure</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-success-500 mr-2" />
                  <span>Transparent</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <p className="text-sm text-gray-500">Portfolio Value</p>
                    <p className="text-3xl font-bold text-gray-900">$24,500.00</p>
                  </div>
                  <div className="h-12 w-12 bg-success-100 rounded-full flex items-center justify-center">
                    <TrendingUp className="h-6 w-6 text-success-600" />
                  </div>
                </div>
                <div className="h-32 bg-gradient-to-t from-primary-100 to-primary-50 rounded-lg flex items-end justify-around p-4">
                  {[40, 65, 45, 80, 55, 90, 70].map((height, i) => (
                    <div
                      key={i}
                      className="w-8 bg-primary-500 rounded-t"
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
                <div className="mt-6 grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">5</p>
                    <p className="text-xs text-gray-500">Groups</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">12%</p>
                    <p className="text-xs text-gray-500">Avg ROI</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">$2.4k</p>
                    <p className="text-xs text-gray-500">Earnings</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">
              Why Choose InvestClub?
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              Everything you need to start collaborative investing
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center p-6">
              <div className="h-16 w-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Group Investing
              </h3>
              <p className="text-gray-600">
                Create or join investment groups with friends, family, or like-minded investors.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="h-16 w-16 bg-success-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-success-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Track Growth
              </h3>
              <p className="text-gray-600">
                Monitor your investments with real-time analytics and ROI tracking.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="h-16 w-16 bg-warning-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-warning-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Secure & Transparent
              </h3>
              <p className="text-gray-600">
                All transactions are recorded and profits distributed fairly based on contributions.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="h-16 w-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Wallet className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Virtual Wallet
              </h3>
              <p className="text-gray-600">
                Manage your funds with a built-in wallet for deposits and contributions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="mt-4 text-xl text-gray-600">
              Start investing in four simple steps
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="relative">
              <div className="h-12 w-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg mb-4">
                1
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Create Account
              </h3>
              <p className="text-gray-600">
                Sign up and verify your email to get started with InvestClub.
              </p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg mb-4">
                2
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Deposit Funds
              </h3>
              <p className="text-gray-600">
                Add money to your virtual wallet to start making contributions.
              </p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg mb-4">
                3
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Join a Group
              </h3>
              <p className="text-gray-600">
                Find or create an investment group that matches your goals.
              </p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-lg mb-4">
                4
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Earn Returns
              </h3>
              <p className="text-gray-600">
                Watch your investments grow and receive profit shares at maturity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Start Investing Together?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Join thousands of investors who are growing their wealth collaboratively.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center px-8 py-4 bg-white text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
          >
            Create Free Account
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">IC</span>
                </div>
                <span className="text-lg font-bold text-white">InvestClub</span>
              </div>
              <p className="text-sm">
                Collaborative investment platform for group investing and wealth building.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/features" className="hover:text-white">
                    Features
                  </Link>
                </li>
                <li>
                  <Link href="/pricing" className="hover:text-white">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link href="/security" className="hover:text-white">
                    Security
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/about" className="hover:text-white">
                    About
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="hover:text-white">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/careers" className="hover:text-white">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/terms" className="hover:text-white">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link href="/privacy" className="hover:text-white">
                    Privacy Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>&copy; {new Date().getFullYear()} InvestClub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
