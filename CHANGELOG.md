# Changelog

All notable changes to the Immoweb Scraper project will be documented in this file.

## [2.0.0] - 2024-01-XX

### Added
- **Interactive Scraper with Selenium**: New interactive scraper that opens a real Chrome browser
  - Full browser control - navigate freely like a normal Chrome browser
  - Uses your real Chrome profile with cookies and session
  - Interactive workflow creation system
  - Test selectors before scraping
  - Save and load workflows as JSON
  - Browser stays open after script ends for continued use

- **Browser Cookie Integration**: Enhanced cookie management
  - Automatic loading of cookies from Chrome, Edge, and Firefox browsers
  - Uses real browser sessions to avoid 403 blocks
  - Fallback to session cookies if browser cookies unavailable

- **Improved Error Handling**:
  - Better handling of empty datasets
  - Graceful handling of missing columns
  - Improved error messages with clear suggestions

- **Sequential Request Mode**: 
  - Replaced threading with sequential requests to avoid blocking
  - Configurable delays between requests
  - Retry mechanism with exponential backoff

### Changed
- **Import Path Fix**: Fixed import from `scraper.scraper6` to `scraper.scraper`
- **Postal Code Filtering**: Fixed logic to keep valid postal codes (length >= 5)
- **Price Extraction**: Fixed bug where `soup.find()` was incorrectly iterated
- **DataFrame Cleaning**: Added checks for empty DataFrames and missing columns
- **Request Headers**: Enhanced headers to better mimic real browsers
- **User-Agent**: Updated to Chrome 120.0.0.0

### Fixed
- Fixed `EmptyDataError` when CSV file is empty
- Fixed Unicode encoding issues on Windows (replaced special characters)
- Fixed `NameError` with psutil import
- Fixed postal code filtering logic (was keeping invalid codes)
- Fixed price extraction bug (iterating over single element)
- Fixed province and region functions to handle NaN values
- Fixed pattern replacement to handle NaN values in Locality name

### Dependencies
- Added `selenium==4.17.2` for browser automation
- Added `webdriver-manager==4.0.2` for automatic ChromeDriver management
- Added `browser-cookie3==0.20.1` for browser cookie extraction
- Added `psutil` for process detection

## [1.0.0] - Initial Release

### Features
- Basic Immoweb scraping functionality
- Command-line interface
- Raw and cleaned data output (CSV)
- Data cleaning and transformation pipeline
- Support for houses and apartments
- Up to 333 pages of search results

