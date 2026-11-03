/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Supabase Signature Palette
        supabase: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#3ECF8E', // Canonical Supabase Emerald
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        dark: {
          bg: '#121212',          // Root canvas
          surface: '#181818',     // Subsurface / Table header
          panel: '#1E1E1E',       // Card / Panel background
          card: '#222222',        // Elevated card
          hover: '#282828',       // Hover row/button
          border: '#2E2E2E',      // Primary border
          borderLight: '#383838', // Elevated border
          borderSubtle: 'rgba(255, 255, 255, 0.08)',
        },
        text: {
          primary: '#EDEDED',
          secondary: '#A1A1A1',
          muted: '#6E6E6E',
          dim: '#4E4E4E',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'supabase': '0 0 0 1px rgba(255, 255, 255, 0.08), 0 4px 12px rgba(0, 0, 0, 0.5)',
        'supabase-glow': '0 0 20px -5px rgba(62, 207, 142, 0.3)',
      }
    },
  },
  plugins: [],
}
