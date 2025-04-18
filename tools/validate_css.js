/**
 * CSS Validation Script for LocalLift
 * 
 * This script validates the integrity of CSS files, checking for issues that might 
 * indicate problems with the Tailwind build process. It can be run as part of the
 * build process or manually to diagnose styling issues.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CSS_SOURCE_PATH = path.join(__dirname, '..', 'frontend', 'styles', 'tailwind.css');
const CSS_OUTPUT_PATH = path.join(__dirname, '..', 'public', 'style.css');
const CRITICAL_SELECTORS = [
  '.container', '.flex', '.grid', '.hidden', '.md\\:flex', 
  '.text-center', '.text-primary-500', '.text-lg', '.text-xl',
  '.font-bold', '.rounded-lg', '.bg-white', '.bg-primary-500',
  '.py-2', '.px-4', '.mt-4', '.mb-4', '.space-x-4'
];

// Min expected file size - CSS should be substantial after Tailwind processing
const MIN_EXPECTED_SIZE = 10000; // bytes

/**
 * Check if CSS file exists and has minimum expected size
 */
function checkFileIntegrity(filePath) {
  console.log(`Checking CSS file integrity: ${filePath}`);
  
  if (!fs.existsSync(filePath)) {
    console.error(`❌ ERROR: File does not exist: ${filePath}`);
    return false;
  }
  
  const stats = fs.statSync(filePath);
  if (stats.size < MIN_EXPECTED_SIZE) {
    console.error(`❌ WARNING: CSS file is suspiciously small (${stats.size} bytes)`);
    console.error('   This might indicate a problem with the Tailwind build process.');
    return false;
  }
  
  console.log(`✅ File exists and has expected size (${stats.size} bytes)`);
  return true;
}

/**
 * Check if critical CSS selectors are present in the built CSS file
 */
function checkCriticalSelectors(filePath) {
  console.log('\nChecking for critical CSS selectors:');
  
  const cssContent = fs.readFileSync(filePath, 'utf8');
  const missingSelectors = [];
  
  for (const selector of CRITICAL_SELECTORS) {
    // For simplicity, just check if the string is present
    // A more robust solution would use CSS parsing
    if (!cssContent.includes(selector) && !cssContent.includes(selector.replace('\\\\', '\\'))) {
      missingSelectors.push(selector);
    }
  }
  
  if (missingSelectors.length > 0) {
    console.error(`❌ ERROR: Missing ${missingSelectors.length} critical CSS selectors:`);
    missingSelectors.forEach(selector => console.error(`   - ${selector}`));
    return false;
  }
  
  console.log(`✅ All ${CRITICAL_SELECTORS.length} critical selectors found`);
  return true;
}

/**
 * Create backup of CSS file
 */
function backupCssFile(filePath) {
  const backupPath = `${filePath}.backup`;
  console.log(`\nCreating backup: ${backupPath}`);
  
  try {
    fs.copyFileSync(filePath, backupPath);
    console.log('✅ Backup created successfully');
    return true;
  } catch (error) {
    console.error(`❌ ERROR creating backup: ${error.message}`);
    return false;
  }
}

/**
 * Main validation function
 */
function validateCss() {
  console.log('====================================');
  console.log('LocalLift CSS Validation');
  console.log('====================================\n');
  
  // Check if source file exists
  if (!fs.existsSync(CSS_SOURCE_PATH)) {
    console.error(`❌ ERROR: Source CSS file not found: ${CSS_SOURCE_PATH}`);
    process.exit(1);
  }
  
  // Validate output file
  const fileIntegrityOk = checkFileIntegrity(CSS_OUTPUT_PATH);
  const selectorsOk = checkCriticalSelectors(CSS_OUTPUT_PATH);
  
  if (fileIntegrityOk && selectorsOk) {
    console.log('\n✅ CSS validation passed!');
    
    // Create backup of valid CSS
    backupCssFile(CSS_OUTPUT_PATH);
  } else {
    console.error('\n❌ CSS validation failed!');
    console.log('\nTroubleshooting steps:');
    console.log('1. Check that Tailwind CSS is properly installed');
    console.log('2. Verify that the build command is correctly configured');
    console.log('3. Ensure the tailwind.config.js file is properly set up');
    console.log('4. Check for syntax errors in the source CSS file');
    console.log('5. Consider running with --debug flag: NODE_ENV=development npx tailwindcss --debug -i ./frontend/styles/tailwind.css -o ./public/style.css');
    
    // Only exit with error code if run in CI environment
    if (process.env.CI === 'true') {
      process.exit(1);
    }
  }
}

// Execute validation
validateCss();
