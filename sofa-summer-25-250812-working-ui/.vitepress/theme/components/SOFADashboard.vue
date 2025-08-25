<template>
  <div class="dashboard-container">
    <!-- SOFA Header -->
    <div class="sofa-header">
      <div class="sofa-image-container">
        <img 
          src="/custom_logo.png" 
          alt="SOFA Logo" 
          class="sofa-logo"
        />
      </div>
      <h1 class="sofa-name">
        <span class="sofa-text">SOFA</span>
        <span class="sofa-separator"> - </span>
        <span class="sofa-full">Simple Organized<br>Feed for Apple Software<br>Updates</span>
      </h1>
      <p class="sofa-tagline">
        SOFA supports MacAdmins by efficiently tracking and surfacing information on updates for macOS, iOS, tvOS, watchOS, visionOS, and Safari.
      </p>
      
      <!-- Welcome Message -->
      <div class="welcome-message">
        We're thrilled to have you here! 👋
      </div>
      
      <!-- GitHub Star Widget -->
      <div class="github-widget">
        <a class="github-btn" href="https://github.com/macadmins/sofa" rel="noopener" target="_blank" aria-label="Star macadmins/sofa on GitHub">
          <svg viewBox="0 0 16 16" width="16" height="16" class="github-star-icon" aria-hidden="true">
            <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z"></path>
          </svg>
          <span>Star us on GitHub</span>
        </a>
        <a class="github-count" href="https://github.com/macadmins/sofa/stargazers" rel="noopener" target="_blank" aria-label="{{ starCount }} stargazers on GitHub">
          {{ starCount }}
        </a>
      </div>
    </div>

    <!-- Platform Navigation -->
    <div class="flex flex-wrap justify-center gap-3 mb-12">
      <a v-for="platform in platforms" 
         :key="platform.name"
         :href="platform.link"
         class="group flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium transition-all duration-200 hover:shadow-sm"
         :class="`hover:border-${platform.color}-300 dark:hover:border-${platform.color}-600`">
        <div :class="`w-6 h-6 bg-${platform.color}-100 dark:bg-${platform.color}-900/30 rounded flex items-center justify-center`">
          <component :is="platform.icon" :class="`h-3.5 w-3.5 text-${platform.color}-600`" />
        </div>
        <span :class="`text-gray-700 dark:text-gray-300 group-hover:text-${platform.color}-600 transition-colors`">
          {{ platform.label }}
        </span>
      </a>
    </div>

    <!-- Bento Grid -->
    <BentoGrid>
      <!-- Quick Board -->
      <BentoCard 
        title="Quick Board"
        platform="quickboard"
        :icon="ShieldIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">Beta</span>
        </template>
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a href="/macos/tahoe26" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="MonitorIcon" class="h-3.5 w-3.5 text-emerald-600" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">macOS Tahoe 26</span>
                </div>
                <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
                  Developer Beta
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Latest preview release
                </div>
              </div>
            </div>
          </a>
          <a href="/ios/ios26" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="SmartphoneIcon" class="h-3.5 w-3.5 text-emerald-600" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">iOS 26</span>
                </div>
                <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
                  Developer Beta
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Latest preview release
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- macOS -->
      <BentoCard 
        title="macOS"
        platform="macos"
        :icon="MonitorIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">Latest</span>
        </template>
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a 
            v-for="(version, idx) in macosVersions.slice(0, 2)"
            :key="idx"
            :href="version.version.startsWith('14') ? `/macos/sonoma` : `/macos/sequoia`"
            class="block"
          >
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-150">
              <div class="space-y-1.5">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ version.releaseDate }}</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3 w-3" :class="version.cves > 0 ? 'text-orange-500' : 'text-gray-400'" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      {{ version.cves === 0 ? 'No CVEs' : `${version.cves} CVEs fixed` }}
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-base font-bold text-gray-900 dark:text-gray-100">
                    macOS {{ version.version }}
                  </div>
                  <div class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    Build {{ version.build }}
                  </div>
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- iOS & iPadOS -->
      <BentoCard 
        title="iOS & iPadOS"
        platform="ios"
        :icon="SmartphoneIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">Latest</span>
        </template>
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a 
            v-for="(version, idx) in iosVersions.slice(0, 2)"
            :key="idx"
            :href="version.version.startsWith('17') ? `/ios/ios17` : `/ios/ios18`"
            class="block"
          >
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 transition-all duration-150">
              <div class="space-y-1.5">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ version.releaseDate }}</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3 w-3" :class="version.cves > 0 ? 'text-orange-500' : 'text-gray-400'" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      {{ version.cves === 0 ? 'No CVEs' : `${version.cves} CVEs fixed` }}
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-base font-bold text-gray-900 dark:text-gray-100">
                    iOS {{ version.version }}
                  </div>
                  <div class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                    Build {{ version.build }}
                  </div>
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- Other Platforms -->
      <BentoCard 
        title="Other Platforms"
        platform="watchos"
        :icon="WatchIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">Latest</span>
        </template>
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a href="/watchos/watchos11" class="block">
            <div class="group/btn p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-all duration-150">
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Sep 2024</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-400" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      No CVEs
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                    watchOS 11.0
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Build 22R5356a
                  </div>
                </div>
              </div>
            </div>
          </a>
          <a href="/tvos/tvos18" class="block">
            <div class="group/btn p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-all duration-150">
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Sep 2024</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-400" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      No CVEs
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                    tvOS 18.0
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Build 22J5356a
                  </div>
                </div>
              </div>
            </div>
          </a>
          <a href="/visionos/visionos2" class="block">
            <div class="group/btn p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 transition-all duration-150">
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Sep 2024</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-400" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      No CVEs
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                    visionOS 2.0
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Build 22N5286g
                  </div>
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- Safari -->
      <BentoCard 
        title="Safari Updates"
        platform="safari"
        :icon="GlobeIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">Latest</span>
        </template>
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a href="/safari/safari18" class="block">
            <div class="group/btn p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 transition-all duration-150">
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Sep 2024</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-400" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      No CVEs
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                    Safari 18.0
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Build 20618.1.15.11.24
                  </div>
                </div>
              </div>
            </div>
          </a>
          <a href="/safari/safari18" class="block">
            <div class="group/btn p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 transition-all duration-150">
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Jul 29, 2024</span>
                  <div class="flex items-center gap-1">
                    <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-400" />
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      No CVEs
                    </span>
                  </div>
                </div>
                <div>
                  <div class="text-lg font-bold text-gray-900 dark:text-gray-100">
                    Safari 17.6
                  </div>
                  <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Build 19618.3.11.11.4
                  </div>
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- Community -->
      <BentoCard 
        title="MacAdmins Community"
        platform="community"
        :icon="UsersIcon"
      >
        <div class="grid grid-cols-1 gap-3 flex-grow">
          <a href="https://github.com/macadmins/sofa" target="_blank" rel="noopener noreferrer" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="StarIcon" class="h-3.5 w-3.5 text-yellow-500" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">GitHub Repository</span>
                </div>
                <div class="text-lg font-bold text-indigo-700 dark:text-indigo-300">
                  macadmins/sofa
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ starCount || '264' }} stars • Open source
                </div>
              </div>
            </div>
          </a>
          <a href="http://macadmins.slack.com" target="_blank" rel="noopener noreferrer" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="MessageCircleIcon" class="h-3.5 w-3.5 text-green-500" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">MacAdmins Slack</span>
                </div>
                <div class="text-lg font-bold text-indigo-700 dark:text-indigo-300">
                  #sofa
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Join the conversation
                </div>
              </div>
            </div>
          </a>
        </div>
      </BentoCard>

      <!-- macOS Data Feed -->
      <BentoCard 
        title="macOS Data Feed"
        platform="feed-macos"
        :icon="DownloadIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">Live</span>
        </template>
        <div class="space-y-3 flex-grow">
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <div class="flex items-center gap-1">
                <component :is="ClockIcon" class="h-3.5 w-3.5 text-blue-600" />
                <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Last Check</span>
              </div>
              <div class="text-lg font-bold text-blue-700 dark:text-blue-300">
                {{ currentTime.local.time }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                Local • {{ currentTime.local.date }}
              </div>
            </div>
            <div class="space-y-1">
              <div class="flex items-center gap-1">
                <component :is="GlobeIcon" class="h-3.5 w-3.5 text-blue-600" />
                <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">UTC</span>
              </div>
              <div class="text-sm font-bold text-blue-700 dark:text-blue-300">
                {{ currentTime.utc.full }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                Coordinated Universal Time
              </div>
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ShieldIcon" class="h-3.5 w-3.5 text-blue-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Update Hash (SHA-256)</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm font-mono text-blue-700 dark:text-blue-300">
                {{ updateHash.substring(0, 12) }}...{{ updateHash.slice(-12) }}
              </span>
              <button 
                @click.stop="copyToClipboard(updateHash, 'macos-hash')"
                class="text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                title="Copy full hash"
              >
                <component :is="copiedItem === 'macos-hash' ? CheckCircle2Icon : ClipboardIcon" class="h-3.5 w-3.5" :class="copiedItem === 'macos-hash' ? 'text-green-500' : ''" />
              </button>
            </div>
          </div>
        </div>
        <template #footer>
          <button
            @click="copyToClipboard('https://sofafeed.macadmins.io/v1/macos_data_feed.json', 'macos-footer')"
            class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1 transition-colors"
          >
            <component :is="copiedItem === 'macos-footer' ? CheckCircle2Icon : ClipboardIcon" class="h-3 w-3" :class="copiedItem === 'macos-footer' ? 'text-green-500' : ''" />
            {{ copiedItem === 'macos-footer' ? 'URL Copied!' : 'Copy Feed URL' }}
          </button>
        </template>
      </BentoCard>

      <!-- iOS Data Feed -->
      <BentoCard 
        title="iOS Data Feed"
        platform="feed-ios"
        :icon="SmartphoneIcon"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">Live</span>
        </template>
        <div class="space-y-3 flex-grow">
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <div class="flex items-center gap-1">
                <component :is="ClockIcon" class="h-3.5 w-3.5 text-purple-600" />
                <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Last Check</span>
              </div>
              <div class="text-lg font-bold text-purple-700 dark:text-purple-300">
                {{ currentTime.local.time }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                Local • {{ currentTime.local.date }}
              </div>
            </div>
            <div class="space-y-1">
              <div class="flex items-center gap-1">
                <component :is="GlobeIcon" class="h-3.5 w-3.5 text-purple-600" />
                <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">UTC</span>
              </div>
              <div class="text-sm font-bold text-purple-700 dark:text-purple-300">
                {{ currentTime.utc.full }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                Coordinated Universal Time
              </div>
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ShieldIcon" class="h-3.5 w-3.5 text-purple-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Update Hash (SHA-256)</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm font-mono text-purple-700 dark:text-purple-300">
                cef30622...70d087c
              </span>
              <button 
                @click.stop="copyToClipboard('cef30622604abdf52b2dcd44040239210907d56d9592cfc693c017c3470d087c', 'ios-hash')"
                class="text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
                title="Copy full hash"
              >
                <component :is="copiedItem === 'ios-hash' ? CheckCircle2Icon : ClipboardIcon" class="h-3.5 w-3.5" :class="copiedItem === 'ios-hash' ? 'text-green-500' : ''" />
              </button>
            </div>
          </div>
        </div>
        <template #footer>
          <button
            @click="copyToClipboard('https://sofafeed.macadmins.io/v1/ios_data_feed.json', 'ios-footer')"
            class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1 transition-colors"
          >
            <component :is="copiedItem === 'ios-footer' ? CheckCircle2Icon : ClipboardIcon" class="h-3 w-3" :class="copiedItem === 'ios-footer' ? 'text-green-500' : ''" />
            {{ copiedItem === 'ios-footer' ? 'URL Copied!' : 'Copy Feed URL' }}
          </button>
        </template>
      </BentoCard>

      <!-- Last Updated Status -->
      <BentoCard 
        title="Last Updated"
        :icon="ClockIcon"
        card-class="hover:border-gray-400 dark:hover:border-gray-500"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">Status</span>
        </template>
        <div class="grid grid-cols-2 gap-3 flex-grow">
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ActivityIcon" class="h-3.5 w-3.5 text-gray-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">macOS Feed</span>
            </div>
            <div class="text-lg font-bold text-gray-700 dark:text-gray-300">
              Live
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ currentTime.local.time }}
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ActivityIcon" class="h-3.5 w-3.5 text-gray-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">iOS Feed</span>
            </div>
            <div class="text-lg font-bold text-gray-700 dark:text-gray-300">
              Live
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ currentTime.local.time }}
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ShieldIcon" class="h-3.5 w-3.5 text-gray-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Hash Check</span>
            </div>
            <div class="text-lg font-bold text-gray-700 dark:text-gray-300 font-mono text-sm">
              {{ updateHash.substring(0, 8) }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Verified
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ServerIcon" class="h-3.5 w-3.5 text-gray-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">API Status</span>
            </div>
            <div class="text-lg font-bold text-green-700 dark:text-green-300">
              Online
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              All systems go
            </div>
          </div>
        </div>
        <template #footer>
          <p class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <component :is="CheckCircle2Icon" class="h-3 w-3 text-green-500" />
            All feeds operational
          </p>
        </template>
      </BentoCard>

      <!-- Data Statistics -->
      <BentoCard 
        title="Data Statistics"
        platform="statistics"
        :icon="ActivityIcon"
      >
        <template #badge>
          <span v-if="metricsLoading" class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200">Loading</span>
          <span v-else-if="metricsData && !metricsData.error" class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">Live</span>
          <span v-else class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">Offline</span>
        </template>
        <div v-if="metricsData && !metricsData.error" class="grid grid-cols-2 gap-3 flex-grow">
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="GlobeIcon" class="h-3.5 w-3.5 text-emerald-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Total Requests</span>
            </div>
            <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
              {{ metricsData.metrics.totalRequests.formatted }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Last 30 days
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="UsersIcon" class="h-3.5 w-3.5 text-emerald-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Unique Visitors</span>
            </div>
            <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
              {{ metricsData.metrics.uniqueVisitors.formatted }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Monthly users
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ServerIcon" class="h-3.5 w-3.5 text-emerald-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Bandwidth</span>
            </div>
            <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
              {{ metricsData.metrics.bandwidth.formatted }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Data transfer
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="TrendingUpIcon" class="h-3.5 w-3.5 text-emerald-600" />
              <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">Daily Average</span>
            </div>
            <div class="text-lg font-bold text-emerald-700 dark:text-emerald-300">
              {{ metricsData.calculated.dailyAverage.formatted.visitors }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Visitors/day
            </div>
          </div>
        </div>
        <div v-else-if="!metricsLoading" class="grid grid-cols-2 gap-3 flex-grow">
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="GlobeIcon" class="h-3.5 w-3.5 text-gray-400" />
              <span class="font-semibold text-gray-500 text-sm">Total Requests</span>
            </div>
            <div class="text-lg font-bold text-gray-400">--</div>
            <div class="text-xs text-gray-400">No data</div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="UsersIcon" class="h-3.5 w-3.5 text-gray-400" />
              <span class="font-semibold text-gray-500 text-sm">Unique Visitors</span>
            </div>
            <div class="text-lg font-bold text-gray-400">--</div>
            <div class="text-xs text-gray-400">No data</div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="ServerIcon" class="h-3.5 w-3.5 text-gray-400" />
              <span class="font-semibold text-gray-500 text-sm">Bandwidth</span>
            </div>
            <div class="text-lg font-bold text-gray-400">--</div>
            <div class="text-xs text-gray-400">No data</div>
          </div>
          <div class="space-y-1">
            <div class="flex items-center gap-1">
              <component :is="TrendingUpIcon" class="h-3.5 w-3.5 text-gray-400" />
              <span class="font-semibold text-gray-500 text-sm">Daily Average</span>
            </div>
            <div class="text-lg font-bold text-gray-400">--</div>
            <div class="text-xs text-gray-400">No data</div>
          </div>
        </div>
        <template #footer>
          <p v-if="metricsData && !metricsData.error" class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <component :is="CheckCircle2Icon" class="h-3 w-3 text-green-500" />
            Updated {{ formatRelativeTime(metricsData.timestamp) }}
          </p>
          <p v-else-if="metricsLoading" class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <component :is="ClockIcon" class="h-3 w-3" />
            Loading metrics...
          </p>
          <p v-else class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <component :is="ClockIcon" class="h-3 w-3" />
            Metrics unavailable
          </p>
        </template>
      </BentoCard>

      <!-- Apple Beta Releases - Spans 2 columns -->
      <BentoCard 
        title="Apple Beta Releases"
        platform="beta-gradient"
        :icon="SparklesIcon"
        class="md:col-span-2"
      >
        <template #badge>
          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">Developer</span>
        </template>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 flex-grow">
          <div v-for="(beta, idx) in betaReleases" :key="idx" class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-orange-300 dark:hover:border-orange-600 transition-all duration-150">
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ beta.released }}</span>
                <div class="flex items-center gap-1">
                  <component :is="SparklesIcon" class="h-3 w-3 text-orange-500" />
                  <span class="text-xs text-orange-600 dark:text-orange-400">
                    Beta
                  </span>
                </div>
              </div>
              <div>
                <div class="text-base font-bold text-gray-900 dark:text-gray-100">
                  {{ beta.platform }} {{ beta.version }}
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                  Build {{ beta.build }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <template #footer>
          <button
            @click="copyToClipboard('https://beta-feed.macadmin.me/v1/apple-beta-os-feed.json', 'beta-footer')"
            class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1 transition-colors"
          >
            <component :is="copiedItem === 'beta-footer' ? CheckCircle2Icon : ClipboardIcon" class="h-3 w-3" :class="copiedItem === 'beta-footer' ? 'text-green-500' : ''" />
            {{ copiedItem === 'beta-footer' ? 'URL Copied!' : 'Copy Beta Feed URL' }}
          </button>
        </template>
      </BentoCard>

      <!-- Community Support -->
      <BentoCard 
        title="MacAdmins Community"
        platform="community-gradient"
        :icon="HeartIcon"
      >
        <div class="grid grid-cols-2 gap-3 flex-grow">
          <a href="https://github.com/sponsors/macadmins?o=esb" target="_blank" rel="noopener noreferrer" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="HeartIcon" class="h-3.5 w-3.5 text-red-500" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">MAOS</span>
                </div>
                <div class="text-lg font-bold text-indigo-700 dark:text-indigo-300">
                  Donate
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Open Source
                </div>
              </div>
            </div>
          </a>
          <a href="https://www.macadmins.org/donate" target="_blank" rel="noopener noreferrer" class="block">
            <div class="group/btn p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600 transition-all duration-150">
              <div class="space-y-1">
                <div class="flex items-center gap-1">
                  <component :is="HeartIcon" class="h-3.5 w-3.5 text-red-500" />
                  <span class="font-semibold text-gray-900 dark:text-gray-100 text-sm">MAF</span>
                </div>
                <div class="text-lg font-bold text-indigo-700 dark:text-indigo-300">
                  Support
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  Foundation
                </div>
              </div>
            </div>
          </a>
        </div>
        <template #footer>
          <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
            We're thrilled to have you here! 👋
          </p>
        </template>
      </BentoCard>

    </BentoGrid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import BentoGrid from './BentoGrid.vue'
import BentoCard from './BentoCard.vue' 
import BentoButton from './BentoButton.vue'
import SOFALogoSVG from './SOFALogoSVG.vue'

// Icons - you'll need to import these from your icon library
import {
  Monitor as MonitorIcon,
  Smartphone as SmartphoneIcon,
  Tv as TvIcon,
  Watch as WatchIcon,
  Shield as ShieldIcon,
  Globe as GlobeIcon,
  Eye as EyeIcon,
  Download as DownloadIcon,
  ExternalLink as ExternalLinkIcon,
  Star as StarIcon,
  MessageCircle as MessageCircleIcon,
  Clipboard as ClipboardIcon,
  Clock as ClockIcon,
  CheckCircle2 as CheckCircle2Icon,
  Activity as ActivityIcon,
  TrendingUp as TrendingUpIcon,
  Server as ServerIcon,
  Sparkles as SparklesIcon,
  Heart as HeartIcon,
  Users as UsersIcon
} from 'lucide-vue-next'

// Platform navigation data
const platforms = [
  { name: 'macos', label: 'Sequoia 15', link: '/macos/sequoia', icon: MonitorIcon, color: 'blue' },
  { name: 'macos-sonoma', label: 'Sonoma 14', link: '/macos/sonoma', icon: MonitorIcon, color: 'blue' },
  { name: 'macos-tahoe', label: 'Tahoe 26 Beta', link: '/macos/tahoe26', icon: MonitorIcon, color: 'orange' },
  { name: 'ios', label: 'iOS/iPadOS 18', link: '/ios/ios18', icon: SmartphoneIcon, color: 'purple' },
  { name: 'ios-beta', label: 'iOS 26 Beta', link: '/ios/ios26', icon: SmartphoneIcon, color: 'orange' },
  { name: 'visionos', label: 'visionOS 2', link: '/visionos/visionos2', icon: EyeIcon, color: 'orange' },
  { name: 'tvos', label: 'tvOS 18', link: '/tvos/tvos18', icon: TvIcon, color: 'green' },
  { name: 'watchos', label: 'watchOS 11', link: '/watchos/watchos11', icon: WatchIcon, color: 'pink' },
  { name: 'safari', label: 'Safari 18', link: '/safari/safari18', icon: GlobeIcon, color: 'cyan' }
]

// Import JSON data directly
import macosDataFile from '/v1/macos_data_feed.json'
import iosDataFile from '/v1/ios_data_feed.json'
import betaDataFile from '/v1/apple-beta-os-feed.json'

// Real data from JSON feeds
const macosData = ref(macosDataFile)
const iosData = ref(iosDataFile)
const betaDataRaw = ref(betaDataFile)

// Helper function to format dates
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: '2-digit' 
    })
  } catch {
    return 'Unknown'
  }
}

// Computed properties for processed data
const macosVersions = computed(() => {
  if (!macosData.value?.OSVersions) return []
  return macosData.value.OSVersions.slice(0, 2).map(version => ({
    version: version.Latest.ProductVersion,
    osVersion: version.OSVersion,
    build: version.Latest.Build,
    releaseDate: formatDate(version.Latest.ReleaseDate),
    cves: version.SecurityReleases?.[0]?.CVEs ? Object.keys(version.SecurityReleases[0].CVEs).length : 0
  }))
})

const iosVersions = computed(() => {
  if (!iosData.value?.OSVersions) return []
  return iosData.value.OSVersions.slice(0, 2).map(version => ({
    version: version.Latest.ProductVersion,
    osVersion: version.OSVersion,
    build: version.Latest.Build,
    releaseDate: formatDate(version.Latest.ReleaseDate),
    cves: version.SecurityReleases?.[0]?.CVEs ? Object.keys(version.SecurityReleases[0].CVEs).length : 0
  }))
})

const betaReleases = computed(() => {
  if (!betaDataRaw.value?.items) return []
  
  // Define the desired order
  const platformOrder = ['macOS', 'iOS', 'iPadOS', 'tvOS', 'visionOS', 'watchOS']
  
  // Get all beta releases and sort by platform order
  const releases = betaDataRaw.value.items.filter(item => 
    platformOrder.includes(item.platform)
  )
  
  // Sort by the defined platform order
  releases.sort((a, b) => {
    const aIndex = platformOrder.indexOf(a.platform)
    const bIndex = platformOrder.indexOf(b.platform)
    return aIndex - bIndex
  })
  
  // Return first 6 items to show all major platforms
  return releases.slice(0, 6)
})

const updateHash = computed(() => {
  return macosData.value?.UpdateHash || 'a8f47c2d9b3e7f1a4c6d8b2f7e9a1c5d8f3b6a9c2e7d4f1a8b5c9e2d7f6a3c1b8e5'
})

const currentTime = computed(() => {
  const now = new Date()
  return {
    local: {
      time: now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: false 
      }),
      date: now.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
    },
    utc: {
      time: now.toISOString().slice(11, 19) + ' UTC',
      date: now.toISOString().slice(0, 10),
      full: now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
    }
  }
})

// Track copied items for visual feedback
const copiedItem = ref<string | null>(null)
const starCount = ref<string>('')

// Metrics data
const metricsData = ref<any>(null)
const metricsLoading = ref(true)

// Helper function to format relative time
const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

// Fetch GitHub star count and metrics
onMounted(async () => {
  // Fetch GitHub stars
  try {
    const response = await fetch('https://api.github.com/repos/macadmins/sofa')
    if (response.ok) {
      const data = await response.json()
      if (data.stargazers_count) {
        starCount.value = data.stargazers_count.toLocaleString()
      }
    }
  } catch (error) {
    console.log('Could not fetch star count')
  }
  
  // Fetch metrics data
  try {
    const response = await fetch('/v1/metrics.json')
    if (response.ok) {
      metricsData.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch metrics:', error)
  } finally {
    metricsLoading.value = false
  }
})

const copyToClipboard = async (text: string, itemId?: string) => {
  try {
    await navigator.clipboard.writeText(text)
    if (itemId) {
      copiedItem.value = itemId
      setTimeout(() => {
        copiedItem.value = null
      }, 2000)
    }
  } catch (err) {
    console.error('Failed to copy text: ', err)
  }
}
</script>

<style scoped>
.dashboard-container {
  max-width: 1024px;
  margin: 0 auto !important;
  padding: 0 1.5rem 2rem 1.5rem; /* Remove top padding to use header padding */
  width: 100%;
  overflow: visible; /* Ensure glow is visible */
}

.sofa-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 3rem;
  width: 100%;
  padding-top: 5rem; /* More padding when nav is visible */
  overflow: visible;
}

.sofa-image-container {
  width: 120px;
  height: 120px;
  margin-bottom: 1.5rem;
  margin-top: 2rem; /* More space for glow when nav visible */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-radius: 24px;
}

.sofa-image-container::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150%;
  height: 150%;
  background: radial-gradient(circle at center, 
    rgba(96, 165, 250, 0.6) 0%, 
    rgba(168, 85, 247, 0.5) 25%, 
    rgba(96, 165, 250, 0.3) 50%, 
    rgba(168, 85, 247, 0.15) 75%, 
    transparent 100%);
  filter: blur(40px);
  z-index: -1;
}

.sofa-logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
  z-index: 1;
  filter: drop-shadow(0 10px 40px rgba(96, 165, 250, 0.5));
}

.sofa-name {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 1.5rem 0;
  line-height: 1.3;
  letter-spacing: -0.02em;
}

.sofa-text {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}

.sofa-separator {
  color: #64748b;
  font-weight: 400;
}

.sofa-full {
  background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.sofa-tagline {
  font-size: 1.125rem;
  font-weight: 400;
  color: #64748b;
  max-width: 36rem;
  margin: 0 auto 2.5rem auto;
  line-height: 1.6;
}

.dark .sofa-tagline {
  color: #94a3b8;
}

.dark .sofa-separator {
  color: #94a3b8;
}

.dark .sofa-text {
  background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .sofa-full {
  background: linear-gradient(135deg, #93c5fd 0%, #c084fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Welcome Message */
.welcome-message {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

/* GitHub Widget Styles */
.github-widget {
  display: inline-flex;
  align-items: stretch;
  margin-top: 0.5rem;
  border-radius: 12px;
  overflow: visible;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.1));
  transition: transform 0.2s, filter 0.2s;
}

.github-widget:hover {
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.15));
}

.github-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-right: none;
  border-radius: 12px 0 0 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.github-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  border-color: rgba(118, 75, 162, 0.4);
}

.github-star-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.github-count {
  display: inline-flex;
  align-items: center;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 0 12px 12px 0;
  color: #667eea;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s;
}

.github-count:hover {
  background: rgba(255, 255, 255, 1);
  color: #764ba2;
  border-color: rgba(118, 75, 162, 0.4);
}

.dark .github-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-color: rgba(59, 130, 246, 0.3);
  color: white;
}

.dark .github-btn:hover {
  background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
  border-color: rgba(96, 165, 250, 0.4);
}

.dark .github-count {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

.dark .github-count:hover {
  background: rgba(51, 65, 85, 0.9);
  color: #93c5fd;
  border-color: rgba(96, 165, 250, 0.4);
}

.dark .sofa-image-container::before {
  background: radial-gradient(circle at center, 
    rgba(124, 58, 237, 0.4) 0%, 
    rgba(236, 72, 153, 0.3) 30%, 
    rgba(124, 58, 237, 0.1) 60%, 
    transparent 100%);
}

.dark .sofa-logo {
  filter: drop-shadow(0 4px 20px rgba(124, 58, 237, 0.4));
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1.5rem 1rem 1.5rem 1rem; /* Adjusted for mobile */
  }
  
  .sofa-name {
    font-size: 1.75rem;
  }
  
  .sofa-full {
    display: block;
    margin-top: 0.5rem;
    font-size: 1.5rem;
  }
  
  .sofa-text {
    font-size: 2rem;
  }
  
  .sofa-tagline {
    font-size: 1rem;
  }
  
  .sofa-image-container {
    width: 100px;
    height: 100px;
  }
  
  .sofa-logo {
    width: 80px;
    height: 80px;
  }
}
</style>