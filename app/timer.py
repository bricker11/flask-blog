# -*— coding:utf-8 -*—
from .models import Post, Note
from config import Config
from datetime import datetime
import requests
#定义任务执行程序
def post_baidu_urls():
    # 提交收录链接
    url = 'http://data.zz.baidu.com/urls?site=https://www.tryblog.top&token=GNsd5RAc8GUDZsiT'
    cposts = Post.query.all()
    cnotes = len(Note.query.all())
    if (cnotes % Config.FLASKY_POSTS_PER_PAGE) != 0:
        pages = int(cnotes / Config.FLASKY_POSTS_PER_PAGE) + 1
    else:
        pages = cnotes / Config.FLASKY_POSTS_PER_PAGE
    data = ''
    for post in cposts:
        data = data + '\nhttps://www.tryblog.top/post' + str(post.id) + '.html'
    for page in range(pages):
        data = data + '\nhttps://www.tryblog.top/note' + str(page+1) + '.html'
    headers = {'User-Agent': 'curl/7.12.1',
               'Host': 'data.zz.baidu.com',
               'Content-Type': 'text/plain',
               'Content-Length': str(len(data))}
    res = requests.post(url=url, headers=headers, data=data)
    print(res.text)
    file = open('site.log', 'a')
    file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' 推送链接：' + data + '\n'
               + '提交状态：' + res.text + '\n\n')
    file.close()