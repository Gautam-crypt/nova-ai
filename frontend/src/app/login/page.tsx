"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export default function LoginPage() {
  const router = useRouter();
  const { loginSequence, error, setError } = useAuthStore();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const role = await loginSequence(email, password);
      if (role === "admin") {
        router.push("/admin/dashboard");
      } else {
        router.push("/dashboard/billing");
      }
    } catch (err) {
      // Error is handled in store, but we catch to stop loading
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0F] relative overflow-hidden">
      {/* Decorative background dots */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#E8E8F0 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
      
      <div className="relative w-full max-w-md">
        {/* Glow behind card */}
        <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-20"></div>
        
        <div className="relative bg-[#12121A] border border-[#1E1E2E] rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-extrabold text-[#7F77DD] tracking-[0.2em] mb-2">N O V A</h1>
            <p className="text-[#6B6B80] tracking-wide text-sm uppercase">AI Assistant</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-[#E8E8F0] text-sm font-medium mb-1">Email / Username</label>
              <input
                type="text"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setError(null); }}
                className="w-full bg-[#0A0A0F] border border-[#1E1E2E] text-white rounded-lg px-4 py-3 focus:outline-none focus:border-[#7F77DD] transition"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-[#E8E8F0] text-sm font-medium mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(null); }}
                  className="w-full bg-[#0A0A0F] border border-[#1E1E2E] text-white rounded-lg px-4 py-3 focus:outline-none focus:border-[#7F77DD] transition"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B6B80] hover:text-[#E8E8F0] transition"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" className="rounded border-[#1E1E2E] bg-[#0A0A0F] text-[#7F77DD] focus:ring-[#7F77DD]" />
                <span className="text-[#6B6B80]">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-[#7F77DD] hover:text-purple-400 transition">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#7F77DD] hover:brightness-110 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center transition disabled:opacity-70 disabled:cursor-not-allowed mt-6"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {error && (
            <div className="mt-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 text-sm animate-in slide-in-from-bottom-2">
              {error}
            </div>
          )}

          <div className="mt-8 text-center text-sm text-[#6B6B80]">
            Don't have an account? <Link href="/register" className="text-[#7F77DD] hover:text-purple-400 transition font-medium">Sign up</Link>
          </div>
        </div>

        <p className="text-center text-[#6B6B80] text-xs mt-6">
          Secure login — your data stays private
        </p>
      </div>
    </div>
  );
}
