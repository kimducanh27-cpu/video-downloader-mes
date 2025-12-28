"""
Module xử lý API của Facebook Messenger
"""
import requests
from config import PAGE_ACCESS_TOKEN, MESSENGER_API_URL


class MessengerAPI:
    def __init__(self):
        self.access_token = PAGE_ACCESS_TOKEN
        self.api_url = MESSENGER_API_URL
        
    def send_text_message(self, recipient_id, text):
        """Gửi tin nhắn text"""
        params = {'access_token': self.access_token}
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': text}
        }
        
        try:
            response = requests.post(
                self.api_url,
                params=params,
                headers=headers,
                json=data
            )
            return response.json()
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn: {e}")
            return None
    
    def send_typing_on(self, recipient_id):
        """Hiển thị typing indicator"""
        params = {'access_token': self.access_token}
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'recipient': {'id': recipient_id},
            'sender_action': 'typing_on'
        }
        
        try:
            requests.post(self.api_url, params=params, headers=headers, json=data)
        except Exception as e:
            print(f"Lỗi khi gửi typing: {e}")
    
    def send_video_file(self, recipient_id, file_path):
        """
        Gửi video file
        
        Args:
            recipient_id: ID người nhận
            file_path: Đường dẫn đến file video
            
        Returns:
            dict: Response từ Facebook API
        """
        params = {'access_token': self.access_token}
        
        # Tạo multipart form data
        files = {
            'filedata': (
                'video.mp4',
                open(file_path, 'rb'),
                'video/mp4'
            )
        }
        
        data = {
            'recipient': f'{{"id":"{recipient_id}"}}',
            'message': '{"attachment":{"type":"video", "payload":{}}}',
        }
        
        try:
            response = requests.post(
                self.api_url,
                params=params,
                data=data,
                files=files
            )
            
            # Đóng file sau khi gửi
            files['filedata'][1].close()
            
            return response.json()
        except Exception as e:
            print(f"Lỗi khi gửi video: {e}")
            # Đảm bảo file được đóng ngay cả khi có lỗi
            try:
                files['filedata'][1].close()
            except:
                pass
            return None
    
    def send_video_url(self, recipient_id, video_url):
        """
        Gửi video qua URL (cho video lớn)
        
        Args:
            recipient_id: ID người nhận
            video_url: URL của video
            
        Returns:
            dict: Response từ Facebook API
        """
        params = {'access_token': self.access_token}
        headers = {'Content-Type': 'application/json'}
        
        data = {
            'recipient': {'id': recipient_id},
            'message': {
                'attachment': {
                    'type': 'video',
                    'payload': {
                        'url': video_url,
                        'is_reusable': False
                    }
                }
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                params=params,
                headers=headers,
                json=data
            )
            return response.json()
        except Exception as e:
            print(f"Lỗi khi gửi video URL: {e}")
            return None
    
    def send_quick_replies(self, recipient_id, text, replies):
        """
        Gửi tin nhắn với quick replies
        
        Args:
            recipient_id: ID người nhận
            text: Nội dung tin nhắn
            replies: List of quick reply titles
        """
        params = {'access_token': self.access_token}
        headers = {'Content-Type': 'application/json'}
        
        quick_replies = [
            {
                'content_type': 'text',
                'title': reply,
                'payload': reply.upper()
            }
            for reply in replies
        ]
        
        data = {
            'recipient': {'id': recipient_id},
            'message': {
                'text': text,
                'quick_replies': quick_replies
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                params=params,
                headers=headers,
                json=data
            )
            return response.json()
        except Exception as e:
            print(f"Lỗi khi gửi quick replies: {e}")
            return None
