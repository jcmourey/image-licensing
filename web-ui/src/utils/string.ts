/**
 * String utility functions
 */

/**
 * Truncates a string with ellipsis in the middle if it exceeds the max length
 * @param str - The string to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated string with ellipsis in the middle
 */
export function truncateMiddle(str: string, maxLength: number): string {
  if (!str || str.length <= maxLength) {
    return str;
  }
  
  const ellipsis = '...';
  const charsToShow = maxLength - ellipsis.length;
  const frontChars = Math.ceil(charsToShow / 2);
  const backChars = Math.floor(charsToShow / 2);
  
  return str.substring(0, frontChars) + ellipsis + str.substring(str.length - backChars);
}

/**
 * Formats a URL for display by removing protocol and trailing slashes
 * @param url - The URL to format
 * @returns Formatted URL string
 */
export function formatUrl(url: string | null): string {
  if (!url) return '';
  
  // Remove protocol (http://, https://, etc.)
  let formatted = url.replace(/^(https?:\/\/)?(www\.)?/, '');
  
  // Remove trailing slash
  formatted = formatted.replace(/\/$/, '');
  
  return formatted;
}

/**
 * Extracts just the domain name from a URL
 * @param url - The URL to extract domain from
 * @returns Domain name (e.g., "example.com")
 */
export function getDomain(url: string | null): string {
  if (!url) return '';
  
  try {
    // Create a URL object to parse the URL properly
    const urlObj = new URL(url);
    // Return just the hostname without www. prefix
    return urlObj.hostname.replace(/^www\./, '');
  } catch (e) {
    // If URL parsing fails, try regex-based extraction
    const match = url.match(/^(?:https?:\/\/)?(?:www\.)?([^\/\?]+)/i);
    return match ? match[1] : url;
  }
}
