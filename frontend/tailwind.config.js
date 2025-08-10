/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design System Colors
        'ocean-deep': '#012A4A',
        'atlantic': '#2A6F97',
        'coastal': '#61A5C2', 
        'wave': '#89C2D9',
        'mist': '#A9D6E5',
        
        // System Colors
        'success': '#059669',
        'warning': '#D97706', 
        'error': '#DC2626',
        'neutral': '#64748B',
        
        // Legacy support (gradually migrate away from these)
        primary: {
          50: '#EEF7FA',
          100: '#A9D6E5', 
          500: '#2A6F97',
          600: '#61A5C2',
          700: '#012A4A',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6', 
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      spacing: {
        'micro': '4px',
        'small': '8px', 
        'medium': '16px',
        'large': '24px',
        'macro': '48px',
      },
      animation: {
        'fade-in': 'fade-in 300ms ease-in-out',
        'slide-up': 'slide-up 300ms ease-out',
        'slide-down': 'slide-down 300ms ease-out',
        'scale-in': 'scale-in 200ms ease-out',
        'bounce-subtle': 'bounce-subtle 600ms ease-in-out',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      }
    },
  },
  plugins: [],
}