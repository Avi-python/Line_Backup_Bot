from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, VideoMessage, ImageMessage
from dotenv import load_dotenv
import os
import uuid
import logging

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
SAVING_DIR = os.getenv('SAVING_DIR')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 確保儲存目錄存在並可寫入
if not os.path.exists(SAVING_DIR):
    try:
        os.makedirs(SAVING_DIR)
    except Exception as e:
        print(f"Error creating storage directory: {e}")
        exit(1)

if not os.access(SAVING_DIR, os.W_OK):
    print(f"Storage directory {SAVING_DIR} is not writable")
    exit(1)

@app.route("/callback", methods=["POST"])
def callback():
    logger.debug("Received callback request")
    logger.info(f"Headers: {dict(request.headers)}")

    x_line_signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, x_line_signature)
    except InvalidSignatureError as e:
        logger.error(f"Signature validation failed: {str(e)}")
        abort(400, description=str(e))

    return "OK"


# Save Image
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    image_data = message_content.content
    user_id = event.source.user_id
    # group_id = event.source.group_id

    file_name = str(uuid.uuid4()) + ".jpg"
    file_path = os.path.join(SAVING_DIR, file_name)
    with open(file_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)


# Save Video
@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    image_data = message_content.content
    user_id = event.source.user_id
    # group_id = event.source.group_id

    file_name = str(uuid.uuid4()) + ".mp4"
    file_path = os.path.join(SAVING_DIR, file_name)
    with open(file_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)