/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./shop1/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'space-black': '#0d0907',
        'space-dark':  '#160d06',
        'glow-orange': '#c8965c',
        'glow-amber':  '#a0714a',
        'soft-light':  '#f5ede4',
        'space-text':  '#f5ede4',
      }
    }
  },
  plugins: [],
}
