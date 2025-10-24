from flask import request, jsonify, session, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_connection, verify_user, verify_admin_user
from markupsafe import escape
from app.authTokens import generate_token, validate_token
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.users.database import create


def verify_user_login(username, password):
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "SELECT id, password FROM users_login WHERE email = %s ",
                (username.strip(),)
            )
            result = cur.fetchone()
            if result:
                user_id, hashed_pass = result
                if check_password_hash(hashed_pass, password.strip()):
                    return user_id
            return None
    finally:
        con.close()


def user_login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = escape(data.get('email', '').strip())
    password = escape(data.get('password', '').strip())

    user_id = verify_user_login(username, password)

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


def user_login_id(user_id):
    global connection
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, email, name,mobile_number,profile_path FROM users_login WHERE id = %s",
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


def user_register():
    data = request.json
    name = escape(data.get('fullname', '').strip())
    email = escape(data.get('email', '').strip())
    mobile = escape(data.get('mobileNo', '').strip())
    password = escape(data.get('password', '').strip())

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users_login WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "User already exists"}), 400

        cursor.execute("INSERT INTO users_login (name, email, mobile_number, password) VALUES (%s, %s, %s,%s)",
                       (name, email, mobile, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    finally:
        conn.close()


def user_product_details():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""SELECT ap.*, ps.active_status, ps.is_featured
                      FROM add_product ap
                      INNER JOIN product_status ps ON ap.PID = ps.pid
                      WHERE ps.active_status = TRUE;""")

    products = cursor.fetchall()

    filtered_products = []  # Store products that match the condition

    for product in products:
        if product['tem_close'] == False:
            product['product_thumbnail'] = product['product_thumbnail']
            product['product_thumbnail'] = f"{product['product_thumbnail']}".replace("./", "") if product[
                "product_thumbnail"] else None
            if product['additional_images']:
                product['additional_images'] = f"{product['additional_images']}".replace("./", "") if product[
                    "additional_images"] else None

            filtered_products.append(product)  # Append matching products

    if cursor:
        cursor.close()
    if conn:
        conn.close()

    return jsonify({'products': filtered_products}), 200


def update_tem_close():
    token_payload = getattr(request, 'token_payload', None)
    if token_payload:
        user_id = token_payload.get('user_id')
    elif session.get('user'):
        user_id = session.get('user')
    else:
        return jsonify({"error": "User not authenticated"}), 401

    data = request.get_json()
    new_status = data.get('status', False)


    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE add_product SET tem_close = %s WHERE userid = %s;",
            (new_status, user_id)
        )
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount > 0:
            return jsonify({"message": "Shop status updated successfully"}), 200
        else:
            return jsonify({"message": "No shop records found to update"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def get_tem_close_status():
    token_payload = getattr(request, 'token_payload', None)
    if token_payload:
        user_id = token_payload.get('user_id')
    elif session.get('user'):
        user_id = session.get('user')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT tem_close FROM add_product WHERE userid = %s LIMIT 1;", (user_id,))
        result = cursor.fetchone()
        if result:
            return jsonify({"tem_close": result[0]}), 200
        else:
            return jsonify({"tem_close": False}), 200  # Default to false

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


def get_single_product_details(pid):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT ap.*, ps.active_status, ps.is_featured
        FROM add_product ap
        INNER JOIN product_status ps ON ap.PID = ps.pid
        WHERE ps.active_status = TRUE AND ap.PID = %s;
    """, (pid,))

    product = cursor.fetchone()

    if product:
        product['product_thumbnail'] = product['product_thumbnail'].replace("./", "") if product[
            "product_thumbnail"] else None
        if product['additional_images']:
            product['additional_images'] = product['additional_images'].replace("./", "")

    if cursor:
        cursor.close()
    if conn:
        conn.close()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify(product), 200


def user_profile_edit():
    try:
        data = request.form

        token_payload = getattr(request, 'token_payload', None)
        if token_payload:
            userid = token_payload.get('user_id')
        elif session.get('user'):
            userid = session.get('user')
        else:
            userid = escape(data.get('user'))

        if not userid:
            return jsonify({"error": "User ID not found"}), 401

        full_name = data.get('name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        new_password = data.get('password')
        profile_picture = request.files.get('profile_picture')

        if not full_name or not email:
            return jsonify({"error": "Full Name and Email are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        update_fields = ["name = %s", "email = %s"]
        params = [full_name, email]

        if phone_number:
            update_fields.append("mobile_number = %s")
            params.append(phone_number)

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            upload_dir = os.path.join('uploads', 'user_profile_pictures')
            os.makedirs(upload_dir, exist_ok=True)
            upload_path = os.path.join(upload_dir, filename)
            profile_picture.save(upload_path)

            update_fields.append("profile_path = %s")
            params.append(upload_path)

        if new_password:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
            update_fields.append("password = %s")
            params.append(hashed_password)

        params.append(userid)

        update_query = f"""
            UPDATE users_login
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, email, mobile_number, profile_path, password
        """

        cursor.execute(update_query, tuple(params))
        updated_user = cursor.fetchone()

        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        conn.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": updated_user
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def create_ticket():
    try:
        data = request.form
        token_payload = getattr(request, 'token_payload', None)

        # Get user ID from token or form
        if token_payload:
            user_id = token_payload.get('user_id')
        else:
            user_id = escape(data.get('user'))

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        subject = data.get('subject')
        ticket_type = data.get('type')
        priority = data.get('priority')
        description = data.get('description')

        if not all([subject, ticket_type, priority, description]):
            return jsonify({
                "error": "Missing required fields. Please provide subject, type, priority, and description"
            }), 400

        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                upload_dir = os.path.join('uploads', 'tickets')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                attachment_path = file_path

        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                       INSERT INTO customer_ticket
                       (user_id, subject, type, priority, description, attachment, status, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, 'Open', CURRENT_TIMESTAMP)
                       RETURNING user_id, subject, type, priority, description, attachment, status, 
                                created_at,pid
                   """, (user_id, subject, ticket_type, priority, description, attachment_path))

            new_ticket = cursor.fetchone()
            new_ticket['created_at'] = new_ticket['created_at'].strftime('%Y-%m-%d %H:%M:%S')

            conn.commit()
            print(new_ticket)
            return jsonify({
                "message": "Ticket created successfully",
                "ticket": new_ticket
            }), 201

        except Exception as e:
            if attachment_path and os.path.exists(attachment_path):
                os.remove(attachment_path)
            print(f"Database error: {e}")
            return jsonify({"error": "Failed to create ticket"}), 500

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error creating ticket: {e}")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"error": "Method not allowed"}), 405


def view_ticket():
    try:
        data = request.form
        token_payload = getattr(request, 'token_payload', None)

        if token_payload:
            user_id = token_payload.get('user_id')
        else:
            user_id = escape(data.get('user'))

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM customer_ticket WHERE user_id = %s", (user_id,))
        ticket = cursor.fetchall()

        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify({
            "ticket": ticket
        }), 201

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to delete ticket"}), 500

    finally:
        cursor.close()
        conn.close()


def delete_ticket():
    try:
        data = request.json
        pid = data.get('pid')

        if not pid:
            return jsonify({"error": "Ticket ID (pid) is required"}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Check if the ticket exists
            cursor.execute("SELECT * FROM customer_ticket WHERE pid = %s", (pid,))
            ticket = cursor.fetchone()

            if not ticket:
                return jsonify({"error": "Ticket not found"}), 404

            # Delete the attachment file if it exists
            attachment_path = ticket.get('attachment')
            if attachment_path and os.path.exists(attachment_path):
                os.remove(attachment_path)

            # Delete the ticket from the database
            cursor.execute("DELETE FROM customer_ticket WHERE pid = %s", (pid,))
            conn.commit()

            return jsonify({"message": f"Ticket with ID {pid} deleted successfully"}), 200

        except Exception as e:
            print(f"Database error: {e}")
            return jsonify({"error": "Failed to delete ticket"}), 500

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error deleting ticket: {e}")
        return jsonify({"error": "Internal server error"}), 500

def admin_view_ticket():
    try:

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM customer_ticket")
        ticket = cursor.fetchall()

        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify(ticket), 201

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to delete ticket"}), 500

    finally:
        cursor.close()
        conn.close()