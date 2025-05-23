/**
 * Format date string to readable format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
export const formatDate = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Calculate interview duration in minutes
 * @param {string} startTime - Start time ISO string
 * @param {string} endTime - End time ISO string
 * @returns {number} - Duration in minutes
 */
export const calculateDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return 0;
  
  const start = new Date(startTime);
  const end = new Date(endTime);
  const durationMs = end - start;
  
  return Math.round(durationMs / (1000 * 60));
};

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Generate score color based on value
 * @param {number} score - Score value (0-100)
 * @returns {string} - CSS color class
 */
export const getScoreColorClass = (score) => {
  if (score >= 80) return 'text-success';
  if (score >= 60) return 'text-info';
  if (score >= 40) return 'text-warning';
  return 'text-danger';
};

/**
 * Convert experience level ID to readable text
 * @param {string} level - Experience level ID
 * @returns {string} - Readable text
 */
export const formatExperienceLevel = (level) => {
  const levels = {
    entry: 'Entry Level (0-2 years)',
    mid: 'Mid Level (3-5 years)',
    senior: 'Senior Level (6-9 years)',
    expert: 'Expert Level (10+ years)'
  };
  
  return levels[level] || level;
};

/**
 * Generate a random color from a list of preset colors
 * @returns {string} - Hex color code
 */
export const getRandomColor = () => {
  const colors = [
    '#3498db', // blue
    '#2ecc71', // green
    '#e74c3c', // red
    '#f39c12', // orange
    '#9b59b6', // purple
    '#1abc9c', // turquoise
    '#d35400', // pumpkin
    '#2c3e50'  // dark blue
  ];
  
  return colors[Math.floor(Math.random() * colors.length)];
};

/**
 * Convert markdown to plain text
 * @param {string} markdown - Markdown content
 * @returns {string} - Plain text
 */
export const markdownToPlainText = (markdown) => {
  if (!markdown) return '';
  
  // Remove headers
  let text = markdown.replace(/#{1,6}\s?([^\n]+)/g, '$1\n');
  
  // Remove emphasis
  text = text.replace(/(\*\*|__)(.*?)\1/g, '$2');
  text = text.replace(/(\*|_)(.*?)\1/g, '$2');
  
  // Remove links
  text = text.replace(/\[(.*?)\]\(.*?\)/g, '$1');
  
  // Remove blockquotes
  text = text.replace(/^\>\s?(.*)$/gm, '$1');
  
  // Remove lists
  text = text.replace(/^\s*[\*\-\+]\s+(.*)$/gm, '$1');
  text = text.replace(/^\s*\d+\.\s+(.*)$/gm, '$1');
  
  // Remove code blocks
  text = text.replace(/```[\s\S]*?```/g, '');
  text = text.replace(/`([^`]+)`/g, '$1');
  
  // Remove horizontal rules
  text = text.replace(/^\s*[\-=_]{3,}\s*$/gm, '');
  
  // Remove extra whitespace
  text = text.replace(/\n{3,}/g, '\n\n');
  
  return text.trim();
};
