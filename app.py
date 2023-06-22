from pymongo import MongoClient
import jwt
import hashlib
from flask import Flask,render_template,jsonify,redirect,url_for,request
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("DB_URI")
DB_NAME = os.environ.get("DB_NAME")
ENV_KEY = os.environ.get("SECRET_KEY")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = './static/profile_pics'
SECRET_KEY = ENV_KEY
TOKEN = 'token'

# MongoDB

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
# Collection
user_data = db.sweeter
user_post = db.sweeter_posts
user_likes = db.sweeter_likes

# ----------------- GET -------------------

@app.route('/')
def home():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = user_data.find_one({'username':payload['id']})
        return render_template('index.html',user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your session has expired'
        return redirect(url_for('login_fn',msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'Something wrong happens'
        return redirect(url_for('login_fn',msg=msg))
    
@app.route('/login',methods=['GET'])
def login_fn():
    msg = request.args.get('msg')
    return render_template('login.html',msg=msg)

@app.route('/user/<username>',methods=['GET'])
def user_render(username):
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        status = username == payload['id']
        user_info = user_data.find_one({'username':username},{'_id':False})
        return render_template('user.html',user_info=user_info,status=status)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/get_posts',methods=['GET'])
def get_posts():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username_receive = request.args.get('username_give')
        if username_receive == '':
            posts = list(user_post.find({}).sort('date',-1).limit(20))
        else:
            posts = list(user_post.find({'username':username_receive}).sort('date',-1).limit(20))
        for post in posts:
            post['_id'] = str(post['_id'])
            post['count_heart'] = user_likes.count_documents({'post_id':post['_id'],'type':'heart'})
            post['heart_by_me'] = bool(user_likes.find_one({'post_id':post['_id'],'type':'heart','username':payload['id']}))

            post['count_star'] = user_likes.count_documents({'post_id':post['_id'],'type':'star'})
            post['star_by_me'] = bool(user_likes.find_one({'post_id':post['_id'],'type':'star','username':payload['id']}))

            post['count_thumbs_up'] = user_likes.count_documents({'post_id':post['_id'],'type':'thumbs_up'})
            post['thumbs_up_by_me'] = bool(user_likes.find_one({'post_id':post['_id'],'type':'thumbs_up','username':payload['id']}))
        return jsonify({'result':'success','msg':'Fetched successfully','posts':posts})
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html')
    
@app.route('/secret',methods=['GET'])
def secret():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = user_data.find_one({'username':payload['id']})
        return render_template('secret.html',user_info=user_info)
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

# ----------------- POST -------------------

@app.route('/sign_in',methods=['POST'])
def sign_in():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = user_data.find_one({"username": username_receive,"password": pw_hash,})
    if not result:
        return jsonify({"result": "fail","msg": "Cannot find user with that combination of id and password",})
    payload = {
        "id": username_receive,
        "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"result": "success","token": token,})

@app.route('/sign_up/save',methods=['POST'])
def sign_up():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # id
        "password": password_hash,                                  # password
        "profile_name": username_receive,                           # user's name is set to their id by default
        "profile_pic": "",                                          # profile image file name
        "profile_pic_real": "profile_pics/profile_placeholder.png", # a default profile image
        "profile_info": ""                                          # a profile description
    }
    user_data.insert_one(doc)
    return jsonify({'result':'success'})

@app.route('/sign_up/check_dup',methods=['POST'])
def check_dup():
    username_receive = request.form.get('username_give')
    exists = bool(user_data.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/update_profile',methods=['POST'])
def update_profile():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        username = payload['id']
        name_receive = request.form.get('name_give')
        about_receive = request.form.get('about_give')
        new_doc = {
            'profile_name':name_receive,
            'profile_info':about_receive
        }
        # sync_doc = {'profile_name':name_receive}
        if 'file_give' in request.files:
            file = request.files['file_give']
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f'profile_pics/{username}.{extension}'
            file.save(f'./static/{file_path}')
            new_doc['profile_pic'] = filename
            new_doc['profile_pic_real'] = file_path
            # sync_doc['profile_pic_real'] = file_path
        # user_post.update_many({'username':username},{'$set':sync_doc})
        user_data.update_one({'username':username},{'$set':new_doc})
        return jsonify({'result':'success','msg':'Your profile has been updated'})
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/posting',methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = user_data.find_one({'username':payload['id']})
        comment_receive = request.form.get('comment_give')
        date_receive = request.form.get('date_give')
        doc = {
            "username": user_info['username'],
            "profile_name": user_info['profile_name'],
            "profile_pic_real": user_info['profile_pic_real'],
            "comment":comment_receive,
            "date":date_receive
        }
        user_post.insert_one(doc)
        return jsonify({'result':'success','msg':'Posted successfully'})
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/update_like',methods=['POST'])
def update_like():
    token_receive = request.cookies.get(TOKEN)
    try:
        payload = jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = user_data.find_one({'username':payload['id']})
        post_id_receive = request.form.get('post_id_give')
        type_receive = request.form.get('type_give')
        action_receive = request.form.get('action_give')
        doc = {
            'post_id':post_id_receive,
            'username':user_info['username'],
            'type':type_receive
        }
        if action_receive == 'like':
            user_likes.insert_one(doc)
        else:
            user_likes.delete_one(doc)
        count = user_likes.count_documents({'post_id':post_id_receive,'type':type_receive})
        return jsonify({'result':'success','msg':'Updated','count':count})
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run('0.0.0.0',5000,debug=True)
