import time
import os
import requests
from bs4 import BeautifulSoup
from main.model import Exhibit, User, Task
from main import app, db
from main.view import im, client
from style_transfer.evaluate import ffwd_to_img
from linebot.models import ImageSendMessage

def spider():
    print("spider active!!")
    url = "https://www.tnam.museum/exhibition/current"
    entry = "https://www.tnam.museum/"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    exhibit_items = soup.find_all(class_='display-item')
    for exhibit_item in exhibit_items:
        name = exhibit_item.find(class_='subject').text
        # check if it has already been in the database
        if not Exhibit.query.filter_by(name=name).first():
            detail_url = entry + exhibit_item['href']
            exhibit_time = exhibit_item.find_all(class_='date')
            start_time, end_time = exhibit_time[0].text, exhibit_time[1].text
            img_url = entry + exhibit_item.find('img')['src']
            extension = img_url.split('.')[-1]
            #store_url = 'storages/' + name + '.' + extension
            #with open(store_url, 'wb') as f:
                #f.write(requests.get(img_url).content)
            # add into db
            new_exhibit = Exhibit(
                detail_url=detail_url, start_time=start_time, end_time=end_time,
                name=name, img_url=img_url
            )
            db.session.add(new_exhibit)
            db.session.commit()
    print("spider end.")

def query_tasks():
    all_tasks = Task.query.all()
    for task in all_tasks:
        user = User.query.filter_by(line_id=task.line_id).first()
        if not user.block:
            # style_transfer
            ffwd_to_img(task.content_url, 'result.jpg', f'static/weights/{task.style_id}.ckpt')
            url = im.upload_image('result.jpg', title=str(int(time.time()))).link
            if task.art_id == 1:
                user.art1 = url
            elif task.art_id == 2:
                user.art2 = url
            elif task.art_id == 3:
                user.art3 = url
            elif task.art_id == 4:
                user.art4 = url
            elif task.art_id == 5:
                user.art5 = url
            line_id = task.line_id
            user.draw_state = "idle"
            db.session.add(user)
            db.session.delete(task)
            db.session.commit()
            # linebot inform
            client.push_message(
                line_id,
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
            )
        time.sleep(1)

if __name__ == '__main__':
    app.app_context().push()
    SPIDER_TIME_INTERVAL = 86400 # every day spider
    last_spider_time = 0
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # ignore package cpu warning

    while (True):

        # if need to grab down the new exhibit
        curr_time = int(time.time())
        if (curr_time - last_spider_time >= SPIDER_TIME_INTERVAL):
            # over 1 day
            last_spider_time = curr_time
            spider()

        # query if there is any task
        query_tasks()
        # delay 5 seconds
        time.sleep( 5 )
