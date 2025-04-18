/**
 * @jest
 * Integration tests for service-worker.js
 * 
 * Note: These tests are designed to run with Jest and Puppeteer
 * To run these tests, you'll need to install Puppeteer:
 * npm install --save-dev puppeteer
 */

const puppeteer = require('puppeteer');
const path = require('path');
const http = require('http');
const fs = require('fs');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);

// Local test server setup
const PORT = 3000;
let server;
let browser;
let page;
let serverRoot = path.join(__dirname, '../../public');

describe('Service Worker Integration Tests', () => {
  // Start a local server and launch browser before tests
  beforeAll(async () => {
    // Create a simple static file server
    server = http.createServer(async (req, res) => {
      try {
        // Default to index.html for root requests
        let filePath = req.url === '/' ? '/index.html' : req.url;
        
        // Check if service worker is requested
        if (filePath === '/service-worker.js') {
          filePath = '/service-worker.js';
        }
        
        const data = await readFile(path.join(serverRoot, filePath));
        
        // Set appropriate content type
        const ext = path.extname(filePath);
        let contentType = 'text/html';
        
        if (ext === '.js') contentType = 'application/javascript';
        else if (ext === '.css') contentType = 'text/css';
        else if (ext === '.json') contentType = 'application/json';
        else if (ext === '.png') contentType = 'image/png';
        else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
        
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
      } catch (err) {
        if (err.code === 'ENOENT') {
          res.writeHead(404);
          res.end('File not found');
        } else {
          res.writeHead(500);
          res.end('Server error');
        }
      }
    });
    
    server.listen(PORT);
    
    // Launch browser
    browser = await puppeteer.launch({
      headless: true,
      args: ['--disable-web-security'] // Allow service worker in this context
    });
    
    page = await browser.newPage();
  });
  
  // Cleanup after tests
  afterAll(async () => {
    await browser.close();
    server.close();
  });
  
  test('Service worker should register successfully', async () => {
    // Navigate to the local test page
    await page.goto(`http://localhost:${PORT}/`);
    
    // Wait for service worker to register
    await page.waitForFunction(() => {
      return navigator.serviceWorker && navigator.serviceWorker.controller != null;
    }, { timeout: 5000 });
    
    // Check if service worker is active
    const isServiceWorkerActive = await page.evaluate(() => {
      return navigator.serviceWorker.controller !== null;
    });
    
    expect(isServiceWorkerActive).toBe(true);
  });
  
  test('Service worker should cache static assets', async () => {
    // Navigate to the test page
    await page.goto(`http://localhost:${PORT}/`);
    
    // Wait for service worker to register
    await page.waitForFunction(() => 
      navigator.serviceWorker && navigator.serviceWorker.controller != null
    );
    
    // Add a test for cache storage
    const cacheContents = await page.evaluate(async () => {
      const cacheNames = await caches.keys();
      const staticCacheName = cacheNames.find(name => name.includes('static'));
      
      if (!staticCacheName) return null;
      
      const cache = await caches.open(staticCacheName);
      const keys = await cache.keys();
      return keys.map(request => request.url);
    });
    
    // Verify that at least some assets were cached
    expect(cacheContents).not.toBeNull();
    expect(cacheContents.length).toBeGreaterThan(0);
  });
  
  test('Service worker should handle offline access', async () => {
    // First, navigate to the page and let service worker initialize
    await page.goto(`http://localhost:${PORT}/`);
    
    // Wait for service worker to register
    await page.waitForFunction(() => 
      navigator.serviceWorker && navigator.serviceWorker.controller != null
    );
    
    // Emulate offline mode
    await page.setOfflineMode(true);
    
    // Try to navigate to the page again
    const response = await page.goto(`http://localhost:${PORT}/`);
    
    // Even in offline mode, we should get a successful response
    // because service worker should serve cached version
    expect(response.status()).toBe(200);
    
    // Reset offline mode
    await page.setOfflineMode(false);
  });
  
  test('Service worker should handle API requests when offline', async () => {
    // Setup a mock API endpoint
    server.on('request', (req, res) => {
      if (req.url.includes('/api/')) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', data: 'test data' }));
      }
    });
    
    // Navigate to the page and let service worker initialize
    await page.goto(`http://localhost:${PORT}/`);
    
    // Wait for service worker to register
    await page.waitForFunction(() => 
      navigator.serviceWorker && navigator.serviceWorker.controller != null
    );
    
    // Make an API request to cache it
    await page.evaluate(async () => {
      await fetch('/api/test');
    });
    
    // Emulate offline mode
    await page.setOfflineMode(true);
    
    // Try to make the same API request while offline
    const offlineResponse = await page.evaluate(async () => {
      const response = await fetch('/api/test');
      return {
        ok: response.ok,
        status: response.status,
        data: await response.json()
      };
    });
    
    // Verify that we get data even while offline
    expect(offlineResponse.ok).toBe(true);
    expect(offlineResponse.data).toBeDefined();
    
    // Reset offline mode
    await page.setOfflineMode(false);
  });
});
