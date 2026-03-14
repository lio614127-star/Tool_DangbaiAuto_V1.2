# Project State: Douyin Downloader & Analyzer

## 🚀 Current Status
**Fully Functional & Packaged.**
The application is mature, synchronized with GitHub, and optimized for both technical and non-technical users. 

## 🛠 Project Journey (From Build to Now)

### Phase 1: Core Infrastructure
- **Base Architecture**: Developed a modular system with `main.py` entry point, `src/ui` for GUI, and `src/core` for scraping logic.
- **Scraping Engine**: Integrated **Playwright** to handle Douyin's dynamic content and security layers.
- **Data Models**: Defined `ChannelInfo` and `VideoInfo` structures for consistent data handling.
- **Persistence**: Implemented persistent browser contexts to save login sessions (cookies).

### Phase 2: Feature Implementation
- **Channel Analysis**: Multi-stage scraping (Script 02, 03, 04) to extract deep metadata: Views, Likes, Shares, Create Time, and Duration.
- **Auto-Translation**: Integrated Google Translate API to automatically convert Chinese titles to Vietnamese.
- **Filtering & Sorting System**: Built advanced logic to filter by likes, duration, and date, with multiple sorting options.
- **Download Manager**: Developed a robust batch downloader with:
  - Watermark removal logic.
  - Automatic retry on failure.
  - Random delays (2-5s) to bypass anti-bot detection.
  - File size validation (>100KB) to Ensure healthy downloads.

### Phase 3: UI/UX Refinement
- **Modern GUI**: Used **CustomTkinter** for a premium dark-themed interface with high-contrast elements.
- **Interactive Table**: A `Treeview` based table supporting multi-selection and real-time STT (Số thứ tự) updates.
- **Log System**: A dedicated terminal-style log box in the UI that provides meaningful status updates.
- **(Latest) Log Cleanup**: Suppressed noisy browser console messages to keep the log focused on actionable info.
- **(Latest) Fixed STT Numbering**: Implemented a "sticky" numbering system where each video maintains its original STT (based on post date, 1 = newest) regardless of subsequent filtering or sorting.

### Phase 4: Packaging & Distribution
- **Standalone EXE**: Created `build.py` and `DouyinDownloader.spec` for one-click packaging via PyInstaller.
- **Assets**: Designed and integrated `app_icon.ico` for the professional executable look.
- **Documentation**: Produced `HUONG_DAN_NHANH.txt` and `README.md` for user guidance.
- **GitHub Sync**: 
  - established repository: `https://github.com/lio614127-star/Tool_DangbaiAuto.git`
  - Configured `.gitignore` to protect personal configs and keep the repo clean.

### Phase 5: Resync & Enhancements
- **Codebase Reset**: Reverted all experimental code to match the stable `origin/master` GitHub version.
- **UI Enhancements**:
  - Changed stats row ("Video", "TB Views", "TB Likes", etc.) to high-visibility white text.
  - Added a dedicated `"↻ Tải lại lỗi"` (Retry failed downloads) button to explicitly fetch failed videos without restarting the batch.
  - Modified "Top 20 / Top 50" quick select logic to sort by **Likes** instead of Views, better suiting Douyin's metric focus.

### Phase 6: Scraper Stabilization & Core Fixes (Latest)
- **Anti-Bot Bypass**: Switched Playwright to `headless=False` for Script 02 channel analysis. The visible Chromium window completely bypasses Douyin's aggressive bot detection (the root cause of empty API responses) and properly leverages existing login cookies.
- **Pagination Reliability**: 
  - Overhauled Script 02 logic to survive page redirects (`Execution context was destroyed` error) by waiting for `networkidle` and increasing timeouts to 10 minutes.
  - Implemented an aggressive cursor override (falling back to timestamps) to force Douyin to yield all videos when its API prematurely returns `has_more=0`, ensuring exact video counts (e.g., 116/116 videos).
- **Download Management**: Updated folder creation to dynamically append the creator's visible ID (`ChannelName_138277198`), preventing folder collisions. The extraction logic strictly prioritizes `unique_id` then `short_id`, while explicitly filtering out internal database values (`uid`) or encrypted strings (`sec_uid`) to keep folder names clean.
- **Performance Optimization**: Completely removed the Google Translate API dependency from the title extraction phase, drastically speeding up analysis time and reducing network error points.

### Phase 7: Channel Management & Incremental Updates (Current)
- **Channel Sidebar**: Integrated a "Kênh đã lưu" (Saved Channels) sidebar to manage frequently analyzed creators.
- **Incremental Scanning**: 
  - Implemented a "5-match" stopping heuristic to efficiently skip pre-analyzed and pinned videos.
  - Significantly reduced API calls and analysis time for daily channel updates.
- **Persistent Data Migration**: 
  - Moved `config.json`, `channels.json`, and `user_data` (browser profile) from the project folder to `%LOCALAPPDATA%\DouyinDownloader`.
  - ensures that settings, saved channels, and login sessions are **not lost** when the tool is updated, deleted, or moved.
  - Implemented an automatic migration logic to seamlessly transfer legacy data on first run.
- **UI Performance**: Refined the right sidebar with a black high-contrast background and restored footer controls for a more stable user experience.

### Phase 8: Visual Cues & Robustness Fixes (Latest)
- **Visual Highlighting**: Implemented a subtle dark green background (`BG_HIGHLIGHT`) for "New" videos in the table. This allows users to immediately distinguish newly found videos during incremental updates.
- **Sidebar Deduplication (Greedy Merging)**:
  - Overhauled the save logic to prevent duplicate channel entries.
  - Implemented "Greedy Merging": when an update is triggered, the tool automatically detects and collapses duplicate records based on normalized URLs or Channel IDs.
  - Added deduplication on application startup to ensure a clean sidebar state from the first second.
- **Incremental Update Refinement**:
  - Re-engineered the communication between Python and the browser scripts using an explicit `__IS_INCREMENTAL__` flag.
  - Fixed a critical regression where "Update Video" would perform a full scan on uninitialized channels; it now correctly returns 0 videos, respecting the "delta-only" intent.
- **Improved Logging**: Added clear, actionable logs in the footer for matching events, target IDs, and merging actions.

## 📋 Handover & Operations
- **To Run**: `python main.py`
- **To Build .exe**: `python build.py`
- **GitHub Policy**: Manual updates only (command: "cập nhật tool lên github").
- **Key Dependencies**: `customtkinter`, `playwright`, `httpx`, `beautifulsoup4`.
- **System Path**: Persistent data is stored at `%LOCALAPPDATA%\DouyinDownloader`.
