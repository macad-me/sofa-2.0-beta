import { defineConfig } from 'vitepress'
import { resolve } from 'path'
import { dataPlugin } from './dataPlugin.mts'

export default defineConfig({
  title: "SOFA",
  titleTemplate: "SOFA - by Mac Admins Open Source",
  description: "Simple Organized Feed for Apple Software Updates - by Mac Admins Open Source",
  cleanUrls: true,
  
  // For custom domain (sofa.macadmin.me), use root path
  base: '/',  // Root path for custom domain
  
  themeConfig: {
    // Navigation data for VitePress mobile menu
    nav: [
      { text: 'macOS', link: '/macos/sequoia' },
      { text: 'iOS/iPadOS', link: '/ios/ios18' },
      { text: 'Safari', link: '/safari/safari18' },
      { text: 'tvOS', link: '/tvos/tvos18' },
      { text: 'visionOS', link: '/visionos/visionos2' },
      { text: 'watchOS', link: '/watchos/watchos11' },
      { text: 'How It Works', link: '/how-it-works' }
    ],
    
    // Ensure mobile navigation works
    siteTitle: 'SOFA',
    logo: '/custom_logo.png',
    
    // Disable next/prev page links if desired
    docFooter: {
      prev: true,
      next: true,
    },
    
    sidebar: [
      {
        text: 'Documentation',
        items: [
          { text: 'How It Works', link: '/how-it-works' },
          { text: 'Scheduled Process', link: '/scheduled-process' }
        ]
      },
      {
        text: 'macOS',
        items: [
          { text: 'macOS Tahoe 26', link: '/macos/tahoe26' },
          { text: 'macOS Sequoia 15', link: '/macos/sequoia' },
          { text: 'macOS Sonoma 14', link: '/macos/sonoma' },
          { text: 'macOS Ventura 13', link: '/macos/ventura' },
          { text: 'macOS Monterey 12', link: '/macos/monterey' },
        ]
      },
      {
        text: 'iOS/iPadOS',
        items: [
          { text: 'iOS/iPadOS 26', link: '/ios/ios26' },
          { text: 'iOS/iPadOS 18', link: '/ios/ios18' },
          { text: 'iOS/iPadOS 17', link: '/ios/ios17' },
        ]
      },
      {
        text: 'Safari',
        items: [
          { text: 'Safari 18', link: '/safari/safari18' },
        ]
      },
      {
        text: 'tvOS',
        items: [
          { text: 'tvOS 26', link: '/tvos/tvos26' },
          { text: 'tvOS 18', link: '/tvos/tvos18' },
          { text: 'tvOS 17', link: '/tvos/tvos17' },
        ]
      },
      {
        text: 'visionOS',
        items: [
          { text: 'visionOS 2', link: '/visionos/visionos2' },
        ]
      },
      {
        text: 'watchOS',
        items: [
          { text: 'watchOS 26', link: '/watchos/watchos26' },
          { text: 'watchOS 11', link: '/watchos/watchos11' },
        ]
      },
      {
        text: 'Tools',
        items: [
          { text: 'CVE Search', link: '/cve-search' },
          { text: 'Release Deferrals', link: '/release-deferrals' },
          { text: 'Model Identifiers', link: '/model-identifier' },
          { text: 'macOS Installers', link: '/macos-installer-info' },
          { text: 'Beta Releases', link: '/beta-releases' },
          { text: 'Essential Info', link: '/essential-info' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/macadmins/sofa' },
    ],
    footer: {
      message: 'Released under the Apache 2.0 License.',
      copyright: 'Copyright © 2024 by Mac Admins Open Source.',
    },
  },
  vite: {
    define: {
      // Make API base URLs available to the client
      __API_BASE_PROD__: JSON.stringify(process.env.VITE_API_BASE_PROD || 'https://sofa-beta.macadmin.me'),
      __API_BASE_DEV__: JSON.stringify(process.env.VITE_API_BASE_DEV || '/data'),
      // GitHub repository configuration
      __GITHUB_REPO__: JSON.stringify(process.env.GITHUB_REPOSITORY || process.env.VITE_GITHUB_REPO || 'macad-me/sofa-2.0-beta'),
      __GITHUB_BRANCH__: JSON.stringify(process.env.GITHUB_REF_NAME || process.env.VITE_GITHUB_BRANCH || 'main'),
    },
    plugins: [
      dataPlugin() // Serve data files from source directories during dev
    ],
    build: {
      rollupOptions: {
        external: [
          // Prevent Vite from trying to bundle our data files
          /^\.\.\/data\//
        ]
      }
    },
    server: {
      fs: {
        allow: [
          resolve(__dirname, '../..'), // Allow access to project root for data directories
        ]
      }
    },
    resolve: {
      alias: {
        // Component aliases
        '@components': resolve(__dirname, './theme/components'),
        
        // Public assets
        '@images': resolve(__dirname, '../public/'),
        
        // Data source directories (for imports)
        '@data/feeds': resolve(__dirname, '../../data/feeds'),
        '@data/resources': resolve(__dirname, '../../data/resources'),
        '@v1': resolve(__dirname, '../../data/feeds/v1'),
        '@v2': resolve(__dirname, '../../data/feeds/v2'),
        '@resources': resolve(__dirname, '../../data/resources'),
        
        // URL path mappings (for fetch requests - handled by serveDataPlugin)
        '/v1': resolve(__dirname, '../../data/feeds/v1'),
        '/v2': resolve(__dirname, '../../data/feeds/v2'),
        '/resources': resolve(__dirname, '../../data/resources'),
      },
    },
    optimizeDeps: {
      include: [
        '@data/feeds/**/*.json',
        '@data/resources/*.json'
      ]
    }
  }
})
