from flask import (
    request,
    jsonify,
    session,
    redirect,
    make_response,
    send_from_directory,
)
from app.database import get_db_connection, verify_user, verify_admin_user
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
import re
import psycopg2
import os,datetime

def get_environment_settings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)  # Using RealDictCursor to get dict results
    cur.execute('SELECT * FROM environment_settings ORDER BY id LIMIT 1')
    settings = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(settings)

def update_environment_settings():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    UPDATE environment_settings SET 
        app_name = %s,
        app_debug = %s,
        app_mode = %s,
        db_connection = %s,
        db_host = %s,
        db_port = %s,
        buyer_username = %s,
        purchase_code = %s
    WHERE id = 1
    RETURNING id
    ''', (
        data.get('app_name'),
        data.get('app_debug'),
        data.get('app_mode'),
        data.get('db_connection'),
        data.get('db_host'),
        data.get('db_port'),
        data.get('buyer_username'),
        data.get('purchase_code')
    ))
    
    result = cur.fetchone()
    if not result:
        cur.execute('''
        INSERT INTO environment_settings 
        (app_name, app_debug, app_mode, db_connection, db_host, db_port, buyer_username, purchase_code)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.get('app_name'),
            data.get('app_debug'),
            data.get('app_mode'),
            data.get('db_connection'),
            data.get('db_host'),
            data.get('db_port'),
            data.get('buyer_username'),
            data.get('purchase_code')
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Environment settings updated successfully"})

def get_app_settings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM app_settings ORDER BY id LIMIT 1')
    settings = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(settings)

def update_app_settings():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    UPDATE app_settings SET 
        android_min_customer_version = %s,
        android_customer_download_url = %s,
        ios_min_customer_version = %s,
        ios_customer_download_url = %s,
        android_min_vendor_version = %s,
        android_vendor_download_url = %s,
        ios_min_vendor_version = %s,
        ios_vendor_download_url = %s
    WHERE id = 1
    RETURNING id
    ''', (
        data.get('android_min_customer_version'),
        data.get('android_customer_download_url'),
        data.get('ios_min_customer_version'),
        data.get('ios_customer_download_url'),
        data.get('android_min_vendor_version'),
        data.get('android_vendor_download_url'),
        data.get('ios_min_vendor_version'),
        data.get('ios_vendor_download_url')
    ))
    
    result = cur.fetchone()
    if not result:
        cur.execute('''
        INSERT INTO app_settings 
        (android_min_customer_version, android_customer_download_url, ios_min_customer_version, ios_customer_download_url,
        android_min_vendor_version, android_vendor_download_url, ios_min_vendor_version, ios_vendor_download_url)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.get('android_min_customer_version'),
            data.get('android_customer_download_url'),
            data.get('ios_min_customer_version'),
            data.get('ios_customer_download_url'),
            data.get('android_min_vendor_version'),
            data.get('android_vendor_download_url'),
            data.get('ios_min_vendor_version'),
            data.get('ios_vendor_download_url')
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "App settings updated successfully"})

def get_languages():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM languages ORDER BY id')
    languages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(languages)



def add_language():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('''
    INSERT INTO languages 
    (name, code, status, is_default)
    VALUES 
    (%s, %s, %s, %s)
    RETURNING id
    ''', (
        data.get('name'),
        data.get('code'),
        data.get('status', True),
        data.get('is_default', False)
    ))
    
    new_language_id = cur.fetchone()['id']
    
    if data.get('is_default'):
        cur.execute('''
        UPDATE languages SET is_default = FALSE WHERE id != %s
        ''', (new_language_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Language added successfully", "id": new_language_id})

def update_language(lang_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    UPDATE languages SET 
        name = %s,
        code = %s,
        status = %s,
        is_default = %s
    WHERE id = %s
    RETURNING id
    ''', (
        data.get('name'),
        data.get('code'),
        data.get('status'),
        data.get('is_default'),
        lang_id
    ))
    
    if data.get('is_default'):
        cur.execute('''
        UPDATE languages SET is_default = FALSE WHERE id != %s
        ''', (lang_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Language updated successfully"})


def get_currencies():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM currencies ORDER BY id')
    currencies = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(currencies)

def add_currency():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('''
    INSERT INTO currencies 
    (name, symbol, code, exchange_rate, status, is_default)
    VALUES 
    (%s, %s, %s, %s, %s, %s)
    RETURNING id
    ''', (
        data.get('name'),
        data.get('symbol'),
        data.get('code'),
        data.get('exchange_rate'),
        data.get('status', True),
        data.get('is_default', False)
    ))
    
    new_currency_id = cur.fetchone()['id']
    
    if data.get('is_default'):
        cur.execute('''
        UPDATE currencies SET is_default = FALSE WHERE id != %s
        ''', (new_currency_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Currency added successfully", "id": new_currency_id})

def set_default_currency(currency_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE currencies SET is_default = FALSE')
    cur.execute('UPDATE currencies SET is_default = TRUE WHERE id = %s RETURNING id', (currency_id,))
    result = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    if result:
        return jsonify({"success": True, "message": "Default currency updated successfully"})
    else:
        return jsonify({"success": False, "message": "Currency not found"}), 404

def get_cookie_settings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM cookie_settings ORDER BY id LIMIT 1')
    settings = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(settings if settings else {})

def update_cookie_settings():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ensure status is correctly handled as boolean
    status = data.get('status')
    if isinstance(status, str):
        status = status.lower() == 'true'
    
    cur.execute('''
    UPDATE cookie_settings SET 
        cookie_text = %s,
        status = %s
    WHERE id = 1
    RETURNING id
    ''', (
        data.get('cookie_text'),
        status
    ))
    
    result = cur.fetchone()
    if not result:
        cur.execute('''
        INSERT INTO cookie_settings 
        (cookie_text, status)
        VALUES 
        (%s, %s)
        ''', (
            data.get('cookie_text'),
            status
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": "Cookie settings updated successfully"})

def clean_database(target):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if target == 'products':
        cur.execute('DELETE FROM products')
    elif target == 'product-reviews':
        cur.execute('DELETE FROM product_reviews')
    elif target == 'orders':
        cur.execute('DELETE FROM orders')
    elif target == 'order-history':
        cur.execute('DELETE FROM order_history')
    elif target == 'users':
        cur.execute('DELETE FROM users')
    elif target == 'user-activity':
        cur.execute('DELETE FROM user_activity_logs')
    elif target == 'system-logs':
        cur.execute('DELETE FROM system_logs')
    elif target == 'cache':
        pass  # Implement cache cleaning logic here
    elif target == 'all':
        tables = ['products', 'product_reviews', 'orders', 'order_history', 
                  'users', 'user_activity_logs', 'system_logs']
        for table in tables:
            try:
                cur.execute(f'DELETE FROM {table}')
            except:
                pass
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "message": f"Successfully cleaned {target}"})

def software_update():
    if request.method == 'GET':
        
        username = request.args.get('username')
        print(username)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            if username:
                cur.execute("SELECT * FROM software_updates WHERE username = %s", (username,))
            else:
                cur.execute("SELECT * FROM software_updates ORDER BY uploaded_at DESC")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            results = [
                {
                    "id": row[0],
                    "username": row[1],
                    "purchase_code": row[2],
                    "file_path": row[3],
                    "uploaded_at": row[4].strftime('%Y-%m-%d %H:%M:%S')
                }
                for row in rows
            ]

            return jsonify(results), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    elif request.method in ['POST', 'PUT']:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']
        username = request.form.get('username')
        purchase_code = request.form.get('purchaseCode')
        print(request.data)
        print(username, purchase_code, file.filename)

        if not username or not purchase_code or file.filename == '':
            return jsonify({"message": "All fields are required"}), 400

        try:
            UPLOAD_FOLDER = os.path.join('uploads', 'software_updates')
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"{username}_{file.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            conn = get_db_connection()
            cur = conn.cursor()

            if request.method == 'POST':
                # Insert new record
                cur.execute("""
                    INSERT INTO software_updates (username, purchase_code, file_path)
                    VALUES (%s, %s, %s)
                """, (username, purchase_code, file_path))

            elif request.method == 'PUT':
                # Update existing record
                cur.execute("""
                    UPDATE software_updates
                    SET purchase_code = %s, file_path = %s, uploaded_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                """, (purchase_code, file_path, username))

            conn.commit()
            cur.close()
            conn.close()

            msg = "Update created successfully" if request.method == 'POST' else "Update updated successfully"
            return jsonify({"message": msg}), 201

        except Exception as e:
            return jsonify({"message": str(e)}), 500
        
    elif request.method == 'DELETE':
        
        username = request.args.get('username')
        print(username)
        conn = get_db_connection()
        cur = conn.cursor()
        if username:
            cur.execute("DELETE FROM software_updates WHERE username = %s", (username,))
        else:
            cur.execute("DELETE FROM software_updates;")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Software updates deleted successfully"}), 200

def login_settings():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute("SELECT * FROM admin_login_settings WHERE id = 1")
        row = cur.fetchone()
        if row:
            keys = [desc[0] for desc in cur.description]
            data = dict(zip(keys, row))
            cur.close()
            conn.close()
            return jsonify(data)
        else:
            cur.close()
            conn.close()
            return jsonify({"error": "No settings found"}), 404

    # For POST and PUT
    data = request.json

    cur.execute("SELECT id FROM admin_login_settings WHERE id = 1")
    exists = cur.fetchone()

    values = (
        data.get('manual_login', True),
        data.get('otp_login', False),
        data.get('email_verification', False),
        data.get('phone_verification', False),
        data.get('max_otp_attempts', 5),
        data.get('otp_resend_time', 30),
        data.get('otp_block_time', 120),
        data.get('max_login_attempts', 10),
        data.get('login_block_time', 120),
        data.get('login_url', '/login')
    )

    if exists:
        update_query = """
        UPDATE admin_login_settings SET
            manual_login = %s,
            otp_login = %s,
            email_verification = %s,
            phone_verification = %s,
            max_otp_attempts = %s,
            otp_resend_time = %s,
            otp_block_time = %s,
            max_login_attempts = %s,
            login_block_time = %s,
            login_url = %s
        WHERE id = 1
        """
        cur.execute(update_query, values)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Login settings updated successfully"})
    else:
        insert_query = """
        INSERT INTO admin_login_settings (
            manual_login, otp_login, email_verification, phone_verification,
            max_otp_attempts, otp_resend_time, otp_block_time,
            max_login_attempts, login_block_time, login_url, id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
        """
        cur.execute(insert_query, values)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Login settings created successfully"}), 201

def payment_methods_handler():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    UPLOAD_FOLDER = os.path.join('uploads', 'payment_logo')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if request.method == 'POST':
        try:
            # File handling
            logo_file = request.files.get('logo')
            username = request.form.get('name')  
           
            logo_path = None
            if logo_file:
                filename = secure_filename(f"{username}_{logo_file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                logo_file.save(file_path)
                logo_path = file_path  # Save to DB

            data = request.form

            cur.execute("""
                INSERT INTO payment_methods (
                    name,
                    type,
                    status,
                    access_token,
                    public_key,
                    private_key,
                    gateway_title,
                    logo,
                    mode,
                    payment_info,
                    required_info
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get('name'),
                data.get('type'),
                data.get('status', 'true').lower() == 'true',
                data.get('access_token'),
                data.get('public_key'),
                data.get('private_key'),
                data.get('gateway_title'),
                logo_path,
                data.get('mode'),
                data.get('payment_info'),
                data.getlist('required_info')  # for list/array input
            ))
            new_id = cur.fetchone()['id']
            conn.commit()
            return jsonify({"message": "Saved successfully!", "id": new_id}), 200

        except Exception as e:
            conn.rollback()
            print("Error in POST:", e)
            return jsonify({"error": "Could not save"}), 500

    elif request.method == 'PUT':
        try:
            data = request.form
            logo_file = request.files.get('logo')
            logo_path = data.get('existing_logo')  # fallback

            if logo_file:
                filename = secure_filename(f"{data.get('name')}_{logo_file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                logo_file.save(file_path)
                logo_path = file_path

            cur.execute("""
                UPDATE payment_methods
                SET name = %s,
                    type = %s,
                    status = %s,
                    access_token = %s,
                    public_key = %s,
                    private_key = %s,
                    gateway_title = %s,
                    logo = %s,
                    mode = %s,
                    payment_info = %s,
                    required_info = %s
                WHERE id = %s
            """, (
                data.get('name'),
                data.get('type'),
                data.get('status', 'true').lower() == 'true',
                data.get('access_token'),
                data.get('public_key'),
                data.get('private_key'),
                data.get('gateway_title'),
                logo_path,
                data.get('mode'),
                data.get('payment_info'),
                data.getlist('required_info'),
                data.get('id')
            ))

            if cur.rowcount == 0:
                conn.rollback()
                return jsonify({"error": "Payment method not found"}), 404
            conn.commit()
            return jsonify({"message": "Updated successfully!"}), 200

        except Exception as e:
            conn.rollback()
            print("Error in PUT:", e)
            return jsonify({"error": "Could not update"}), 500

    elif request.method == 'GET':
        try:
            cur.execute("SELECT * FROM payment_methods")
            rows = cur.fetchall()
            conn.commit()
            return jsonify(rows), 200
        except Exception as e:
            conn.rollback()
            print("Error in GET:", e)
            return jsonify({"error": "Could not retrieve data"}), 500

    cur.close()
    conn.close()