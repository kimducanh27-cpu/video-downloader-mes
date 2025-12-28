"""
Cấu hình cho Bot Messenger
"""
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Facebook Messenger Configuration
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'my_verify_token_123')

# Video Download Configuration
DOWNLOAD_DIR = 'downloads'
MAX_FILE_SIZE_MB = 25  # Facebook Messenger giới hạn ~25MB
VIDEO_QUALITY = 'best'  # 'best' hoặc 'worst'

# Messenger API URLs
MESSENGER_API_URL = 'https://graph.facebook.com/v18.0/me/messages'

# Supported platforms
SUPPORTED_PLATFORMS = ['youtube', 'youtu.be', 'tiktok', 'facebook', 'fb.watch']

# Messages (tiếng Việt)
MESSAGES = {
    'welcome': '👋 Chào bạn! Gửi link video YouTube, TikTok hoặc Facebook để tôi tải cho bạn nhé!',
    'processing': '⏳ Đang xử lý video của bạn...',
    'downloading': '📥 Đang tải video chất lượng cao nhất...',
    'uploading': '📤 Đang gửi video cho bạn...',
    'success': '✅ Đã tải xong! Đây là video của bạn:',
    'file_too_large': '⚠️ Video này quá lớn (>25MB). Đây là link tải xuống:\n{url}',
    'error_download': '❌ Không thể tải video này. Vui lòng kiểm tra lại link hoặc thử link khác.',
    'error_unsupported': '❌ Link này không được hỗ trợ. Hiện tại tôi chỉ hỗ trợ YouTube, TikTok và Facebook.',
    'error_no_url': '🔗 Vui lòng gửi link video YouTube, TikTok hoặc Facebook.',
    'help': '📌 Hướng dẫn sử dụng:\n\n'
            '1️⃣ Gửi link video từ YouTube, TikTok hoặc Facebook\n'
            '2️⃣ Đợi bot tải video\n'
            '3️⃣ Nhận video chất lượng cao nhất!\n\n'
            '✨ Hỗ trợ: YouTube, TikTok, Facebook'
}

# Tạo thư mục downloads nếu chưa có
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
