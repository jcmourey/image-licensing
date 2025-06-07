/**
 * Application configuration
 * 
 * This module manages configuration settings including environment variables
 * with sensible defaults for local development.
 */

// Feature flags
export const config = {
  // Set to true to show a Tailwind CSS test component for styling verification
  showTailwindTest: import.meta.env.VITE_SHOW_TAILWIND_TEST === 'true',
};

// Helper to get the environment
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;
