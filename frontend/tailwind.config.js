/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          cyan: '#00f3ff',
          neon: '#00ff66',
          alert: '#ff0055',
          warning: '#ffaa00',
          purple: '#a855f7',
          dark: '#060810',
          panel: 'rgba(10, 16, 26, 0.85)',
          border: 'rgba(0, 243, 255, 0.35)',
          glow: 'rgba(0, 243, 255, 0.6)'
        }
      },
      fontFamily: {
        mono: ['"Share Tech Mono"', '"JetBrains Mono"', 'monospace'],
        hud: ['"Orbitron"', '"Rajdhani"', 'sans-serif']
      }
    },
  },
  plugins: [],
}
