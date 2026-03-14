import os
import threading
import asyncio
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from src.ui import styles as T
from src.core.models import Platform, URLType, ChannelInfo, VideoInfo
from src.core.scrapers.douyin_scraper import DouyinScraper
from src.utils.constants import DEFAULT_DOWNLOAD_PATH, CONFIG_FILE

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Douyin Downloader & Analyzer v1.0.0")
        self.geometry("1200x800")
        self.configure(fg_color=T.BG_PRIMARY)

        # Scraper logic
        self.scraper = DouyinScraper()
        self.all_selected = False
        self.current_channel = None
        self.failed_downloads: list = [] # Track failed (vid, filename)
        self._async_loop = None
        
        # Load Settings
        self.settings = self._load_settings()
        
        self._start_async_loop()
        self._setup_ui()
        self.after(1000, lambda: asyncio.run_coroutine_threadsafe(self._update_login_status(), self._async_loop))

    def _load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"download_path": DEFAULT_DOWNLOAD_PATH}

    def _save_settings(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except: pass

    def _start_async_loop(self):
        """Start an asyncio event loop in a background thread."""
        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self._async_loop = asyncio.new_event_loop()
        t = threading.Thread(target=run_loop, args=(self._async_loop,), daemon=True)
        t.start()

    def _setup_ui(self):
        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Main body row

        # 1. Header (Search Bar) - Row 0
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=T.PAD_LG, pady=(T.PAD_LG, T.PAD_MD))
        self.header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.header, text="🎵 Douyin Downloader", font=(T.FONT_FAMILY, T.FONT_SIZE_TITLE, "bold"), text_color=T.ACCENT).grid(row=0, column=0, padx=(0, T.PAD_LG))
        
        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            self.header, 
            placeholder_text="Dán mã ID hoặc link kênh vào đây...",
            textvariable=self.url_var,
            height=40,
            fg_color=T.BG_TERTIARY,
            border_color=T.ACCENT,
            text_color=T.TEXT,
            placeholder_text_color=T.TEXT_SECONDARY
        )
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=T.PAD_MD)

        self.analyze_btn = ctk.CTkButton(
            self.header, 
            text="🔍 Phân tích kênh", 
            width=150,
            height=40,
            fg_color=T.ACCENT, 
            hover_color=T.ACCENT_HOVER,
            text_color="#FFFFFF",
            font=(T.FONT_FAMILY, 14, "bold"),
            command=self._on_analyze
        )
        self.analyze_btn.grid(row=0, column=2, padx=T.PAD_SM)

        self.login_btn = ctk.CTkButton(
            self.header,
            text="🔑 Đăng nhập",
            width=120,
            height=40,
            fg_color=T.BG_TERTIARY,
            command=self._on_login
        )
        self.login_btn.grid(row=0, column=3, padx=(T.PAD_SM, 0))

        # 2. Stats Bar - Row 1
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=T.PAD_LG, pady=T.PAD_MD)
        
        self.stat_cards = []
        labels = ["Video", "TB Views", "TB Likes", "Trending", "Top Views"]
        for i, label in enumerate(labels):
            self.stats_frame.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(self.stats_frame, fg_color=T.BG_SECONDARY, height=70, corner_radius=T.RADIUS_MD)
            card.grid(row=0, column=i, padx=T.PAD_SM, sticky="ew")
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=label, font=(T.FONT_FAMILY, T.FONT_SIZE_SMALL), text_color="white").grid(row=0, column=0, pady=(10, 0))
            ctk.CTkLabel(card, text="0", font=(T.FONT_FAMILY, 18, "bold"), text_color="white").grid(row=1, column=0)
            self.stat_cards.append(card)

        # 3. Main Body - Row 2
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, sticky="nsew", padx=T.PAD_LG, pady=T.PAD_MD)
        self.body.grid_columnconfigure(1, weight=1) # Table expands
        self.body.grid_rowconfigure(0, weight=1)

        # Sidebar (Left)
        self.sidebar = ctk.CTkFrame(self.body, fg_color=T.BG_SECONDARY, width=280, corner_radius=T.RADIUS_LG)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, T.PAD_MD))
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="⚙️ Bộ lọc & Sắp xếp", font=(T.FONT_FAMILY, T.FONT_SIZE_HEADING, "bold"), text_color=T.TEXT).pack(pady=T.PAD_LG)
        
        ctk.CTkLabel(self.sidebar, text="Sắp xếp theo:", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD)
        self.sort_option = ctk.CTkOptionMenu(self.sidebar, values=["Likes (cao -> thấp)", "Mới nhất", "Cũ nhất", "Thời lượng (dài -> ngắn)"], fg_color=T.BG_TERTIARY, text_color=T.TEXT)
        self.sort_option.pack(fill="x", padx=T.PAD_MD, pady=(0, T.PAD_MD))

        ctk.CTkLabel(self.sidebar, text="❤️ Lượt like tối thiểu:", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD)
        self.min_likes_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Ví dụ: 5000", fg_color=T.BG_TERTIARY, text_color=T.TEXT)
        self.min_likes_entry.pack(fill="x", padx=T.PAD_MD, pady=(0, T.PAD_SM))

        btn_grid = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_grid.pack(fill="x", padx=T.PAD_MD)
        for val, num in [("1K", 1000), ("5K", 5000), ("10K", 10000), ("50K", 50000)]:
            ctk.CTkButton(btn_grid, text=val, width=55, height=30, fg_color=T.BG_TERTIARY, text_color=T.TEXT,
                          command=lambda n=num: self._set_min_likes(n)).pack(side="left", padx=2, expand=True)

        ctk.CTkLabel(self.sidebar, text="📅 Khoảng thời gian:", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD, pady=(T.PAD_MD, 0))
        self.time_range = ctk.CTkOptionMenu(self.sidebar, values=["Tất cả", "24h qua", "7 ngày qua", "30 ngày qua"], fg_color=T.BG_TERTIARY, text_color=T.TEXT)
        self.time_range.pack(fill="x", padx=T.PAD_MD)

        ctk.CTkLabel(self.sidebar, text="🕒 Thời lượng (giây):", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD, pady=(T.PAD_MD, 0))
        dur_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        dur_row.pack(fill="x", padx=T.PAD_MD)
        self.min_duration_entry = ctk.CTkEntry(dur_row, placeholder_text="Tối thiểu", width=100, fg_color=T.BG_TERTIARY, text_color=T.TEXT)
        self.min_duration_entry.pack(side="left", expand=True, fill="x", padx=(0, 4))
        ctk.CTkLabel(dur_row, text="~", font=(T.FONT_FAMILY, 14, "bold"), text_color=T.TEXT_SECONDARY).pack(side="left")
        self.max_duration_entry = ctk.CTkEntry(dur_row, placeholder_text="Tối đa", width=100, fg_color=T.BG_TERTIARY, text_color=T.TEXT)
        self.max_duration_entry.pack(side="left", expand=True, fill="x", padx=(4, 0))

        ctk.CTkLabel(self.sidebar, text="📏 Hiển thị thời gian:", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD, pady=(T.PAD_MD, 0))
        self.duration_unit = ctk.CTkSegmentedButton(self.sidebar, values=["Giây (s)", "Phút (m)"], command=lambda _: self._apply_filter())
        self.duration_unit.set("Giây (s)")
        self.duration_unit.pack(fill="x", padx=T.PAD_MD)

        ctk.CTkButton(self.sidebar, text="🔄 Áp dụng bộ lọc", fg_color=T.ACCENT_SECONDARY, height=45, font=(T.FONT_FAMILY, 14, "bold"), command=self._apply_filter).pack(fill="x", padx=T.PAD_MD, pady=T.PAD_LG)

        ctk.CTkLabel(self.sidebar, text="🎯 Chọn nhanh:", font=(T.FONT_FAMILY, 12, "bold"), text_color=T.TEXT).pack(anchor="w", padx=T.PAD_MD)
        sel_grid = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sel_grid.pack(fill="x", padx=T.PAD_MD, pady=T.PAD_SM)
        ctk.CTkButton(sel_grid, text="Top 20", width=65, height=35, command=lambda: self._select_top(20)).pack(side="left", padx=2, expand=True)
        ctk.CTkButton(sel_grid, text="Top 50", width=65, height=35, command=lambda: self._select_top(50)).pack(side="left", padx=2, expand=True)
        ctk.CTkButton(sel_grid, text="Trend", width=65, height=35, command=lambda: self._select_top(10)).pack(side="left", padx=2, expand=True)

        # Video Table (Right)
        self.table_frame = ctk.CTkFrame(self.body, fg_color=T.BG_SECONDARY, corner_radius=T.RADIUS_LG)
        self.table_frame.grid(row=0, column=1, sticky="nsew")

        self._setup_table()

        # 4. Footer - Row 3
        self.footer = ctk.CTkFrame(self, fg_color=T.BG_SECONDARY, height=150)
        self.footer.grid(row=3, column=0, sticky="ew", padx=T.PAD_LG, pady=(T.PAD_MD, T.PAD_LG))
        self.footer.grid_propagate(False)
        self.footer.grid_columnconfigure(0, weight=1) # Log area expands
        self.footer.grid_rowconfigure(0, weight=1)

        # Log box area
        log_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        log_container.grid(row=0, column=0, sticky="nsew", padx=T.PAD_MD, pady=T.PAD_MD)
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)
        
        self.log_box = ctk.CTkTextbox(log_container, fg_color=T.BG_PRIMARY, text_color="#22C55E", font=("Consolas", 11))
        self.log_box.grid(row=0, column=0, sticky="nsew")

        ctk.CTkButton(log_container, text="🗑️ Xóa Nhật ký", width=120, height=25, font=(T.FONT_FAMILY, 11), 
                      fg_color=T.BG_TERTIARY, command=self._clear_logs).place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

        # Controls area
        self.controls_panel = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.controls_panel.grid(row=0, column=1, sticky="nse", padx=T.PAD_MD, pady=T.PAD_MD)

        self.path_var = ctk.StringVar(value=self.settings.get("download_path", DEFAULT_DOWNLOAD_PATH))
        path_row = ctk.CTkFrame(self.controls_panel, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, T.PAD_MD))
        ctk.CTkLabel(path_row, text="💾 Lưu vào:", font=(T.FONT_FAMILY, 12, "bold")).pack(side="left")
        ctk.CTkEntry(path_row, textvariable=self.path_var, width=250, height=30).pack(side="left", padx=T.PAD_SM)
        ctk.CTkButton(path_row, text="📁 Chọn", width=70, height=30, fg_color=T.BG_TERTIARY, command=self._browse_folder).pack(side="left")

        actions_row = ctk.CTkFrame(self.controls_panel, fg_color="transparent")
        actions_row.pack(fill="x")
        ctk.CTkButton(actions_row, text="↓ Tải Top 20", width=110, height=40, font=(T.FONT_FAMILY, 12, "bold"), fg_color=T.ACCENT_GREEN, command=lambda: self._on_download_top(20)).pack(side="left", padx=2)
        ctk.CTkButton(actions_row, text="↓ Tải Top 50", width=110, height=40, font=(T.FONT_FAMILY, 12, "bold"), fg_color=T.ACCENT, command=lambda: self._on_download_top(50)).pack(side="left", padx=2)
        ctk.CTkButton(actions_row, text="↓ Tải đã chọn", width=110, height=40, font=(T.FONT_FAMILY, 12, "bold"), fg_color=T.ACCENT_SECONDARY, command=self._on_download_selected).pack(side="left", padx=2)
        ctk.CTkButton(actions_row, text="↻ Tải lại lỗi", width=110, height=40, font=(T.FONT_FAMILY, 12, "bold"), fg_color="#EF4444", command=self._retry_failed_downloads).pack(side="left", padx=2)

    def _retry_failed_downloads(self):
        if not hasattr(self, 'failed_downloads') or not self.failed_downloads:
            messagebox.showinfo("Thông báo", "Không có video nào bị lỗi hoặc cần tải lại.")
            return
            
        # Create channel-specific folder again just to be safe
        base_path = self.path_var.get()
        clean_channel_name = "".join([c for c in self.current_channel.title if c.isalnum() or c in " _-"]).strip()
        if not clean_channel_name: clean_channel_name = "Douyin_Channel"
        
        # Thêm channel_id vào tên folder
        if hasattr(self.current_channel, 'channel_id') and self.current_channel.channel_id:
            clean_channel_name = f"{clean_channel_name}_{self.current_channel.channel_id}"
            
        download_path = os.path.join(base_path, clean_channel_name)
        
        retry_tasks = list(self.failed_downloads)
        self.failed_downloads.clear()
        
        threading.Thread(target=self._run_batch_download, args=(retry_tasks, download_path, True), daemon=True).start()
    def _set_min_likes(self, value):
        self.min_likes_entry.delete(0, "end")
        self.min_likes_entry.insert(0, str(value))
        self.log(f"Đã đặt mức like tối thiểu là {value:,}")

    def _setup_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", background=T.BG_SECONDARY, foreground=T.TEXT, fieldbackground=T.BG_SECONDARY, rowheight=35, font=(T.FONT_FAMILY, 11))
        style.configure("Custom.Treeview.Heading", background=T.BG_TERTIARY, foreground=T.TEXT, relief="flat", font=(T.FONT_FAMILY, 11, "bold"))
        style.map("Custom.Treeview", background=[('selected', T.ACCENT)])

        columns = ("index", "select", "id", "views", "likes", "ratio", "date", "duration")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Custom.Treeview")
        
        self.tree.heading("index", text="STT")
        self.tree.heading("select", text="☐")
        self.tree.heading("id", text="Video ID")
        self.tree.heading("views", text="👁 Views")
        self.tree.heading("likes", text="❤ Likes")
        self.tree.heading("ratio", text="📊 Like%")
        self.tree.heading("date", text="📅 Ngày đăng")
        self.tree.heading("duration", text="⏳ TG")

        # Set column proportions - Balanced for full screen
        self.tree.column("index", width=50, anchor="center", stretch=False)
        self.tree.column("select", width=50, anchor="center", stretch=False)
        self.tree.column("id", width=220, anchor="w", stretch=True)    # Left align ID for readability
        self.tree.column("views", width=120, anchor="center", stretch=True)
        self.tree.column("likes", width=120, anchor="center", stretch=True)
        self.tree.column("ratio", width=100, anchor="center", stretch=True)
        self.tree.column("date", width=150, anchor="center", stretch=True)
        self.tree.column("duration", width=90, anchor="center", stretch=True)

        # Container for Treeview + Scrollbars
        self.tree.pack(side="left", fill="both", expand=True, padx=(T.PAD_MD, 0), pady=T.PAD_MD)
        
        scrollbar = ctk.CTkScrollbar(self.table_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, T.PAD_MD), pady=T.PAD_MD)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Events
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.heading("select", command=self._toggle_select_all)

    def log(self, message):
        def _log():
            self.log_box.insert("end", f"> {message}\n")
            self.log_box.see("end")
        self.after(0, _log)

    def _clear_logs(self):
        self.log_box.delete("1.0", "end")

    async def _update_login_status(self):
        """Check if logged in and update button UI."""
        is_logged_in = self.scraper.check_login_status()
        if is_logged_in:
            self.login_btn.configure(text="✅ Đã đăng nhập", fg_color=T.ACCENT_GREEN)
        else:
            self.login_btn.configure(text="🔑 Đăng nhập", fg_color=T.BG_TERTIARY)

    def _set_min_views(self, value):
        self.min_views_entry.delete(0, "end")
        self.min_views_entry.insert(0, str(value))
        self.log(f"Đã chọn lượt xem tối thiểu: {value:,}")

    def _browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.settings["download_path"] = path
            self._save_settings()

    def _on_analyze(self):
        url = self.url_var.get().strip()
        if not url: return
        
        self.analyze_btn.configure(state="disabled", text="⏳ Đang phân tích...", text_color="#FFFFFF")
        asyncio.run_coroutine_threadsafe(self._async_analyze(url), self._async_loop)

    async def _async_analyze(self, url):
        channel = await self.scraper.analyze_channel(url, self.log)
        
        def _update_ui():
            self.analyze_btn.configure(state="normal", text="🔍 Phân tích kênh")
            if channel:
                self.current_channel = channel
                self._populate_table(channel.videos)
                
                # Update Stats
                stats = [
                    str(channel.total_videos),
                    f"{channel.avg_views:,}",
                    f"{channel.avg_likes:,}",
                    "Trending", 
                    f"{channel.top_views:,}"
                ]
                for i, card in enumerate(self.stat_cards):
                    label_val = card.winfo_children()[1]
                    label_val.configure(text=stats[i])
                
                self.log(f"Đã cập nhật bảng với {len(channel.videos)} video.")
            else:
                messagebox.showerror("Lỗi", "Không thể phân tích kênh. Vui lòng kiểm tra Nhật ký để biết chi tiết lỗi.")

        self.after(0, _update_ui)

    def _populate_table(self, videos):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        import datetime
        use_minutes = "Phút" in self.duration_unit.get()
        
        for v in videos:
            date_str = datetime.datetime.fromtimestamp(v.create_time).strftime('%Y-%m-%d')
            
            if use_minutes:
                minutes = v.duration // 60
                seconds = v.duration % 60
                duration_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            else:
                duration_str = f"{v.duration}s"
                
            self.tree.insert("", "end", values=(
                v.original_index,
                "☐",

                v.id,
                f"{v.views:,}",
                f"{v.likes:,}",
                f"{v.like_ratio:.1f}%",
                date_str,
                duration_str
            ), tags=(v.id,))


    def _select_top(self, count):
        if not self.current_channel: return
        sorted_videos = sorted(self.current_channel.videos, key=lambda x: x.likes, reverse=True)
        top_ids = [v.id for v in sorted_videos[:count]]
        
        for item_id in self.tree.get_children():
            v_id = self.tree.item(item_id, "tags")[0]
            values = list(self.tree.item(item_id, "values"))
            if v_id in top_ids:
                values[1] = "☑" # Column index changed
            else:
                values[1] = "☐"
            self.tree.item(item_id, values=values)
        self.log(f"Đã tự động chọn {len(top_ids)} video có lượt like cao nhất.")

    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2": # Select column shifted to #2
                item_id = self.tree.identify_row(event.y)
                values = list(self.tree.item(item_id, "values"))
                values[1] = "☑" if values[1] == "☐" else "☐"
                self.tree.item(item_id, values=values)

    def _toggle_select_all(self):
        self.all_selected = not self.all_selected
        new_mark = "☑" if self.all_selected else "☐"
        self.tree.heading("select", text=new_mark)
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            values[1] = new_mark # Updated index
            self.tree.item(item_id, values=values)

    def _apply_filter(self):
        if not self.current_channel: return
        
        min_likes = 0
        min_likes_str = self.min_likes_entry.get().strip()
        if min_likes_str:
            try:
                min_likes = int(min_likes_str.replace(",", "").replace(".", ""))
            except:
                pass
        
        min_duration = 0
        min_duration_str = self.min_duration_entry.get().strip()
        if min_duration_str:
            try:
                min_duration = int(min_duration_str)
            except:
                pass

        max_duration = 999999
        max_duration_str = self.max_duration_entry.get().strip()
        if max_duration_str:
            try:
                max_duration = int(max_duration_str)
            except:
                pass

        sort_by = self.sort_option.get()
        time_limit = self.time_range.get()
        import time
        now = time.time()
        
        def filter_func(v):
            if v.likes < min_likes: return False
            if v.duration < min_duration: return False
            if v.duration > max_duration: return False
            if time_limit == "24h qua" and (now - v.create_time) > 86400: return False
            if time_limit == "7 ngày qua" and (now - v.create_time) > 604800: return False
            if time_limit == "30 ngày qua" and (now - v.create_time) > 2592000: return False
            return True

        filtered = [v for v in self.current_channel.videos if filter_func(v)]
        
        if "Likes" in sort_by:
            filtered.sort(key=lambda x: x.likes, reverse=True)
        elif "Mới nhất" in sort_by:
            filtered.sort(key=lambda x: x.create_time, reverse=True)
        elif "Cũ nhất" in sort_by:
            filtered.sort(key=lambda x: x.create_time)
        elif "Thời lượng" in sort_by:
            filtered.sort(key=lambda x: x.duration, reverse=True)
            
        self._populate_table(filtered)
        self.log(f"Đã áp dụng bộ lọc: còn {len(filtered)}/{len(self.current_channel.videos)} video.")

    def _on_login(self):
        self.log("Đang mở trình duyệt để đăng nhập...")
        
        async def run_login():
            await self.scraper.open_login_browser(self.log)
            self.after(0, lambda: asyncio.run_coroutine_threadsafe(self._update_login_status(), self._async_loop))
            
        asyncio.run_coroutine_threadsafe(run_login(), self._async_loop)

    def _on_download_top(self, count):
        self._select_top(count)
        self._on_download_selected()

    def _on_download_selected(self):
        selected_tasks = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            if values[1] == "☑": # Updated index
                tags = self.tree.item(item_id, "tags")
                if tags:
                    v_id = tags[0]
                    stt = values[0]
                    filename = f"{stt}_{v_id}.mp4"
                    selected_tasks.append((v_id, filename))
        
        if not selected_tasks:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 video để tải.")
            return

        if not self.current_channel:
            messagebox.showwarning("Cảnh báo", "Vui lòng phân tích kênh trước khi tải.")
            return

        # Create channel-specific folder
        base_path = self.path_var.get()
        clean_channel_name = "".join([c for c in self.current_channel.title if c.isalnum() or c in " _-"]).strip()
        if not clean_channel_name: clean_channel_name = "Douyin_Channel"
        
        # Thêm channel_id vào tên folder
        if hasattr(self.current_channel, 'channel_id') and self.current_channel.channel_id:
            clean_channel_name = f"{clean_channel_name}_{self.current_channel.channel_id}"
            
        download_path = os.path.join(base_path, clean_channel_name)
        os.makedirs(download_path, exist_ok=True)

        self.failed_downloads.clear() # Reset explicit user download

        threading.Thread(target=self._run_batch_download, args=(selected_tasks, download_path), daemon=True).start()

    def _run_batch_download(self, tasks, download_path, is_retry=False):
        status_msg = "Tải lại" if is_retry else "chuỗi tải"
        self.log(f"🚀 Bắt đầu {status_msg} {len(tasks)} video vào thư mục: {os.path.basename(download_path)}...")
        import random
        
        for i, (vid, filename) in enumerate(tasks):
            url = f"https://www.douyin.com/video/{vid}"
            target_path = os.path.join(download_path, filename)
            
            if os.path.exists(target_path):
                self.log(f"⏭️ [Bỏ qua] File đã tồn tại: {filename}")
                continue
            
            success = False
            for attempt in range(2):
                self.log(f"[{i+1}/{len(tasks)}] Đang tải: {filename}")
                future = asyncio.run_coroutine_threadsafe(
                    self.scraper.download_video(url, download_path, filename=filename, v_id=vid, logger_callback=self.log), 
                    self._async_loop
                )
                try:
                    future.result(timeout=180)
                    if os.path.exists(target_path):
                        if os.path.getsize(target_path) > 102400:
                            success = True
                            break
                        else:
                            self.log(f"⚠️ Cảnh báo: File tải về quá nhỏ ({os.path.getsize(target_path)} bytes), thử lại...")
                            os.remove(target_path)
                except Exception as e:
                    self.log(f"⚠️ Lỗi lần {attempt+1}: {e}")
                    if attempt < 1: import time; time.sleep(2)
            
            if success:
                if i < len(tasks) - 1:
                    delay = random.uniform(2, 5)
                    self.log(f"⏳ Đợi {delay:.1f}s né Bot...")
                    import time; time.sleep(delay)
            else:
                self.log(f"❌ Thất bại hoàn toàn video: {vid}")
                self.failed_downloads.append((vid, filename))

        self.log("✅ Hoàn thành lượt tải hàng loạt!")
        if self.failed_downloads:
            self.log(f"⚠️ Có {len(self.failed_downloads)} video lỗi! Hãy bấm nút '↻ Tải lại lỗi' để thử tải lại các video này.")

        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except: pass
        
        self.after(0, lambda: messagebox.showinfo("Thành công", f"Đã xử lý xong {len(tasks)} video!"))

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
