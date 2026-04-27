from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # 본인 MySQL 계정
app.config['MYSQL_PASSWORD'] = '비밀번호'  # 본인 MySQL 비밀번호
app.config['MYSQL_DB'] = 'lumberdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/lumber', methods=['GET'])
def get_lumber():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT l.*, 
            IFNULL(SUM(h.in_amount), 0) as total_in,
            (l.import_amount - IFNULL(SUM(h.in_amount), 0)) as remain
        FROM imported_lumber l
        LEFT JOIN import_history h ON l.id = h.lumber_id
        GROUP BY l.id
        ORDER BY l.id DESC
    """)
    data = cur.fetchall()
    return jsonify(data)

@app.route('/api/lumber', methods=['POST'])
def add_lumber():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO imported_lumber
        (company_name, bl_number, import_date, L, W, T, spec, import_amount, remarks)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['company_name'], data['bl_number'], data['import_date'],
        data['L'], data['W'], data['T'], data['spec'], data['import_amount'], data.get('remarks', '')
    ))
    mysql.connection.commit()
    return jsonify({'result': 'success'})

@app.route('/api/history/<int:lumber_id>', methods=['GET'])
def get_history(lumber_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM import_history WHERE lumber_id=%s ORDER BY in_date", (lumber_id,))
    data = cur.fetchall()
    return jsonify(data)

@app.route('/api/history', methods=['POST'])
def add_history():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO import_history (lumber_id, in_date, in_amount)
        VALUES (%s, %s, %s)
    """, (data['lumber_id'], data['in_date'], data['in_amount']))
    mysql.connection.commit()
    return jsonify({'result': 'success'})

@app.route('/api/summary', methods=['GET'])
def get_summary():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT spec, SUM(l.import_amount - IFNULL(h.total_in,0)) as remain_sum
        FROM imported_lumber l
        LEFT JOIN (
            SELECT lumber_id, SUM(in_amount) as total_in
            FROM import_history
            GROUP BY lumber_id
        ) h ON l.id = h.lumber_id
        GROUP BY spec
        ORDER BY spec
    """)
    data = cur.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True) 