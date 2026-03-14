async function getIdPage(sec_user_id, max_cursor) {
const url = `https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=${sec_user_id}&max_cursor=${max_cursor}`;
try {
    const res = await fetch(url, { method: "GET", credentials: "include" });
    return await res.json();
} catch (e) {
    await new Promise(r => setTimeout(r, 800));
    return getIdPage(sec_user_id, max_cursor);
}
}

function safeText(text) {
if (!text) return "";
return text.replace(/\r?\n|\r/g, " ").replace(/\s+/g, " ").trim();
}

async function scrapeSorted(){
const sec_user_id = location.pathname.replace("/user/", "");
if(!sec_user_id){ return {error: "No sec_user_id"}; }

let max_cursor = 0, hasMore = 1;
let globalIndex = 1;
let videoInfoExport = [];

while(hasMore == 1) {
    const page = await getIdPage(sec_user_id, max_cursor);
    if(!page || !page.aweme_list || page.aweme_list.length === 0) break;

    hasMore = page.has_more;
    max_cursor = page.max_cursor;

    for(let i = 0; i < page.aweme_list.length; i++){
        const item = page.aweme_list[i];
        const stats = item.statistics || {};
        videoInfoExport.push({
            position: globalIndex,
            aweme_id: item.aweme_id,
            desc: safeText(item.desc),
            digg_count: stats.digg_count || 0,
            share_count: stats.share_count || 0,
            play_count: stats.play_count || 0,
            create_time: item.create_time,
            duration: Math.floor((item.video?.duration || 0) / 1000)
        });
        globalIndex++;
    }
    await new Promise(r => setTimeout(r, 500));
}
videoInfoExport.sort((a, b) => b.digg_count - a.digg_count);
return videoInfoExport;
};
return await scrapeSorted();
