import os
import time
import pyimgur
from flask import Flask, request, abort
from main import app, db
from main.model import User, Task, Exhibit
from main.config import Config

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, FollowEvent, UnfollowEvent, PostbackEvent,
    TemplateSendMessage, CarouselTemplate, CarouselColumn, URIAction, MessageAction, PostbackAction
)

client = LineBotApi(Config.LINEAPI)
handler = WebhookHandler(Config.WEBHOOK)
CLIENT_ID = Config.CLIENTID
im = pyimgur.Imgur(CLIENT_ID)
style_urls = [
    'https://i.imgur.com/kKCHsgB.jpg', 'https://i.imgur.com/yrGLIhl.jpg', 'https://i.imgur.com/X0ChrwE.jpg',
    'https://i.imgur.com/JifhiJn.jpg', 'https://i.imgur.com/eoVXRqk.jpg', 'https://i.imgur.com/4xBLEo5.jpg'
]
style_names = [
    'la_muse', 'rain_princess', 'scream', 'udnie', 'wave', 'wreck'
]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(PostbackEvent)
def handle_message(event):
    line_user_profile = client.get_profile(event.source.user_id)
    line_id = line_user_profile.user_id
    user = User.query.filter_by(line_id=line_id).first()
    style_id = int(event.postback.data[-1])
    user.draw_state = f"wait_{style_id}"
    db.session.add(user)
    db.session.commit()
    client.reply_message(
        event.reply_token,
        TextSendMessage(text="給我一張圖片吧我現在沒有靈感")
    )

@handler.add(FollowEvent)
def handle_follow(event):
    line_user_profile = client.get_profile(event.source.user_id)
    line_id = line_user_profile.user_id
    user_query = User.query.filter_by(line_id=line_id).first()
    if not user_query:
        # not unfollow before
        name = line_user_profile.display_name
        user = User(
            line_id=line_id, art_count=0, name=name, block=False,
            use_buffer=False, draw_state="idle"
        )
        db.session.add(user)
        db.session.commit()
    else:
        # unfollow before
        user_query.block = False
        db.session.add(user)
        db.session.commit()

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    line_user_profile = client.get_profile(event.source.user_id)
    line_id = line_user_profile.user_id
    user_query = User.query.filter_by(line_id=line_id).first()
    if user_query:
        user_query.block = True
        db.session.add(user_query)
        db.session.commit()

# message handler
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    line_id = client.get_profile(event.source.user_id).user_id
    msg = event.message.text
    reply = reply_template(line_id, msg)
    client.reply_message(
        event.reply_token,
        reply
    )

# image handler
@handler.add(MessageEvent, ImageMessage)
def handle_image(event):
    line_id = client.get_profile(event.source.user_id).user_id
    user = User.query.filter_by(line_id=line_id).first()
    message_content = client.get_message_content(event.message.id)
    if user.draw_state.startswith("wait"):
        with open('main/buffers/draw/'+line_id+'.jpg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        style_id = user.draw_state.split('_')[-1]
        user.draw_state = "draw"
        user.art_count += 1
        if not user.art1:
            art_id = 1
            user.art1 = "draw"
        elif not user.art2:
            art_id = 2
            user.art2 = "draw"
        elif not user.art3:
            art_id = 3
            user.art3 = "draw"
        elif not user.art4:
            art_id = 4
            user.art4 = "draw"
        else:
            art_id = 5
            user.art5 = "draw"
        task = Task(
            line_id=user.line_id, style_id=style_id, art_id=art_id,
            content_url='main/buffers/draw/'+line_id+'.jpg'
        )
        db.session.add(task)
        db.session.add(user)
        db.session.commit()
        client.reply_message(
            event.reply_token,
            TextSendMessage(text="努力創作中.....")
        )
    else:
        with open('main/buffers/temp/'+line_id+'.jpg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        user.use_buffer = True
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        db.session.add(user)
        db.session.commit()
        client.reply_message(
            event.reply_token,
            TextSendMessage(text="已暫存此圖片")
        )

def reply_template(line_id, msg):
    if msg == '我的畫廊':
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        if user.art_count == 0:
            db.session.add(user)
            db.session.commit()
            return TextSendMessage(text="目前沒有保存任何藝術品喔")
        else:
            # go through all pick out not null
            art_columns = []
            if user.art1 and user.art1 != "draw":
                art_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=user.art1,
                        text="嘔心瀝血之作",
                        title="編號1",
                        actions=[
                            MessageAction(
                                label='刪除',
                                text='刪除藝術品1'
                            )
                        ],
                    )
                )
            if user.art2 and user.art2 != "draw":
                art_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=user.art2,
                        text="嘔心瀝血之作",
                        title="編號2",
                        actions=[
                            MessageAction(
                                label='刪除',
                                text='刪除藝術品2'
                            )
                        ],
                    )
                )
            if user.art3 and user.art3 != "draw":
                art_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=user.art3,
                        text="嘔心瀝血之作",
                        title="編號3",
                        actions=[
                            MessageAction(
                                label='刪除',
                                text='刪除藝術品3'
                            )
                        ],
                    )
                )
            if user.art4 and user.art4 != "draw":
                art_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=user.art4,
                        text="嘔心瀝血之作",
                        title="編號4",
                        actions=[
                            MessageAction(
                                label='刪除',
                                text='刪除藝術品4'
                            )
                        ],
                    )
                )
            if user.art5 and user.art5 != "draw":
                art_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=user.art5,
                        text="嘔心瀝血之作",
                        title="編號5",
                        actions=[
                            MessageAction(
                                label='刪除',
                                text='刪除藝術品5'
                            )
                        ],
                    )
                )
        db.session.add(user)
        db.session.commit()
        return  TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=art_columns
                    )
                )

    elif msg.startswith('刪除藝術品') and len(msg) == 6:
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        if '1' <= msg[5] <= '5':
            art_id = int(msg[5])
            if art_id == 1:
                if user.art1: # exists
                    if user.art1 != "draw":
                        user.art1 = None
                        user.art_count -= 1
                        db.session.add(user)
                        db.session.commit()
                        return TextSendMessage(text="成功刪除")
                    else:
                        return TextSendMessage(text="這個藝術品還在繪製中...不能刪除")
                else:
                    return TextSendMessage(text="藝術品標號不存在")
            elif art_id == 2:
                if user.art2: # exists
                    if user.art2 != "draw":
                        user.art2 = None
                        user.art_count -= 1
                        db.session.add(user)
                        db.session.commit()
                        return TextSendMessage(text="成功刪除")
                    else:
                        return TextSendMessage(text="這個藝術品還在繪製中...不能刪除")
                else:
                    return TextSendMessage(text="藝術品標號不存在")
            elif art_id == 3:
                if user.art3: # exists
                    if user.art3 != "draw":
                        user.art3 = None
                        user.art_count -= 1
                        db.session.add(user)
                        db.session.commit()
                        return TextSendMessage(text="成功刪除")
                    else:
                        return TextSendMessage(text="這個藝術品還在繪製中...不能刪除")
                    return TextSendMessage(text="成功刪除")
                else:
                    return TextSendMessage(text="藝術品標號不存在")
            elif art_id == 4:
                if user.art4: # exists
                    if user.art4 != "draw":
                        user.art4 = None
                        user.art_count -= 1
                        db.session.add(user)
                        db.session.commit()
                        return TextSendMessage(text="成功刪除")
                    else:
                        return TextSendMessage(text="這個藝術品還在繪製中...不能刪除")
                    return TextSendMessage(text="成功刪除")
                else:
                    return TextSendMessage(text="藝術品標號不存在")
            else:
                if user.art5: # exists
                    if user.art5 != "draw":
                        user.art5 = None
                        user.art_count -= 1
                        db.session.add(user)
                        db.session.commit()
                        return TextSendMessage(text="成功刪除")
                    else:
                        return TextSendMessage(text="這個藝術品還在繪製中...不能刪除")
                else:
                    return TextSendMessage(text="藝術品標號不存在")
        else:
            db.session.add(user)
            db.session.commit()
            return TextSendMessage(text="錯誤數字範圍")
    elif msg == '清空畫廊':
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        if user:
            user.art1 = None if user.art1 != "draw" else "draw"
            user.art2 = None if user.art2 != "draw" else "draw"
            user.art3 = None if user.art4 != "draw" else "draw"
            user.art4 = None if user.art4 != "draw" else "draw"
            user.art5 = None if user.art5 != "draw" else "draw"
            if user.draw_state == "draw":
                user.art_count = 1
                db.session.add(user)
                db.session.commit()
                return TextSendMessage(text="畫廊還剩一個在繪製的畫作")
            else:
                user.art_count = 0
                db.session.add(user)
                db.session.commit()
                return TextSendMessage(text="畫廊目前沒有藝術品")

    elif msg == '放入畫廊':
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        if not user.use_buffer:
            db.session.add(user)
            db.session.commit()
            return TextSendMessage(text="目前沒有暫存任何藝術品")
        else:
            if user.art_count == 5:
                # full
                db.session.add(user)
                db.session.commit()
                return TextSendMessage(text="畫廊已滿！請先做清理")
            src = 'main/buffers/temp/' + line_id + '.jpg'
            uploaded_image = im.upload_image(src, title=str(int(time.time())))
            dest = uploaded_image.link
            user.use_buffer = False
            user.art_count += 1
            if not user.art1:
                user.art1 = dest
            elif not user.art_count:
                user.art2 = dest
            elif not user.art_count:
                user.art3 = dest
            elif not user.art_count:
                user.art4 = dest
            elif not user.art_count:
                user.art5 = dest
            db.session.add(user)
            db.session.commit()
            return TextSendMessage(text="成功保存藝術品")

    elif msg == '創建藝術品':
        user = User.query.filter_by(line_id=line_id).first()
        art_columns = []
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        db.session.add(user)
        db.session.commit()
        if user.draw_state == "draw":
            return TextSendMessage(text="還有作品在繪製..too busy...")
        else:
            if user.art_count <= 4: # can create
                for i, url in enumerate(style_urls):
                    name = "風格"+str(i+1)
                    art_columns.append(
                        CarouselColumn(
                            thumbnail_image_url=url,
                            title=name,
                            text=style_names[i],
                            actions=[
                                PostbackAction(
                                    label='就是你了',
                                    display_text=f'我選風格{i+1}',
                                    data=f'style={i}'
                                )
                            ],
                        )
                    )
                return  TemplateSendMessage(
                            alt_text='Carousel template',
                            template=CarouselTemplate(
                                columns=art_columns
                            )
                        )
            else: # can't create
                return TextSendMessage(text="至少保留一個空間給畫作")

    elif msg == '近期藝術活動':
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        db.session.add(user)
        db.session.commit()
        exhibit_items = Exhibit.query.order_by(Exhibit.end_time).all()
        exhibit_columns = []
        for i, exhibit_item in enumerate(exhibit_items):
            if i >= 10:
                break
            name = exhibit_item.name if len(exhibit_item.name) <= 15 else exhibit_item.name[:12]+"..."
            exhibit_columns.append(
                CarouselColumn(
                    thumbnail_image_url=exhibit_item.img_url,
                    title=name,
                    text=exhibit_item.start_time+ " ~ " +exhibit_item.end_time,
                    actions=[
                        URIAction(
                            label='詳細資訊',
                            uri=exhibit_item.detail_url
                        )
                    ],
                )
            )
        return  TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=exhibit_columns
                    )
                )
    else:
        user = User.query.filter_by(line_id=line_id).first()
        user.draw_state = "idle" if user.draw_state != "draw" else "draw"
        db.session.add(user)
        db.session.commit()
        return TextSendMessage(text="跟藝術無關的工作我可不會喔")
