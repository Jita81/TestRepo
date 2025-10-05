module.exports = {
  projects: [
    {
      displayName: 'backend',
      testEnvironment: 'node',
      testMatch: ['**/backend/tests/**/*.test.js'],
      setupFilesAfterEnv: ['<rootDir>/backend/tests/setup.js'],
    },
  ],
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'backend/src/**/*.js',
    '!backend/src/server.js',
  ],
  testTimeout: 10000,
  verbose: true,
};