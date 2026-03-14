import os
import asyncio
import json
import logging
from typing import Optional, Callable
from playwright.async_api import async_playwright
from src.core.models import ChannelInfo, VideoInfo, Platform
from src.utils.constants import SCRIPT_01, SCRIPT_02, SCRIPT_03, SCRIPT_04, DEFAULT_USER_AGENT, USER_DATA_DIR
import httpx
import urllib.parse
import asyncio

logger = logging.getLogger(__name__)

class DouyinScraper:
    def __init__(self):
        self._browser = None
        self._context = None
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    async def translate_text(self, text: str) -> str:
        """Call Google Translate API to translate Chinese to Vietnamese."""
        if not text: return ""
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=vi&dt=t&q={urllib.parse.quote(text)}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and data[0]:
                        return "".join([item[0] for item in data[0] if item[0]])
        except Exception as e:
            logger.error(f"Translation error: {e}")
        return text

    async def open_login_browser(self, logger_callback: Optional[Callable] = None):
        """Open a visible browser for the user to log in and auto-close when success."""
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=False,
                user_agent=DEFAULT_USER_AGENT
            )
            page = await context.new_page()
            await page.goto("https://www.douyin.com", wait_until="networkidle")
            
            if logger_callback: logger_callback("Vui lòng đăng nhập... Tool sẽ tự đóng khi thành công.")
            
            # Watch for login success (cookies often change or a specific element appears)
            # Douyin often sets specific cookies like 'sid_guard' on login
            for _ in range(300): # Max 5 minutes wait
                await asyncio.sleep(2)
                if page.is_closed(): break
                
                cookies = await context.cookies()
                # Check for critical login cookies
                if any(c['name'] == 'sid_guard' for c in cookies) or \
                   any(c['name'] == 'passport_csrf_token' for c in cookies):
                    if logger_callback: logger_callback("✅ Đăng nhập thành công! Đang lưu session...")
                    await asyncio.sleep(3) # Let it settle
                    break
            
            await context.close()

    def check_login_status(self) -> bool:
        """Check if we have valid-looking cookies in the user_data_dir."""
        # This is a bit tricky without a browser, but we can check if the directory has content
        # or we can try a quick headless check. For now, we'll look at the cookie files if possible.
        cookie_path = os.path.join(USER_DATA_DIR, "Default", "Network", "Cookies")
        return os.path.exists(cookie_path) and os.path.getsize(cookie_path) > 0

    async def _get_script_content(self, script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def analyze_channel(self, url: str, logger_callback: Optional[Callable] = None, known_video_ids: Optional[list[str]] = None) -> Optional[ChannelInfo]:
        """Analyze Douyin channel using Scripts 02, 03, 04."""
        self._is_cancelled = False
        if logger_callback: logger_callback("Đang khởi tạo trình duyệt ẩn...")
        
        async with async_playwright() as p:
            # headless=False: Chạy Chrome có giao diện, giống y hệt khi dùng thủ công
            # Đây là cách duy nhất đảm bảo Douyin không phát hiện bot và cookies hoạt động đúng
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=False,
                user_agent=DEFAULT_USER_AGENT,
                ignore_default_args=["--enable-automation"],
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-infobars",
                    "--window-size=1280,800",
                ]
            )
            page = await context.new_page()
            # Override webdriver flag
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                delete navigator.__proto__.webdriver;
            """)
            
            try:
                # 1. Validate / Fix URL
                url = url.strip()
                # If they pasted a partial ID or a broken link containing MS4w (Douyin ID token)
                if "MS4w" in url:
                    # Look for the MS4w part and take everything after (and including) it
                    import re
                    match = re.search(r"(MS4w[A-Za-z0-9_-]+)", url)
                    if match:
                        sec_uid = match.group(1)
                        url = f"https://www.douyin.com/user/{sec_uid}"
                
                # If it's still not a full URL
                if not url.startswith("http"):
                    url = f"https://www.douyin.com/{url.lstrip('/')}"
                
                if logger_callback: logger_callback("Đang kết nối tới Douyin...")
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    if logger_callback: logger_callback(f"⚠️ Cảnh báo kết nối chờ: {e}")
                
                if self._is_cancelled: return None

                if logger_callback: logger_callback("Đang chạy Script 02 - Lấy thông tin video toàn bộ kênh...")
                script_02 = await self._get_script_content(SCRIPT_02)
                
                # Đợi trang ổn định hoàn toàn trước khi chạy script
                # Tránh lỗi 'Execution context was destroyed' do redirect/navigate giữ a chừng
                try:
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    await page.wait_for_timeout(3000)  # fallback nếu networkidle timeout
                
                # Script 02 có thể chạy lâu (nhiều trang video) — đặt timeout 10 phút
                page.set_default_timeout(600_000)
                
                # Truyền danh sách video đã biết xuống context của JS
                if known_video_ids is not None:
                    await page.evaluate(f"window.__KNOWN_VIDEO_IDS__ = {json.dumps(known_video_ids)};")
                    await page.evaluate("window.__IS_INCREMENTAL__ = true;")
                    if logger_callback: logger_callback("Đang chạy ở chế độ: Cập nhật video mới...")
                else:
                    await page.evaluate("window.__KNOWN_VIDEO_IDS__ = [];")
                    await page.evaluate("window.__IS_INCREMENTAL__ = false;")
                    if logger_callback: logger_callback("Đang chạy ở chế độ: Phân tích toàn bộ kênh...")
                    
                res_data = await page.evaluate(script_02)

                raw_data = []
                nickname = "Dữ liệu từ Douyin"
                channel_id = ""
                
                if isinstance(res_data, dict):
                    raw_data = res_data.get("videos", [])
                    nickname = res_data.get("nickname", nickname)
                    channel_id = res_data.get("channel_id", "")
                elif isinstance(res_data, list):
                    raw_data = res_data

                if not raw_data:
                    # If it's an incremental update, finding 0 new videos is a valid SUCCESS (already up to date/empty history)
                    if known_video_ids is not None and nickname != "Dữ liệu từ Douyin":
                        if logger_callback: logger_callback("✅ Kênh đã ở trạng thái mới nhất (không có video mới).")
                        # Return an empty channel object instead of None
                        return ChannelInfo(title=nickname, channel_id=channel_id, total_videos=0, avg_views=0, avg_likes=0, top_views=0, videos=[])

                    logger.warning(f"[DEBUG] Script 02 returned empty. res_data={str(res_data)[:300]}")
                    if logger_callback: logger_callback(f"[DEBUG] Douyin trả về: {str(res_data)[:200]}")
                    if logger_callback: logger_callback("Lỗi: Script không tìm thấy video nào hoặc bị chặn.")
                    return None

                if logger_callback: logger_callback(f"Đang xử lý {len(raw_data)} video...")

                async def process_video(item):
                    stats = item.get("statistics", {})
                    original_title = item.get("desc", "")
                    play_count = (
                        stats.get("play_count") or stats.get("view_count") or
                        item.get("play_count") or item.get("view_count") or 0
                    )
                    return VideoInfo(
                        id=item.get("aweme_id", ""),
                        original_index=0,
                        title=original_title,
                        translated_title=original_title,  # Không dịch nữa, dùng tiêu đề gốc
                        author=item.get("author", {}).get("nickname", item.get("nickname", "Unknown")),
                        views=play_count,
                        likes=stats.get("digg_count", item.get("digg_count", 0)),
                        shares=stats.get("share_count", item.get("share_count", 0)),
                        create_time=item.get("create_time", 0),
                        duration=int((item.get("video", {}).get("duration", 0) or item.get("duration", 0) or 0) / 1000)
                    )

                videos = []
                chunk_size = 10
                for i in range(0, len(raw_data), chunk_size):
                    if self._is_cancelled: break
                    chunk_raw = raw_data[i : i + chunk_size]
                    chunk_tasks = [process_video(item) for item in chunk_raw]
                    chunk_results = await asyncio.gather(*chunk_tasks)
                    videos.extend(chunk_results)
                    if logger_callback: logger_callback(f"Đã xử lý: {len(videos)}/{len(raw_data)} video")

                total_views = sum(v.views for v in videos)
                total_likes = sum(v.likes for v in videos)
                top_views = max((v.views for v in videos), default=0)
                avg_views = total_views // len(videos) if videos else 0
                avg_likes = total_likes // len(videos) if videos else 0

                sorted_videos = sorted(videos, key=lambda x: x.create_time, reverse=True)
                for idx, v in enumerate(sorted_videos, 1):
                    v.original_index = idx

                channel = ChannelInfo(
                    title=nickname,
                    channel_id=channel_id,
                    total_videos=len(videos),
                    avg_views=avg_views,
                    avg_likes=avg_likes,
                    top_views=top_views,
                    videos=sorted_videos
                )

                if logger_callback: logger_callback(f"Phân tích thành công! Tìm thấy {len(videos)} video từ {nickname}.")
                return channel

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Scraper error details: {error_details}")
                if logger_callback: logger_callback(f"Lỗi: {str(e)}")
                return None
            finally:
                await context.close()


    async def download_video(self, url: str, download_path: str, filename: str = "", v_id: str = "", logger_callback: Optional[Callable] = None):
        """Download video using Script 01 and Playwright download handler."""
        if logger_callback: logger_callback(f"Chuẩn bị tải video: {v_id}")
        
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=True,
                user_agent=DEFAULT_USER_AGENT,
                accept_downloads=True
            )
            page = await context.new_page()
            
            try:
                # Capture the download event
                async with page.expect_download(timeout=120000) as download_info:
                    # Navigation timeout increased. Use 'commit' to get in fast, then wait for content.
                    try:
                        await page.goto(url, wait_until="commit", timeout=60000)
                        # Wait a bit for Douyin to initialize the window._ROUTER_DATA or similar
                        await page.wait_for_timeout(3000) 
                    except Exception as e:
                        if logger_callback: logger_callback(f"⚠️ Navigation warning: {e}. Thử tiếp tục...")

                    if logger_callback: logger_callback(f"Đang lấy link tải...")
                    
                    # Optimized Script 01 logic for Single Video Page
                    # This bypasses the need for "allow pasting" and "sec_user_id" on a video page
                    single_download_js = f"""
                    (async () => {{
                        console.clear(); 
                        const aweme_id = "{v_id}" || location.pathname.split('/').pop();
                        
                        async function triggerDownload(videoUrl, vid) {{
                            const res = await fetch(videoUrl, {{ headers: {{ "range": "bytes=0-" }}, credentials: "omit" }});
                            const blob = await res.blob();
                            const a = document.createElement("a");
                            a.href = window.URL.createObjectURL(blob);
                            a.download = "{filename}";
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }}

                        try {{
                            // Strategy 1: Look for ID in API detail
                            const detailUrl = `https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&aweme_id=${{aweme_id}}`;
                            const resp = await fetch(detailUrl, {{ credentials: "include" }});
                            const json = await resp.json();
                            const videoUrl = json.aweme_detail.video.play_addr.url_list[0].replace("http:", "https:");
                            await triggerDownload(videoUrl, aweme_id);
                        }} catch (e) {{
                            console.error("Download failed:", e);
                        }}
                    }})();
                    """
                    
                    await page.evaluate(single_download_js)
                    
                    # Wait for download to start
                    download = await download_info.value
                
                # If we have a custom filename from Python (passed from UI)
                final_filename = filename if filename else download.suggested_filename
                if not final_filename.endswith(".mp4"): final_filename += ".mp4"
                
                final_path = os.path.join(download_path, final_filename)
                await download.save_as(final_path)
                
                if logger_callback: logger_callback(f"✅ Đã lưu file: {final_filename}")
            except Exception as e:
                if logger_callback: logger_callback(f"❌ Lỗi tải: {str(e)}")
            finally:
                await context.close()
