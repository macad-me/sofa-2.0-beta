#!/usr/bin/env node

import puppeteer from 'puppeteer';

async function inspectDarkMode() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('🚀 Navigating to localhost:5174...');
    await page.goto('http://localhost:5174/', { waitUntil: 'networkidle0' });
    
    console.log('🌙 Switching to dark mode...');
    // Find and click the dark mode toggle
    const darkModeButton = await page.$('[class*="dark"]') || await page.$('button[title*="toggle"]') || await page.$('.vp-switch-appearance');
    if (darkModeButton) {
      await darkModeButton.click();
      await page.waitForTimeout(1000);
    } else {
      // Try to manually add dark class to html
      await page.evaluate(() => {
        document.documentElement.classList.add('dark');
      });
    }
    
    console.log('🔍 Inspecting bento card styling...');
    
    // Get computed styles for bento cards
    const bentoCardStyles = await page.evaluate(() => {
      const bentoCard = document.querySelector('.bento-card');
      if (!bentoCard) return { error: 'No bento-card found' };
      
      const computedStyle = window.getComputedStyle(bentoCard);
      const classList = Array.from(bentoCard.classList);
      
      return {
        element: 'bento-card',
        classes: classList,
        backgroundColor: computedStyle.backgroundColor,
        borderColor: computedStyle.borderColor,
        backdropFilter: computedStyle.backdropFilter,
        color: computedStyle.color,
        display: computedStyle.display
      };
    });
    
    console.log('📊 Bento Card Styles:', JSON.stringify(bentoCardStyles, null, 2));
    
    // Check platform navigation buttons
    const platformButtonStyles = await page.evaluate(() => {
      const platformButton = document.querySelector('a[href*="platform"]') || document.querySelector('.group');
      if (!platformButton) return { error: 'No platform button found' };
      
      const computedStyle = window.getComputedStyle(platformButton);
      const classList = Array.from(platformButton.classList);
      
      return {
        element: 'platform-button',
        classes: classList,
        backgroundColor: computedStyle.backgroundColor,
        borderColor: computedStyle.borderColor,
        color: computedStyle.color
      };
    });
    
    console.log('🎯 Platform Button Styles:', JSON.stringify(platformButtonStyles, null, 2));
    
    // Check if dark mode class is applied to HTML
    const isDarkMode = await page.evaluate(() => {
      return {
        htmlClasses: Array.from(document.documentElement.classList),
        bodyClasses: Array.from(document.body.classList),
        darkModeActive: document.documentElement.classList.contains('dark')
      };
    });
    
    console.log('🌙 Dark Mode Status:', JSON.stringify(isDarkMode, null, 2));
    
    // Get all elements with bg-white class in dark mode
    const whiteElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="bg-white"]');
      return Array.from(elements).map(el => ({
        tagName: el.tagName,
        classes: Array.from(el.classList),
        computedBg: window.getComputedStyle(el).backgroundColor
      }));
    });
    
    console.log('⚪ Elements with bg-white:', JSON.stringify(whiteElements, null, 2));
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await browser.close();
  }
}

inspectDarkMode().catch(console.error);