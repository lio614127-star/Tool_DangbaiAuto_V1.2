# Requirements

## Functional Requirements
1. **URL Support**: Support for Douyin channel and video links (short and long URLs).
2. **Data Extraction**:
    - Use injected JS scripts (02, 03, 04) to extract channel and video metadata.
    - Extract: Title, Views, Likes, Like ratio, Date, and Duration.
3. **Filtering & Sorting**:
    - Filter videos by minimum view count.
    - Sort results by Views (High-to-Low), Likes, Recency.
4. **Downloading**:
    - Batch download selected or filtered videos.
    - Use injected JS script (01) for the download process.
    - Save to a user-specified folder.
5. **UI/UX**:
    - Premium Dark Theme.
    - Real-time logging of internal steps.
    - Progress visualization for downloads.

## Non-Functional Requirements
1. **Performance**: Headless browser execution to keep the environment clean.
2. **Reliability**: Handle network timeouts and script execution errors gracefully.
3. **Usability**: Intuitive feedback through the log box and status messages.
