from flask import Flask
from flask import url_for
from markupsafe import  escape
print(__name__)
app=Flask(__name__)
#__name__是一个全局变量，随着脚本执行或模块的引入而改变

#注册 请求处理函数（view function）
#Web程序可以看作一堆视图函数的集合，编写不同的view function来处理对应的url请求
@app.route('/')
def hello():
    """
    当访问指定url规则时会出发该函数，获取返回值并把返回值显示到浏览器窗口
    app.route()的参数称为URL规则（rule），
    如'/user/<name>',name是从url中解析获得的变量，可作为后端请求处理函数的参数
    视图函数 view function的名称用于
    表达所要处理页面的含义；
    代表某个路由的端点(endpoint)，从而用来生成视图函数对应的URL(使用url_for()生成)
    :return: 响应的主体，默认被浏览器以HTML格式解析
    """

    return f'<h1>Hello Flask!!!</h1><img src="http://helloflask.com/totoro.gif">'
@app.route('/user/<name>')
def user_page(name):
    return f'User:{escape(name)}'

@app.route('/test')
def test_url_for():
    #测试使用url_for()为视图函数会如何生成url，print打印在命令行界面中
    """
    通常将路由的端点（endpoint）默认为视图函数的名称，
    后面接参数，可以是视图函数的参数；
    若不是，则作为查询字符串附加在URL后面
    """
    print(url_for('hello'))

    print(url_for('user_page',name="yzm"))
    print(url_for('user_page',name="Luffyzm"))
    print(url_for('test_url_for',num=1))
    return "Test Page"

#flask run : 使用development server运行程序，默认监听本地的5000端口
#访问http://localhost:5000 or http://127.0.0.1:5000
#flask默认把程序存储在名为app.py或wsgi.py的文件中
#如果要使用其他名称需要设置 系统环境变量 FLASK_APP 为要启动的程序名

