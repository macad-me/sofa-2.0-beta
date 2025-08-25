<template>
  <div class="latest-features">
    <h2 class="latest-release-heading" :id="'beta-release-info'" tabindex="-1">
      Beta Release Info
      <a class="header-anchor" href="#beta-release-info" aria-hidden="true">#</a>
    </h2>

    <!-- Grid Layout similar to LatestFeatures -->
    <div v-if="betaDataFromFeed" class="grid-container">
      <!-- Latest Beta Info Card -->
      <div class="grid-item">
        <div class="content-box">
          <div class="card-header">
            <div class="card-icon">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <h2 class="card-title">Latest {{ title }} Beta</h2>
          </div>
          
          <!-- OS Showcase for Beta -->
          <div class="os-showcase">
            <img :src="osImage" alt="OS Image" class="os-hero-image" @error="handleImageError" />
          </div>
          
          <div class="os-details-grid">
            <div class="os-detail-item">
              <div class="detail-icon">
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Version</span>
                <span class="detail-value">{{ betaDataFromFeed.version }}</span>
              </div>
            </div>
            
            <div class="os-detail-item">
              <div class="detail-icon">
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Build</span>
                <span class="detail-value">{{ betaDataFromFeed.build }}</span>
              </div>
            </div>
            
            <div class="os-detail-item">
              <div class="detail-icon">
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Released</span>
                <span class="detail-value">{{ formatDate(betaDataFromFeed.released) }}</span>
              </div>
            </div>
            
            <div class="os-detail-item">
              <div class="detail-icon">
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="detail-content">
                <span class="detail-label">Age</span>
                <span class="detail-value">{{ getDaysAvailable(betaDataFromFeed.released) }} days</span>
              </div>
            </div>
          </div>
          
          <!-- Action Links -->
          <div class="action-links">
            <a v-if="betaDataFromFeed.release_notes_url" :href="betaDataFromFeed.release_notes_url" target="_blank" class="action-link primary">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              Release Notes
            </a>
            <a v-if="betaDataFromFeed.downloads_url" :href="betaDataFromFeed.downloads_url" target="_blank" class="action-link">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
              </svg>
              Downloads
            </a>
          </div>
        </div>
      </div>
    
      <!-- Beta History Card -->
      <div v-if="allBetaVersions.length > 0" class="grid-item">
        <div class="content-box">
          <div class="card-header">
            <div class="card-icon">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <h2 class="card-title">Beta History</h2>
          </div>
          
          <div class="beta-versions-list">
            <div v-for="beta in allBetaVersions" :key="beta.build" class="beta-version-item">
              <div class="beta-version-header">
                <span class="beta-version-number">{{ beta.version }}</span>
                <span class="beta-build-number">{{ beta.build }}</span>
              </div>
              <div class="beta-version-meta">
                <span class="beta-date">{{ formatShortDate(beta.released) }}</span>
                <span class="beta-type-badge">Dev</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Cards Grid -->
    <div class="info-cards-grid">
      <!-- Beta Program Card -->
      <div class="info-card">
        <div class="info-card-header">
          <div class="info-card-icon">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
          </div>
          <h3 class="info-card-title">Beta Program</h3>
        </div>
        <p class="info-card-text">Join the {{ platform }} beta program to test new features before release.</p>
        <a href="https://beta.apple.com" target="_blank" class="info-card-link">
          Learn More
          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
        </a>
      </div>

      <!-- Developer Resources Card -->
      <div class="info-card">
        <div class="info-card-header">
          <div class="info-card-icon">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
            </svg>
          </div>
          <h3 class="info-card-title">Developer Resources</h3>
        </div>
        <p class="info-card-text">Access developer documentation and tools for {{ platform }} development.</p>
        <a href="https://developer.apple.com" target="_blank" class="info-card-link">
          Visit Developer Portal
          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
        </a>
      </div>

      <!-- Feedback Card -->
      <div class="info-card">
        <div class="info-card-header">
          <div class="info-card-icon">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
          <h3 class="info-card-title">Report Feedback</h3>
        </div>
        <p class="info-card-text">Help improve {{ platform }} by reporting bugs and suggesting features.</p>
        <a href="https://feedbackassistant.apple.com" target="_blank" class="info-card-link">
          Feedback Assistant
          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import betaHistoryData from '/v1/apple-beta-os-history.json'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  platform: {
    type: String,
    required: true
  }
})

const betaDataFromFeed = ref(null)
const osImage = ref('')
const imageError = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const formatShortDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  })
}

const formatBetaType = (type) => {
  if (!type) return 'Beta'
  return type === 'pb' ? 'Public Beta' : 'Developer Beta'
}

const getDaysAvailable = (releaseDate) => {
  if (!releaseDate) return 0
  const date = new Date(releaseDate)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const findBetaData = () => {
  if (!betaHistoryData.items) return null
  
  // Try to find matching beta data - get the latest one
  const platformKey = props.platform === 'macOS' ? 'macOS' : props.platform
  const versionNumber = props.title.match(/\d+/)?.[0]
  
  // Get all matching items and sort by date to get the latest
  const matchingItems = betaHistoryData.items.filter(item => {
    const itemPlatform = item.platform
    const itemVersion = item.version
    
    return itemPlatform === platformKey && 
           itemVersion.includes(versionNumber)
  })
  
  // Return the most recent one
  if (matchingItems.length > 0) {
    return matchingItems.sort((a, b) => new Date(b.released) - new Date(a.released))[0]
  }
  
  return null
}

const allBetaVersions = computed(() => {
  const platformKey = props.platform === 'macOS' ? 'macOS' : props.platform
  const versionNumber = props.title.match(/\d+/)?.[0]
  
  // Use only historical data
  const historicalItems = betaHistoryData.items || []
  
  // Get all betas for this platform and version
  const platformBetas = historicalItems.filter(item => {
    return item.platform === platformKey && 
           item.version.includes(versionNumber)
  })
  
  // Sort by release date (newest first) and limit to 8
  return platformBetas
    .sort((a, b) => new Date(b.released) - new Date(a.released))
    .slice(0, 8)
})

const getOsImage = (platform, title) => {
  // Map beta OS versions to their icons
  const images = {
    'Tahoe': '/Tahoe.png',
    'iOS 26': '/ios_26.png',
    'watchOS 26': '/watchos_26.png',
    'tvOS 26': '/tvos_26.png',
    'visionOS': '/ios_18.png', // Use iOS 18 as fallback for visionOS
    'default': '/SWUpdate.png'
  }

  // Check for OS 26 versions
  if (title.includes('Tahoe') || title.includes('26')) {
    for (const key in images) {
      if (title.includes(key)) {
        return getAssetPath(images[key])
      }
    }
  }
  
  // Default fallback
  return getAssetPath('/SWUpdate.png')
}

const getAssetPath = (relativePath) => {
  // Use relative path that works with any base path setting
  if (relativePath.startsWith('/')) {
    return relativePath
  }
  return '/' + relativePath
}

const handleImageError = (e) => {
  console.error('Image failed to load:', e.target.src)
  imageError.value = true
  // Set fallback image to SWUpdate.png
  e.target.src = '/SWUpdate.png'
}

onMounted(() => {
  betaDataFromFeed.value = findBetaData()
  osImage.value = getOsImage(props.platform, props.title)
})
</script>

<style scoped>
.latest-features {
  margin-top: 1rem;
}

.latest-release-heading {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--vp-c-text-1);
}

.header-anchor {
  margin-left: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.latest-release-heading:hover .header-anchor {
  opacity: 1;
}

/* Beta Info Container */
.beta-info-container {
  background: var(--vp-c-bg-soft);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.beta-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.beta-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--vp-c-brand-soft);
  border-radius: 6px;
  color: var(--vp-c-brand);
}

.beta-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.beta-message {
  color: var(--vp-c-text-2);
  margin: 0;
  line-height: 1.6;
}

/* Features Container */
.features-container {
  margin-bottom: 1.5rem;
}

.info-container {
  margin-bottom: 1.5rem;
}

.custom-block {
  padding: 1rem;
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
}

.custom-block-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--vp-c-text-1);
}

.custom-block p:last-child {
  margin: 0;
  color: var(--vp-c-text-2);
}

/* Grid Layout matching LatestFeatures */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.grid-item {
  height: 100%;
}

.content-box {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.content-box:hover {
  border-color: var(--vp-c-brand);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--vp-c-brand-soft);
  border-radius: 6px;
  color: var(--vp-c-brand);
  flex-shrink: 0;
}

.card-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0;
  line-height: 28px;
}

/* OS Showcase */
.os-showcase {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  position: relative;
  padding: 0.875rem;
  background: rgba(0, 0, 0, 0);
  border-radius: 8px;
}

.os-hero-image {
  width: 80px;
  height: auto;
  border-radius: 12px;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.os-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.os-detail-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
}

.detail-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: var(--vp-c-text-3);
  flex-shrink: 0;
  margin-top: 2px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.detail-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.action-links {
  display: flex;
  gap: 0.625rem;
  margin-top: 1rem;
  padding-top: 0.875rem;
  border-top: 1px solid #f3f4f6;
}

.action-link {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 0.875rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
  transition: all 0.15s ease;
}

.action-link:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.action-link.primary {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.action-link.primary:hover {
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.25);
}

.action-link svg {
  width: 0.875rem;
  height: 0.875rem;
  opacity: 0.7;
}

/* Beta Info Card */
.beta-info-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.beta-info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--vp-c-divider);
}

.beta-info-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--vp-c-brand-soft), var(--vp-c-brand));
  border-radius: 8px;
  color: white;
}

.beta-info-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.beta-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.beta-detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.detail-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.rc-status {
  color: #f59e0b;
}

.beta-action-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--vp-c-divider);
}

.beta-action-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--vp-c-brand-soft);
  border: 1px solid var(--vp-c-brand-soft);
  border-radius: 6px;
  color: var(--vp-c-brand);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.beta-action-link:hover {
  background: var(--vp-c-brand);
  color: white;
}

/* All Beta Versions Card */
.all-betas-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.all-betas-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.all-betas-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--vp-c-brand-soft);
  border-radius: 6px;
  color: var(--vp-c-brand);
}

.all-betas-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0;
}

.beta-versions-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.beta-versions-list::-webkit-scrollbar {
  width: 4px;
}

.beta-versions-list::-webkit-scrollbar-track {
  background: var(--vp-c-bg-soft);
  border-radius: 2px;
}

.beta-versions-list::-webkit-scrollbar-thumb {
  background: var(--vp-c-divider);
  border-radius: 2px;
}

.beta-versions-list::-webkit-scrollbar-thumb:hover {
  background: var(--vp-c-text-3);
}

.beta-version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.75rem;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.beta-version-item:hover {
  border-color: var(--vp-c-brand);
  background: var(--vp-c-bg-mute);
}

.beta-version-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.beta-version-number {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.beta-build-number {
  font-size: 0.8125rem;
  color: var(--vp-c-text-2);
}

.beta-version-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.beta-date {
  font-size: 0.8125rem;
  color: var(--vp-c-text-3);
}

.mini-rc-badge {
  padding: 0.125rem 0.375rem;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 4px;
  color: #f59e0b;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
}

.beta-type-badge {
  padding: 0.125rem 0.375rem;
  background: var(--vp-c-brand-soft);
  border: 1px solid var(--vp-c-brand-soft);
  border-radius: 4px;
  color: var(--vp-c-brand);
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
}

/* Latest Card */
.latest-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--vp-c-brand-soft);
  border-radius: 8px;
  color: var(--vp-c-brand);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.version-info {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.version-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.build-label {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
  font-weight: 500;
}

.release-date {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
}

.rc-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 6px;
  color: #f59e0b;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-top: 0.5rem;
  width: fit-content;
}

/* Info Cards Grid */
.info-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.info-card:hover {
  border-color: var(--vp-c-brand);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.info-card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.info-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--vp-c-brand-soft);
  border-radius: 6px;
  color: var(--vp-c-brand);
}

.info-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0;
}

.info-card-text {
  color: var(--vp-c-text-2);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 1rem 0;
  flex-grow: 1;
}

.info-card-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--vp-c-brand);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}

.info-card-link:hover {
  color: var(--vp-c-brand-dark);
}

/* Dark mode */
/* Dark Mode */
:root.dark .beta-info-container {
  background: rgba(31, 41, 55, 0.3);
}

:root.dark .content-box {
  background: rgba(31, 41, 55, 0.3);
  border-color: rgba(55, 65, 81, 0.5);
}

:root.dark .content-box:hover {
  background: rgba(31, 41, 55, 0.5);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:root.dark .action-link {
  background: rgba(31, 41, 55, 0.5);
  border-color: rgba(55, 65, 81, 0.5);
}

:root.dark .info-card {
  background: rgba(31, 41, 55, 0.3);
  border-color: rgba(55, 65, 81, 0.5);
}

:root.dark .info-card:hover {
  background: rgba(31, 41, 55, 0.5);
}

:root.dark .beta-version-item {
  background: rgba(31, 41, 55, 0.2);
  border-color: rgba(55, 65, 81, 0.3);
}

:root.dark .beta-version-item:hover {
  background: rgba(31, 41, 55, 0.4);
}

/* Dark mode styles for action links */
:root.dark .action-links,
.dark .action-links {
  border-top-color: rgba(55, 65, 81, 0.3);
}

:root.dark .action-link,
.dark .action-link {
  background: rgba(31, 41, 55, 0.5);
  border-color: rgba(55, 65, 81, 0.5);
  color: #e2e8f0;
}

:root.dark .action-link:hover,
.dark .action-link:hover {
  background: rgba(31, 41, 55, 0.7);
  border-color: rgba(75, 85, 99, 0.5);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

:root.dark .action-link.primary,
.dark .action-link.primary {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.25);
  color: #93c5fd;
}

:root.dark .action-link.primary:hover,
.dark .action-link.primary:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
}

/* Enhanced Mobile UX - Tablets */
@media (max-width: 768px) {
  .beta-versions-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .os-showcase-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Enhanced Mobile UX - Smartphones */
@media (max-width: 480px) {
  .beta-features-container {
    padding: 0.5rem;
  }
  
  /* Header adjustments */
  .header h2 {
    font-size: 1.25rem;
  }
  
  /* Beta version cards */
  .beta-versions-grid {
    gap: 0.75rem;
  }
  
  .beta-version-item {
    padding: 0.875rem;
    border-radius: 8px;
  }
  
  .beta-header {
    padding: 0.75rem;
    gap: 0.625rem;
  }
  
  .beta-title {
    font-size: 0.9375rem;
  }
  
  .beta-build {
    font-size: 0.7rem;
  }
  
  /* OS showcase adjustments */
  .os-showcase-section {
    padding: 0.75rem;
    margin-bottom: 0.75rem;
  }
  
  .os-showcase-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .os-showcase-item {
    padding: 0.625rem;
  }
  
  .os-image {
    width: 40px;
    height: 40px;
  }
  
  .os-label {
    font-size: 0.75rem;
  }
  
  /* Beta content */
  .beta-content {
    padding: 0.75rem;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    padding: 0.625rem 0;
  }
  
  .info-label {
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--vp-c-text-3);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .info-value {
    font-size: 0.875rem;
    font-weight: 500;
    margin-left: 0;
  }
  
  /* Action links - proper touch targets */
  .action-links {
    padding: 0.75rem;
    gap: 0.5rem;
  }
  
  .action-link {
    padding: 0.625rem 1rem;
    min-height: 44px;
    font-size: 0.8125rem;
    border-radius: 8px;
  }
  
  /* Resources section */
  .resources-section {
    margin-top: 0.875rem;
    padding-top: 0.875rem;
  }
  
  .resources-title {
    font-size: 0.875rem;
    margin-bottom: 0.625rem;
  }
  
  .info-card {
    padding: 0.875rem;
  }
  
  .info-card h4 {
    font-size: 0.875rem;
  }
  
  .info-card p {
    font-size: 0.75rem;
  }
  
  /* Loading state */
  .loading-placeholder {
    height: 150px;
  }
}

/* iPhone Pro models (390px) */
@media (max-width: 390px) {
  .beta-version-item {
    padding: 0.75rem;
  }
  
  .beta-title {
    font-size: 0.875rem;
  }
  
  .os-showcase-item {
    padding: 0.5rem;
  }
  
  .os-image {
    width: 35px;
    height: 35px;
  }
  
  .action-link {
    padding: 0.5rem 0.875rem;
    font-size: 0.75rem;
  }
}

/* iPhone SE and older (375px) */
@media (max-width: 375px) {
  .header h2 {
    font-size: 1.125rem;
  }
  
  .beta-build {
    font-size: 0.65rem;
  }
  
  .os-label {
    font-size: 0.7rem;
  }
  
  .info-card {
    padding: 0.75rem;
  }
}
</style>