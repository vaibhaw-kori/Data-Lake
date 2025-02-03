from flask import Flask, request, jsonify,Response,send_file
from flask_cors import CORS
import json
import psycopg2
import mysql.connector
from pymongo import MongoClient
import pymongo
import chardet




postgres_conn = psycopg2.connect(database="postgres", user='postgres', password='postgres', host='mypostgres', port= '5432')
sql_conn = mysql.connector.connect(user='root', password='root', host='mysqlhost', port="3306", database='test_db')
app = Flask(__name__)
CORS(app)
# resources = {r"/api/*": {"origins": "*"}}
# app.config["CORS_HEADERS"] = "Content-Type"
# app.config['JSON_SORT_KEYS'] = False


@app.route('/datalake/test')
def test():
    return jsonify({"Message":"This is your flask app with docker"})


@app.route('/datalake/insert_string',methods=['POST']) #api to insert a string in to postgres, returns unique id of the string
def insert_string():
    # comm = request.args.get('text')
    comm = request.form['text']
    dir(request)
    print("user sent comment == ",comm)
    cursor = sql_conn.cursor()
    insert_query = f"""INSERT INTO string_table (text) VALUES('{comm}');"""
    cursor.execute(insert_query)
    cursor.execute("SELECT * FROM string_table")
    data = cursor.fetchall()
    sql_conn.commit()
    print("data fetched == ",data[len(data)-1][0])
    # print("size of the cursor rows == ",len(cursor))
    # uid = data[len(data)-1][0]
    # print("data fetched == ",data[len(data)-1][0])
    return str(data[len(data)-1][0])

@app.route('/datalake/get_string',methods=['GET'])
def get_string():
    id = request.args.get('id')
    cursor = sql_conn.cursor()
    query = f"""SELECT text FROM string_table WHERE id={id}"""
    cursor.execute(query)
    string = cursor.fetchone()
    print("string fetched == ",string)
    if string == None:
        print("no content for id == ",id)
        response = Response(status=404)
        return response
    return string[0]

@app.route('/datalake/pdf_upload',methods=['POST'])
def pdf_upload():
    file = request.files['file']
    file_contents = file.read()
    client = MongoClient('mongodb://mongohost',27017)
    # filename = request.args.get('yess')
    db = client['pdf_db']
    collection= db['pdf_collection']
    document = collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])
    uid = int(document['filename']) + 1
    db.pdf_collection.insert_one({'filename': uid, 'contents': file_contents})
    # return f"returned id {uid}"
    return str(uid)

@app.route('/datalake/download_pdf',methods=['GET'])
def pdf_download():
    uid = request.args.get('id')
    print("id recieved == ",uid)
    client = MongoClient('mongodb://mongohost',27017)
    db = client['pdf_db']
    collection= db['pdf_collection']
    bin_data = collection.find_one({"filename": int(uid)})
    if bin_data == None:
        response = Response(status=404)
        return response
    bin_data = bytes(bin_data['contents'])
    print("pdf fetched == ",bin_data)
    print("type of pdf file == ",type(bin_data))
    response = Response(bin_data,content_type='application/pdf')
    return response
    # non_bin_data = collection.find_one({"filename": int(uid)})['contents']
    # return send_file(bytes(non_bin_data), mimetype='application/pdf',download_name="response", as_attachment=True)
    

@app.route('/datalake/image_upload',methods=['POST'])  #api to insert images into postgres returns unique id of the image
def image_upload():
    print("request from server 1",request.files)
    file = request.files['file']
    # image_data = request.get_data()
    image_data = file.read()
    # print("request from server 1",bytes(image_data))
    # print(image_data)
    curr = postgres_conn.cursor()
    curr.execute("INSERT INTO images(data) VALUES (%s) RETURNING id;", (bytes(image_data),))
    img_id = curr.fetchall()
    # img_id = 2
    # postgres_conn.commit()
    # return f"image upload testing {img_id}"
    res = {'id':img_id[0][0]}
    print("id == ",res['id'])
    return str(img_id[0][0])



@app.route('/datalake/image_download',methods=['GET'])
def image_download():
    img_id = request.args.get('id')
    print("user sent image id == ",img_id)
    curr = postgres_conn.cursor()
    curr.execute("SELECT data FROM images WHERE id = %s", (img_id,))
    image = curr.fetchone()
    print("image fetched == ",image)
    if(image == None):
        response = Response(status=404)
        print("image == None")
        return response
    bin_data = bytes(image[0])
    print("content of image == ",bin_data[:5])
    # encoded_image = str(bin_data).encode('iso-8859-1')
    # result = chardet.detect(bytes(encoded_image))
    # print("encoidng of image == ",result['encoding'])
    print("typee of image = ",type(bin_data))
    response = Response(bin_data,content_type='image/jpeg')
    return response


if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=7007)