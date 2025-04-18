/**
 * Jest configuration file for LocalLift
 */

module.exports = {
  // The root directory that Jest should scan for tests and modules
  rootDir: '.',
  
  // The test environment that will be used for testing
  testEnvironment: 'jsdom',
  
  // A list of paths to directories that Jest should use to search for files in
  roots: [
    '<rootDir>/tests/js'
  ],
  
  // The glob patterns Jest uses to detect test files
  testMatch: [
    '**/__tests__/**/*.js?(x)',
    '**/?(*.)+(spec|test).js?(x)'
  ],
  
  // An array of regexp pattern strings that are matched against all test paths
  // tests that match these patterns will be skipped
  testPathIgnorePatterns: [
    '/node_modules/'
  ],
  
  // An array of regexp pattern strings that are matched against all source file paths
  // before re-running tests related to the updated files
  watchPathIgnorePatterns: [
    '/node_modules/'
  ],
  
  // Indicates whether each individual test should be reported during the run
  verbose: true,
  
  // Automatically clear mock calls and instances between every test
  clearMocks: true,
  
  // Indicates whether the coverage information should be collected while executing the test
  collectCoverage: true,
  
  // The directory where Jest should output its coverage files
  coverageDirectory: 'coverage',
  
  // An array of regexp pattern strings used to skip coverage collection
  coveragePathIgnorePatterns: [
    '/node_modules/'
  ],
  
  // A list of reporter names that Jest uses when writing coverage reports
  coverageReporters: [
    'json',
    'text',
    'lcov',
    'clover'
  ],
  
  // A map from regular expressions to module names that allow to stub out resources
  moduleNameMapper: {
    // Handle CSS imports (with CSS modules)
    '^.+\\.module\\.(css|sass|scss)$': 'identity-obj-proxy',
    
    // Handle CSS imports (without CSS modules)
    '^.+\\.(css|sass|scss)$': '<rootDir>/__mocks__/styleMock.js',
    
    // Handle image imports
    '^.+\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
    
    // Handle module aliases
    '^@/(.*)$': '<rootDir>/public/$1'
  },
  
  // Transform files with babel-jest
  transform: {
    '^.+\\.jsx?$': 'babel-jest'
  },
  
  // Setup files after environment is set up
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup.js'
  ],
  
  // Test timeout in milliseconds
  testTimeout: 10000,
  
  // A list of paths to modules that run some code to configure or set up the testing environment
  setupFiles: [],
  
  // Separate test suites for unit and integration tests
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/tests/js/**/*.test.js'],
      testPathIgnorePatterns: [
        '<rootDir>/tests/js/service-worker.test.js'
      ]
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/js/service-worker.test.js']
    }
  ]
};
