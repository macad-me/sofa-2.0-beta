#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

/**
 * CSS Mapping Tool for Tailwind 3 → 4 Migration
 * 
 * Analyzes current working Tailwind 3 CSS and creates:
 * 1. Complete @apply directive mapping
 * 2. Tailwind 4 compatibility report
 * 3. Conversion strategy recommendations
 */

const CURRENT_CSS_FILE = 'docs/.vitepress/theme/bento-system.css';
const OUTPUT_FILE = 'TAILWIND-CSS-MAPPING.md';

// Tailwind 4 incompatible utilities
const INCOMPATIBLE_UTILITIES = [
  'hover:bg-opacity-20',
  'bg-opacity-',
  'text-opacity-',
  'border-opacity-',
];

// Utilities that need special handling in Tailwind 4
const SPECIAL_HANDLING = {
  'backdrop-filter': 'backdrop-blur-sm/md/lg',
  'filter': 'blur-*/brightness-*/contrast-*',
};

function analyzeCSSFile() {
  console.log('🔍 Analyzing Tailwind CSS usage...');
  
  const cssContent = readFileSync(CURRENT_CSS_FILE, 'utf8');
  const lines = cssContent.split('\n');
  
  const analysis = {
    totalLines: lines.length,
    applyDirectives: [],
    manualCSS: [],
    mediaQueries: [],
    incompatibleUtilities: [],
    customColors: [],
    specialCases: []
  };
  
  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const lineNum = index + 1;
    
    // Find @apply directives
    if (trimmed.includes('@apply')) {
      const applyContent = trimmed.replace('@apply', '').trim();
      const utilities = applyContent.split(/\s+/).filter(u => u && u !== ';');
      
      analysis.applyDirectives.push({
        line: lineNum,
        selector: getPreviousSelector(lines, index),
        utilities: utilities,
        raw: trimmed
      });
      
      // Check for incompatible utilities
      utilities.forEach(util => {
        if (INCOMPATIBLE_UTILITIES.some(inc => util.includes(inc))) {
          analysis.incompatibleUtilities.push({
            line: lineNum,
            utility: util,
            selector: getPreviousSelector(lines, index)
          });
        }
      });
    }
    
    // Find media queries
    if (trimmed.includes('@media')) {
      analysis.mediaQueries.push({
        line: lineNum,
        query: trimmed
      });
    }
    
    // Find manual CSS rules (not @apply)
    if (trimmed.includes(':') && !trimmed.includes('@') && !trimmed.startsWith('/*') && !trimmed.startsWith('*')) {
      analysis.manualCSS.push({
        line: lineNum,
        property: trimmed.split(':')[0].trim(),
        value: trimmed.split(':')[1]?.replace(';', '').trim(),
        raw: trimmed
      });
    }
    
    // Find custom color usage
    if (trimmed.includes('hsl(') || trimmed.includes('rgba(')) {
      analysis.customColors.push({
        line: lineNum,
        color: trimmed
      });
    }
  });
  
  return analysis;
}

function getPreviousSelector(lines, currentIndex) {
  for (let i = currentIndex - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (line.endsWith('{')) {
      return line.replace('{', '').trim();
    }
  }
  return 'unknown';
}

function generateConversionPlan(analysis) {
  console.log('📋 Generating conversion plan...');
  
  const plan = {
    highRisk: [],
    mediumRisk: [],
    lowRisk: [],
    conversions: []
  };
  
  analysis.applyDirectives.forEach(directive => {
    const hasResponsive = directive.utilities.some(u => u.includes('md:') || u.includes('lg:') || u.includes('sm:'));
    const hasDarkMode = directive.utilities.some(u => u.includes('dark:'));
    const hasIncompatible = directive.utilities.some(u => 
      INCOMPATIBLE_UTILITIES.some(inc => u.includes(inc))
    );
    
    const risk = hasIncompatible ? 'highRisk' : 
                 (hasResponsive || hasDarkMode) ? 'mediumRisk' : 'lowRisk';
    
    plan[risk].push({
      selector: directive.selector,
      line: directive.line,
      utilities: directive.utilities,
      issues: {
        responsive: hasResponsive,
        darkMode: hasDarkMode,
        incompatible: hasIncompatible
      }
    });
    
    // Generate conversion recommendations
    if (hasResponsive || hasDarkMode) {
      plan.conversions.push({
        selector: directive.selector,
        current: directive.raw,
        recommended: generateAlternativeCSS(directive)
      });
    }
  });
  
  return plan;
}

function generateAlternativeCSS(directive) {
  // Generate manual CSS alternative for problematic @apply directives
  let css = `${directive.selector} {\n`;
  
  directive.utilities.forEach(utility => {
    if (utility.includes('md:') || utility.includes('lg:')) {
      css += `  /* Convert ${utility} to media query */\n`;
    } else if (utility.includes('dark:')) {
      css += `  /* Convert ${utility} to .dark selector */\n`;
    } else {
      css += `  /* Keep ${utility} as Tailwind utility */\n`;
    }
  });
  
  css += '}';
  return css;
}

function generateReport(analysis, plan) {
  console.log('📝 Generating migration report...');
  
  const report = `# 🗺️ Tailwind CSS Migration Mapping

## 📊 Current Usage Analysis

### **File Statistics:**
- **Total lines**: ${analysis.totalLines}
- **@apply directives**: ${analysis.applyDirectives.length}
- **Manual CSS rules**: ${analysis.manualCSS.length}
- **Media queries**: ${analysis.mediaQueries.length}
- **Incompatible utilities**: ${analysis.incompatibleUtilities.length}

## ⚠️ Migration Risk Assessment

### **🔴 HIGH RISK (${plan.highRisk.length} items)**
${plan.highRisk.map(item => `
- **Line ${item.line}**: \`${item.selector}\`
  - **Issue**: ${item.issues.incompatible ? 'Incompatible utilities' : ''}
  - **Utilities**: ${item.utilities.join(', ')}
`).join('')}

### **🟡 MEDIUM RISK (${plan.mediumRisk.length} items)**
${plan.mediumRisk.map(item => `
- **Line ${item.line}**: \`${item.selector}\`
  - **Issues**: ${item.issues.responsive ? 'Responsive utilities' : ''} ${item.issues.darkMode ? 'Dark mode utilities' : ''}
  - **Utilities**: ${item.utilities.join(', ')}
`).join('')}

### **🟢 LOW RISK (${plan.lowRisk.length} items)**
${plan.lowRisk.slice(0, 5).map(item => `
- **Line ${item.line}**: \`${item.selector}\` - Standard utilities
`).join('')}
${plan.lowRisk.length > 5 ? `... and ${plan.lowRisk.length - 5} more` : ''}

## 🔄 Conversion Recommendations

${plan.conversions.slice(0, 10).map(conv => `
### **${conv.selector}**
**Current:**
\`\`\`css
${conv.current}
\`\`\`

**Recommended:**
\`\`\`css
${conv.recommended}
\`\`\`
`).join('')}

## 📋 Migration Checklist

### **Pre-Migration:**
- [x] Document current working state
- [ ] Create @apply → CSS conversion mapping
- [ ] Test each critical component individually
- [ ] Prepare fallback CSS for high-risk items

### **During Migration:**
- [ ] Update dependencies to Tailwind 4.1.12
- [ ] Convert high-risk @apply directives first
- [ ] Test visual appearance after each change
- [ ] Use @reference directive for remaining @apply

### **Post-Migration:**
- [ ] Verify all styling matches original
- [ ] Test dark mode thoroughly  
- [ ] Test responsive behavior
- [ ] Performance benchmark

## 🛡️ Rollback Strategy

**If migration fails:**
1. \`git checkout backup-tailwind-3\`
2. \`git checkout -b rollback-to-working\`
3. \`git push origin main --force-with-lease\`

**Working reference:** http://localhost:5175/ (backup-tailwind-3 branch)

---

**Generated**: ${new Date().toISOString()}
**Working Commit**: a7635df
**Baseline**: Tailwind CSS 3.4.17 with perfect visual design
`;

  return report;
}

// Main execution
try {
  console.log('🎯 Starting CSS mapping analysis...');
  
  const analysis = analyzeCSSFile();
  const plan = generateConversionPlan(analysis);
  const report = generateReport(analysis, plan);
  
  writeFileSync(OUTPUT_FILE, report);
  
  console.log('✅ Analysis complete!');
  console.log(`📊 Found ${analysis.applyDirectives.length} @apply directives`);
  console.log(`⚠️ Found ${analysis.incompatibleUtilities.length} incompatible utilities`);
  console.log(`📝 Report saved to: ${OUTPUT_FILE}`);
  console.log('');
  console.log('🎯 Next steps:');
  console.log('1. Review the generated mapping report');
  console.log('2. Test individual component conversions');
  console.log('3. Create fallback CSS for critical styles');
  console.log('4. Plan gradual migration approach');
  
} catch (error) {
  console.error('❌ Error:', error.message);
}