# Testing v26 OS Data Deployment

## macOS 26 Test

<LatestFeatures title="26" platform="macOS" />

## iOS 26 Test

<LatestFeatures title="26" platform="iOS" />

## watchOS 26 Test

<LatestFeatures title="26" platform="watchOS" />

## tvOS 26 Test

<LatestFeatures title="26" platform="tvOS" />

---

## Version Ordering Test

The JSON files now contain v26 as the **first** entry in the OSVersions array, ensuring proper ordering:

1. **macOS 26** (26.0) - newest
2. **Sequoia 15** (15.4.1) - current
3. Previous versions...

This follows the expected pattern: `macOS 14 < macOS 15 < macOS 26`

## Expected Results

- ✅ v26 versions should display as "Latest" 
- ✅ Release date: September 16, 2025
- ✅ Build numbers: 26A100 (macOS), 26A100 (iOS), 26R100 (watchOS), 26J100 (tvOS)
- ✅ No CVEs (clean initial release)
- ✅ Proper version ordering in component dropdowns