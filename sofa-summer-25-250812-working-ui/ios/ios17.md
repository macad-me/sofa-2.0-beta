---
title: iOS/iPadOS 17
platform: iOS
layout: doc
---

<script setup>
import LatestFeatures from '@components/LatestFeatures.vue'
import SecurityInfo from '@components/SecurityInfo.vue'
import LinksComponent from '@components/LinksComponent.vue'
import linksData from '@v1/essential_links.json'
</script>

# iOS/iPadOS 17

<LatestFeatures 
  title="iOS 17" 
  platform="iOS"
  dataPath="/v1/ios_data_feed.json" 
  linksData="/v1/essential_links.json"
>
</LatestFeatures>

<SecurityInfo 
  title="iOS 17" 
  platform="iOS" 
  dataPath="/v1/ios_data_feed.json" 
/>

## Essential Resources

<LinksComponent
  title="iOS 17"
  platform="iOS"
  :linksData="linksData"
/>
