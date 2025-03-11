from flask import Flask, jsonify, request, session, render_template, url_for, redirect
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

DATABASE = "SeniorCapstoneDatabase.db"

app.secret_key = 'your secret key'

@app.route('/')
def home():
    return render_template('Homepage.html')

def connect_db():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn



@app.route('/homepage')
def homepage():
    return render_template('Homepage.html')

@app.route('/contactus', methods=['GET','POST']) #For help desk and test labled index
def contactus():
    conn = connect_db()
    cursor = conn.cursor()
    if request.method == 'POST':
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
    else:
        return render_template('contactform.html')

@app.route('/login', methods =['GET', 'POST']) #base is geeksforge
def login():
    conn = connect_db()
    cursor = conn.cursor()
    msg = ''
    print("boser")
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        accountType = request.form['accountType']
        username = request.form['username']
        password = request.form['password']
        print("boser1")
        if accountType == "Buyer":
            print("boser2")
            cursor.execute("SELECT * FROM Buyer WHERE BuyerEmail = ? AND BuyerPasscode = ?", (username, password, ))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['BuyerID']
                session['username'] = account['BuyerName']
                msg = 'Logged in successfully !'
                return redirect(url_for('Bhomepage'))
            else:
                msg = 'Incorrect username / password !'
        else:
            cursor.execute('SELECT * FROM Supplier WHERE SupplierEmail = ? AND SupplierPasscode = ?', (username, password, ))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return render_template('VendorMainpage.html', msg = msg)
            else:
                msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/Bhomepage')
def Bhomepage():
    return render_template('BuyerMainpage.html', username=session['username'])

@app.route('/test', methods=['GET']) #used for test page
def test():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")  # Change 'Product' if incorrect
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


@app.route('/history', methods=['GET']) #purchase history
def history():
    if request.method == 'GET':
        print("here1")
        conn = connect_db()
        cursor = conn.cursor()
        search = request.args.get('search')
        cursor.execute("SELECT * FROM 'Order' WHERE BuyerID=:search", {"search":search})
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()
        return jsonify(data)
    else:
        return render_template('cancelorder.html')
            
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
    print(desc)
    try:
        cursor.execute("INSERT INTO Product (SupplierID, ProdName, ProdPrice, ProdQuantity, ProdDesc) VALUES (?, ?, ?, ?, ?)", 
         (supplier, name, price, quant, desc))
        conn.commit()
        conn.close()
        return jsonify({'success': 'Product added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search') #used for search page
def search():
    print("boser")
    return render_template('Search.html', username=session['username'])

@app.route('/searchS', methods=['GET']) #used for search feature Except it isnt working 
def searchS():
    conn = connect_db()
    cursor = conn.cursor()
    print("boser")
    search = request.args.get('search')
    cursor.execute("SELECT * FROM Product WHERE ProdName LIKE ?", (f"%{search}%",))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)
        
@app.route('/filterp', methods=['GET'])
def filter():
    print("boser")
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

@app.route('/cancel', methods=['GET','DELETE'])
def cancel():
    if request.method == 'DELETE':
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
    else:
        return render_template('cancelorder.html', username=session['username'])

@app.route('/cancel/<int:OrderID>', methods=['DELETE'])
def cancelOrder(OrderID):
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
