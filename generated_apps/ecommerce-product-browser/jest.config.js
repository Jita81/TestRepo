module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'backend/src/**/*.js',
    '!backend/src/server.js',
    '!backend/src/config/**',
  ],
  testMatch: [
    '**/backend/tests/**/*.test.js',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/backend/tests/setup.js'],
  testTimeout: 10000,
};