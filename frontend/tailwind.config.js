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
        // Brand
        primary: {
          DEFAULT: '#6366F1',
          light: '#EEF2FF',
          dim: 'rgba(99, 102, 241, 0.1)',
        },
        gain: {
          DEFAULT: '#10B981',
          bg: '#ECFDF5',
          dim: 'rgba(16, 185, 129, 0.1)',
        },
        loss: {
          DEFAULT: '#EF4444',
          bg: '#FEF2F2',
        },
        // Dark void theme (from TaxChain.html)
        void: '#010204',
        surface: '#070913',
        panel: '#0d1120',
        glass: 'rgba(13, 17, 32, 0.5)',
        'border-dim': 'rgba(255, 255, 255, 0.05)',
        'border-glow': 'rgba(99, 102, 241, 0.2)',
        // Text
        'text-main': '#ffffff',
        'text-muted': '#94a3b8',
        'text-faint': '#475569',
        // Sidebar (kept for dashboard)
        sidebar: {
          bg: '#0F172A',
          text: '#E2E8F0',
        },
        // Chain colors — all 8
        chains: {
          eth: '#627EEA',
          bnb: '#F3BA2F',
          polygon: '#8247E5',
          sol: '#9945FF',
          arbitrum: '#28A0F0',
          optimism: '#FF0420',
          base: '#0052FF',
          btc: '#F7931A',
        },
      },
      fontFamily: {
        ui: ['var(--font-ui)', 'sans-serif'],
        data: ['var(--font-data)', 'monospace'],
      },
      backgroundImage: {
        'text-gradient': 'linear-gradient(180deg, #fff 0%, #64748b 100%)',
        'ambient-core': 'radial-gradient(ellipse at center, rgba(99,102,241,0.08), transparent 70%)',
      },
    },
  },
  plugins: [],
}
