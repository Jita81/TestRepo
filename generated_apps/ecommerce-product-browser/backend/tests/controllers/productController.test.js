const request = require('supertest');
const { app } = require('../../src/server');
const ProductService = require('../../src/services/ProductService');

jest.mock('../../src/services/ProductService');

describe('Product Controller', () => {
  const mockProducts = {
    items: [
      {
        id: '1',
        name: 'Test Product',
        price: 29.99,
        category: 'electronics',
      },
    ],
    pagination: {
      total: 1,
      page: 1,
      limit: 20,
      totalPages: 1,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /api/v1/products', () => {
    it('should return products with pagination', async () => {
      ProductService.getProducts.mockResolvedValue(mockProducts);

      const response = await request(app)
        .get('/api/v1/products')
        .expect(200);

      expect(response.body).toEqual(mockProducts);
      expect(ProductService.getProducts).toHaveBeenCalled();
    });

    it('should handle query parameters', async () => {
      ProductService.getProducts.mockResolvedValue(mockProducts);

      await request(app)
        .get('/api/v1/products?page=1&limit=20&category=electronics')
        .expect(200);

      expect(ProductService.getProducts).toHaveBeenCalledWith(
        expect.objectContaining({
          page: 1,
          limit: 20,
          category: 'electronics',
        }),
      );
    });

    it('should validate query parameters', async () => {
      const response = await request(app)
        .get('/api/v1/products?page=-1')
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });
  });

  describe('GET /api/v1/products/:id', () => {
    it('should return a single product', async () => {
      const mockProduct = { id: '1', name: 'Test Product' };
      ProductService.getProductById.mockResolvedValue(mockProduct);

      const response = await request(app)
        .get('/api/v1/products/1')
        .expect(200);

      expect(response.body).toEqual(mockProduct);
    });

    it('should return 404 for non-existent product', async () => {
      ProductService.getProductById.mockResolvedValue(null);

      await request(app)
        .get('/api/v1/products/999')
        .expect(404);
    });
  });
});