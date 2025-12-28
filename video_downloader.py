"""
Module tải video từ YouTube, TikTok, Facebook sử dụng yt-dlp
"""
import os
import re
from pathlib import Path
import yt_dlp
from config import DOWNLOAD_DIR, VIDEO_QUALITY, MAX_FILE_SIZE_MB


class VideoDownloader:
    def __init__(self):
        self.download_dir = DOWNLOAD_DIR
        
    def is_supported_url(self, url):
        """Kiểm tra xem URL có được hỗ trợ không"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'(?:https?://)?(?:vm\.)?tiktok\.com/[\w-]+',
            r'(?:https?://)?(?:www\.)?facebook\.com/.*?/videos/\d+',
            r'(?:https?://)?(?:www\.)?fb\.watch/[\w-]+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def download_video(self, url, user_id=None):
        """
        Tải video từ URL
        
        Args:
            url: URL của video
            user_id: ID người dùng (để tạo tên file unique)
        
        Returns:
            dict: {
                'success': bool,
                'file_path': str,
                'file_size_mb': float,
                'title': str,
                'error': str (nếu có lỗi)
            }
        """
        try:
            # Tạo tên file output
            output_template = os.path.join(
                self.download_dir,
                f'{user_id or "video"}_%(id)s.%(ext)s'
            )
            
            # Cấu hình yt-dlp
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Ưu tiên MP4, chất lượng cao nhất
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                # Giới hạn kích thước file nếu cần
                'max_filesize': MAX_FILE_SIZE_MB * 1024 * 1024 * 2,  # x2 để download trước, kiểm tra sau
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Lấy đường dẫn file đã tải
                video_id = info.get('id', 'video')
                ext = info.get('ext', 'mp4')
                file_path = os.path.join(
                    self.download_dir,
                    f'{user_id or "video"}_{video_id}.{ext}'
                )
                
                # Kiểm tra file có tồn tại không
                if not os.path.exists(file_path):
                    return {
                        'success': False,
                        'error': 'File không được tạo sau khi tải xuống'
                    }
                
                # Kiểm tra kích thước file
                file_size_bytes = os.path.getsize(file_path)
                file_size_mb = file_size_bytes / (1024 * 1024)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'file_size_mb': round(file_size_mb, 2),
                    'title': info.get('title', 'Video'),
                    'url': info.get('webpage_url', url),
                    'thumbnail': info.get('thumbnail', ''),
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_file(self, file_path):
        """Xóa file sau khi đã gửi"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Lỗi khi xóa file {file_path}: {e}")
        return False
    
    def cleanup_old_files(self, max_age_hours=24):
        """Xóa các file cũ hơn max_age_hours"""
        import time
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for file_path in Path(self.download_dir).glob('*'):
                if file_path.is_file():
                    file_age = now - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        print(f"Đã xóa file cũ: {file_path}")
        except Exception as e:
            print(f"Lỗi khi dọn dẹp file: {e}")


def extract_url_from_text(text):
    """Trích xuất URL từ text"""
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    return urls[0] if urls else None
