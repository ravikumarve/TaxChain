'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { authApi } from '@/lib/api'

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      // Call login API using the configured client
      const response = await authApi.login(formData.email, formData.password)
      
      // Store tokens
      localStorage.setItem('accessToken', response.data.access_token)
      localStorage.setItem('refreshToken', response.data.refresh_token)
      
      // Redirect to dashboard
      window.location.href = '/dashboard'
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-6">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Sign in to TaxChain
          </h2>
          <p className="text-center text-gray-600 mt-2">
            Access your crypto portfolio and tax reports
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Enter your password"
            />
          </div>
          
          <div>
            <Button
              type="submit"
              isLoading={isLoading}
              className="w-full"
            >
              Sign in
            </Button>
          </div>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link href="/auth/signup" className="text-primary hover:text-primary/80 font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}