/**
 * Greeting routes
 * Defines endpoints for greeting operations
 */

const express = require('express');
const router = express.Router();
const greetingService = require('../services/greetingService');
const { validateGreetingRequest } = require('../middleware/validator');

/**
 * GET /api/greeting
 * Returns a greeting message
 * 
 * Query parameters:
 * - lang: Language code (optional, default: 'en')
 * - name: Name for personalized greeting (optional)
 * 
 * Responses:
 * - 200: Successful greeting
 * - 400: Invalid request parameters
 * - 429: Rate limit exceeded
 */
router.get('/', validateGreetingRequest, async (req, res, next) => {
  try {
    const { lang = 'en', name = '' } = req.query;
    
    // Get greeting from service
    const greeting = greetingService.getGreeting(lang, name);
    
    // Return successful response
    res.status(200).json(greeting);
  } catch (error) {
    // Pass error to error handler middleware
    next(error);
  }
});

/**
 * GET /api/greeting/languages
 * Returns list of supported languages
 * 
 * Responses:
 * - 200: List of supported languages
 */
router.get('/languages', (req, res) => {
  const languages = greetingService.getSupportedLanguages();
  res.status(200).json({
    languages,
    count: languages.length
  });
});

module.exports = router;