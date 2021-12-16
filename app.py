import os
import boto3
from PIL import Image

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextSendMessage, ImageMessage
)


line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

s3 = boto3.client('s3')
s3_bucket_name = os.environ['S3_BUCKET_NAME']


def resize_image(image_path, resized_path):
    thumbnail_max_size = int(os.environ['thumbnail_max_size'])
    with Image.open(image_path) as image:
        x, y = image.size
        size = min(x, y)

        if x > y:
            crop_area = ((x - size) // 2, 0, (x + size) // 2, y)
        else:
            crop_area = (0, (y - size) // 2, x, (y + size) // 2)

        image = image.crop(crop_area)

        size = min(size, thumbnail_max_size)
        image.thumbnail((size, size))
        image.save(resized_path)


def reply_message(reply_token):
    message = os.environ['reply_message']
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=message),
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    original_local_path = f'/tmp/{message_id}.jpg'
    thumbnail_local_path = f'/tmp/thumbnail-{message_id}.jpg'

    with open(original_local_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)

    resize_image(original_local_path, thumbnail_local_path)
    upload_key = original_local_path.split('/')[-1]

    original_s3_path = f'original/{upload_key}'
    thumbnail_s3_path = f'thumbnail/{upload_key}'

    s3.upload_file(original_local_path, s3_bucket_name,
                   original_s3_path, ExtraArgs={"ContentType": 'image/jpeg'})

    s3.upload_file(thumbnail_local_path, s3_bucket_name, thumbnail_s3_path,
                   ExtraArgs={'ContentType': 'image/jpeg'})

    try:
        if event.message.image_set.index == 1:
            reply_message(event.reply_token)
        else:
            pass
    except:
        reply_message(event.reply_token)


def lambda_handler(event, context):
    signature = event['headers']['x-line-signature']
    body = event['body']

    handler.handle(body, signature)

    return {
        'statusCode': 200,
    }
