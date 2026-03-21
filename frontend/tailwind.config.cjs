/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        heading: ['Merriweather', 'serif'],
      },
      colors: {
        brand: {
          50: '#ebf8f7',
          100: '#c5ece7',
          200: '#9ae0d6',
          300: '#67d1c2',
          400: '#39b6a6',
          500: '#228f82',
          600: '#1c766b',
          700: '#1b5e56',
          800: '#1b4b45',
          900: '#173e3a',
        },
        accent: {
          100: '#fff4e8',
          200: '#ffe2be',
          300: '#ffcc93',
          400: '#ffb166',
          500: '#f18d35',
          600: '#d47321',
          700: '#ad5a1b',
          800: '#874717',
          900: '#6e3a16',
        },
      },
      boxShadow: {
        surface: '0 18px 35px -18px rgba(23, 62, 58, 0.35)',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.45s ease-out both',
      },
    },
  },
  plugins: [],
};
