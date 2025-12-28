"""
Bot Facebook Messenger - Tải Video từ YouTube, TikTok, Facebook
"""
from flask import Flask, request, jsonify
import threading
import os
from config import VERIFY_TOKEN, MESSAGES, MAX_FILE_SIZE_MB
from messenger_api import MessengerAPI
from video_downloader import VideoDownloader, extract_url_from_text

app = Flask(__name__)
messenger = MessengerAPI()
downloader = VideoDownloader()


def process_video_download(sender_id, url):
    """
    Xử lý tải và gửi video (chạy trong thread riêng)
    """
    try:
        # Gửi thông báo đang tải
        messenger.send_text_message(sender_id, MESSAGES['downloading'])
        messenger.send_typing_on(sender_id)
        
        # Tải video
        result = downloader.download_video(url, user_id=sender_id)
        
        if not result['success']:
            messenger.send_text_message(
                sender_id,
                MESSAGES['error_download']
            )
            return
        
        # Kiểm tra kích thước file
        file_size_mb = result['file_size_mb']
        file_path = result['file_path']
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            # File quá lớn, gửi link thay vì file
            message = MESSAGES['file_too_large'].format(url=result['url'])
            messenger.send_text_message(sender_id, message)
        else:
            # Gửi video
            messenger.send_text_message(sender_id, MESSAGES['uploading'])
            messenger.send_typing_on(sender_id)
            
            response = messenger.send_video_file(sender_id, file_path)
            
            if response and not response.get('error'):
                messenger.send_text_message(sender_id, MESSAGES['success'])
            else:
                messenger.send_text_message(
                    sender_id,
                    MESSAGES['error_download']
                )
        
        # Xóa file sau khi gửi
        downloader.cleanup_file(file_path)
        
    except Exception as e:
        print(f"Lỗi khi xử lý video: {e}")
        messenger.send_text_message(sender_id, MESSAGES['error_download'])


def handle_message(sender_id, message_text):
    """
    Xử lý tin nhắn từ người dùng
    """
    message_text = message_text.strip()
    
    # Xử lý các lệnh đặc biệt
    if message_text.lower() in ['help', 'hướng dẫn', 'huong dan', 'bắt đầu', 'start']:
        messenger.send_text_message(sender_id, MESSAGES['help'])
        return
    
    # Trích xuất URL từ tin nhắn
    url = extract_url_from_text(message_text)
    
    if not url:
        messenger.send_text_message(sender_id, MESSAGES['error_no_url'])
        return
    
    # Kiểm tra URL có được hỗ trợ không
    if not downloader.is_supported_url(url):
        messenger.send_text_message(sender_id, MESSAGES['error_unsupported'])
        return
    
    # Gửi thông báo đang xử lý
    messenger.send_text_message(sender_id, MESSAGES['processing'])
    
    # Xử lý tải video trong thread riêng để không block webhook
    thread = threading.Thread(
        target=process_video_download,
        args=(sender_id, url)
    )
    thread.start()


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Xác thực webhook với Facebook
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('Webhook đã được xác thực!')
        return challenge
    else:
        print('Xác thực webhook thất bại!')
        return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Nhận messages từ Facebook Messenger
    """
    data = request.get_json()
    
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                sender_id = messaging_event['sender']['id']
                
                # Xử lý tin nhắn text
                if messaging_event.get('message'):
                    message = messaging_event['message']
                    
                    # Bỏ qua nếu là tin nhắn từ bot (echo)
                    if message.get('is_echo'):
                        continue
                    
                    message_text = message.get('text', '')
                    
                    if message_text:
                        handle_message(sender_id, message_text)
                
                # Xử lý postback (quick replies)
                elif messaging_event.get('postback'):
                    payload = messaging_event['postback']['payload']
                    
                    if payload == 'GET_STARTED':
                        messenger.send_text_message(sender_id, MESSAGES['welcome'])
    
    return 'OK', 200


@app.route('/', methods=['GET'])
def home():
    """
    Trang chủ để kiểm tra bot đang chạy
    """
    return '''
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Bot Tải Video Messenger</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: #f0f2f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #1877f2; }
            .status { color: #42b72a; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot Tải Video Messenger</h1>
            <p class="status">✅ Bot đang chạy!</p>
            <h2>Tính năng:</h2>
            <ul>
                <li>📹 Tải video YouTube chất lượng cao</li>
                <li>🎵 Tải video TikTok</li>
                <li>📘 Tải video Facebook</li>
            </ul>
            <h2>Cách sử dụng:</h2>
            <ol>
                <li>Nhắn tin cho bot trên Messenger</li>
                <li>Gửi link video YouTube, TikTok hoặc Facebook</li>
                <li>Đợi bot tải và gửi video cho bạn!</li>
            </ol>
        </div>
    </body>
    </html>
    '''


@app.route('/cleanup', methods=['GET'])
def cleanup():
    """
    Endpoint để dọn dẹp file cũ
    """
    downloader.cleanup_old_files(max_age_hours=1)
    return 'Cleanup completed', 200


if __name__ == '__main__':
    import sys
    import io
    
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print('Bot Messenger dang khoi dong...')
    print('Nho cau hinh PAGE_ACCESS_TOKEN trong file .env')
    print('Webhook URL: http://your-domain.com/webhook')
    
    # Chạy Flask app
    # Render cần đọc PORT từ environment variable
    port = int(os.environ.get('PORT', 10000))
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

