# Roadmap

## Phase 1: UI Skeleton & Architecture (Finalized)
- [x] Initial project folder structure.
- [x] Core UI design with CustomTkinter (User approved aesthetics).
- [x] Background async loop for stability.
- [x] Environment setup (Playwright + Chromium installed).
- [x] Script management strategy (Files in `src/scripts/`).

## Phase 2: Core Logic & Script Integration (Finalized)
- [x] Script Repository: All 4 scripts (01-04) saved in `src/scripts/`.
- [x] Data Model Upgrade: `VideoInfo` updated with extra stat fields.
- [x] Logic: Implement `page.evaluate()` injection for Script 02.
- [x] Logic: Bridge `console.log` from browser to UI Log Box.
- [x] UI: Populate Stats Cards and Video Table with real data from scripts.
- [x] Logic: Implement "Login Mode" to persistent browser context/cookies.
- [x] Integration: Connect Script 03 for server-side (browser) sorting test.
- [x] Logic: Fix UI "Select All" checkbox functionality.

## Phase 3: Selection, Filter Logic & Batch Download (Finalized)
- [x] Select All/Individual logic.
- [x] UI: Added "Translated Title" column to the main table.
- [x] Logic: Implement "Time Range" filtering (24h, 7d, 30d).
- [x] UI: Added "Select Top X" buttons (20, 50, Trends).
- [x] Logic: Implement smart download with bot-prevention delay (3-7s).
- [x] Logic: File management (Capture downloads and save to custom path).
- [x] UI: Add "Download Top X" quick actions (Footer buttons).

## Phase 4: Polish, Robustness & Packaging (Finalized)
- [x] Persistence: Save/Load download path in `config.json`.
- [x] Logic: Implement "Skip if exists" for downloads.
- [x] Robustness: File size validation (>100KB) after download + automatic cleanup.
- [x] UI: Add "🗑️ Clear Log" button.
- [x] Feedback: Add Windows Beep/Sound alert on batch completion.
- [x] Packaging: Script for building single-file EXE (`build.py`).

## Phase 5: Final Verification & Delivery (Finalized)
- [x] Full end-to-end testing (Login -> Analyze -> Filter -> Batch Download).
- [x] Final UI aesthetics check (Icon added).
- [x] Handover documentation (`HUONG_DAN_NHANH.txt`).

## Phase 6: Scraper Stabilization & Core Fixes (Finalized)
- [x] Switch Playwright to `headless=False` to bypass aggressive Douyin bot detection.
- [x] Implement cursor override logic to handle premature `has_more=0` reports.
- [x] Increase script timeouts and handle page navigation interruptions.
- [x] Optimize analysis speed by removing real-time translation dependency.
- [x] Standardize download folder names using extracted Channel IDs.

## Phase 7: Channel Management, Incremental Updates & Visual Cues (Finalized)
- [x] Implement "Saved Channels" sidebar UI with clickable interaction.
- [x] Build incremental scanning logic (Stop-at-ID).
- [x] Migrate all persistent data (config, channels, browser profile) to `%LOCALAPPDATA%`.
- [x] Add data migration logic for legacy project-folder files.
- [x] **Visual Highlighting**: Implement subtle green background for new videos.
- [x] **Greedy Merging**: Automatically collapse duplicate sidebar entries.
- [x] **Logic Refinement**: Fix incremental update behavior for new channels and explicit flags.
