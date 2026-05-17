/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    fontFamily: {
      sans: ['Inter', 'Segoe UI', 'Helvetica Neue', 'Arial', 'sans-serif'],
      mono: ['SFMono-Regular', 'Consolas', 'Liberation Mono', 'monospace'],
    },
    extend: {},
  },
  plugins: [],
}