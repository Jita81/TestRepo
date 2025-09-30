/**
 * Constants for the greeting API
 */

const SUPPORTED_LANGUAGES = {
  en: {
    default: 'Hello!',
    withName: 'Hello, {name}!'
  },
  es: {
    default: '¡Hola!',
    withName: '¡Hola, {name}!'
  },
  fr: {
    default: 'Bonjour!',
    withName: 'Bonjour, {name}!'
  }
};

const MAX_NAME_LENGTH = 50;

// Valid Unicode pattern for names: letters, spaces, hyphens, and apostrophes
const NAME_PATTERN = /^[\p{L}\s'-]+$/u;

module.exports = {
  SUPPORTED_LANGUAGES,
  MAX_NAME_LENGTH,
  NAME_PATTERN
};