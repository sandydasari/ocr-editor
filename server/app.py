from flask import Flask, request, jsonify, send_from_directory
import json
import sqlite3
from libs.storeDoc import addDoctoDirectory
import uuid
from flask_cors import CORS
import os.path
from urllib.request import urlopen
from urllib.parse import quote

app = Flask(__name__,static_url_path='', static_folder='static')
CORS(app)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("books.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn


@app.route("/books", methods=["GET", "POST"])
def books():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor = conn.execute("SELECT * FROM book")
        books = [dict(bookuuid=row[0], title=row[1], author=row[2], fullpath=row[3], noofpages=row[4], isIndexed=row[4], category=row[5])
            for row in cursor.fetchall()
        ]
        if books is not None:
            return jsonify(books)

    if request.method == "POST":
        bookuuid = uuid.uuid4().hex
        uploaded_file = request.files["uploaded_file"]
        if ("pdf" not in uploaded_file.content_type):
             raise TypeError("Only pdf files are allowed for upload")
        new_title = request.form.get["title"]
        new_author = request.form.get["author"]
        new_fullpath = addDoctoDirectory(bookuuid, uploaded_file)
        new_noofpages = int(request.form.get["noofpages"])
        new_isIndexed = request.form.get["isIndexed"]
        new_category = request.form.get["category"]
        sql = """INSERT INTO book (title, author, fullpath, noofpages, isIndexed, category)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        cursor = cursor.execute(sql, (new_title, new_author, new_fullpath,new_noofpages,new_isIndexed,new_category))
        conn.commit()
        return f"Book with the id: 0 created successfully", 201


@app.route("/book/<uuid:bookuuid>", methods=["GET", "PUT", "DELETE"])
def single_book(bookuuid):
    conn = db_connection()
    cursor = conn.cursor()
    book = None
    if request.method == "GET":
        cursor.execute("SELECT * FROM book WHERE bookuuid=?", (bookuuid,))
        rows = cursor.fetchall()
        for r in rows:
            book = r
        if book is not None:
            return jsonify(book), 200
        else:
            return "Something wrong", 404

    if request.method == "PUT":
        sql = """UPDATE book
                SET title=?,
                    author=?,
                    fullpath=?,
                    noofpages=?,
                    isIndexed=?,
                    category=?,
                WHERE bookuuid=? """

        title = request.form["title"]
        author = request.form["author"]
        fullpath = request.form["fullpath"]
        noofpages = request.form["nooofpages"]
        isIndexed = request.form["isIndexed"]
        category = request.form["category"]
        updated_book = {
            "bookuuid": bookuuid,
            "title": title,
            "author": author,
            "fullpath": fullpath,
            "noofpages": noofpages,
            "isIndexed": isIndexed,
            "category": category
        }
        conn.execute(sql, (bookuuid, title, author, fullpath, noofpages, isIndexed, category))
        conn.commit()
        return jsonify(updated_book)

    if request.method == "DELETE":
        sql = """ DELETE FROM book WHERE bookuuid=? """
        conn.execute(sql, (bookuuid,))
        conn.commit()
        return "The book with id: {} has been deleted.".format(bookuuid), 200
@app.route("/cli", strict_slashes=False)
@app.route("/cli/pageview", strict_slashes=False)
def serve():
    return send_from_directory(app.static_folder, 'index.html')
@app.route("/s/<string:query>", strict_slashes=False)
def get(self, query):
    connection = urlopen('http://localhost:8983/solr/sandhi_core/select?q=pagecontent:'+quote(query) +"&hl=true&hl.fl=pagecontent&hl.usePhraseHighLighter=false&hl.requireFieldMatch=false&hl.simple.pre=<em%20style%3D\"background-color:yellow\">&hl.simple.post=<%2Fem>")
    response = json.load(connection)
    return response
@app.route("/i/b/<string:bid>/p/<int:pid>/", strict_slashes=False)
def image(self, bid, pid):
    image_dir = "./static"
    book = single_book(bookuuid=bid)
    if (not book or not pid or '.' in bid):
        return {
            "status":
            "error",
            "message":
            "no resource found for " + bid + "or page number not present"
        }

    resourcepath = book.fullpath.replace(".pdf", "") + "/page_images/O0001-" + format(pid, "03d") + ".jpg"
    if os.path.isfile(resourcepath):
        return send_file(resourcepath, mimetype='image/jpeg')
    else:
        return {
            "status": "error",
            "message": "no image found at path " + resourcepath
        }
@app.route("/h/b/<string:bid>/p/<int:pid>/", strict_slashes=False)
def hocr(self, bid, pid):
    image_dir = "./static"
    book = single_book(bookuuid=bid)
    if (not book or not pid or '.' in bid):
        return {
            "status":
            "error",
            "message":
            "no resource found for " + bid + "or page number not present"
        }

    resourcepath = book.fullpath.replace(".pdf", "") + "/output_files/O0001-" + format(pid, "03d") + ".hocr"
    if os.path.isfile(resourcepath):
        return send_file(resourcepath, mimetype='text/html')
    else:
        return {
            "status": "error",
            "message": "no hocr found at path " + resourcepath
        }
if __name__ == "__main__":
    app.run(debug=True)


