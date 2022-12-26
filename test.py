import pyimgur
import os
import time
from main import app, db
"""
CLIENT_ID = "be13c068af5737e"
srcs = os.listdir('./static/styles')
im = pyimgur.Imgur(CLIENT_ID)
for src in srcs:
    a = im.upload_image('./static/styles/'+src, title=str(int(time.time())))
    print(a.link)
    """
app.app_context().push()
db.drop_all()
db.create_all()
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#ffwd_to_img('main/buffers/U9f9dcd9b48fdc5090357712b873cf6cc.jpg', 'result.jpg', 'static/weights/wave.ckpt')
