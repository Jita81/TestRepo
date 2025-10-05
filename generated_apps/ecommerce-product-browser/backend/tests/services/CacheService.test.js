const CacheService = require('../../src/services/CacheService');

describe('CacheService', () => {
  describe('generateKey', () => {
    it('should generate consistent cache keys', () => {
      const params = { page: 1, limit: 20 };
      const key1 = CacheService.generateKey('products', params);
      const key2 = CacheService.generateKey('products', params);
      
      expect(key1).toBe(key2);
      expect(key1).toContain('ecommerce:products:');
    });

    it('should generate different keys for different params', () => {
      const key1 = CacheService.generateKey('products', { page: 1 });
      const key2 = CacheService.generateKey('products', { page: 2 });
      
      expect(key1).not.toBe(key2);
    });
  });

  describe('get/set operations', () => {
    it('should return null when Redis is not available', async () => {
      const result = await CacheService.get('test-key');
      expect(result).toBeNull();
    });

    it('should return false when Redis is not available for set', async () => {
      const result = await CacheService.set('test-key', { data: 'test' });
      expect(result).toBe(false);
    });
  });
});