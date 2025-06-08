/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Add valid theme extensions here
    },
  },
  plugins: [
    // Add custom utility classes for text formatting
    function({ addUtilities }) {
      addUtilities({
        // Word break utilities
        '.word-break-normal': { wordBreak: 'normal' },
        '.word-break-break-all': { wordBreak: 'break-all' },
        '.word-break-break-word': { wordBreak: 'break-word' },
        
        // Hyphens utilities
        '.hyphens-none': { hyphens: 'none' },
        '.hyphens-manual': { hyphens: 'manual' },
        '.hyphens-auto': { hyphens: 'auto' },
        
        // Overflow wrap utilities
        '.overflow-wrap-normal': { overflowWrap: 'normal' },
        '.overflow-wrap-break-word': { overflowWrap: 'break-word' },
        '.overflow-wrap-anywhere': { overflowWrap: 'anywhere' },
      });
    }
  ],
  future: {
    // Enable latest features
    hoverOnlyWhenSupported: true,
  }
}
