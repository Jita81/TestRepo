/**
 * Integration tests for Greeting API
 */

const request = require('supertest');
const app = require('../../src/app');

describe('Greeting API Integration Tests', () => {
  describe('GET /api/greeting', () => {
    // Acceptance Criteria Tests
    it('should return 200 and default greeting', async () => {
      const response = await request(app)
        .get('/api/greeting');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Hello!' });
      expect(response.headers['content-type']).toMatch(/json/);
    });

    it('should return 200 and personalized greeting with name parameter', async () => {
      const response = await request(app)
        .get('/api/greeting?name=John');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Hello, John!' });
    });

    it('should return Spanish greeting with 200 status code', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=es');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: '¡Hola!' });
    });

    it('should return personalized Spanish greeting', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=es&name=Juan');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: '¡Hola, Juan!' });
    });

    it('should return French greeting', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=fr');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Bonjour!' });
    });

    it('should return personalized French greeting', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=fr&name=Marie');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Bonjour, Marie!' });
    });

    it('should return 400 for invalid language code', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=xx');
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('message');
    });

    // CORS Headers Tests
    it('should include CORS headers', async () => {
      const response = await request(app)
        .get('/api/greeting');
      
      expect(response.headers['access-control-allow-origin']).toBeDefined();
    });

    // Response Format Tests
    it('should return JSON content type', async () => {
      const response = await request(app)
        .get('/api/greeting');
      
      expect(response.headers['content-type']).toMatch(/json/);
    });

    // Edge Cases Tests
    it('should handle empty name parameter', async () => {
      const response = await request(app)
        .get('/api/greeting?name=');
      
      expect(response.status).toBe(400);
    });

    it('should handle special characters in name', async () => {
      const response = await request(app)
        .get('/api/greeting?name=María-José');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Hello, María-José!' });
    });

    it('should handle names with apostrophes', async () => {
      const response = await request(app)
        .get('/api/greeting?name=O\'Brien');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: "Hello, O'Brien!" });
    });

    it('should reject very long names', async () => {
      const longName = 'A'.repeat(100);
      const response = await request(app)
        .get(`/api/greeting?name=${longName}`);
      
      expect(response.status).toBe(400);
    });

    it('should reject names with invalid characters', async () => {
      const response = await request(app)
        .get('/api/greeting?name=John123');
      
      expect(response.status).toBe(400);
    });

    it('should reject names with special symbols', async () => {
      const response = await request(app)
        .get('/api/greeting?name=John@Doe');
      
      expect(response.status).toBe(400);
    });

    it('should handle case insensitive language codes', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=ES');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: '¡Hola!' });
    });

    it('should reject invalid language code length', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=eng');
      
      expect(response.status).toBe(400);
    });

    it('should handle multiple spaces in name', async () => {
      const response = await request(app)
        .get('/api/greeting?name=John   Doe');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Hello, John Doe!' });
    });

    it('should handle Unicode characters', async () => {
      const response = await request(app)
        .get('/api/greeting?name=Björk');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Hello, Björk!' });
    });

    // Performance Test
    it('should respond within 200ms', async () => {
      const startTime = Date.now();
      await request(app).get('/api/greeting');
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeLessThan(200);
    });

    // Multiple parameter combinations
    it('should handle both lang and name parameters', async () => {
      const response = await request(app)
        .get('/api/greeting?lang=fr&name=Pierre');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ message: 'Bonjour, Pierre!' });
    });
  });

  describe('GET /api/greeting/languages', () => {
    it('should return list of supported languages', async () => {
      const response = await request(app)
        .get('/api/greeting/languages');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('languages');
      expect(response.body).toHaveProperty('count');
      expect(response.body.languages).toContain('en');
      expect(response.body.languages).toContain('es');
      expect(response.body.languages).toContain('fr');
      expect(response.body.count).toBe(3);
    });
  });

  describe('GET /health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('uptime');
    });
  });

  describe('404 Not Found', () => {
    it('should return 404 for non-existent routes', async () => {
      const response = await request(app)
        .get('/api/nonexistent');
      
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toHaveProperty('message', 'Route not found');
    });
  });

  describe('Security Headers', () => {
    it('should include security headers from helmet', async () => {
      const response = await request(app)
        .get('/api/greeting');
      
      // Helmet sets various security headers
      expect(response.headers['x-content-type-options']).toBeDefined();
    });
  });
});