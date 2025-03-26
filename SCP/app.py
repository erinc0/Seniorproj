from flask import Flask, jsonify, request, session, render_template, url_for, redirect
import sqlite3
from flask_cors import CORS
import base64  # Required for encoding/decoding images
import os
from werkzeug.utils import secure_filename

from flask import send_file
import io

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

DATABASE = "SeniorCapstoneDatabase.db"

app.secret_key = 'your secret key'

@app.route('/')
def home():
    return render_template('Homepage.html')

@app.route('/get_product_image/<int:product_id>')
def get_product_image(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ProdImage FROM Product WHERE ProductID=?", (product_id,))
    image_data = cursor.fetchone()
    conn.close()
    
    if image_data and image_data["ProdImage"]:
        return send_file(io.BytesIO(image_data["ProdImage"]), mimetype='image/jpeg')

    return "", 404  # Return a 404 error if no image is found

def connect_db():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

@app.route('/VendorEdit')
def VendorEdit():
    return render_template('VendorEdit.html')

@app.route('/vendor_products', methods=['GET'])
def vendor_products():
    search = request.args.get('search', '')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE SupplierID=? AND ProdName LIKE ?", (session['id'], f"%{search}%"))
    rows = cursor.fetchall()
    
    data = []
    for row in rows:
        product = dict(row)
        if product["ProdImage"]:
            product["ProdImage"] = base64.b64encode(product["ProdImage"]).decode('utf-8')  # Convert to Base64
        data.append(product)
    
    conn.close()
    return jsonify(data)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        description = request.form.get('description')
        image_file = request.files.get('image')

        if image_file:
            image_data = image_file.read()
            cursor.execute("""
                UPDATE Product SET ProdName=?, ProdPrice=?, ProdQuantity=?, ProdDesc=?, ProdImage=?
                WHERE ProductID=?
            """, (name, price, quantity, description, image_data, product_id))
        else:
            cursor.execute("""
                UPDATE Product SET ProdName=?, ProdPrice=?, ProdQuantity=?, ProdDesc=?
                WHERE ProductID=?
            """, (name, price, quantity, description, product_id))

        conn.commit()
        conn.close()
        return redirect(url_for('VendorEdit'))

    cursor.execute("SELECT * FROM Product WHERE ProductID=?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        return render_template('edit_product.html', product=product)
    else:
        return "Product not found", 404


@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    description = request.form.get('description')
    image = request.files.get('image')
    image_data = image.read() if image else None

    try:
        if image_data:
            cursor.execute("""
                UPDATE Product 
                SET ProdName = ?, ProdPrice = ?, ProdQuantity = ?, ProdDesc = ?, ProdImage = ? 
                WHERE ProductID = ?
            """, (name, price, quantity, description, image_data, product_id))
        else:
            cursor.execute("""
                UPDATE Product 
                SET ProdName = ?, ProdPrice = ?, ProdQuantity = ?, ProdDesc = ?
                WHERE ProductID = ?
            """, (name, price, quantity, description, product_id))

        conn.commit()
        return redirect(url_for('Vhomepage'))
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


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
            
@app.route('/VendorAdd', methods=['GET', 'POST']) 
def VendorAdd():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()            

        supplier = session['id']
        name = request.form.get('name')
        price = request.form.get('price')
        quant = request.form.get('quantity')
        desc = request.form.get('description')

        # Handle Image Upload
        image_file = request.files.get('image')  # Get the file
        image_data = None
        if image_file:
            image_data = image_file.read()  # Read file as BLOB

        try:
            cursor.execute("""
                INSERT INTO Product (SupplierID, ProdName, ProdPrice, ProdQuantity, ProdDesc, ProdImage) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (supplier, name, price, quant, desc, image_data))

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

@app.route('/searchS', methods=['GET']) 
def searchS():
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor.execute("SELECT * FROM Product WHERE ProdName LIKE ?", (f"%{search}%",))
    rows = cursor.fetchall()
    
    # Convert results to JSON with Base64 image encoding
    data = []
    for row in rows:
        product = dict(row)
        if product["ProdImage"]:
            product["ProdImage"] = base64.b64encode(product["ProdImage"]).decode('utf-8')
        data.append(product)

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

@app.route('/item/<int:ItemID>', methods=['GET'])
def item(ItemID):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE ProductID = ?", (ItemID,))
    item_data = cursor.fetchone()
    conn.close()

    if item_data:
        # Convert image BLOB to Base64
        item_dict = dict(item_data)
        if item_data["ProdImage"]:
            item_dict["ProdImage"] = base64.b64encode(item_data["ProdImage"]).decode('utf-8')
        return render_template('item.html', item=item_dict)
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
