from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Platform(Enum):
    DOUYIN = "DOUYIN"
    TIKTOK = "TIKTOK"
    FACEBOOK = "FACEBOOK"
    INSTAGRAM = "INSTAGRAM"
    UNKNOWN = "UNKNOWN"

class URLType(Enum):
    VIDEO = "VIDEO"
    CHANNEL = "CHANNEL"
    UNKNOWN = "UNKNOWN"

@dataclass
class VideoInfo:
    id: str
    original_index: int = 0
    title: str = ""

    translated_title: str = ""
    author: str = "Unknown"
    views: int = 0
    likes: int = 0
    shares: int = 0
    create_time: int = 0
    duration: int = 0
    cover_url: str = ""
    video_url: str = ""
    platform: Platform = Platform.DOUYIN
    
    @property
    def like_ratio(self) -> float:
        if self.views > 0:
            return (self.likes / self.views) * 100
        return 0.0

@dataclass
class ChannelInfo:
    title: str = ""
    channel_id: str = ""
    total_videos: int = 0
    avg_views: int = 0
    avg_likes: int = 0
    trending_score: float = 0.0
    top_views: int = 0
    videos: list[VideoInfo] = field(default_factory=list)

@dataclass
class SavedChannel:
    id: str
    url: str
    title: str
    last_update: str
    known_video_ids: list[str] = field(default_factory=list)
