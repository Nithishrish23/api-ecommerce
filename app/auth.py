from flask import request, jsonify, session, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_connection, verify_user, verify_admin_user
import time
import os
from markupsafe import escape
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor
from app.authTokens import generate_token, validate_token
import json

SESSION_TIMEOUT = 5 * 60
WARNING_TIME = 2 * 60


def register():
    data = request.json
    name = data.get('fullname', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM seller_users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "User already exists"}), 400

        cursor.execute("INSERT INTO seller_users (first_name, email, password) VALUES (%s, %s, %s)",
                       (name, email, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    finally:
        conn.close()


def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = data.get('email', '').strip()
    password = data.get('password', '').strip()

    user_id = verify_user(username, password)

    if user_id:
        user_data = {
            'user_id': user_id,
            'email': username,
            'is_admin': False
        }

        token = generate_token(user_data)
        print(token)

        session['token'] = token
        session['user_id'] = user_id
        session.permanent = True

        return jsonify({
            "message": "true",
            "user": user_id,
            "token": token
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


def admin_login():
    if request.method == 'POST' or request.method == 'GET':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        username = data.get('email', '').strip()
        password = data.get('password', '').strip()

        user_id = verify_admin_user(username, password)
        if user_id:
            user_data = {
                'user_id': user_id,
                'email': username,
                'is_admin': True
            }

            token = generate_token(user_data)

            session['token'] = token
            session['user_id'] = user_id
            session.permanent = True

            return jsonify({
                "message": "true",
                "user": user_id,
                "token": token
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


def check_session():
    if 'user_id' in session:
        last_active = session.get('last_active', time.time())
        time_elapsed = time.time() - last_active

        if time_elapsed > SESSION_TIMEOUT:
            session.clear()
            return jsonify({"status": "logged_out", "message": "Session timed out"}), 401
        elif time_elapsed > SESSION_TIMEOUT - WARNING_TIME:

            return jsonify({"status": "warning", "remaining_time": SESSION_TIMEOUT - time_elapsed})
        else:
            session['last_active'] = time.time()
            return jsonify({"status": "active"})

    token = session.get('token')
    if token and validate_token(token):
        return jsonify({
            'session_valid': True,
            'user_id': session.get('user_id')
        }), 200

    return jsonify({'status': 'logged_out', 'message': 'No active session'}), 401


def user(user_id):
    global connection
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, email, first_name,phone_number,profile_path FROM seller_users WHERE id = %s",
                       (user_id,))
        user = cursor.fetchone()

        if user:
            return jsonify({
                "id": user[0],
                "email": user[1],
                "name": user[2],
                "phone_number": user[3],
                "profile_picture": user[4]
            })
        else:
            return jsonify({"error": "User not found"}), 404
    finally:
        if connection:
            connection.close()

def handle_seller_registration():
    conn = get_db_connection()
    cursor = conn.cursor() if conn else None
    try:
        data = request.form.to_dict()
        files = request.files

        token_payload = getattr(request, 'token_payload', None)

        if token_payload:
            userid = token_payload.get('user_id')
        elif session.get('user'):
            userid = session.get('user')
        else:
            userid = escape(data.get('user'))

        cursor.execute("SELECT * FROM Seller_Registation WHERE userid = %s", (userid,))
        existing_user = cursor.fetchone()

        if request.method == 'GET':
            if existing_user:
                user_data = {column.name: existing_user[i] for i, column in enumerate(cursor.description)}
                return jsonify({"message": "User data retrieved", "user_data": user_data}), 200
            return jsonify({"message": "User not found"}), 404

        name = escape(data.get('fullName'))
        dob = escape(data.get('dob'))
        country = escape(data.get('country'))
        state = escape(data.get('state'))
        place = escape(data.get('place'))
        mobile_no = escape(data.get('mobileNo'))
        email = escape(data.get('email'))

        profile = files.get('profilePicture')
        profile_filepath = existing_user[8] if existing_user else None
        if profile and profile.filename:
            filename = secure_filename(profile.filename)
            profile_filepath = os.path.join('./uploads/profile', filename)
            os.makedirs('./uploads/profile', exist_ok=True)
            profile.save(profile_filepath)

        company_name = escape(data.get('companyName'))
        official_mobile_no = escape(data.get('officialMobileNo'))
        official_email = escape(data.get('officialEmail'))

        certificate_upload = files.get('certificateUpload')
        certificate_filepath = existing_user[12] if existing_user else None
        if certificate_upload and certificate_upload.filename:
            filename = secure_filename(certificate_upload.filename)
            certificate_filepath = os.path.join('./uploads/certificate', filename)
            os.makedirs('./uploads/certificate', exist_ok=True)
            certificate_upload.save(certificate_filepath)

        bank_name = escape(data.get('bankName'))
        branch_ifsc_code = escape(data.get('branchIFSCCode'))
        account_holder_name = escape(data.get('accountHolderName'))
        account_number = escape(data.get('accountNumber'))
        swift_bic = escape(data.get('swiftBIC'))
        upi_id = escape(data.get('upiId'))
        paypal = escape(data.get('payPal'))
        payment_terms_accepted = bool(data.get('paymentTermsAccepted'))

        ie_code = escape(data.get('ieCode'))
        ie_certificate = files.get("ieCertificate")
        ie_certificate_filepath = existing_user[22] if existing_user else None
        if ie_certificate and ie_certificate.filename:
            filename = secure_filename(ie_certificate.filename)
            ie_certificate_filepath = os.path.join('./uploads/IEC', filename)
            os.makedirs('./uploads/IEC', exist_ok=True)
            ie_certificate.save(ie_certificate_filepath)

        exporter_terms_accepted = bool(data.get('exporterTermsAccepted'))

        if existing_user:
            update_query = """
                UPDATE Seller_Registation SET
                    name=%s, dob=%s, country=%s, state=%s, place=%s, mobile_no=%s, email=%s,
                    profile_picture_path=%s, company_name=%s, official_mobile_no=%s, official_email=%s,
                    certificate_path=%s, bank_name=%s, branch_ifsc_code=%s,
                    account_holder_name=%s, account_number=%s, swift_bic=%s, upi_id=%s, paypal_email=%s,
                    payment_terms_accepted=%s, ie_code=%s, ie_certificate_path=%s, exporter_terms_accepted=%s
                WHERE userid=%s
            """
            cursor.execute(update_query, (
                name, dob, country, state, place, mobile_no, email,
                profile_filepath, company_name, official_mobile_no, official_email,
                certificate_filepath, bank_name, branch_ifsc_code,
                account_holder_name, account_number, swift_bic, upi_id, paypal,
                payment_terms_accepted, ie_code, ie_certificate_filepath, exporter_terms_accepted,
                userid
            ))
            conn.commit()
            return jsonify({"message": "Seller information updated successfully"}), 200

        insert_query = """
            INSERT INTO Seller_Registation (
                userid, name, dob, country, state, place, mobile_no, email,
                profile_picture_path, company_name, official_mobile_no, official_email,
                certificate_path, bank_name, branch_ifsc_code,
                account_holder_name, account_number, swift_bic, upi_id, paypal_email,
                payment_terms_accepted, ie_code, ie_certificate_path, exporter_terms_accepted
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_query, (
            userid, name, dob, country, state, place, mobile_no, email,
            profile_filepath, company_name, official_mobile_no, official_email,
            certificate_filepath, bank_name, branch_ifsc_code,
            account_holder_name, account_number, swift_bic, upi_id, paypal,
            payment_terms_accepted, ie_code, ie_certificate_filepath, exporter_terms_accepted
        ))
        conn.commit()
        return jsonify({"message": "Seller registration successful"}), 201

    except Exception as e:
        print(f"Error during seller registration: {e}")
        return jsonify({"error": "An error occurred during registration"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def add_product():
    if request.method == "POST":
        try:
            conn = get_db_connection()
            cursor = conn.cursor() if conn else None

            data = request.form.to_dict()
            files = request.files
            token_payload = getattr(request, 'token_payload', None)

            if token_payload:
                user_id = token_payload.get('user_id')
            elif session.get('user'):
                user_id = session.get('user')

            else:
                user_id = escape(data.get('user'))

            product_name = escape(data.get('productName'))
            product_description = escape(data.get('productDescription'))
            product_category = escape(data.get('productCategory'))
            sub_category = escape(data.get('subCategory'))
            sub_sub_category = escape(data.get('subSubCategory'))
            product_type = escape(data.get('productType'))
            product_sku = escape(data.get('productSku'))
            unit = escape(data.get('unit'))

            unit_price = data.get('unitPrice') or None
            minimum_order_qty = data.get('minimumOrderQty') or None
            current_stock_qty = data.get('currentStockQty') or None
            discount_type = data.get('discountType') or None
            discount_amount = data.get('discountAmount') or None
            tax_amount = data.get('taxAmount') or None
            tax_calculation = data.get('taxCalculation') or None
            shipping_cost = data.get('shippingCost') or None
            shipping_cost_multiply = data.get('shippingCostMultiply')

            product_thumbnail = files.get('productThumbnail')
            product_thumbnail_path = None

            if product_thumbnail and product_thumbnail.filename:
                filename = secure_filename(product_thumbnail.filename)
                product_thumbnail_path = os.path.join('./uploads/thumbnail', filename)
                os.makedirs('./uploads/thumbnail', exist_ok=True)
                product_thumbnail.save(product_thumbnail_path)

            additional_images = []
            additional_files = files.getlist('additionalImages') or []
            for file in additional_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('./uploads/additional', filename)
                    os.makedirs('./uploads/additional', exist_ok=True)
                    file.save(file_path)
                    additional_images.append(file_path)

            meta_title = escape(data.get('metaTitle'))
            meta_description = escape(data.get('metaDescription'))

            # Insert product and return its PID
            cursor.execute("""
                INSERT INTO add_product (
                    userid, product_name, product_description, product_category, sub_category,
                    sub_sub_category, product_type, product_sku, unit,
                    unit_price, minimum_order_qty, current_stock_qty, discount_type, discount_amount,
                    tax_amount, tax_calculation, shipping_cost, shipping_cost_multiply,
                    product_thumbnail, additional_images, meta_title, meta_description
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING pid;
            """, (
                user_id, product_name, product_description, product_category, sub_category,
                sub_sub_category, product_type, product_sku, unit,
                unit_price, minimum_order_qty, current_stock_qty, discount_type, discount_amount,
                tax_amount, tax_calculation, shipping_cost, shipping_cost_multiply,
                product_thumbnail_path, ','.join(additional_images), meta_title, meta_description
            ))
            new_pid = cursor.fetchone()[0]
            conn.commit()

            # Create default status entry for the new product
            status_cursor = conn.cursor()
            status_cursor.execute(
                "INSERT INTO product_status (pid, active_status, is_featured) VALUES (%s, %s, %s)",
                (new_pid, False, False)
            )
            conn.commit()
            status_cursor.close()

            return jsonify({'message': 'Product added successfully', 'pid': new_pid}), 200

        except Exception as e:
            print("Error:", str(e))
            return jsonify({'error': 'Failed to add product'}), 400


def admin_product_details():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Join product_status to include active_status and is_featured for each product
        cursor.execute("""
            SELECT p.*, ps.active_status, ps.is_featured
            FROM add_product p
            LEFT JOIN product_status ps ON p.PID = ps.pid;
        """)
        products = cursor.fetchall()

        return jsonify({'products': products}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch product details'}), 500

    finally:
        if cursor:
            cursor.close()



def product_details():
    global conn
    token_payload = getattr(request, 'token_payload', None)

    if token_payload:
        user_id = token_payload.get('user_id')
    else:
        user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            'error': 'Unable to determine user ID',
            'token_payload': token_payload,
            'session': dict(session)
        }), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Accept optional filters in JSON body (POST) or query params (GET)
        filters = request.get_json(silent=True) or {}
        # Also accept query params as fallback
        verify_status = (filters.get('verify_status') or request.args.get('verify_status'))
        search_term = (filters.get('search') or request.args.get('search') or '')

        # Build base query joining product_status to allow status-based filtering
        query = """
        SELECT p.*, ps.active_status, ps.is_featured
        FROM add_product p
        LEFT JOIN product_status ps ON p.PID = ps.pid
        WHERE p.userid = %s
        """
        params = [user_id]

        if verify_status:
            # Map simple values: Approved -> active_status = TRUE, Denied -> FALSE
            if str(verify_status).lower() in ('approved', 'true', '1'):
                query += " AND ps.active_status = TRUE"
            elif str(verify_status).lower() in ('denied', 'false', '0'):
                query += " AND ps.active_status = FALSE"
            # else leave unfiltered for other values like 'pending'

        if search_term:
            query += " AND p.product_name ILIKE %s"
            params.append(f"%{search_term}%")

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()

        return jsonify({
            'products': products,
            'user_id': user_id
        }, 200)

    except Exception as e:
        print("Database Error:", str(e))
        return jsonify({
            'error': 'Failed to fetch product details',
            'details': str(e)
        }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def product_detail_id(pid):
    token_payload = getattr(request, 'token_payload', None)

    if token_payload:
        user_id = token_payload.get('user_id')
    else:
        user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            'error': 'Unable to determine user ID',
            'token_payload': token_payload,
            'session': dict(session)
        }), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Join product_status to include active_status and is_featured
        cursor.execute("""
            SELECT p.*, ps.active_status, ps.is_featured
            FROM add_product p
            LEFT JOIN product_status ps ON p.PID = ps.pid
            WHERE p.userid = %s AND p.PID = %s;
        """, (user_id, pid))
        products = cursor.fetchall()

        return jsonify({
            'products': products,
            'user_id': user_id
        }), 200

    except Exception as e:
        print("Database Error:", str(e))
        return jsonify({
            'error': 'Failed to fetch product details',
            'details': str(e)
        }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def delete_product(pid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "DELETE FROM add_product WHERE pid = %s"
        cursor.execute(query, (pid,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify({'message': 'Product deleted successfully'}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to delete product'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def edit_product(pid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        update_data = request.form.to_dict()
        files = request.files

        product_thumbnail = files.get('product_thumbnail')
        if product_thumbnail and product_thumbnail.filename:
            filename = secure_filename(product_thumbnail.filename)
            product_thumbnail_path = os.path.join('./uploads/thumbnail', filename)
            os.makedirs('./uploads/thumbnail', exist_ok=True)
            product_thumbnail.save(product_thumbnail_path)
            update_data['product_thumbnail'] = product_thumbnail_path

        additional_images = []
        if 'additional_images' in files:
            additional_files = files.getlist('additional_images')
            for file in additional_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('./uploads/additional', filename)
                    os.makedirs('./uploads/additional', exist_ok=True)
                    file.save(file_path)
                    additional_images.append(file_path)

        if additional_images:
            update_data['additional_images'] = ','.join(additional_images)

        if not update_data:
            return jsonify({'error': 'No data provided for update'}), 400

        # Get existing product data
        cursor.execute("SELECT product_thumbnail, additional_images FROM add_product WHERE pid = %s", (pid,))
        existing_product = cursor.fetchone()

        if not existing_product:
            return jsonify({'error': 'Product not found'}), 404

        if product_thumbnail and product_thumbnail.filename and existing_product['product_thumbnail']:
            old_thumbnail = existing_product['product_thumbnail']
            if os.path.exists(old_thumbnail):
                try:
                    os.remove(old_thumbnail)
                except Exception as e:
                    print(f"Error deleting old thumbnail: {str(e)}")

        if additional_images and existing_product['additional_images']:
            try:
                old_images = json.loads(existing_product['additional_images']) if existing_product[
                    'additional_images'] else []
                for old_image in old_images:
                    if os.path.exists(old_image):
                        try:
                            os.remove(old_image)
                        except Exception as e:
                            print(f"Error deleting old additional image: {str(e)}")
            except json.JSONDecodeError as e:
                print(f"Error parsing existing additional_images: {str(e)}")

        set_clauses = []
        values = []
        for column, value in update_data.items():
            if column not in ['pid', 'userid']:
                set_clauses.append(f"{column} = %s")
                values.append(value)

        values.append(pid)

        query = f"""
            UPDATE add_product
            SET {', '.join(set_clauses)}
            WHERE pid = %s
            RETURNING *;
        """

        cursor.execute(query, tuple(values))
        updated_product = cursor.fetchone()
        conn.commit()

        return jsonify({
            'message': 'Product updated successfully',
            'product': updated_product
        }), 200

    except Exception as e:
        print("Error:", str(e))
        if conn:
            conn.rollback()
        return jsonify({'error': 'Failed to update product'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def admin_manufacture_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seller_product_view")
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    data = [dict(zip(column_names, row)) for row in rows]
    result = {}
    for item in data:
        userid = item["userid"]
        if userid not in result:
            result[userid] = {
                "userid": userid,
                "seller_name": item["seller_name"],
                "seller_email": item["seller_email"],
                "seller_mobile": item["seller_mobile"],
                "company_name": item["company_name"],
                "bank_name": item["bank_name"],
                "branch_ifsc_code": item["branch_ifsc_code"],
                "profile": f'{item["profile_picture_path"]}'.replace("./", "") if item[
                    "profile_picture_path"] else None,
                "total_products": 0,
                "total_current_quantity": 0,
                "products": []
            }
        result[userid]["total_products"] += 1
        result[userid]["total_current_quantity"] += item["current_stock_qty"] if item[
                                                                                     "current_stock_qty"] is not None else 0

        result[userid]["products"].append({
            "product_name": item["product_name"],
            "product_category": item["product_category"],
            "sub_category": item["sub_category"],
            "product_description": item["product_description"],
            "unit_price": item["unit_price"],
            "current_stock_qty": item["current_stock_qty"],
            "product_thumbnail": f'{item["product_thumbnail"]}'.replace("./", "") if item[
                "product_thumbnail"] else None,
        })

    cursor.close()
    conn.close()
    return jsonify(list(result.values())), 200


def get_seller_dashboard_data(userid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Example: Get order stats for this seller
        cursor.execute('''SELECT 
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN status = 'Packaging' THEN 1 ELSE 0 END) AS packaging,
            SUM(CASE WHEN status = 'Out For Delivery' THEN 1 ELSE 0 END) AS out_for_delivery,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
            SUM(CASE WHEN status = 'Canceled' THEN 1 ELSE 0 END) AS canceled,
            SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) AS returned,
            SUM(CASE WHEN status = 'Failed To Delivery' THEN 1 ELSE 0 END) AS failed_to_delivery
            FROM orders WHERE seller_id = %s''', (userid,))
        order_stats = cursor.fetchone()

        # Example: Wallet stats (replace with your actual logic)
        cursor.execute('''SELECT 
            COALESCE(SUM(balance), 0) AS withdrawable_balance,
            COALESCE(SUM(pending_withdraw), 0) AS pending_withdraw,
            COALESCE(SUM(already_withdrawn), 0) AS already_withdrawn,
            COALESCE(SUM(tax_given), 0) AS total_tax_given,
            COALESCE(SUM(commission_given), 0) AS total_commission_given,
            COALESCE(SUM(delivery_charge_earned), 0) AS total_delivery_charge_earned
            FROM seller_wallet WHERE seller_id = %s''', (userid,))
        wallet_stats = cursor.fetchone()

        # Example: Top products (replace with your actual logic)
        cursor.execute('''SELECT product_name, total_sales FROM products WHERE seller_id = %s ORDER BY total_sales DESC LIMIT 5''', (userid,))
        top_products = cursor.fetchall()

        data = {
            'order_stats': order_stats,
            'wallet_stats': wallet_stats,
            'top_products': [dict(zip([desc[0] for desc in cursor.description], row)) for row in top_products]
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def get_admin_dashboard_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Example: Get global order stats
        cursor.execute('''SELECT 
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN status = 'Packaging' THEN 1 ELSE 0 END) AS packaging,
            SUM(CASE WHEN status = 'Out For Delivery' THEN 1 ELSE 0 END) AS out_for_delivery,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
            SUM(CASE WHEN status = 'Canceled' THEN 1 ELSE 0 END) AS canceled,
            SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) AS returned,
            SUM(CASE WHEN status = 'Failed To Delivery' THEN 1 ELSE 0 END) AS failed_to_delivery
            FROM orders''')
        order_stats = cursor.fetchone()

        # Example: Global wallet stats (replace with your actual logic)
        cursor.execute('''SELECT 
            COALESCE(SUM(balance), 0) AS withdrawable_balance,
            COALESCE(SUM(pending_withdraw), 0) AS pending_withdraw,
            COALESCE(SUM(already_withdrawn), 0) AS already_withdrawn,
            COALESCE(SUM(tax_given), 0) AS total_tax_given,
            COALESCE(SUM(commission_given), 0) AS total_commission_given,
            COALESCE(SUM(delivery_charge_earned), 0) AS total_delivery_charge_earned
            FROM seller_wallet''')
        wallet_stats = cursor.fetchone()

        # Example: Top products (replace with your actual logic)
        cursor.execute('''SELECT product_name, total_sales FROM products ORDER BY total_sales DESC LIMIT 5''')
        top_products = cursor.fetchall()

        data = {
            'order_stats': order_stats,
            'wallet_stats': wallet_stats,
            'top_products': [dict(zip([desc[0] for desc in cursor.description], row)) for row in top_products]
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def logout():
    session.pop('token', None)
    session.pop('user_id', None)
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


def get_seller_orders():
    """Get all orders for the authenticated seller"""
    token_payload = getattr(request, 'token_payload', None)
    
    if token_payload:
        seller_id = token_payload.get('user_id')
    else:
        seller_id = session.get('user_id')

    if not seller_id:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT o.order_id, o.user_id, o.product_id, o.quantity, o.total_price, 
                   o.status, o.order_date, p.product_name, p.product_description,
                   u.username as customer_name, u.email as customer_email
            FROM orders o
            JOIN add_product p ON o.product_id = p.pid
            JOIN users_login u ON o.user_id = u.id
            WHERE o.seller_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (seller_id,))
        orders = cursor.fetchall()

        return jsonify({'orders': orders}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch seller orders'}), 500
    finally:
        if conn:
            conn.close()


def get_seller_order_by_status(status):
    """Get orders for seller filtered by status"""
    token_payload = getattr(request, 'token_payload', None)
    
    if token_payload:
        seller_id = token_payload.get('user_id')
    else:
        seller_id = session.get('user_id')

    if not seller_id:
        return jsonify({'error': 'Authentication required'}), 401

    valid_statuses = ['Pending', 'Confirmed', 'Packaging', 'Out For Delivery', 
                     'Delivered', 'Canceled', 'Returned', 'Failed To Delivery']
    
    if status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT o.order_id, o.user_id, o.product_id, o.quantity, o.total_price, 
                   o.status, o.order_date, p.product_name, p.product_description,
                   u.username as customer_name, u.email as customer_email
            FROM orders o
            JOIN add_product p ON o.product_id = p.pid
            JOIN users_login u ON o.user_id = u.id
            WHERE o.seller_id = %s AND o.status = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (seller_id, status))
        orders = cursor.fetchall()

        return jsonify({'status': status, 'orders': orders}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': f'Failed to fetch {status} orders'}), 500
    finally:
        if conn:
            conn.close()


def update_order_status():
    """Update order status (seller can update status)"""
    token_payload = getattr(request, 'token_payload', None)
    
    if token_payload:
        seller_id = token_payload.get('user_id')
    else:
        seller_id = session.get('user_id')

    if not seller_id:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.json
    order_id = data.get('order_id')
    new_status = data.get('status')

    if not order_id or not new_status:
        return jsonify({'error': 'Order ID and status are required'}), 400

    valid_statuses = ['Pending', 'Confirmed', 'Packaging', 'Out For Delivery', 
                     'Delivered', 'Canceled', 'Returned', 'Failed To Delivery']
    
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the order belongs to this seller
        cursor.execute('SELECT seller_id FROM orders WHERE order_id = %s', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order[0] != seller_id:
            return jsonify({'error': 'Unauthorized to update this order'}), 403

        # Update the order status
        cursor.execute('UPDATE orders SET status = %s WHERE order_id = %s', 
                      (new_status, order_id))
        conn.commit()

        return jsonify({'message': 'Order status updated successfully'}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to update order status'}), 500
    finally:
        if conn:
            conn.close()


def get_seller_order_stats():
    """Get order statistics for seller dashboard"""
    token_payload = getattr(request, 'token_payload', None)
    
    if token_payload:
        seller_id = token_payload.get('user_id')
    else:
        seller_id = session.get('user_id')

    if not seller_id:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''SELECT 
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN status = 'Packaging' THEN 1 ELSE 0 END) AS packaging,
            SUM(CASE WHEN status = 'Out For Delivery' THEN 1 ELSE 0 END) AS out_for_delivery,
            SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
            SUM(CASE WHEN status = 'Canceled' THEN 1 ELSE 0 END) AS canceled,
            SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) AS returned,
            SUM(CASE WHEN status = 'Failed To Delivery' THEN 1 ELSE 0 END) AS failed_to_delivery,
            COUNT(*) AS total_orders,
            COALESCE(SUM(total_price), 0) AS total_revenue
            FROM orders WHERE seller_id = %s'''
        
        cursor.execute(query, (seller_id,))
        stats = cursor.fetchone()

        if stats:
            columns = [desc[0] for desc in cursor.description]
            stats_dict = dict(zip(columns, stats))
            return jsonify(stats_dict), 200
        else:
            return jsonify({'error': 'No orders found'}), 404

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch order statistics'}), 500
    finally:
        if conn:
            conn.close()

