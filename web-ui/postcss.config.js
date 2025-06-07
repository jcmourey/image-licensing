export default {
  plugins: {
    '@tailwindcss/postcss': {
      // Ensure v4 compatibility
      configPath: './tailwind.config.js',
    },
    autoprefixer: {},
  },
}