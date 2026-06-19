/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // TaxChain color system from AGENTS.md
        primary: {
          DEFAULT: '#6366F1', // brand
          light: '#EEF2FF',
        },
        gain: {
          DEFAULT: '#10B981',
          bg: '#ECFDF5',
        },
        loss: {
          DEFAULT: '#EF4444',
          bg: '#FEF2F2',
        },
        sidebar: {
          bg: '#0F172A',
          text: '#E2E8F0',
        },
        chains: {
          eth: '#627EEA',
          bnb: '#F3BA2F',
          polygon: '#8247E5',
          sol: '#9945FF',
        },
      },
      fontFamily: {
        ui: ['var(--font-ui)', 'sans-serif'],
        data: ['var(--font-data)', 'monospace'],
      },
    },
  },
  plugins: [],
}