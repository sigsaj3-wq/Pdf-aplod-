from flask import Flask, request, redirect, render_template_string, session
import os, hashlib

app = Flask(__name__)
app.secret_key = "saaji123"
os.makedirs("uploads", exist_ok=True)

users = {}  # phone/email -> {name, dp}
books = []  # {title, file, uploader, type, hash}
hashes = set()

HTML = """
<html><head><title>saaji</title>
<style>
body{background:black;color:white;font-family:Arial;text-align:center}
h1{color:black;background:red;padding:15px;border-radius:10px}
input,select{padding:10px;margin:5px;border-radius:8px;width:80%}
button{background:red;color:white;padding:10px 20px;border:none;border-radius:10px}
.card{background:#1a1a1a;padding:15px;margin:10px;border-radius:15px;border:1px solid red}
a{color:red}
</style></head>
<body>
<h1>saaji</h1>
<p>❤️ Red & Black Book App ❤️</p>

{% if not session.get('user') %}
<h3>Account Banao</h3>
<form method="post" action="/signup">
<input name="name" placeholder="Tera Naam" required><br>
<input name="phone" placeholder="Phone / Gmail" required><br>
<input name="dp" placeholder="DP Link (Instagram link v chalega)"><br>
<button>Account Banao</button>
</form>
{% else %}
<p>Welcome {{session['user']}} | <a href="/logout">Logout</a></p>
<h3>Book Upload Karo - Instagram Wangu</h3>
<form method="post" action="/upload" enctype="multipart/form-data">
<input name="title" placeholder="Book Da Naam" required><br>
<select name="privacy"><option>public</option><option>private</option></select><br>
<input type="file" name="file" accept=".pdf,.docx,.txt,.html" required><br>
<button>Upload</button>
</form>
{% endif %}

<h3>🔍 Search</h3>
<form method="get" action="/">
<input name="q" placeholder="Book / ID Search Karo..." value="{{q}}">
<button>Search</button>
</form>

{% for b in books %}
<div class="card">
<b>{{b['title']}}</b><br>
Uploader: {{b['uploader']}} | Type: {{b['privacy']}} | File: {{b['file']}}<br>
<a href="/read/{{b['file']}}">📖 Book Padho</a>
</div>
{% endfor %}
<p>{{msg}}</p>
</body></html>
"""

@app.route("/", methods=["GET"])
def home():
    q = request.args.get("q","").lower()
    show = [b for b in books if b['privacy']=='public' or b['uploader']==session.get('user')]
    if q:
        show = [b for b in show if q in b['title'].lower() or q in b['uploader'].lower()]
    return render_template_string(HTML, books=show, q=q, msg="")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form['name']
    phone = request.form['phone']
    users[phone] = {'name':name}
    session['user'] = name + " ("+phone+")"
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/upload", methods=["POST"])
def upload():
    if 'user' not in session:
        return redirect("/")
    f = request.files['file']
    data = f.read()
    # Copyright / Duplicate Check - Same file dobara upload nahi hovegi
    h = hashlib.md5(data).hexdigest()
    if h in hashes:
        return "<h2 style='color:red'>Eh Book Pehla Hi Upload Ho Chuki Hai! Copyright Issue - Upload Nahi Hoyi</h2><a href='/'>Back</a>"
    hashes.add(h)
    filename = f.filename
    open(os.path.join("uploads", filename), "wb").write(data)
    books.append({"title":request.form['title'], "file":filename, "uploader":session['user'], "privacy":request.form['privacy']})
    return redirect("/")

@app.route("/read/<name>")
def read(name):
    return f"<h1>{name}</h1><p>Yeh file uploads folder ch save ho gayi hai. Pydroid ch isnu khol ke padh sakde ho.</p><a href='/'>Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
