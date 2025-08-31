import { resolve } from 'path'
import { readFileSync, existsSync, readdirSync } from 'fs'
import type { Plugin } from 'vite'

export function dataPlugin(): Plugin {
  const dataRoot = resolve(__dirname, '../../data')
  
  return {
    name: 'vitepress-data-plugin',
    enforce: 'pre', // Ensure this plugin runs before others
    configureServer(server) {
      // During dev, serve data files directly from source
      // Add middleware at the very beginning
      server.middlewares.use((req, res, next) => {
          if (!req.url) return next()
          
          let url = req.url
          
          // Remove query parameters for cleaner matching
          url = url.split('?')[0]
          
          // Remove base path prefix if present
          url = url.replace(/^\/sofa-2\.0/, '')
          
          // Log ALL requests for debugging
          if (req.url?.includes('/v1/') || req.url?.includes('/v2/') || req.url?.includes('/resources/')) {
            console.log('🔍 DataPlugin - Original URL:', req.url)
            console.log('🔍 DataPlugin - After base removal:', url)
          }
          
          // Map URLs to actual data file paths
          const mappings: Record<string, string> = {
            '/data/feeds/v2/': 'feeds/v2/',
            '/data/feeds/v1/': 'feeds/v1/',
            '/data/resources/': 'resources/',
            '/v2/': 'feeds/v2/',
            '/v1/': 'feeds/v1/',
            '/resources/': 'resources/',
          }
          
          // Simple aliases for common files
          const aliases: Record<string, string> = {
            '/v2/metadata.json': 'resources/sofa-status.json',
            '/v1/macos.json': 'feeds/v1/macos_data_feed.json',
            '/v1/ios.json': 'feeds/v1/ios_data_feed.json',
            '/v1/rss.xml': 'feeds/v1/rss_feed.xml',
            '/v2/macos.json': 'feeds/v2/macos_data_feed.json', 
            '/v2/ios.json': 'feeds/v2/ios_data_feed.json',
            '/resources/timestamp.json': 'feeds/v2/last_feed_timestamp.json',
            '/resources/bulletin.json': 'resources/bulletin_data.json',
            '/resources/links.json': 'resources/essential_links.json'
          }
          
          // Check aliases first
          if (aliases[url]) {
            const fullPath = resolve(dataRoot, aliases[url])
            console.log('🔗 DataPlugin - Alias mapping:', url, '→', aliases[url])
            console.log('🔍 DataPlugin: Looking for aliased file at:', fullPath)
            
            if (existsSync(fullPath)) {
              try {
                const content = readFileSync(fullPath, 'utf-8')
                res.setHeader('Content-Type', url.endsWith('.xml') ? 'application/xml' : 'application/json')
                res.setHeader('Cache-Control', 'no-cache')
                res.end(content)
                console.log('✅ DataPlugin: Successfully served aliased file:', fullPath)
                return
              } catch (err) {
                console.error('❌ Error reading aliased file', fullPath, ':', err)
              }
            } else {
              console.log('❌ DataPlugin: Aliased file not found:', fullPath)
            }
          }
          
          for (const [urlPrefix, dataPath] of Object.entries(mappings)) {
            if (url.startsWith(urlPrefix)) {
              const filePath = url.replace(urlPrefix, '')
              const fullPath = resolve(dataRoot, dataPath, filePath)
              
              console.log('🔍 DataPlugin: Looking for file at:', fullPath)
              
              if (existsSync(fullPath)) {
                try {
                  const content = readFileSync(fullPath, 'utf-8')
                  res.setHeader('Content-Type', 'application/json')
                  res.setHeader('Cache-Control', 'no-cache')
                  res.end(content)
                  console.log('✅ DataPlugin: Successfully served file:', fullPath)
                  return
                } catch (err) {
                  console.error('❌ Error reading', fullPath, ':', err)
                }
              } else {
                console.log('❌ DataPlugin: File not found:', fullPath)
              }
            }
          }
          
          next()
        })
    },
    
    // For production build, generate the data files
    generateBundle() {
      // Define source and target mappings
      const mappings = [
        { from: resolve(dataRoot, 'feeds/v1'), to: 'v1' },
        { from: resolve(dataRoot, 'feeds/v2'), to: 'v2' },
        { from: resolve(dataRoot, 'resources'), to: 'resources' }
      ]
      
      console.log('🏗️ DataPlugin: Generating data files for production build...')
      
      for (const mapping of mappings) {
        if (existsSync(mapping.from)) {
          try {
            // Read all files in the source directory
            const files = readdirSync(mapping.from, { withFileTypes: true })
              .filter(dirent => dirent.isFile() && (dirent.name.endsWith('.json') || dirent.name.endsWith('.ndjson')))
              .map(dirent => dirent.name)
            
            for (const file of files) {
              const sourcePath = resolve(mapping.from, file)
              const content = readFileSync(sourcePath, 'utf-8')
              
              // Emit the file to the build output
              this.emitFile({
                type: 'asset',
                fileName: `${mapping.to}/${file}`,
                source: content
              })
              
              console.log(`✅ Emitted: ${mapping.to}/${file}`)
            }
          } catch (err) {
            console.error(`❌ Error processing ${mapping.from}:`, err)
          }
        } else {
          console.log(`⚠️ Source directory not found: ${mapping.from}`)
        }
      }
    }
  }
}