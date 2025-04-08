from flask import Flask, jsonify, request, session, render_template, url_for, redirect
from datetime import datetime
import json
import sqlite3
import base64
from flask_cors import CORS
from flask import Response
#test

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

DATABASE = "SeniorCapstoneDatabase.db"

app.secret_key = 'your secret key'

@app.route('/')
def home():
    username = session.get('username')
    usertype = session.get('usertype')
    return render_template('search.html', username=username, usertype=usertype)


def connect_db():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn



@app.route('/homepage')
def homepage():
    usertype = session.get('usertype')
    username = session.get('username')
    if usertype == "Buyer":
        return render_template('BuyerMainpage.html', username=username)
    elif usertype == "Vendor":
        return render_template('VendorMainpage.html', username=username)
    else:
        return render_template('Search.html')

@app.route('/get_product_image/<int:product_id>')
def get_product_image(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ProdImage FROM Product WHERE ProductID = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row["ProdImage"]:
        return Response(row["ProdImage"], mimetype='image/jpeg')
    else:
        return '', 404  # Image not found


@app.route('/contactus', methods=['GET','POST']) #For help desk and test labled index
def contactus():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()
        name = request.form.get('name')
        email = request.form.get('email')
        desc= request.form.get('desc')
        try:
            cursor.execute("INSERT INTO HelpDesk (Name, Email, Description) VALUES (?, ?, ?)", (name, email, desc))
            conn.commit()
            conn.close()
            return jsonify({'success': 'Ticket added successfully'}), 201
        except sqlite3.Error as e:
            return jsonify({'error': str(e)}), 500
    else:
        return render_template('contactform.html')
@app.route('/search_category')
def search_category():
    category = request.args.get('category')
    search = request.args.get('search', '')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE ProdCategory = ? AND ProdName LIKE ?", (category, f"%{search}%"))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)


@app.route('/login', methods=['GET', 'POST'])  # login form
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        conn = connect_db()
        cursor = conn.cursor()
        accountType = request.form['accountType']
        username = request.form['username']
        password = request.form['password']

        if accountType == "Buyer":
            cursor.execute("SELECT * FROM Buyer WHERE BuyerEmail = ? AND BuyerPasscode = ?", (username, password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['BuyerID']
                session['usertype'] = 'Buyer'
                session['username'] = account['BuyerName']
                return redirect(url_for('Bhomepage'))
            else:
                return render_template('login.html', error="Incorrect username/password!")

        else:
            cursor.execute("SELECT * FROM Supplier WHERE SupplierEmail = ? AND SupplierPasscode = ?", (username, password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['SupplierID']
                session['usertype'] = 'Vendor'
                session['username'] = account['SupplierName']
                return redirect(url_for('Vhomepage'))
            else:
                return render_template('login.html', error="Incorrect Username/Password")
    else:
        return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear() #clears sessions data
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        account_type = request.form.get('accountType')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        phone = request.form.get('phone')

        # Basic validation
        if len(username) < 3:
            return render_template('signup.html', error="Username must be at least 3 characters long.")

        if len(password) < 3:
            return render_template('signup.html', error="Password must be at least 3 characters long.")

        if not (email.count("@") == 1 and ".com" in email):
            return render_template('signup.html', error="Invalid email format. Must contain '@' and '.com'.")

        if not phone.isdigit():
            return render_template('signup.html', error="Phone number must contain only digits.")

        conn = connect_db()
        cursor = conn.cursor()

        # Check if the email is already in use for both buyers and suppliers
        cursor.execute("SELECT * FROM Buyer WHERE BuyerEmail = ?", (email,))
        buyer_account = cursor.fetchone()

        cursor.execute("SELECT * FROM Supplier WHERE SupplierEmail = ?", (email,))
        supplier_account = cursor.fetchone()

        if buyer_account or supplier_account:
            return render_template('signup.html', error="Email already in use. Please choose another.")

        try:
            if account_type == "Buyer":
                cursor.execute("""
                    INSERT INTO Buyer (BuyerName, BuyerEmail, BuyerPasscode, BuyerAddress, BuyerPhone)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, password, address, phone))
            else:
                cursor.execute("""
                    INSERT INTO Supplier (SupplierName, SupplierEmail, SupplierPasscode, SupplierAddress, SupplierPhone)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, password, address, phone))

            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            conn.close()
            return render_template('signup.html', error=f"Database error: {str(e)}")
    return render_template('signup.html')

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

@app.route('/BuyerOrders')
def BuyerOrders():
    return render_template('BuyerOrder.html', username=session['username'])

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
        return render_template('BuyerOrder.html')
    
@app.route('/VendorOrders')
def VendorOrders():
    return render_template('VendorOrder.html', username=session['username'])
    
@app.route('/Vhistory', methods=['GET'])
def Vhistory():
    conn = connect_db()
    cursor = conn.cursor()
    SupplierID = session['id']
    cursor.execute("""
        SELECT 
            OI.OrderItemID,
            OI.OrderID,
            B.BuyerName,
            P.ProdName,
            OI.DateStart,
            OI.DateEnd,
            OI.Quantity,
            OI.Subtotal,
            OI.Status
        FROM OrderIWS OI
        JOIN Buyer B ON OI.BuyerID = B.BuyerID
        JOIN Product P ON OI.ProductID = P.ProductID
        WHERE OI.SupplierID = ?
    """, (SupplierID,))
    rows = cursor.fetchall()
    data = []
    for row in rows:
        row = dict(row)
        if row["DateEnd"] in (None, "null"):
            row["DateEnd"] = "N/A"
        data.append(row)
    conn.close()
    return jsonify(data)


@app.route('/vendor_cancel/<int:OrderItemID>', methods=['POST'])
def vendor_cancel(OrderItemID):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ProductID, Quantity FROM OrderItems WHERE OrderItemID = ?", (OrderItemID,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'OrderItem not found'}), 404
        ProductID = row["ProductID"]
        Quantity = row["Quantity"]
        cursor.execute("""
            UPDATE OrderItems
            SET Status = 'Vendor Cancelled',
                DateEnd = CURRENT_DATE
            WHERE OrderItemID = ?
        """, (OrderItemID,))
        cursor.execute("""
            UPDATE Product
            SET ProdQuantity = ProdQuantity + ?
            WHERE ProductID = ?
        """, (Quantity, ProductID))
        conn.commit()
        return jsonify({'success': True}), 200
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/vendor_approve/<int:OrderItemID>', methods=['POST'])
def vendor_approve(OrderItemID):
        conn = connect_db()
        cursor = conn.cursor()
        if (OrderItemID == 0):
            try:
                cursor.execute("""UPDATE OrderItems SET Status = 'Processing'
                WHERE ProductID IN (
                    SELECT ProductID FROM Product WHERE SupplierID = ?
                ) AND Status = 'Pending'""", (session['id'],))
                conn.commit()
                return jsonify({'success': True}), 200
            except sqlite3.Error as e:
                return jsonify({'error': str(e)}), 500
        else:  
            try:
                cursor.execute("""UPDATE OrderItems SET Status = 'Processing'
                WHERE OrderItemID=? AND Status = 'Pending'""", (OrderItemID,))
                conn.commit()
                return jsonify({'success': True}), 200
            except sqlite3.Error as e:
                return jsonify({'error': str(e)}), 500
            finally:
                conn.close()           
        
@app.route('/pcbuilder')
def pcbuilder():
    return render_template('pcbuilder.html')

@app.route('/helpvideos')
def helpvideos():
    return render_template('helpvideos.html')
            
@app.route('/VendorAdd', methods=['GET', 'POST'])
def VendorAdd():
    if request.method == 'POST':
    
        conn = connect_db()
        cursor = conn.cursor()
        supplier = session['id']
        name = request.form.get('name')
        price = float(request.form.get('price'))
        quant = int(request.form.get('quantity'))
        category = request.form.get('category')  # New category field
        desc = request.form.get('description')
        image = request.files.get('file')
        shipping_ids = request.form.getlist('shipping')  # This gives a list of selected IDs
        if image and image.filename != '':
            image_data = image.read()
        else:
            image_data = None
        print("POST data:", request.form)
        print("Files:", request.files)
        print("Session:", session)
        try:
            cursor.execute("""
                INSERT INTO Product (SupplierID, ProdName, ProdPrice, ProdQuantity, ProdDesc, ProdImage, ProdCategory) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (supplier, name, price, quant, desc, image_data, category))
            print("boser2")
            product_id = cursor.lastrowid  # After inserting into Product
            for ship_id in shipping_ids:
                cursor.execute("INSERT INTO ProductShipping (ProductID, ShippingID) VALUES (?, ?)", (product_id, ship_id))
            conn.commit()
            conn.close()
            return redirect(url_for('Vhomepage'))
        except sqlite3.Error as e:
            print("DB error:", e)  # <--- Add this
            conn.close()
            return render_template('VendorAdd.html', error=str(e), username=session.get('username'))
    else:
        return render_template('VendorAdd.html', username=session['username'])

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


@app.route('/VendorEditProd/<int:product_id>', methods=['GET', 'POST'])
def VendorEditProd(product_id):
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
        return render_template('VendorEditProd.html', product=product)
    else:
        return "Product not found", 404
    

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Product WHERE ProductID = ?", (product_id,))
        cursor.execute("DELETE FROM ProductShipping WHERE ProductID = ?", (product_id,))
        conn.commit()
        return redirect(url_for('Vhomepage'))
    except sqlite3.Error as e:
        return f"Error deleting product: {e}", 500
    finally:
        conn.close()



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


@app.route('/search')
def search():
    return render_template('Search.html', username=session.get('username'), usertype=session.get('usertype'))

    
@app.route('/Vsearch') #used for search page for vendors   
def Vsearch():
    #print("boser")
    return render_template('VSearch.html', username=session['username'])

@app.route('/searchS', methods=['GET'])
def searchS():
    conn = connect_db()
    cursor = conn.cursor()
    search = request.args.get('search')
    cursor.execute("SELECT * FROM Product WHERE ProdName LIKE ? OR ProdCategory LIKE ?", (f"%{search}%",search))
    rows = cursor.fetchall()
    data = []

    for row in rows:
        product = dict(row)
        # 👇 Remove the image data to avoid JSON errors
        if "ProdImage" in product:
            del product["ProdImage"]
        data.append(product)

    conn.close()
    return jsonify(data)

            
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
        
@app.route('/filterp', methods=['GET'])
def filter():
    conn = connect_db()
    cursor = conn.cursor()
    minval = request.args.get('minval', type=int)
    maxval = request.args.get('maxval', type=int)
    search = request.args.get('search')
    cursor.execute("SELECT * FROM Product WHERE ProdPrice >=? AND ProdPrice <=? AND ProdName LIKE ?", 
                   (minval, maxval, f"%{search}%"))
    rows = cursor.fetchall()
    data = []

    for row in rows:
        product = dict(row)
        if "ProdImage" in product:
            del product["ProdImage"]
        data.append(product)

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
        return render_template('BuyerOrder.html', username=session['username'])
        
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
    cursor.execute("SELECT COUNT(*) FROM Reviews WHERE ProductID = ?", (ItemID,))# Fetch item details
    num_reviews = cursor.fetchone()[0]
    conn.close()
    if item_data:
        return render_template('item.html', item=item_data, review=num_reviews)
    else:
        return "Item not found", 404

@app.route('/get_reviews/<int:ItemID>', methods=['GET', 'POST'])
def get_reviews(ItemID):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Buyer.BuyerName, Reviews.RevRating, Reviews.RevDesc, Reviews.BuyerID, Reviews.RevDate
            FROM Reviews 
            INNER JOIN Buyer ON Reviews.BuyerID = Buyer.BuyerID 
            WHERE ProductID = ?
        """, (ItemID,))
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        return jsonify(data)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/post_review/<int:ItemID>', methods=['GET', 'POST'])
def post_review(ItemID):
    conn = connect_db()
    cursor = conn.cursor()
    BuyerID = session['id']
    Rating = int(request.form.get('rate') or 0)
    print(Rating)
    RevDesc = request.form.get('RevDesc')
    print(RevDesc)
    try:
        cursor.execute("DELETE FROM Reviews WHERE BuyerID=?", (BuyerID,))
        cursor.execute("""
            INSERT INTO Reviews (BuyerID, ProductID, RevRating, RevDesc) 
                VALUES (?, ?, ?, ?)
        """, (BuyerID,ItemID,Rating,RevDesc))
        conn.commit()
        return jsonify({'success': 'Post Submitted'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/add_to_cart/<int:ItemID>/<int:quantity>', methods=['POST'])
def add_to_cart(ItemID,quantity):
    if 'loggedin' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    if (session['usertype'] != "Buyer"):
        return jsonify({'error': 'Vendors cant buy'}), 401    
    print("boser")
    conn = connect_db()
    cursor = conn.cursor()
    CartID = session['id']
    try:
        # Check if the item is already in the cart
        cursor.execute("SELECT * FROM CartItems WHERE CartID = ? AND ProductID = ?", (CartID, ItemID))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update quantity if the item is already in the cart
            cursor.execute("UPDATE CartItems SET CartQuantity = CartQuantity + ? WHERE CartID = ? AND ProductID = ?",
                           (quantity, CartID, ItemID))
        else:
            # Insert new item to cart
            cursor.execute("INSERT INTO CartItems (CartID, ProductID, CartQuantity) VALUES (?, ?, ?)", 
             (CartID, ItemID, quantity))
        conn.commit()
        return jsonify({'success': True}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
@app.route('/cartpage', methods=['GET']) #cart
def cartpage():
    return render_template('Cart.html')

@app.route('/cart', methods=['GET'])
def cart():
    if 'id' not in session:
        print("No session ID found")
        return jsonify({'error': 'Not logged in'}), 403
    
    conn = connect_db()
    cursor = conn.cursor()
    BuyerID = session['id']
    print("boser1")
    try:
        cursor.execute("""
            SELECT Product.ProductID, ProdName, ProdPrice, ProdQuantity, CartQuantity, 
                   Shipping.ShippingID, Shipping.ShippingName, Shipping.Cost, Shipping.ShipDays
            FROM CartItems 
            INNER JOIN Product ON CartItems.ProductID = Product.ProductID
            INNER JOIN ProductShipping ON Product.ProductID = ProductShipping.ProductID
            INNER JOIN Shipping ON ProductShipping.ShippingID = Shipping.ShippingID
            WHERE CartID = :BuyerID
        """, {"BuyerID": BuyerID})
        
        rows = cursor.fetchall()
        grouped = {}
        data = []  # Initialize data list here
        print("boser2")
        for row in rows:
            item = dict(row)
            pid = item["ProductID"]

            if pid not in grouped:
                grouped[pid] = {
                    "ProductID": pid,
                    "ProdName": item["ProdName"],
                    "ProdPrice": item["ProdPrice"],
                    "ProdQuantity": item["ProdQuantity"],
                    "CartQuantity": item["CartQuantity"],
                    "ShippingOptions": []
                }

            grouped[pid]["ShippingOptions"].append({
                "ShippingID": item["ShippingID"],
                "ShippingName": item["ShippingName"],
                "Cost": item["Cost"],
                "ShipDays": item["ShipDays"]
            })

        return jsonify(list(grouped.values()))
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()




@app.route('/update_cart/<int:ItemID>/<int:quantity>', methods=['POST']) #cart
def update_cart(ItemID, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    CartID = session['id']
    try:
        cursor.execute("UPDATE CartItems SET CartQuantity = ? WHERE CartID = ? AND ProductID = ?",
                           (quantity, CartID, ItemID))
        conn.commit()
        return jsonify({'success': True}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
    
@app.route('/remove_from_cart/<int:ItemID>', methods=['DELETE']) #cart
def remove_from_cart(ItemID):
    conn = connect_db()
    cursor = conn.cursor()
    CartID = session['id']
    try:
        cursor.execute("DELETE FROM CartItems WHERE CartID = ? AND ProductID = ?", (CartID, ItemID))
        conn.commit()
        return jsonify({'success': True}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
    
@app.route('/checkout', methods=['GET'])
def checkoutpage():
    return render_template('Checkout.html')
    
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if request.method == 'POST':
        print("boser1")
        conn = connect_db()
        cursor = conn.cursor()
        ID = session['id']
        #print(ID)
        now = datetime.today().strftime('%Y-%m-%d')
        #print(now)
        grandTotal = request.form.get('grandTotal')
        #print(grandTotal)
        PaymentType = request.form.get('Payment')
        street1 = request.form.get('Street1') or ''
        #print(street1)
        street2 = request.form.get('Street2') or ''
        #print(street2)
        city = request.form.get('City') or ''
        #print(city)
        state = str(request.form.get('State')) or ''
        #print(state)
        ZIP = request.form.get('ZIP') or ''
        #print(ZIP)
        Address = street1 + street2 + "\n" + city + "\n" + state + "\n" + ZIP
        #print(Address)
        shipping_json = request.form.get('shippingSelections')
        shipping_map = json.loads(shipping_json) if shipping_json else {}
        #print("RAW shippingSelections:", shipping_json)
        try:
            shipping_map = json.loads(shipping_json) if shipping_json else {}
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return jsonify({'error': 'Invalid shippingSelections JSON'}), 400
        try:
            #print("boser2")
            cursor.execute("INSERT INTO 'Order' (BuyerID, DateStart, Status, Amount, Address, PayMethod) VALUES (?, ?, ?, ?, ?, ?)", (ID, now, "Active", grandTotal, Address, PaymentType))
            #print("boser3")
            OrderID = cursor.lastrowid
            #print(OrderID)
            cursor.execute("SELECT * FROM CartItems INNER JOIN Product ON CartItems.ProductID = Product.ProductID WHERE CartID=:ID", {"ID":ID})
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            for item in data:
                ProductID = item["ProductID"]
                Quantity = item["CartQuantity"]
                Price = item["ProdPrice"]
                Subtotal = Quantity * Price
                ShippingID = int(shipping_map.get(str(ProductID), 0))
                #print(ShippingID)
                cursor.execute("INSERT INTO OrderItems (OrderID, ProductID, Quantity, Subtotal, ShipOption) VALUES (?,?,?,?,?)", (OrderID, ProductID, Quantity, Subtotal, ShippingID))
                cursor.execute("UPDATE Product SET ProdQuantity = ProdQuantity - ? WHERE ProductID = ?",(Quantity, ProductID))
            cursor.execute("DELETE FROM CartItems WHERE CartID = ?", (ID,))
            conn.commit()
            return jsonify({'success': True}), 201
        except sqlite3.Error as e:
            print("DB Error:", e)  # helpful in dev logs
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
