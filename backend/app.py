from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from openai import OpenAI
import jwt
import datetime
from functools import wraps
from config import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEFAULT_CHAT_MODEL, SERVICE_PORT
from database import init_db, create_user, verify_user, get_user_by_id
from database import get_books_by_user, create_book, update_book, delete_book
from database import get_book_by_id, add_chapter, update_chapter, delete_chapter
from database import update_book_settings, reorder_chapters

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"code": 401, "msg": "请先登录", "data": None})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({"code": 401, "msg": "用户不存在", "data": None})
        except jwt.ExpiredSignatureError:
            return jsonify({"code": 401, "msg": "登录已过期", "data": None})
        except jwt.InvalidTokenError:
            return jsonify({"code": 401, "msg": "无效的token", "data": None})

        return f(current_user, *args, **kwargs)
    return decorated

@app.post("/api/auth/register")
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空", "data": None})

    if len(username) < 3:
        return jsonify({"code": 400, "msg": "用户名至少3个字符", "data": None})

    if len(password) < 6:
        return jsonify({"code": 400, "msg": "密码至少6个字符", "data": None})

    if create_user(username, password):
        return jsonify({"code": 200, "msg": "注册成功", "data": None})
    else:
        return jsonify({"code": 400, "msg": "用户名已存在", "data": None})

@app.post("/api/auth/login")
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空", "data": None})

    user = verify_user(username, password)
    if user:
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": token,
                "username": user['username']
            }
        })
    else:
        return jsonify({"code": 401, "msg": "用户名或密码错误", "data": None})

@app.get("/api/auth/me")
@token_required
def get_me(current_user):
    return jsonify({
        "code": 200,
        "msg": "成功",
        "data": {
            "id": current_user['id'],
            "username": current_user['username']
        }
    })

@app.post("/api/auth/logout")
@token_required
def logout(current_user):
    return jsonify({"code": 200, "msg": "退出成功", "data": None})

@app.get("/api/books")
@token_required
def get_books(current_user):
    books = get_books_by_user(current_user['id'])
    return jsonify({"code": 200, "msg": "成功", "data": books})

@app.post("/api/books")
@token_required
def add_book(current_user):
    data = request.get_json()
    title = data.get('title', '').strip()
    style = data.get('style', '')

    if not title:
        return jsonify({"code": 400, "msg": "作品名称不能为空", "data": None})

    book_id = create_book(current_user['id'], title, style)
    return jsonify({"code": 200, "msg": "添加成功", "data": {"id": book_id}})

@app.put("/api/books/<int:book_id>")
@token_required
def modify_book(current_user, book_id):
    data = request.get_json()
    title = data.get('title', '').strip()
    style = data.get('style', '')

    if not title:
        return jsonify({"code": 400, "msg": "作品名称不能为空", "data": None})

    if update_book(book_id, current_user['id'], title, style):
        return jsonify({"code": 200, "msg": "更新成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.delete("/api/books/<int:book_id>")
@token_required
def remove_book(current_user, book_id):
    if delete_book(book_id, current_user['id']):
        return jsonify({"code": 200, "msg": "删除成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.get("/api/books/<int:book_id>")
@token_required
def get_book(current_user, book_id):
    book = get_book_by_id(book_id, current_user['id'])
    if book:
        return jsonify({"code": 200, "msg": "成功", "data": book})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.post("/api/books/<int:book_id>/chapters")
@token_required
def new_chapter(current_user, book_id):
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')

    chapter_id = add_chapter(book_id, current_user['id'], title, content)
    if chapter_id:
        return jsonify({"code": 200, "msg": "章节创建成功", "data": {"id": chapter_id}})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.put("/api/books/<int:book_id>/chapters/<int:chapter_id>")
@token_required
def modify_single_chapter(current_user, book_id, chapter_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if update_chapter(chapter_id, current_user['id'], title, content):
        return jsonify({"code": 200, "msg": "保存成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "章节不存在或无权限", "data": None})

@app.delete("/api/books/<int:book_id>/chapters/<int:chapter_id>")
@token_required
def remove_chapter(current_user, book_id, chapter_id):
    if delete_chapter(chapter_id, current_user['id']):
        return jsonify({"code": 200, "msg": "删除成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "章节不存在或无权限", "data": None})

@app.put("/api/books/<int:book_id>/chapters/reorder")
@token_required
def reorder_book_chapters(current_user, book_id):
    data = request.get_json()
    orders = data.get('orders', [])

    if reorder_chapters(book_id, current_user['id'], orders):
        return jsonify({"code": 200, "msg": "排序成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.put("/api/books/<int:book_id>/settings")
@token_required
def modify_settings(current_user, book_id):
    data = request.get_json()
    settings = data.get('settings', {})

    if update_book_settings(book_id, current_user['id'], settings):
        return jsonify({"code": 200, "msg": "保存成功", "data": None})
    else:
        return jsonify({"code": 404, "msg": "作品不存在或无权限", "data": None})

@app.post("/api/chat")
def get_ai_answer():
    req_data = request.get_json()
    user_question = req_data.get("question")

    if not user_question:
        return jsonify({"code": 400, "msg": "请输入问题", "data": None})

    try:
        response = deepseek_client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "你是一个友好的AI助手，回答简洁清晰"},
                {"role": "user", "content": user_question}
            ],
            stream=False
        )
        ai_answer = response.choices[0].message.content

        return jsonify({
            "code": 200,
            "msg": "成功",
            "data": {"answer": ai_answer}
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"请求失败: {str(e)}", "data": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
