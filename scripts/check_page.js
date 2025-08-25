import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Listen for console messages
  page.on('console', msg => {
    console.log(`Browser console [${msg.type()}]:`, msg.text());
  });
  
  // Listen for page errors
  page.on('pageerror', err => {
    console.log('Page error:', err.message);
  });
  
  // Listen for failed requests
  page.on('requestfailed', request => {
    console.log('Failed request:', request.url(), '-', request.failure().errorText);
  });
  
  // Log successful requests
  page.on('response', response => {
    if (response.url().includes('.json')) {
      console.log(`JSON request: ${response.url()} - Status: ${response.status()}`);
    }
  });
  
  try {
    console.log('Navigating to http://localhost:5175/sofa-2.0/');
    const response = await page.goto('http://localhost:5175/sofa-2.0/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    console.log('Page status:', response.status());
    
    // Wait a bit for Vue components to mount
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check if SOFADashboard component exists
    const dashboardExists = await page.evaluate(() => {
      return document.querySelector('.dashboard-container') !== null;
    });
    console.log('SOFADashboard component found:', dashboardExists);
    
    // Check loading state
    const loadingText = await page.evaluate(() => {
      const loadingEl = document.querySelector('.loading-state');
      return loadingEl ? loadingEl.textContent : null;
    });
    if (loadingText) {
      console.log('Loading state:', loadingText);
    }
    
    // Check if data loaded
    const hasData = await page.evaluate(() => {
      const content = document.querySelector('.bento-grid');
      return content !== null;
    });
    console.log('Bento grid loaded:', hasData);
    
    // Check for SOFA header
    const sofaHeader = await page.evaluate(() => {
      const header = document.querySelector('.sofa-header');
      return header ? header.textContent.includes('SOFA') : false;
    });
    console.log('SOFA header found:', sofaHeader);
    
    // Get any security alerts
    const securityAlert = await page.evaluate(() => {
      const alert = document.querySelector('.security-alert');
      return alert ? alert.textContent.trim() : null;
    });
    if (securityAlert) {
      console.log('Security alert:', securityAlert);
    }
    
    // Get first release card info
    const firstRelease = await page.evaluate(() => {
      const card = document.querySelector('.release-card');
      if (!card) return null;
      return {
        platform: card.querySelector('.platform-name')?.textContent,
        version: card.querySelector('.release-version')?.textContent,
        build: card.querySelector('.release-build')?.textContent
      };
    });
    if (firstRelease) {
      console.log('First release card:', firstRelease);
    }
    
    // Check for any error messages
    const errors = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.error, .warning, [class*="error"]'))
        .map(el => el.textContent)
        .filter(text => text && text.length < 200);
    });
    if (errors.length > 0) {
      console.log('Error messages found:', errors);
    }
    
  } catch (error) {
    console.error('Navigation error:', error.message);
  }
  
  await browser.close();
})();