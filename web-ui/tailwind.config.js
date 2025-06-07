/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // Tailwind CSS v4 syntax
  theme: {
    extend: {
      wordBreak: {
        'normal': 'normal',
        'break-all': 'break-all',
        'break-word': 'break-word',
      },
      hyphens: {
        'none': 'none',
        'manual': 'manual',
        'auto': 'auto',
      },
      overflow: {
        'wrap-normal': 'normal',
        'wrap-break-word': 'break-word',
        'wrap-anywhere': 'anywhere',
      },
    },
  },
  // v4 plugins format
  plugins: {
    // Add any Tailwind plugins here
  },
  // v4 specific settings
  future: {
    // Enable latest features
    hoverOnlyWhenSupported: true,
  },
  // Disable class sorting for more deterministic output
  classAttributes: ['class', 'className'],
}
