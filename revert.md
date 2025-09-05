# Platform Data Source Changes - Revert Instructions

## Changes Made (2025-09-05)

**File**: `docs/.vitepress/theme/components/SOFADashboard.vue`

### Data Sources Added
```javascript
// Added V2 feed data sources
const safari = useSOFAData('feeds/v2/safari_data_feed.json')
const watchos = useSOFAData('feeds/v2/watchos_data_feed.json')
const tvos = useSOFAData('feeds/v2/tvos_data_feed.json')
const visionos = useSOFAData('feeds/v2/visionos_data_feed.json')
```

### Computed Properties Changed

#### safariVersion (lines ~1582-1594)
**Changed FROM:** Reading `bulletinData.value?.recent_releases`  
**Changed TO:** Reading `safari.data.value?.AppVersions?.[0]?.Latest`

#### watchOSVersion (lines ~1597-1611)  
**Changed FROM:** Reading `bulletinData.value?.latest_releases?.watchos`
**Changed TO:** Reading `watchos.data.value?.OSVersions?.[0]?.Latest`

#### tvOSVersion (lines ~1613-1627)
**Changed FROM:** Reading `bulletinData.value?.latest_releases?.tvos`  
**Changed TO:** Reading `tvos.data.value?.OSVersions?.[0]?.Latest`

#### visionOSVersion (lines ~1629-1643)
**Changed FROM:** Reading `bulletinData.value?.latest_releases?.visionos`
**Changed TO:** Reading `visionos.data.value?.OSVersions?.[0]?.Latest`

## To Revert When Bulletin Data Fixed

### 1. Remove Added Data Sources
```javascript
// Remove these lines:
const safari = useSOFAData('feeds/v2/safari_data_feed.json')
const watchos = useSOFAData('feeds/v2/watchos_data_feed.json') 
const tvos = useSOFAData('feeds/v2/tvos_data_feed.json')
const visionos = useSOFAData('feeds/v2/visionos_data_feed.json')
```

### 2. Revert Computed Properties

#### safariVersion - Revert to:
```javascript
const safariVersion = computed(() => {
  // Get Safari data from bulletin
  if (bulletinData.value?.recent_releases) {
    const safariRelease = bulletinData.value.recent_releases.find(r => r.platform === 'safari')
    if (safariRelease) {
      return {
        version: safariRelease.version,
        releaseDate: formatDate(safariRelease.release_date),
        name: safariRelease.name
      }
    }
  }
  return null
})
```

#### watchOSVersion - Revert to:
```javascript
const watchOSVersion = computed(() => {
  if (bulletinData.value?.latest_releases?.watchos) {
    const latest = bulletinData.value.latest_releases.watchos
    return {
      version: latest.version,
      build: latest.build || 'N/A',
      releaseDate: formatDate(latest.release_date),
      cves: latest.total_cve_count,
      name: `watchOS ${latest.version}`
    }
  }
  return null
})
```

#### tvOSVersion - Revert to:
```javascript
const tvOSVersion = computed(() => {
  if (bulletinData.value?.latest_releases?.tvos) {
    const latest = bulletinData.value.latest_releases.tvos
    return {
      version: latest.version,
      build: latest.build || 'N/A',
      releaseDate: formatDate(latest.release_date),
      cves: latest.total_cve_count,
      name: `tvOS ${latest.version}`
    }
  }
  return null
})
```

#### visionOSVersion - Revert to:
```javascript
const visionOSVersion = computed(() => {
  if (bulletinData.value?.latest_releases?.visionos) {
    const latest = bulletinData.value.latest_releases.visionos
    return {
      version: latest.version,
      build: latest.build || 'N/A',
      releaseDate: formatDate(latest.release_date),
      cves: latest.total_cve_count,
      name: `visionOS ${latest.version}`
    }
  }
  return null
})
```

## Reason for Changes
Bulletin data was showing incorrect information:
- Safari showing "No CVEs" when it actually has 6+ CVEs
- watchOS/tvOS showing "Build N/A" when build info exists
- tvOS missing 24 security issues from display

## When to Revert
When `bulletin_data.json` is updated to include accurate data for all platforms, revert these changes to use the centralized bulletin data source instead of individual V2 feeds.