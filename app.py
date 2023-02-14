from flask import Flask, render_template
from flask import url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from markupsafe import  escape
import click
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
import os

app=Flask(__name__)
#设置mysql数据库URI，告诉SQLAlchemy数据库的连接地址
"""
SQLAlchemy indicates the source of an Engine as a URI combined with optional keyword arguments to specify options for the Engine. 
The form of the URI is:
dialect+driver://username:password@host:port/database
"""
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:yzm@localhost:3306/dbOne'
#dbOne是通过mysql为该项目建立的数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False #关闭对模型修改的监控
#在扩展类实例化之前修改加载配置
app.config['SECRET_KEY']='dev'
db=SQLAlchemy(app) #import扩展类并初始化扩展，传入实例app


#对于初始化扩展Flask-login，不仅需要实例化扩展类，还需要实现一个用户加载回调函数
login_manager=LoginManager(app)
login_manager.login_view='login'
#开启视图保护后，若未登录并访问被保护的视图，会重定向回login_view并发出错误提示
@login_manager.user_loader#用户加载回调函数
def load_user(user_id):
    """
    实现 用户加载回调函数
    接受 用户 id作为参数
    返回值是用户id对应的用户模型类记录
    Flask-login提供了一个current_user变量，
    运行程序后，current_user变量的值回事当前用户的用户模型类记录
    :param user_id:
    :return:
    """
    user=User.query.get(int(user_id))
    return user

#__name__是一个全局变量，随着脚本执行或模块的引入而改变
class User(db.Model,UserMixin):
    """
    创建数据库模型
    模型类和字段
    模型类的声明要继承db.Model
    类字段要实例化db.Column,传入的参数为字段类型等，还有：
    primary_key:bool
    nullable:bool
    index:bool
    unique:bool
    default:bool
    表中的记录以模型类的实例表示
    """
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    username=db.Column(db.String(20))
    password_hash=db.Column(db.String(128))
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)

class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(60))
    year=db.Column(db.String(4))










#@app.route('/')
#def index():
#    return render_template('index.html',name=name,movies=movies)

#注册 请求处理函数（view function）
#Web程序可以看作一堆视图函数的集合，编写不同的view function来处理对应的url请求
@app.route('/',methods=['GET','POST'])
def index():
    """
    当访问指定url规则时会出发该函数，获取返回值并把返回值显示到浏览器窗口
    app.route()的参数称为URL规则（rule），
    如'/user/<name>',name是从url中解析获得的变量，可作为后端请求处理函数的参数
    视图函数 view function的名称用于
    表达所要处理页面的含义；
    代表某个路由的端点(endpoint)，从而用来生成视图函数对应的URL(使用url_for()生成)
    :return: 响应的主体，默认被浏览器以HTML格式解析
    """

    f'<h1>Hello Flask!!!</h1><img src="http://helloflask.com/totoro.gif">'

    if request.method=='POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        #从request中获取表单数据
        title=request.form.get("title")
        year=request.form.get("year")
        #验证数据
        if not title or not year or len(year)>4 or len(title)>60:
            flash("Invalid input.")
            #flash()在内部会把消息存储在session对象中，
            #session用于在请求见存储数据，会把数据签名后存储在浏览器的cookie中
            #因此需要设置签名所需的密钥
            #display message to user.
            return redirect(url_for('index'))

        #保存表单数据
        movie=Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash("Item created.")
        return redirect(url_for("index"))

    movies=Movie.query.all()
    """
    render_template()用于渲染模板，传入参数有：
    模板文件名
    通过关键字参数传入模板内部使用的变量
    render_template()调用后执行模板里所有的Jinja2语句并返回渲染好的模板内容
    """
    return render_template('index.html',movies=movies)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user=User.query.first()
        if username==user.username and user.validate_password(password):
            login_user(user)#登入用户
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required #用于视图保护
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie=Movie.query.get_or_404(movie_id)

    if request.method=='POST': #处理编辑页面表单的提交请求
        title=request.form['title']
        year=request.form['year']

        if not title or not year or len(year)!=4 or len(title)>60:
            flash("Invalid input.")
            return redirect(url_for('edit'),movie_id=movie_id)
        movie.title=title
        movie.year=year
        db.session.commit() #提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index')) #重定向回主页

    return render_template('edit.html',movie=movie) #渲染编辑页面的模板

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    """
    为了安全考虑，一般会使用 POST请求 提交 删除请求，使用表单而非链接来实现删除
    :param movie_id:
    :return:
    """
    movie=Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

@app.route('/setting',methods=['GET','POST'])
@login_required
def setting():
    if request.method=='POST':
        name=request.form['name']
        if not name or len(name)>20:
            flash('Invalid input.')
            return redirect(url_for('setting'))
        current_user.name=name
        db.session.commit()
        flash('Setting Updated.')
        return redirect(url_for('index'))

    return render_template('setting.html')

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
    print(url_for('index'))

    print(url_for('user_page',name="yzm"))
    print(url_for('user_page',name="Luffyzm"))
    print(url_for('test_url_for',num=1))
    return "Test Page"

#flask run : 使用development server运行程序，默认监听本地的5000端口
#访问http://localhost:5000 or http://127.0.0.1:5000
#flask默认把程序存储在名为app.py或wsgi.py的文件中
#如果要使用其他名称需要设置 系统环境变量 FLASK_APP 为要启动的程序名

@app.errorhandler(404)
def page_not_found(e):
    """
    和视图函数类似，收到错误或异常时，该函数触发执行。
    :param e:
    :return:
    """

    return render_template('404.html'),404
#返回响应主体，状态码
@app.context_processor
def inject_user():
    """
    上下文处理函数，该函数的返回值（以字典键值对的形式）将会统一注入到
    模板的上下文环境中，因此返回值中的变量可以直接在模板中使用
    :return:
    """
    user=User.query.first()
    return dict(user=user)


@app.cli.command()
def forge():
    """
    自定义命令函数，用于一次性执行，相当于编写批处理
    :return:
    """
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user=User(name=name)
    db.session.add(user)
    for m in movies:
        movie=Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo("Done.")

@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
#prompt=True 表示会有提示参数输入，confirmation_prompt 表示会有提示重新输入以确认
def admin(username,password):
    """
    通过命令行创建管理员账户，若之前账户存在则更新账号和密码
    :param username:
    :param password:
    :return:
    """
    """creat user."""
    user=User.query.first()
    if user is not None:
        user.username=username
        user.set_password(password)
    else:
        click.echo("Creating user...")
        user=User(username=username,name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo("Done.")


if __name__=="__main__":
    db.drop_all()
    db.create_all()