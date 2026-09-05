/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        agri: {
          50: '#f2f9f0',
          100: '#e1f3dc',
          500: '#3a832e',
          600: '#2d6a23',
          700: '#25541c',
          900: '#14310f',
        }
      }
    },
  },
  plugins: [],
}
