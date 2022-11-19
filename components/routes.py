from components import app, conn, bcrypt, db2
from flask import render_template, flash, request, url_for, redirect, session
import ibm_db
from components.form import Item
import datetime
import pytz


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home_page():
    return render_template('home.html')


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['user_password']

        query = "SELECT * FROM JBG49873.USER WHERE USER.USERNAME = ? LIMIT 1";
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, user_name)
        ibm_db.execute(prep_stmt)
        result_dict = ibm_db.fetch_assoc(prep_stmt)
        if result_dict and bcrypt.check_password_hash(result_dict['PASSWORD'], password):
            session['loggedin'] = True
            session['id'] = result_dict['USER_ID']
            session['username'] = result_dict['USERNAME']
            flash(f'Log into the account successfully!!', category='success')
            return redirect(url_for('dashboard_page'))
        else:
            flash(f'Username and/or password are incorrect to login!',
                  category='danger')
            return redirect(url_for('home_page'))

    return render_template('home.html')


@app.route("/", methods=['GET', 'POST'])
def register_page():
    error_msg = []
    msg = ''
    if request.method == 'POST':
        first_name = request.form['fname']
        last_name = request.form['lname']
        user_name = request.form['uname']
        email_id = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['Address']
        city = request.form['City']
        state = request.form['State']
        pincode = request.form['pincode']

        # check username exist
        query = "SELECT COUNT(USERNAME) AS IS_PRESENT FROM JBG49873.USER WHERE USER.USERNAME = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, user_name)
        ibm_db.execute(prep_stmt)
        result_dict = ibm_db.fetch_assoc(prep_stmt)
        if result_dict['IS_PRESENT'] >= 1:
            error_msg.append("username already exist. try other username!")

        # check emailid exist
        query = "SELECT COUNT(USERNAME) AS IS_PRESENT FROM JBG49873.USER WHERE USER.EMAIL_ID = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, email_id)
        ibm_db.execute(prep_stmt)
        result_dict = ibm_db.fetch_assoc(prep_stmt)
        if result_dict['IS_PRESENT'] >= 1:
            error_msg.append("email id already exist.try other emailid!")

        # check password and confirm password are equal
        if password != confirm_password:
            error_msg.append("password and confirm password are not same")

        if len(error_msg) > 0:
            for i in error_msg:
                flash(f'There was an error with creating a user: {i}',
                      category='danger')
            return redirect(url_for('home_page'))

        else:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            query = "INSERT INTO JBG49873.USER(" \
                    "FIRST_NAME,LAST_NAME,USERNAME,EMAIL_ID,PASSWORD" \
                    ") VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, first_name)
            ibm_db.bind_param(prep_stmt, 2, last_name)
            ibm_db.bind_param(prep_stmt, 3, user_name)
            ibm_db.bind_param(prep_stmt, 4, email_id)
            ibm_db.bind_param(prep_stmt, 5, password_hash)
            ibm_db.execute(prep_stmt)

            query = "INSERT INTO JBG49873.LOCATION(USER_NAME,ADDRESS,CITY,STATE,PINCODE) VALUES(?,?,?,?,?) ;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, user_name)
            ibm_db.bind_param(prep_stmt, 2, address)
            ibm_db.bind_param(prep_stmt, 3, city)
            ibm_db.bind_param(prep_stmt, 4, state)
            ibm_db.bind_param(prep_stmt, 5, pincode)
            ibm_db.execute(prep_stmt)

            flash(f'Account created successfully!!',
                  category='success')
            return redirect(url_for('login_page'))


@app.route('/dashboard')
def dashboard_page():
    if 'id' in session:
        query = "SELECT * FROM JBG49873.ITEM WHERE USER_NAME != ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, session['username'])
        ibm_db.execute(prep_stmt)
        item = ibm_db.fetch_assoc(prep_stmt)
        items = []

        while (item):
            items.append(item)
            item = ibm_db.fetch_assoc(prep_stmt)

        return render_template('dashboard.html', items=items)
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/inventory/update', methods=['POST'])
def update_item_inventory_page():
    if 'id' in session:
        try:
            item_name = request.form['item_name']
            totalStock = request.form['totalStock']
            query = "UPDATE JBG49873.ITEM SET TOTAL_STOCK=?  WHERE ITEM.ITEM_NAME = ? AND ITEM.USER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, totalStock)
            ibm_db.bind_param(prep_stmt, 2, item_name)
            ibm_db.bind_param(prep_stmt, 3, session['username'])
            ibm_db.execute(prep_stmt)
            flash(f'Item updated successfully!!',
                  category='success')
        except:
            print(ibm_db.conn_errormsg(), "\n\n")
            flash(f'Failure to update an item!!',
                  category='danger')
        return redirect(url_for('inventory_page'))
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/inventory/delete/<item_name>')
def delete_item_inventory_page(item_name):
    if 'id' in session:
        try:
            query = "DELETE FROM JBG49873.ITEM WHERE ITEM.ITEM_NAME = ? AND ITEM.USER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, item_name)
            ibm_db.bind_param(prep_stmt, 2, session['username'])
            ibm_db.execute(prep_stmt)
            flash(f'Item deleted successfully!!',
                  category='success')
        except:
            print(ibm_db.conn_errormsg(), "\n\n")
            flash(f'Failure to delete an item!!',
                  category='danger')
        return redirect(url_for('inventory_page'))
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/inventory', methods=['GET', 'POST'])
def inventory_page():
    global variable
    if 'id' in session:
        itemForm = Item()
        username = session['username']
        if request.method == 'POST':
            item_name = itemForm.Item_name.data
            item_description = itemForm.Description.data
            avail = itemForm.Available.data
            totalStock = itemForm.TotalStock.data
            cps = itemForm.CostPerItem.data
            error_msg = []
            # checking product exits
            query = "SELECT COUNT(ITEM_NAME) AS IS_PRESENT FROM JBG49873.ITEM WHERE ITEM.ITEM_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, item_name)
            ibm_db.execute(prep_stmt)
            result_dict = ibm_db.fetch_assoc(prep_stmt)
            if result_dict['IS_PRESENT'] >= 1:
                error_msg.append("item name already exist.try other emailid!")

            if len(error_msg) > 0:
                for i in error_msg:
                    flash(f'Cant create a product: {i}',
                          category='danger')

            else:
                query = "INSERT INTO JBG49873.ITEM( ITEM_NAME,DESCRIPTION,AVAILABLE,TOTAL_STOCK,COST_PER_ITEM,USER_NAME) VALUES (?,?,?,?,?,?);"
                prep_stmt = ibm_db.prepare(conn, query)
                ibm_db.bind_param(prep_stmt, 1, item_name)
                ibm_db.bind_param(prep_stmt, 2, item_description)
                ibm_db.bind_param(prep_stmt, 3, avail)
                ibm_db.bind_param(prep_stmt, 4, totalStock)
                ibm_db.bind_param(prep_stmt, 5, cps)
                ibm_db.bind_param(prep_stmt, 6, username)

                ibm_db.execute(prep_stmt)
                flash(f'Item created successfully!!',
                      category='success')

        query = "SELECT * FROM JBG49873.ITEM WHERE ITEM.USER_NAME = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.execute(prep_stmt)
        item = ibm_db.fetch_assoc(prep_stmt)
        items = []

        while (item):
            items.append(item)
            item = ibm_db.fetch_assoc(prep_stmt)

        return render_template('inventory.html', form=itemForm, items=items)
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/logs', methods=['GET', 'POST'])
def logs_page():
    if 'id' in session:
        query = "SELECT * FROM LOG WHERE SUPPLIER_NAME = ? and STATUS =  'Request';"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, session['username'])
        ibm_db.execute(prep_stmt)
        item = ibm_db.fetch_assoc(prep_stmt)
        items = []

        while (item):
            items.append(item)
            item = ibm_db.fetch_assoc(prep_stmt)

        totalCost = []
        address = []

        for item in items:
            query = "SELECT COST_PER_ITEM FROM ITEM WHERE ITEM_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, item['ITEM_NAME'])
            ibm_db.execute(prep_stmt)
            res = ibm_db.fetch_assoc(prep_stmt)
            cost = item['QUANTITY'] * int(res['COST_PER_ITEM'])
            totalCost.append(cost)

            query = "SELECT * FROM LOCATION WHERE USER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, session['username'])
            # ibm_db.bind_param(prep_stmt, 2, 'Request')
            ibm_db.execute(prep_stmt)
            res = ibm_db.fetch_assoc(prep_stmt)
            s = res['ADDRESS'] + ' , ' + res['CITY'] + ' , ' + res['STATE'] + ' , ' + res['COUNTRY'] + ' , ' + res[
                'PINCODE']
            address.append(s)

        print(totalCost)
        return render_template('logs.html', res=items, totalCost=totalCost, length=len(items), location=address)
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/logs/approve/<timestamp>/<receiver_name>/<item_name>', methods=['GET', 'POST'])
def logs_approval_page(timestamp, receiver_name, item_name):
    if 'id' in session:
        try:
            # update quantity in item table
            query = "SELECT TOTAL_STOCK FROM JBG49873.ITEM WHERE ITEM.ITEM_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, item_name)
            ibm_db.execute(prep_stmt)
            res = ibm_db.fetch_assoc(prep_stmt)
            total_qnty = int(res['TOTAL_STOCK'])

            query = "SELECT QUANTITY FROM JBG49873.LOG WHERE TIMESTAMP = ? AND RECEIVER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, timestamp)
            ibm_db.bind_param(prep_stmt, 2, receiver_name)
            ibm_db.execute(prep_stmt)
            res = ibm_db.fetch_assoc(prep_stmt)
            qnty = int(res['QUANTITY'])

            total_qnty = total_qnty - qnty

            query = "UPDATE JBG49873.ITEM SET TOTAL_STOCK=?  WHERE ITEM.ITEM_NAME = ?;;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, total_qnty)
            ibm_db.bind_param(prep_stmt, 2, item_name)
            ibm_db.execute(prep_stmt)

            query = "UPDATE JBG49873.LOG SET STATUS='Approved'  WHERE TIMESTAMP = ? AND RECEIVER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, timestamp)
            ibm_db.bind_param(prep_stmt, 2, receiver_name)
            ibm_db.execute(prep_stmt)

            flash(f'updated successfuly!!',
                  category='success')
            return redirect(url_for('logs_page'))
        except:
            print(ibm_db.stmt_error(), "\n\n")
            print("Error {}".format(ibm_db.stmt_errormsg()))
            flash(f'Fail to update!!',
                  category='danger')
            return redirect(url_for('logs_page'))
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/logs/denied/<timestamp>/<receiver_name>', methods=['GET', 'POST'])
def logs_denied_page(timestamp, receiver_name):
    if 'id' in session:
        query = "UPDATE JBG49873.lOG SET STATUS='Approved'  WHERE TIMESTAMP = ? AND RECEIVER_NAME = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, timestamp)
        ibm_db.bind_param(prep_stmt, 2, receiver_name)
        ibm_db.execute(prep_stmt)
        flash(f'updated successfuly!!',
              category='success')
        return redirect(url_for('logs_page'))
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/track', methods=['GET', 'POST'])
def track_page():
    if 'id' in session:
        query = "SELECT * FROM LOG WHERE RECEIVER_NAME = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, session['username'])
        ibm_db.execute(prep_stmt)
        item = ibm_db.fetch_assoc(prep_stmt)
        items = []

        while (item):
            items.append(item)
            item = ibm_db.fetch_assoc(prep_stmt)

        totalCost = []
        address = []
        sorted(items, key=lambda i: i['TIMESTAMP'])

        for item in items:
            query = "SELECT * FROM LOCATION WHERE USER_NAME = ?;"
            prep_stmt = ibm_db.prepare(conn, query)
            ibm_db.bind_param(prep_stmt, 1, session['username'])
            ibm_db.execute(prep_stmt)
            res = ibm_db.fetch_assoc(prep_stmt)
            s = res['ADDRESS'] + ' , ' + res['CITY'] + ' , ' + res['STATE'] + ' , ' + res['COUNTRY'] + ' , ' + res[
                'PINCODE']
            address.append(s)

        print(totalCost)
        return render_template('track.html', res=items, totalCost=totalCost, length=len(items), location=address)
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/track/personal', methods=['GET', 'POST'])
def track_personal_page():
    if 'id' in session:
        return render_template('personal.html')
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/track/product', methods=['GET', 'POST'])
def track_product_page():
    if 'id' in session:
        return render_template('track_product.html')
    else:
        flash(f'Cant see this page without login!!',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/logout')
def logout_page():
    if 'id' in session:
        session.pop('id', None)
        session.pop('username', None)
        flash("You have been logged out!", category='success')
        return redirect(url_for('home_page'))
    else:
        flash(f'You are already logged out',
              category='danger')
        return redirect(url_for('home_page'))


@app.route('/request/<item_name>', methods=['GET', 'POST'])
def request_page(item_name):
    if 'id' in session:
        quantity = int(request.form['quantity'])

        # check quantity
        query = "SELECT TOTAL_STOCK,USER_NAME FROM JBG49873.ITEM WHERE ITEM.ITEM_NAME = ?;"
        prep_stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(prep_stmt, 1, item_name)
        ibm_db.execute(prep_stmt)
        res = ibm_db.fetch_assoc(prep_stmt)
        total_qnty = res['TOTAL_STOCK']
        if int(total_qnty) >= quantity:
            #   put into logs table
            current_time = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
            receiver_name = session['username']
            supplier_name = res['USER_NAME']
            status = "Request"
            try:
                query = "INSERT INTO JBG49873.LOG(TIMESTAMP,ITEM_NAME,RECEIVER_NAME,SUPPLIER_NAME, QUANTITY, STATUS) VALUES (?,?,?,?,?,?);"
                prep_stmt = ibm_db.prepare(conn, query)
                ibm_db.bind_param(prep_stmt, 1, current_time)
                ibm_db.bind_param(prep_stmt, 2, item_name)
                ibm_db.bind_param(prep_stmt, 3, receiver_name)
                ibm_db.bind_param(prep_stmt, 4, supplier_name)
                ibm_db.bind_param(prep_stmt, 5, quantity)
                ibm_db.bind_param(prep_stmt, 6, status)
                ibm_db.execute(prep_stmt)
                flash("Your product request successfully!!", category='success')
                return redirect(url_for('dashboard_page'))
            except:
                print(ibm_db.stmt_error(), "\n\n")
                print("Error {}".format(ibm_db.stmt_errormsg()))

                flash(f'Failure to request an item!!',
                      category='danger')
                return redirect(url_for('dashboard_page'))
        else:
            flash("No stock available", category='danger')
            return redirect(url_for('dashboard_page'))
    else:
        flash(f'Cant logged into this page',
              category='danger')
        return redirect(url_for('home_page'))
