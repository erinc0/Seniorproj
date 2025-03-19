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
    if request.method == 'POST':
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
    else:
        return render_template('contactform.html')

@app.route('/login', methods =['GET', 'POST']) #login form
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        conn = connect_db()
        cursor = conn.cursor()
        msg = ''
        print("boser")
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
                session['usertype'] = 'Buyer'
                session['username'] = account['BuyerName']
                msg = 'Logged in successfully !'
                return redirect(url_for('Bhomepage'))
            else:
                msg = 'Incorrect username / password !'
        else:
            print("boser3")
            cursor.execute('SELECT * FROM Supplier WHERE SupplierEmail = ? AND SupplierPasscode = ?', (username, password, ))
            account = cursor.fetchone()
            if account:
                print("boser4")
                session['loggedin'] = True
                session['id'] = account['SupplierID']
                session['usertype'] = 'Vendor'
                session['username'] = account['SupplierName']
                msg = 'Logged in successfully !'
                return redirect(url_for('Vhomepage'))
            else:
                msg = 'Incorrect username / password !'
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login'))


@app.route('/Bhomepage')
def Bhomepage():
    return render_template('BuyerMainpage.html', username=session['username'])

@app.route('/Vhomepage')
def Vhomepage():
    return render_template('VendorMainpage.html', username=session['username'])

@app.route('/test', methods=['GET']) #used for test page
def test():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")
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
            
@app.route('/VendorAdd', methods=['GET','POST']) # used for create new listing
def VendorAdd():
    if request.method == 'POST':
        print("here1")
        conn = connect_db()
        cursor = conn.cursor()            
        supplier = session['id']
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
            conn.close()
            return jsonify({'error': str(e)}), 500
    else:
        return render_template('VendorAdd.html', username=session['username'])

@app.route('/search') #used for search page for customer
def search():
    print("boser")
    return render_template('Search.html', username=session['username'])
    
@app.route('/Vsearch') #used for search page for vendors   
def Vsearch():
    print("boser")
    return render_template('VSearch.html', username=session['username'])

@app.route('/Vmetricspage')
def Vmetricspage():
    return render_template('vendormetrics.html', username=session['username'])

@app.route('/Vmetrics', methods=['GET']) #purchase history
def Vmetrics():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM 'Order'")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)

@app.route('/searchS', methods=['GET']) #the actual search action
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

@app.route('/cancel', methods=['GET','DELETE']) #i think this part aint completely necesary
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

@app.route('/cartpage', methods=['GET']) #purchase history
def cartpage():
    return render_template('Cart.html')

@app.route('/cart', methods=['GET']) #purchase history
def cart():
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    print(search)
    cursor.execute("SELECT * FROM CartItems WHERE CartID=:search", {"search":search})
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)
        
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

@app.route('/item/<int:ItemID>', methods=['GET','POST'])
def item(ItemID):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE ProductID = ?", (ItemID,))# Fetch item details
    item_data = cursor.fetchone()
    conn.close()
    if item_data:
        return render_template('item.html', item=item_data)
    else:
        return "Item not found", 404

@app.route('/add_to_cart/<int:ItemID>/<int:quantity>', methods=['POST'])
def add_to_cart(ItemID,quantity):
    print("boser")
    conn = connect_db()
    cursor = conn.cursor()
    CartID = session['id']
    try:
            cursor.execute("INSERT INTO CartItems (CartID, ProductID, CartQuantity) VALUES (?, ?, ?)", 
             (CartID, ItemID, quantity))
            conn.commit()
            return jsonify({'success': True}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
if __name__ == '__main__':
    app.run(debug=True)
