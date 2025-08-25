import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  console.log('Navigating to dashboard...');
  await page.goto('http://localhost:5175/sofa-2.0/', {
    waitUntil: 'networkidle2',
    timeout: 30000
  });
  
  // Wait for data to load
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Extract the actual displayed data
  const displayedData = await page.evaluate(() => {
    const results = {};
    
    // Get all text containing "macOS" followed by a version
    const allText = document.body.innerText;
    const macosMatch = allText.match(/macOS\s+([\d.]+)/);
    if (macosMatch) {
      results.macOS = macosMatch[1];
    }
    
    // Get iOS version
    const iosMatch = allText.match(/iOS\s+([\d.]+)/);
    if (iosMatch) {
      results.iOS = iosMatch[1];
    }
    
    // Get Safari version
    const safariMatch = allText.match(/Safari\s+([\d.]+)/);
    if (safariMatch) {
      results.Safari = safariMatch[1];
    }
    
    // Get watchOS version
    const watchMatch = allText.match(/watchOS\s+([\d.]+)/);
    if (watchMatch) {
      results.watchOS = watchMatch[1];
    }
    
    // Get beta versions
    const betaMacMatch = allText.match(/macOS\s+(26\s+beta\s+\d+)/);
    if (betaMacMatch) {
      results.macOSBeta = betaMacMatch[1];
    }
    
    const betaIOSMatch = allText.match(/iOS\s+(26\s+beta\s+\d+)/);
    if (betaIOSMatch) {
      results.iOSBeta = betaIOSMatch[1];
    }
    
    return results;
  });
  
  console.log('\n=== Data Currently Displayed on Dashboard ===');
  console.log(JSON.stringify(displayedData, null, 2));
  
  // Now fetch the bulletin data to compare
  const bulletinResponse = await page.evaluate(() => {
    return fetch('/sofa-2.0/v1/bulletin_data.json').then(r => r.json());
  });
  
  console.log('\n=== Expected Data from bulletin_data.json ===');
  console.log('macOS version:', bulletinResponse.latest_releases.macos.version);
  console.log('iOS version:', bulletinResponse.latest_releases.ios.version);
  console.log('watchOS version:', bulletinResponse.latest_releases.watchos.version);
  console.log('Safari version:', bulletinResponse.recent_releases.find(r => r.platform === 'safari')?.version);
  console.log('macOS Beta:', bulletinResponse.beta_releases.macos.version);
  console.log('iOS Beta:', bulletinResponse.beta_releases.ios.version);
  
  console.log('\n=== Verification ===');
  const macosMatch = displayedData.macOS?.includes(bulletinResponse.latest_releases.macos.version);
  const iosMatch = displayedData.iOS?.includes(bulletinResponse.latest_releases.ios.version);
  console.log('macOS data matches bulletin:', macosMatch ? '✅' : '❌');
  console.log('iOS data matches bulletin:', iosMatch ? '✅' : '❌');
  
  await browser.close();
})();