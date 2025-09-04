# 🗺️ Tailwind CSS Migration Mapping

## 📊 Current Usage Analysis

### **File Statistics:**
- **Total lines**: 618
- **@apply directives**: 93
- **Manual CSS rules**: 80
- **Media queries**: 7
- **Incompatible utilities**: 1

## ⚠️ Migration Risk Assessment

### **🔴 HIGH RISK (1 items)**

- **Line 281**: `.bento-copy-url`
  - **Issue**: Incompatible utilities
  - **Utilities**: flex, items-center, gap-1, px-2, py-1, text-gray-400, hover:bg-opacity-20, rounded, transition-colors;


### **🟡 MEDIUM RISK (58 items)**

- **Line 12**: `.bento-grid`
  - **Issues**: Responsive utilities 
  - **Utilities**: grid, grid-cols-1, md:grid-cols-2, lg:grid-cols-3, gap-6, mb-16, items-stretch;

- **Line 50**: `.bento-card`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-white, dark:bg-slate-800/50, border, border-gray-200, dark:border-slate-700/50

- **Line 83**: `.bento-card-title`
  - **Issues**:  Dark mode utilities
  - **Utilities**: font-semibold, text-gray-900, dark:text-white, text-sm, flex-shrink-0;

- **Line 105**: `.bento-macos .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-blue-50, dark:bg-blue-900/30;

- **Line 109**: `.bento-macos .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-blue-600, dark:text-blue-400;

- **Line 117**: `.bento-ios .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-purple-50, dark:bg-purple-900/30;

- **Line 121**: `.bento-ios .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-purple-600, dark:text-purple-400;

- **Line 132**: `.bento-visionos .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-green-50, dark:bg-green-900/50;

- **Line 138**: `.bento-visionos .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-green-600, dark:text-green-400;

- **Line 147**: `.bento-safari .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-orange-50, dark:bg-orange-900/50;

- **Line 151**: `.bento-safari .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-orange-600, dark:text-orange-400;

- **Line 160**: `.bento-community .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-indigo-50, dark:bg-indigo-900/50;

- **Line 164**: `.bento-community .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-indigo-600, dark:text-indigo-400;

- **Line 170**: `.bento-quickboard`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-white, dark:bg-gray-900

- **Line 175**: `.bento-quickboard .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-emerald-50, dark:bg-emerald-900/50;

- **Line 179**: `.bento-quickboard .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-emerald-600, dark:text-emerald-400;

- **Line 183**: `.bento-statistics`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-white, dark:bg-slate-800/50

- **Line 189**: `.bento-statistics .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-emerald-50, dark:bg-emerald-900/50;

- **Line 193**: `.bento-statistics .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-emerald-600, dark:text-emerald-400;

- **Line 197**: `.bento-beta-gradient`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-white, dark:bg-slate-800/50

- **Line 203**: `.bento-beta-gradient .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-orange-50, dark:bg-orange-900/30;

- **Line 207**: `.bento-beta-gradient .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-orange-600, dark:text-orange-400;

- **Line 211**: `.bento-community-gradient`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-white, dark:bg-slate-800/50

- **Line 217**: `.bento-community-gradient .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-indigo-50, dark:bg-indigo-900/30;

- **Line 221**: `.bento-community-gradient .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-indigo-600, dark:text-indigo-400;

- **Line 230**: `.bento-feed-macos .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-cyan-50, dark:bg-cyan-900/30;

- **Line 234**: `.bento-feed-macos .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-cyan-600, dark:text-cyan-400;

- **Line 242**: `.bento-feed-ios .bento-card-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-blue-50, dark:bg-blue-900/30;

- **Line 246**: `.bento-feed-ios .bento-card-icon svg`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-blue-600, dark:text-blue-400;

- **Line 285**: `.bento-copy-url-macos`
  - **Issues**:  Dark mode utilities
  - **Utilities**: hover:text-cyan-600, dark:hover:text-cyan-400, hover:bg-cyan-50, dark:hover:bg-cyan-900/20;

- **Line 289**: `.bento-copy-url-ios`
  - **Issues**:  Dark mode utilities
  - **Utilities**: hover:text-blue-600, dark:hover:text-blue-400, hover:bg-blue-50, dark:hover:bg-blue-900/20;

- **Line 299**: `.bento-version-label`
  - **Issues**:  Dark mode utilities
  - **Utilities**: font-semibold, text-gray-900, dark:text-white, flex-shrink-0;

- **Line 307**: `.bento-version-details`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, text-gray-700, dark:text-gray-300, space-y-1, mt-1;

- **Line 313**: `.bento-security-shield`
  - **Issues**:  Dark mode utilities
  - **Utilities**: h-3.5, w-3.5, text-gray-600, dark:text-gray-400;

- **Line 317**: `.bento-timestamp`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-xs, text-gray-700, dark:text-gray-300, font-mono, leading-relaxed;

- **Line 321**: `.bento-badge-tbd`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-xs, px-2, py-0, bg-gray-100, dark:bg-gray-800, text-gray-600, dark:text-gray-400, border-gray-200, dark:border-gray-700;

- **Line 449**: `.bento-info-display`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, text-gray-600, dark:text-gray-400, space-y-2;

- **Line 457**: `.bento-info-label`
  - **Issues**:  Dark mode utilities
  - **Utilities**: font-medium, text-gray-800, dark:text-gray-200;

- **Line 461**: `.bento-info-value`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-right, text-gray-600, dark:text-gray-400;

- **Line 470**: `.bento-deferral-table th`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-left, font-medium, text-gray-800, dark:text-gray-200, pb-2, border-b, border-gray-200, dark:border-gray-700;

- **Line 474**: `.bento-deferral-table td`
  - **Issues**:  Dark mode utilities
  - **Utilities**: py-2, text-gray-600, dark:text-gray-400, border-b, border-gray-100, dark:border-gray-800;

- **Line 483**: `.bento-xprotect-item`
  - **Issues**:  Dark mode utilities
  - **Utilities**: flex, justify-between, items-start, py-2, border-b, border-gray-100, dark:border-gray-800, last:border-b-0;

- **Line 487**: `.bento-xprotect-name`
  - **Issues**:  Dark mode utilities
  - **Utilities**: font-medium, text-gray-800, dark:text-gray-200;

- **Line 491**: `.bento-xprotect-version`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, text-gray-600, dark:text-gray-400;

- **Line 496**: `.bento-resource-link`
  - **Issues**:  Dark mode utilities
  - **Utilities**: block, p-3, rounded-lg, bg-white/30, dark:bg-gray-700/30, border, border-gray-100, dark:border-gray-600/50

- **Line 502**: `.bento-resource-link:hover`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-gray-900, dark:text-white;

- **Line 507**: `.bento-info-display h4`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, font-semibold, text-gray-900, dark:text-gray-100, mt-4, mb-2, first:mt-0;

- **Line 529**: `.version-label`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, font-medium, text-gray-600, dark:text-gray-400;

- **Line 533**: `.version-value`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-sm, font-semibold, text-gray-900, dark:text-gray-100;

- **Line 538**: `.button-group`
  - **Issues**:  Dark mode utilities
  - **Utilities**: flex, border, border-gray-200, dark:border-gray-600, rounded-lg, overflow-hidden;

- **Line 542**: `.button-group button`
  - **Issues**:  Dark mode utilities
  - **Utilities**: px-3, py-1.5, text-sm, font-medium, bg-white, dark:bg-gray-800, text-gray-700, dark:text-gray-300

- **Line 557**: `.xprotect-meta`
  - **Issues**:  Dark mode utilities
  - **Utilities**: mt-2, pt-2, border-t, border-gray-200, dark:border-gray-700;

- **Line 561**: `.meta-text`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-xs, text-gray-500, dark:text-gray-400;

- **Line 570**: `.bento-card-title-section .bento-card-title`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-base, font-semibold, text-gray-900, dark:text-white, mb-1;

- **Line 574**: `.release-date`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-xs, text-gray-500, dark:text-gray-400, flex, items-center, gap-1;

- **Line 582**: `.expand-icon`
  - **Issues**:  Dark mode utilities
  - **Utilities**: text-xl, font-light, text-gray-500, dark:text-gray-400, cursor-pointer, ml-4;

- **Line 591**: `.cve-link`
  - **Issues**:  Dark mode utilities
  - **Utilities**: inline-flex, items-center, px-2, py-1, text-xs, font-mono, bg-blue-50, dark:bg-blue-900/30

- **Line 597**: `.cve-link.exploited`
  - **Issues**:  Dark mode utilities
  - **Utilities**: bg-red-50, dark:bg-red-900/30, border-red-200, dark:border-red-800


### **🟢 LOW RISK (34 items)**

- **Line 22**: `.bento-grid-section` - Standard utilities

- **Line 59**: `.bento-card-content` - Standard utilities

- **Line 63**: `.bento-card-header` - Standard utilities

- **Line 68**: `.bento-card-icon` - Standard utilities

- **Line 94**: `.bento-card-body` - Standard utilities

... and 29 more

## 🔄 Conversion Recommendations


### **.bento-grid**
**Current:**
```css
@apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16 items-stretch;
```

**Recommended:**
```css
.bento-grid {
  /* Keep grid as Tailwind utility */
  /* Keep grid-cols-1 as Tailwind utility */
  /* Convert md:grid-cols-2 to media query */
  /* Convert lg:grid-cols-3 to media query */
  /* Keep gap-6 as Tailwind utility */
  /* Keep mb-16 as Tailwind utility */
  /* Keep items-stretch; as Tailwind utility */
}
```

### **.bento-card**
**Current:**
```css
@apply bg-white dark:bg-slate-800/50 border border-gray-200 dark:border-slate-700/50
```

**Recommended:**
```css
.bento-card {
  /* Keep bg-white as Tailwind utility */
  /* Convert dark:bg-slate-800/50 to .dark selector */
  /* Keep border as Tailwind utility */
  /* Keep border-gray-200 as Tailwind utility */
  /* Convert dark:border-slate-700/50 to .dark selector */
}
```

### **.bento-card-title**
**Current:**
```css
@apply font-semibold text-gray-900 dark:text-white text-sm flex-shrink-0;
```

**Recommended:**
```css
.bento-card-title {
  /* Keep font-semibold as Tailwind utility */
  /* Keep text-gray-900 as Tailwind utility */
  /* Convert dark:text-white to .dark selector */
  /* Keep text-sm as Tailwind utility */
  /* Keep flex-shrink-0; as Tailwind utility */
}
```

### **.bento-macos .bento-card-icon**
**Current:**
```css
@apply bg-blue-50 dark:bg-blue-900/30;
```

**Recommended:**
```css
.bento-macos .bento-card-icon {
  /* Keep bg-blue-50 as Tailwind utility */
  /* Convert dark:bg-blue-900/30; to .dark selector */
}
```

### **.bento-macos .bento-card-icon svg**
**Current:**
```css
@apply text-blue-600 dark:text-blue-400;
```

**Recommended:**
```css
.bento-macos .bento-card-icon svg {
  /* Keep text-blue-600 as Tailwind utility */
  /* Convert dark:text-blue-400; to .dark selector */
}
```

### **.bento-ios .bento-card-icon**
**Current:**
```css
@apply bg-purple-50 dark:bg-purple-900/30;
```

**Recommended:**
```css
.bento-ios .bento-card-icon {
  /* Keep bg-purple-50 as Tailwind utility */
  /* Convert dark:bg-purple-900/30; to .dark selector */
}
```

### **.bento-ios .bento-card-icon svg**
**Current:**
```css
@apply text-purple-600 dark:text-purple-400;
```

**Recommended:**
```css
.bento-ios .bento-card-icon svg {
  /* Keep text-purple-600 as Tailwind utility */
  /* Convert dark:text-purple-400; to .dark selector */
}
```

### **.bento-visionos .bento-card-icon**
**Current:**
```css
@apply bg-green-50 dark:bg-green-900/50;
```

**Recommended:**
```css
.bento-visionos .bento-card-icon {
  /* Keep bg-green-50 as Tailwind utility */
  /* Convert dark:bg-green-900/50; to .dark selector */
}
```

### **.bento-visionos .bento-card-icon svg**
**Current:**
```css
@apply text-green-600 dark:text-green-400;
```

**Recommended:**
```css
.bento-visionos .bento-card-icon svg {
  /* Keep text-green-600 as Tailwind utility */
  /* Convert dark:text-green-400; to .dark selector */
}
```

### **.bento-safari .bento-card-icon**
**Current:**
```css
@apply bg-orange-50 dark:bg-orange-900/50;
```

**Recommended:**
```css
.bento-safari .bento-card-icon {
  /* Keep bg-orange-50 as Tailwind utility */
  /* Convert dark:bg-orange-900/50; to .dark selector */
}
```


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
1. `git checkout backup-tailwind-3`
2. `git checkout -b rollback-to-working`
3. `git push origin main --force-with-lease`

**Working reference:** http://localhost:5175/ (backup-tailwind-3 branch)

---

**Generated**: 2025-09-04T08:25:45.556Z
**Working Commit**: a7635df
**Baseline**: Tailwind CSS 3.4.17 with perfect visual design
