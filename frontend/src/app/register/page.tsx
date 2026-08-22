"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2, User, Mail } from 'lucide-react';
import { authAPI } from '@/api/client';
import { useToastStore } from '@/stores/toastStore';

export default function RegisterPage() {
  const router = useRouter();
  const { addToast } = useToastStore();
  
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '', confirm_password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [terms, setTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inlineErrors, setInlineErrors] = useState<{ [key: string]: string }>({});

  const validate = () => {
    const errs: { [key: string]: string } = {};
    if (formData.full_name.length < 2) errs.full_name = "Name must be at least 2 characters";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) errs.email = "Invalid email format";
    if (formData.password.length < 8) errs.password = "Password must be at least 8 characters";
    if (formData.password !== formData.confirm_password) errs.confirm_password = "Passwords do not match";
    if (!terms) errs.terms = "You must agree to the Terms of Service";
    
    setInlineErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    
    setLoading(true);
    setError('');
    
    try {
      await authAPI.register({ email: formData.email, password: formData.password, full_name: formData.full_name });
      addToast("Account created! Redirecting to login...", "success");
      setTimeout(() => router.push("/login?registered=true"), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0F] relative overflow-hidden py-12">
      <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#E8E8F0 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
      
      <div className="relative w-full max-w-md">
        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-20"></div>
        
        <div className="relative bg-[#12121A] border border-[#1E1E2E] rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-extrabold text-[#E8E8F0] mb-2">Create Account</h1>
            <p className="text-[#6B6B80] text-sm">Join NOVA and get your personal AI.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-[#6B6B80]" />
                </div>
                <input
                  type="text"
                  placeholder="Full Name"
                  value={formData.full_name}
                  onChange={(e) => { setFormData({...formData, full_name: e.target.value}); setInlineErrors({...inlineErrors, full_name: ''}); }}
                  className={`w-full bg-[#0A0A0F] border ${inlineErrors.full_name ? 'border-red-500' : 'border-[#1E1E2E]'} text-white rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#7F77DD] transition`}
                />
              </div>
              {inlineErrors.full_name && <p className="text-red-400 text-xs mt-1">{inlineErrors.full_name}</p>}
            </div>

            <div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-[#6B6B80]" />
                </div>
                <input
                  type="email"
                  placeholder="Email Address"
                  value={formData.email}
                  onChange={(e) => { setFormData({...formData, email: e.target.value}); setInlineErrors({...inlineErrors, email: ''}); }}
                  className={`w-full bg-[#0A0A0F] border ${inlineErrors.email ? 'border-red-500' : 'border-[#1E1E2E]'} text-white rounded-lg pl-10 pr-4 py-3 focus:outline-none focus:border-[#7F77DD] transition`}
                />
              </div>
              {inlineErrors.email && <p className="text-red-400 text-xs mt-1">{inlineErrors.email}</p>}
            </div>

            <div>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => { setFormData({...formData, password: e.target.value}); setInlineErrors({...inlineErrors, password: ''}); }}
                  className={`w-full bg-[#0A0A0F] border ${inlineErrors.password ? 'border-red-500' : 'border-[#1E1E2E]'} text-white rounded-lg px-4 py-3 focus:outline-none focus:border-[#7F77DD] transition`}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B6B80] hover:text-[#E8E8F0] transition">
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {inlineErrors.password && <p className="text-red-400 text-xs mt-1">{inlineErrors.password}</p>}
            </div>

            <div>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Confirm Password"
                value={formData.confirm_password}
                onChange={(e) => { setFormData({...formData, confirm_password: e.target.value}); setInlineErrors({...inlineErrors, confirm_password: ''}); }}
                className={`w-full bg-[#0A0A0F] border ${inlineErrors.confirm_password ? 'border-red-500' : 'border-[#1E1E2E]'} text-white rounded-lg px-4 py-3 focus:outline-none focus:border-[#7F77DD] transition`}
              />
              {inlineErrors.confirm_password && <p className="text-red-400 text-xs mt-1">{inlineErrors.confirm_password}</p>}
            </div>

            <div>
              <label className="flex items-start space-x-2 cursor-pointer mt-2">
                <input type="checkbox" checked={terms} onChange={(e) => { setTerms(e.target.checked); setInlineErrors({...inlineErrors, terms: ''}); }} className="rounded border-[#1E1E2E] bg-[#0A0A0F] text-[#7F77DD] focus:ring-[#7F77DD] mt-1" />
                <span className="text-[#6B6B80] text-sm leading-tight">I agree to Terms of Service and Privacy Policy</span>
              </label>
              {inlineErrors.terms && <p className="text-red-400 text-xs mt-1">{inlineErrors.terms}</p>}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#7F77DD] hover:brightness-110 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center transition disabled:opacity-70 disabled:cursor-not-allowed mt-6"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : null}
              {loading ? 'Creating...' : 'Create Account'}
            </button>
          </form>

          {error && (
            <div className="mt-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 text-sm animate-in slide-in-from-bottom-2">
              {error}
            </div>
          )}

          <div className="mt-6 text-center text-sm text-[#6B6B80]">
            Already have an account? <Link href="/login" className="text-[#7F77DD] hover:text-purple-400 transition font-medium">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
