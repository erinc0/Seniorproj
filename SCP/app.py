from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

DATABASE = "SCP/SeniorCapstoneDatabase.db"

def connect_db():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

@app.route('/test', methods=['GET']) #used for test page
def test():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")  # Change 'Product' if incorrect
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


@app.route('/order', methods=['GET']) #purchase history
def order():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM 'Order'")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


@app.route('/history', methods=['GET']) #purchase history
def history():
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor.execute("SELECT * FROM 'Order' WHERE BuyerID=:search", {"search":search})
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


        
        
@app.route('/data', methods=['POST']) #For help desk and test labled index
def submit_help_ticket():
    conn = connect_db()
    cursor = conn.cursor()
    name = request.form.get('name')
    email = request.form.get('email')
    desc = request.form.get('desc')
    try:
        cursor.execute("INSERT INTO HelpDesk (Name, Email, Description) VALUES (?, ?, ?)", (name, email, desc))
        conn.commit()
        conn.close()
        return jsonify({'success': 'Ticket added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
            
@app.route('/newlisting', methods=['POST']) # used for create new listing
def all_i_feel_is_sad():
    print("here1")
    conn = connect_db()
    cursor = conn.cursor()            
    supplier = '1'
    name = request.form.get('name')
    price = request.form.get('price')
    quant = request.form.get('quantity')
    desc = request.form.get('description')
    image = request.form.get('file')

    print(desc)
    try:
        cursor.execute("INSERT INTO Product (SupplierID, ProdName, ProdPrice, ProdQuantity, ProdDesc, ProdImage) VALUES (?, ?, ?, ?, ?, ?)",
         (supplier, name, price, quant, desc, image))
        conn.commit()
        conn.close()
        return jsonify({'success': 'Product added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET', 'POST']) #used for search feature
def all_i_feel_is_bad():           
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    #https://stackoverflow.com/questions/62199521/how-to-properly-use-sql-like-statement-to-query-db-from-flask-application
    cursor.execute("SELECT * FROM Product WHERE ProdName LIKE :search", {"search": '%' + search + '%'}) 
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)

@app.route('/help', methods=['GET']) #used for search feature
def help():
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor.execute("SELECT * FROM 'HelpDesk'")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


@app.route('/filterp', methods=['GET'])
def filter():
    conn = connect_db()
    cursor = conn.cursor()
    minval = request.args.get('minval', type=int)
    maxval=request.args.get('maxval', type=int)
    search = request.args.get('search')
    cursor.execute("SELECT * FROM Product WHERE ProdPrice >=? AND ProdPrice<=? AND ProdName LIKE ?", (minval, maxval, f"%{search}%"))
    rows = cursor.fetchall()
    data=[dict(row) for row in rows]
    conn.close()
    return jsonify(data)

@app.route('/cancel/<int:OrderID>', methods=['DELETE'])
def cancel(OrderID):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM OrderItems WHERE OrderID=?", (OrderID,))
        cursor.execute("DELETE FROM 'Order' WHERE OrderID=?", (OrderID,))

        conn.commit()
        return jsonify({'success': True}), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()



if __name__ == '__main__':
    app.run(debug=True)
