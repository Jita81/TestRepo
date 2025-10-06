const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright configuration for E2E testing
 * Tests responsive design across multiple devices and breakpoints
 */
module.exports = defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:8888',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  
  // Configure projects for different devices and breakpoints
  projects: [
    // Desktop browsers
    {
      name: 'Desktop Chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'Desktop Firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    {
      name: 'Desktop Safari',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1920, height: 1080 }
      },
    },
    
    // Tablet devices
    {
      name: 'iPad',
      use: { ...devices['iPad (gen 7)'] },
    },
    {
      name: 'iPad Landscape',
      use: { ...devices['iPad (gen 7) landscape'] },
    },
    
    // Mobile devices
    {
      name: 'iPhone 12',
      use: { ...devices['iPhone 12'] },
    },
    {
      name: 'iPhone 12 Landscape',
      use: { ...devices['iPhone 12 landscape'] },
    },
    {
      name: 'iPhone SE',
      use: { 
        ...devices['iPhone SE'],
        // Test smallest supported width (320px)
      },
    },
    {
      name: 'Pixel 5',
      use: { ...devices['Pixel 5'] },
    },
    
    // Custom breakpoint tests
    {
      name: 'Mobile 320px',
      use: {
        ...devices['iPhone SE'],
        viewport: { width: 320, height: 568 }
      },
    },
    {
      name: 'Tablet 768px',
      use: {
        viewport: { width: 768, height: 1024 }
      },
    },
    {
      name: 'Desktop 1024px',
      use: {
        viewport: { width: 1024, height: 768 }
      },
    },
  ],
  
  // Run local dev server before starting tests
  webServer: {
    command: 'python3 server.py 8888',
    url: 'http://localhost:8888',
    reuseExistingServer: !process.env.CI,
    timeout: 10000,
  },
});
