/**
 * @jest
 * Tests for performance-utils.js
 */

import { performance } from 'perf_hooks';
global.performance = performance;

// Mock for browser APIs
global.navigator = {
  serviceWorker: {
    register: jest.fn().mockResolvedValue(true)
  }
};

// Mock the LocalLift global object
global.LocalLift = {
  config: {
    environment: 'test'
  }
};

// Import the module (this is the module path that would be used in the actual application)
const performanceUtils = require('../../public/js/performance-utils');

describe('Performance Utilities', () => {
  beforeEach(() => {
    // Reset any mocks or state
    jest.clearAllMocks();
    
    // Reset performance marks and measures
    if (typeof performance.clearMarks === 'function') {
      performance.clearMarks();
    }
    if (typeof performance.clearMeasures === 'function') {
      performance.clearMeasures();
    }
  });

  describe('Initialization', () => {
    test('should initialize successfully', () => {
      expect(performanceUtils.init).toBeDefined();
      const result = performanceUtils.init();
      expect(result).toBeTruthy();
    });

    test('should register event listeners', () => {
      // Mock document event listeners
      document.addEventListener = jest.fn();
      
      performanceUtils.init();
      
      // Verify that event listeners were registered
      expect(document.addEventListener).toHaveBeenCalledWith('DOMContentLoaded', expect.any(Function));
      expect(document.addEventListener).toHaveBeenCalledWith('load', expect.any(Function));
    });
  });

  describe('Memoization', () => {
    test('should memoize function results', () => {
      // Create a mock expensive function
      const mockFn = jest.fn(x => x * 2);
      const memoizedFn = performanceUtils.memoize(mockFn);
      
      // Call twice with the same argument
      const result1 = memoizedFn(5);
      const result2 = memoizedFn(5);
      
      // Function should be called only once
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(result1).toBe(10);
      expect(result2).toBe(10);
      
      // Call with a different argument
      const result3 = memoizedFn(10);
      
      // Function should be called again for new argument
      expect(mockFn).toHaveBeenCalledTimes(2);
      expect(result3).toBe(20);
    });
  });

  describe('Debounce', () => {
    test('should debounce function calls', () => {
      jest.useFakeTimers();
      
      const mockFn = jest.fn();
      const debouncedFn = performanceUtils.debounce(mockFn, 100);
      
      // Call multiple times
      debouncedFn();
      debouncedFn();
      debouncedFn();
      
      // Function should not be called immediately
      expect(mockFn).not.toHaveBeenCalled();
      
      // Fast-forward time
      jest.advanceTimersByTime(101);
      
      // Function should be called once
      expect(mockFn).toHaveBeenCalledTimes(1);
      
      // Clean up
      jest.useRealTimers();
    });
  });

  describe('Throttle', () => {
    test('should throttle function calls', () => {
      jest.useFakeTimers();
      
      const mockFn = jest.fn();
      const throttledFn = performanceUtils.throttle(mockFn, 100);
      
      // Call function multiple times
      throttledFn();  // Should execute immediately
      throttledFn();  // Should not execute
      throttledFn();  // Should not execute
      
      // Function should be called once
      expect(mockFn).toHaveBeenCalledTimes(1);
      
      // Fast-forward time
      jest.advanceTimersByTime(101);
      
      // Call again after cooldown
      throttledFn();
      
      // Function should be called again
      expect(mockFn).toHaveBeenCalledTimes(2);
      
      // Clean up
      jest.useRealTimers();
    });
  });

  describe('Resource Loading', () => {
    test('should preload resources', () => {
      // Mock document createElement and appendChild
      const mockLink = {
        rel: '',
        href: '',
        as: ''
      };
      
      document.createElement = jest.fn().mockReturnValue(mockLink);
      document.head.appendChild = jest.fn();
      
      // Call preloadResources
      performanceUtils.preloadResources(['/style.css']);
      
      // Verify link element was created and appended
      expect(document.createElement).toHaveBeenCalledWith('link');
      expect(mockLink.rel).toBe('preload');
      expect(mockLink.href).toBe('/style.css');
      expect(document.head.appendChild).toHaveBeenCalled();
    });
    
    test('should lazy load resources', () => {
      // Mock setTimeout
      jest.useFakeTimers();
      
      // Mock createElement and appendChild
      const mockScript = {
        src: '',
        onload: null
      };
      
      document.createElement = jest.fn().mockReturnValue(mockScript);
      document.body.appendChild = jest.fn();
      
      // Call lazyLoadResources
      performanceUtils.lazyLoadResources([
        { id: 'test', url: '/test.js', type: 'script' }
      ]);
      
      // Fast-forward time
      jest.advanceTimersByTime(1000);
      
      // Verify script element was created and appended
      expect(document.createElement).toHaveBeenCalledWith('script');
      expect(mockScript.src).toBe('/test.js');
      expect(document.body.appendChild).toHaveBeenCalled();
      
      // Clean up
      jest.useRealTimers();
    });
  });

  describe('Performance Metrics', () => {
    test('should collect performance metrics', () => {
      // Mock performance.mark and performance.measure
      performance.mark = jest.fn();
      performance.measure = jest.fn();
      
      // Call markStart
      performanceUtils.markStart('test');
      
      // Verify mark was created
      expect(performance.mark).toHaveBeenCalledWith('test:start');
      
      // Call markEnd
      performanceUtils.markEnd('test');
      
      // Verify measure was created
      expect(performance.measure).toHaveBeenCalledWith(
        'test',
        'test:start',
        'test:end'
      );
    });
    
    test('should get performance metrics', () => {
      // Mock performance.getEntriesByType
      performance.getEntriesByType = jest.fn().mockReturnValue([
        { name: 'test', duration: 100 }
      ]);
      
      // Get metrics
      const metrics = performanceUtils.getMetrics();
      
      // Verify metrics structure
      expect(metrics).toBeDefined();
      expect(metrics.measures).toContainEqual(
        expect.objectContaining({
          name: 'test',
          duration: 100
        })
      );
    });
  });

  describe('CSS Containment', () => {
    test('should apply CSS containment', () => {
      // Mock document.querySelectorAll and style setting
      const mockElements = [
        { style: {} },
        { style: {} }
      ];
      
      document.querySelectorAll = jest.fn().mockReturnValue(mockElements);
      
      // Call applyCSSContainment
      performanceUtils.applyCSSContainment(['.card', '.sidebar']);
      
      // Verify containment was applied to all elements
      expect(document.querySelectorAll).toHaveBeenCalledTimes(2);
      mockElements.forEach(element => {
        expect(element.style.contain).toBe('content');
      });
    });
  });

  describe('Idle Time Operations', () => {
    test('should execute operations during idle time', () => {
      // Mock requestIdleCallback
      window.requestIdleCallback = jest.fn(callback => {
        callback({ timeRemaining: () => 50 });
        return 123;  // Mock ID
      });
      
      const mockFn = jest.fn();
      
      // Run function during idle time
      performanceUtils.runWhenIdle(mockFn);
      
      // Verify function was called
      expect(mockFn).toHaveBeenCalled();
      expect(window.requestIdleCallback).toHaveBeenCalled();
    });
  });

  describe('Animation Optimization', () => {
    test('should create optimized animation', () => {
      // Mock requestAnimationFrame
      window.requestAnimationFrame = jest.fn(callback => {
        callback(performance.now());
        return 123;  // Mock ID
      });
      
      const mockAnimationFn = jest.fn();
      
      // Create animation
      const animation = performanceUtils.createOptimizedAnimation(mockAnimationFn);
      
      // Start animation
      animation.start();
      
      // Verify animation frame was requested
      expect(window.requestAnimationFrame).toHaveBeenCalled();
      
      // Animation callback should have been called with delta
      expect(mockAnimationFn).toHaveBeenCalledWith(expect.any(Number));
      
      // Stop animation
      animation.stop();
    });
  });
});
