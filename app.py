from flask import Flask, request, abort
import json
import time

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
from src.control import Control
from src.remind_thread import myThread


app = Flask(__name__)
control = Control()


# Channel Access Token
line_bot_api = LineBotApi('ev6iAarug1Sr8ZBPCuy+4cRfW6qcZE3965WfrQqjD+T+ahJ2boVCjRx0uVSIrlH5173IE0n4iKoC4XxSYqmCN0odTmg59LecALNAl8DW0g9EQNgcpNADgL38VGMN/DYD9v8nGNxBrWeNHiTXLcZ+4AdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('c969e7d926d6e299ab6296bb1fe60f3a')


def checkKey(message):
    keywordList = ['Language', 'profile', 'project', 'team work', 'Lab']
    for i in keywordList:
        if i == message:
            return True
    return False

def get_push():
    thread_push = myThread("thread_push", "push",linebotapi=line_bot_api, textsendmessage=TextSendMessage)
    thread_push.start()

def background():
    thread_no_idle = myThread("thread_no_idle", "no_idle")
    thread_no_idle.start()

def minus_count_remind():
    thread_minus_count_remind = myThread("thread_minus_count_remind", "minus_count_remind")
    control.minus_count_remind(thread_minus_count_remind.start())

get_push()
background()
minus_count_remind()


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("*****Input details in body*****")
    print(body)
    if (checkKey(json.loads(body)['events'][0]['message']['text'])):
        return 'OK'
    app.logger.info("Request body: " + body)
    user_id = json.loads(body)['events'][0]['source']['userId']
    user_text = json.loads(body)['events'][0]['message']['text']
    control.to_db(user_id, user_text)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    response = control.response()
    message = TextSendMessage(text=response)

    print(event.__class__)
    line_bot_api.reply_message(event.reply_token, message)
    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
