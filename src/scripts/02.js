(async () => {
    async function getIdPage(sec_user_id, max_cursor, retries = 0, isFirst = false) {
        const url = `https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=${sec_user_id}&max_cursor=${max_cursor}&count=20`;
        try {
            const res = await fetch(url, {
                method: "GET",
                credentials: "include",
                headers: {
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "vi,en;q=0.9",
                    "referer": location.href,
                    "sec-ch-ua": "\"Google Chrome\";v=\"124\", \"Not;A=Brand\";v=\"99\", \"Chromium\";v=\"124\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin"
                }
            });
            if (!res.ok) {
                const errText = await res.text();
                console.error(`[API Error] Status: ${res.status} | Body: ${errText.substring(0, 200)}`);
                return null;
            }
            const text = await res.text();
            if (isFirst) console.log(`[API RAW] First response (300 chars): ${text.substring(0, 300)}`);
            return JSON.parse(text);
        } catch (e) {
            console.error(`[Fetch Exception] Lỗi mạng hoặc định dạng: ${e.message}`);
            if (retries >= 3) {
                console.error(`[Fetch Error] Vượt quá giới hạn thử lại.`);
                return null;
            }
            await new Promise(r => setTimeout(r, 1500));
            return getIdPage(sec_user_id, max_cursor, retries + 1, isFirst);
        }
    }

    function safeText(text) {
        if (!text) return "";
        return text.replace(/\r?\n|\r/g, " ").replace(/\s+/g, " ").trim();
    }

    async function scrape(){
        // Strategy 1: Find MS4wLjABAAAA... in URL
        let sec_user_id = "";
        const match = location.href.match(/(MS4w[A-Za-z0-9_-]+)/);
        if (match) {
            sec_user_id = match[1];
        } else {
            // Strategy 2: Read from Douyin's internal window.__ROUTER_DATA__
            try {
                const routerData = window.__ROUTER_DATA__;
                // Douyin stores user info in loaderData under a dynamic key
                if (routerData && routerData.loaderData) {
                    for (const key of Object.keys(routerData.loaderData)) {
                        const val = routerData.loaderData[key];
                        const uid = val?.userInfo?.user?.sec_uid || val?.user?.sec_uid || val?.userData?.user?.sec_uid;
                        if (uid && uid.startsWith('MS4w')) {
                            sec_user_id = uid;
                            console.log(`[Fallback] Found sec_user_id from __ROUTER_DATA__: ${uid.substring(0, 20)}...`);
                            break;
                        }
                    }
                }
            } catch(e) {
                console.error('[Fallback] Could not read __ROUTER_DATA__:', e.message);
            }

            // Strategy 3: Pathname last segment
            if (!sec_user_id) {
                sec_user_id = location.pathname.split('/').pop();
            }
        }

        if(!sec_user_id || sec_user_id.length < 20){ 
            return {error: `Không tìm thấy sec_user_id. URL hiện tại: ${location.href}`}; 
        }
        console.log(`[Scrape] sec_user_id: ${sec_user_id.substring(0, 20)}...`);

        let nickname = "Douyin_Videos";
        let channelId = "";
        let max_cursor = 0;
        let globalIndex = 1;
        let videoInfoExport = [];
        let emptyRetries = 0;
        const MAX_EMPTY_RETRIES = 6;
        
        let falseEndRetries = 0;
        const MAX_FALSE_END_RETRIES = 3;
        let seenIds = new Set();
        
        const knownVideoIds = window.__KNOWN_VIDEO_IDS__ || [];
        let consecutiveKnown = 0;
        let isIncrementalUpdate = !!window.__IS_INCREMENTAL__;
        
        // Nếu là update video tăng cường nhưng chưa có lịch sử, coi như xong luôn (trả về 0 video mới)
        if (isIncrementalUpdate && knownVideoIds.length === 0) {
            console.log("[Douyin API] Chế độ Update Video Mới nhưng danh sách cũ rỗng. Dừng ngay.");
            return { videos: [], nickname: nickname, channel_id: channelId };
        }

        console.log(`[Scrape] Mode: ${isIncrementalUpdate ? 'Incremental' : 'Full Scan'}. Known videos: ${knownVideoIds.length}`);

        while (true) {
            const page = await getIdPage(sec_user_id, max_cursor, 0, max_cursor === 0);
            
            if(!page || !page.aweme_list || page.aweme_list.length === 0) {
                emptyRetries++;
                console.log(`[Douyin API] Kết quả rỗng. Đợi 5 giây và thử lại... (${emptyRetries}/${MAX_EMPTY_RETRIES})`);
                if (emptyRetries >= MAX_EMPTY_RETRIES) {
                    break;
                }
                await new Promise(r => setTimeout(r, 5000));
                continue;
            }

            // Lấy được dữ liệu
            emptyRetries = 0;

            if (page.aweme_list[0]?.author) {
                if (page.aweme_list[0].author.nickname) {
                    nickname = page.aweme_list[0].author.nickname;
                }
                if (!channelId) {
                    const author = page.aweme_list[0].author;
                    // ID tuỳ chỉnh của người dùng (nếu có)
                    let uId = author.unique_id || "";
                    if (uId === "0") uId = "";
                    
                    // ID mặc định hệ thống cấp (như 138277198)
                    let sId = author.short_id || "";
                    if (sId === "0") sId = "";
                    
                    // Fallback cuối cùng là sec_uid (mã MS4w) nếu cả hai ID kia đều rỗng
                    let secId = author.sec_uid || "";
                    
                    channelId = uId || sId || secId;
                }
            }

            let newVideosCount = 0;

            for(let i = 0; i < page.aweme_list.length; i++){
                const item = page.aweme_list[i];
                
                // Tránh lỗi video trùng lặp khi kẹt cursor
                if (seenIds.has(item.aweme_id)) continue;
                seenIds.add(item.aweme_id);
                
                if (isIncrementalUpdate) {
                    if (knownVideoIds.includes(item.aweme_id)) {
                        consecutiveKnown++;
                        console.log(`[Douyin API] Gặp video đã biết (${consecutiveKnown}/5): ${item.aweme_id}`);
                        continue; // Bỏ qua video cũ, KHÔNG cho vào videoInfoExport
                    } else {
                        consecutiveKnown = 0; // Reset nếu gặp video mới
                    }
                }
                
                newVideosCount++;

                const stats = item.statistics || {};
                const diggCount = stats.digg_count || 0;
                const shareCount = stats.share_count || 0;

                // Try multiple fields for play count
                let playCount = stats.play_count || stats.view_count || stats.playCount || 
                                 item.play_count || item.view_count || 
                                 item.statistics?.play_count || item.statistics?.view_count || 
                                 stats.play_addr?.play_count || 
                                 item.video?.play_addr?.play_count || 0;
                
                // Fallback cho playCount
                if (playCount === 0) {
                    for (const key in stats) {
                        if (key.includes('count') && !['digg_count', 'share_count', 'comment_count', 'collect_count', 'recommend_count', 'admire_count'].includes(key)) {
                            if (stats[key] > 0) {
                                playCount = stats[key];
                                break;
                            }
                        }
                    }
                }

                videoInfoExport.push({
                    position: globalIndex,
                    aweme_id: item.aweme_id,
                    desc: safeText(item.desc),
                    digg_count: diggCount,
                    share_count: shareCount,
                    play_count: playCount,
                    create_time: item.create_time,
                    nickname: item.author?.nickname || nickname,
                    duration: Math.floor((item.video?.duration || 0) / 1000)
                });
                globalIndex++;
            }
            
            if (isIncrementalUpdate && consecutiveKnown >= 5) {
                console.log(`[Douyin API] Đã gặp 5 video cũ liên tiếp. Dừng Update Viedeo Mới tại đây.`);
                break;
            }

            console.log(`[Douyin API] Lọc được ${newVideosCount} video mới. Tổng: ${videoInfoExport.length}.`);

            // Nếu toàn trả về video trùng lặp hoặc API báo hết
            if (newVideosCount === 0 || page.has_more === 0) {
                falseEndRetries++;
                console.log(`[Douyin API] API báo hết hoặc trùng lặp (lần ${falseEndRetries}/${MAX_FALSE_END_RETRIES}).`);
                if (falseEndRetries >= MAX_FALSE_END_RETRIES) {
                    console.log("[Douyin API] Đã vét cạn dữ liệu. Kết thúc.");
                    break;
                }
            } else {
                falseEndRetries = 0; // Reset nếu tiến triển bình thường
            }

            let oldCursor = max_cursor;
            max_cursor = page.max_cursor;

            // Xử lý max_cursor lỗi từ API (Douyin thỉnh thoảng báo has_more=0 sớm)
            if (max_cursor === oldCursor || page.has_more === 0 || newVideosCount === 0) {
                if (videoInfoExport.length > 0) {
                    let oldestTime = videoInfoExport[videoInfoExport.length - 1].create_time;
                    max_cursor = oldestTime * 1000;
                    console.log(`[Douyin API] Ép max_cursor theo thời gian = ${max_cursor} để vét thêm...`);
                }
            }

            await new Promise(r => setTimeout(r, 1000));
        }

        return { videos: videoInfoExport, nickname: nickname, channel_id: channelId };
    }

    return await scrape();
})();
