### 基于flask + layui + sqlite的个人博客系统（前台+后台）

#### 一、主要特点

- 支持markdown
- 支持短笔记
- 响应式布局，移动终端显示友好
- 部署迁移便捷

#### 二、开发环境

1. Web框架：python flask

2. 前端框架：layui

3. 数据库：sqlite

4. markdown支持: editor.md

5. 代码高亮：highlight.js

6. 部署环境：centos 8.2


#### 三、博客前台

##### （一）主体内容区

##### 1. 首页

以列表的形式展示文章标题及内容摘要（200字），每个显示10篇文章，提供分页机制。
![前台首页.png](snapshot/前台首页20210411202117.png)

##### 2. 正文

点击首页文章的标题，跳转到正文页面。正文显示markdown渲染后的文章内容，包括标题，文章信息，文章正文，文章标签，文章留言等部分，留言区分页显示。
![前台正文.png](https://tryblog.top//static/uploads/2021/04/前台正文20210411202134.png)

##### 3. 归档

按年月对文章进行归类，以列表形式展示，该页面不分页。

##### 4. 笔记

笔记是本博客不同于传统个人博客之处，笔记与文章并列，用于记录一些简短的信息（支持markdown），且该页面直接以列表形式显示每条笔记的全部内容，不用跳转，因而查询更加快捷，每页显示10条笔记，提供分页机制。
![前台笔记.png](https://tryblog.top//static/uploads/2021/04/前台笔记20210411202152.png)

##### 5. 留言

该页面用于读者与作者进行互动。读者填写用户名和合法邮箱后便可以自由留言，也可以回复其他读者的留言，管理员通过输入口令可在该页回复读者，同时回复将被标记为来自管理员。
![前台留言.png](https://tryblog.top//static/uploads/2021/04/前台留言20210411202209.png)

##### 6. 关于

该页展示博主基本信息。

##### （二）侧边栏

![前台首页2.png](https://tryblog.top//static/uploads/2021/04/前台首页220210411202534.png)

##### 1. 搜索框

- 非"笔记"页面，根据关键词搜索相关文章

- "笔记"页面，根据关键词搜索相关笔记

##### 2. 头像区

- 背景图片：每日自动更换，每日第一次访问博客时，自动从"必应"图片网上下载高清壁纸，降低图片分辨率后存储（2021_xx_xx.jpg）
- 用户头像和昵称：点击进入博客后台，头像图片和用户昵称可在后台更换
- 链接：新页面打开Github和邮箱

##### 3. 文章分类

- 显示所有文章的分类和每个分类下的文章数量

- 点击进入分类页面（上有面包屑导航），以列表形式展示该分类下的所有文章，提供分页机制。

##### 4. 最新文章

显示最近发布的5篇文章

##### 5. 文章标签

- 显示所有文章标签，标签颜色为创建时随机生成
- 点击进入标签页面（上有面包屑导航），以列表形式展示该含有该标签的所有文章，提供分页机制。

#### 四、博客后台

##### 1. 控制台

- 显示博客基本信息（文章数、笔记数、分类数、标签数等信息）

- 撰写修改文章的快捷方式
- 显示最近发布的文章列表
![后台首页.png](https://tryblog.top//static/uploads/2021/04/后台首页20210411202244.png)

##### 2. 撰写

采用开源的editor.md编辑器

- 撰写文章
  - 添加文章标签
  - 上传图片，删除图片，点击图片名一键在文章中添加图片链接
- 撰写笔记
![后台撰写页.png](https://tryblog.top//static/uploads/2021/04/后台撰写页20210411202257.png)

##### 3. 编辑

- 编辑文章
- 编辑笔记

##### 4. 管理

- 管理文章
- 管理笔记
- 管理分类
- 管理标签
- 管理留言
- 管理评论
![后台管理页.png](https://tryblog.top//static/uploads/2021/04/后台管理页20210411202312.png)

#### 五、部署上线

##### 1. 安装python3.6和virtualenv

```bash
# 安装python3.6
wget http://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
tar -xvzf Python-3.6.4.tgz
cd Python-3.6.4
./configure --with-ssl
# ubuntu下
apt-get install openssl
apt-get install libssl-dev
make #系统需要安装gcc环境（apt-get install build-essential）
make install #过程中解压缩需要安装zlib（apt-get install zlib*）
# centos下
yum install openssl
yum install openssl-devel
make
make install

# 安装virtualenv
pip3 install virtualenv
```

将python3.6设为默认pyhon3，将pyhon3设为默认python。

##### 2. 使用virtualenv创建虚拟环境，并安装项目所需的python包

在`/var/www/blog`目录下，执行

```bash
virtualenv venv  #创建名为venv的虚拟环境
source venv/bin/activate  #激活虚拟环境
pip3 install -r requirements.txt  #安装项目所需的python包
deactive  #退出虚拟环境
```

##### 3. 安装nginx并配置

```bash
sudo apt-get install nginx  #ubuntu下
sudo yum install nginx  #centos下
```

删去`/etc/nginx/nginx.conf`中的server段配置，在`/etc/nginx/conf.d`中建立配置文件`uwsgi_nginx.conf`如下：

``` ini
sserver {
	listen 80;
	server_name www.tryblog.top;
	charset utf-8;
	client_max_body_size 75M;
	location / {
		include uwsgi_params;
		uwsgi_pass 127.0.0.1:8000;
		uwsgi_param UWSGI_PYHOME /var/www/blog/venv; #虚拟环境目录
	        uwsgi_param UWSGI_CHDIR /var/www/blog; # 应用根目录
	        uwsgi_param UWSGI_SCRIPT manage:app; # 启动程序
	}
	location /static {
		alias /var/www/blog/app/static;
	}
}

server{
	listen 443 ssl ;
	server_name www.tryblog.top;

	ssl on;
	#证书文件
	ssl_certificate /var/www/blog/ssl/tryblog.top.pem;
	ssl_certificate_key /var/www/blog/ssl/tryblog.top.key;
	ssl_session_timeout 5m;
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	#密码加密方式
	ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
	#依赖SSLv3和TLSv1协议的服务器密码将优先于客户端密码
	ssl_prefer_server_ciphers on;

	charset utf-8;
	client_max_body_size 75M;
	location / {
		include uwsgi_params;
		uwsgi_pass 127.0.0.1:8000;
		uwsgi_param UWSGI_PYHOME /var/www/blog/venv; #虚拟环境目录
	        uwsgi_param UWSGI_CHDIR /var/www/blog; # 应用根目录
	        uwsgi_param UWSGI_SCRIPT manage:app; # 启动程序
	}
	location /static {
		alias /var/www/blog/app/static;
	}
}

#监控80端口，强制跳转到443端口
server {
	listen 80;
	server_name tryblog.top;
	rewrite ^(.*)$ https://www.$server_name$1 permanent;
}

```

重启nginx服务器，使配置生效。

##### 4. 安装uwsgi并配置

```bash
# ubuntu下
sudo apt-get install build-essential python-dev
pip3 install uwsgi
# centos下
sudo yum install make automake gcc gcc-c++ kernel-devel python3-devel
pip3 install uwsgi
```

在博客根目录`/var/www/blog`下创建配置文件`uwsgi.ini`如下：

``` ini
[uwsgi]
#配合nginx使用
socket = 127.0.0.1:8000
#项目路径 
chdir = /var/www/blog
wsgi-file= /var/www/blog/manage.py
callable = app
#指定工作进程
processes = 4
#主进程
master = true
#每个工作进程有2个线程
threads = 2
#指的后台启动 日志输出的地方
daemonize = uwsgi.log
#保存主进程的进程号
pidfile = uwsgi.pid
#虚拟环境环境路径
virtualenv = /var/www/blog/venv

```

启动uwsgi服务器，浏览器中输入网址即可正常访问，启动关闭命令如下：

```bash
uwsgi --ini uwsgi.ini   #启动
uwsgi --stop uwsgi.pid  #停止
```



部署效果：我的博客：https://tryblog.top

