/**
 * Test setup file for LocalLift
 * This file is run before each test file is executed
 */

// Set up DOM environment for testing
if (typeof window === 'undefined') {
  global.window = {};
}

// Mock browser APIs
global.document = global.document || {
  createElement: jest.fn(() => ({
    setAttribute: jest.fn(),
    style: {},
    appendChild: jest.fn()
  })),
  head: {
    appendChild: jest.fn()
  },
  body: {
    appendChild: jest.fn()
  },
  addEventListener: jest.fn(),
  querySelectorAll: jest.fn(() => [])
};

// Mock localStorage
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock sessionStorage
global.sessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    status: 200
  })
);

// Mock for requestAnimationFrame and cancelAnimationFrame
global.requestAnimationFrame = callback => setTimeout(callback, 0);
global.cancelAnimationFrame = jest.fn();

// Mock for requestIdleCallback and cancelIdleCallback
global.requestIdleCallback = callback => setTimeout(() => callback({ timeRemaining: () => 50 }), 0);
global.cancelIdleCallback = jest.fn();

// Mock for window.location
Object.defineProperty(global, 'location', {
  value: {
    href: 'http://localhost/',
    origin: 'http://localhost',
    protocol: 'http:',
    host: 'localhost',
    hostname: 'localhost',
    port: '',
    pathname: '/',
    search: '',
    hash: ''
  },
  writable: true
});

// Mock for console methods to reduce noise during tests
// Uncomment this to suppress console output during tests
/*
global.console = {
  ...console,
  log: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  debug: jest.fn()
};
*/

// Setup for LocalLift global object
global.LocalLift = global.LocalLift || {
  config: {
    environment: 'test',
    apiUrl: 'http://localhost/api'
  },
  performance: {
    init: jest.fn(() => true),
    markStart: jest.fn(),
    markEnd: jest.fn(),
    getMetrics: jest.fn(() => ({
      measures: [],
      apiCallTimes: {},
      resourceLoadTimes: {},
      pageLoadTime: 0
    })),
    memoize: jest.fn(fn => fn),
    debounce: jest.fn(fn => fn),
    throttle: jest.fn(fn => fn),
    preloadResources: jest.fn(),
    lazyLoadResources: jest.fn(),
    applyCSSContainment: jest.fn(),
    runWhenIdle: jest.fn(fn => fn()),
    createOptimizedAnimation: jest.fn(() => ({
      start: jest.fn(),
      stop: jest.fn()
    }))
  },
  analytics: {
    trackEvent: jest.fn(),
    trackPageView: jest.fn(),
    trackPerformance: jest.fn()
  }
};

// Add any custom matchers for your tests
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false
      };
    }
  }
});

// Clean up between tests
afterEach(() => {
  // Reset all mocks
  jest.clearAllMocks();
  
  // Clear any timers
  jest.clearAllTimers();
});
