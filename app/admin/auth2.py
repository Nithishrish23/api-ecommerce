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
import os

def get_restock_requests():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM restock_requests ORDER BY last_request_date DESC")
    restock_requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(restock_requests), 200


# def get_restock_request_seller():
#     token_payload = getattr(request, 'token_payload', None)
#
#     if token_payload:
#         user_id = token_payload.get('user_id')
#     else:
#         user_id = session.get('user_id')
#     conn = get_db_connection()
#     cursor = conn.cursor(cursor_factory=RealDictCursor)
#     cursor.execute("SELECT * FROM restock_requests WHERE user_id = %s", (user_id,))
#     restock_request = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if restock_request:
#         return jsonify(restock_request), 200
#     return jsonify({"message": "Restock request not found"}), 404


def create_restock_request():
    data = request.json
    print(data)
    conn = get_db_connection()
    cursor = conn.cursor()
    token_payload = getattr(request, "token_payload", None)

    if token_payload:
        user_id = token_payload.get("user_id")
    else:
        user_id = session.get("user_id")

    cursor.execute(
        """
        INSERT INTO restock_requests (user_id, product_name, selling_price, last_request_date, number_of_requests)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """,
        (
            user_id,
            data["product_name"],
            data["selling_price"],
            data["last_request_date"],
            data["number_of_requests"],
        ),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Restock request created", "id": new_id}), 201


def update_restock_request(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE restock_requests
        SET user_id = %s, product_name = %s, selling_price = %s, last_request_date = %s, number_of_requests = %s
        WHERE id = %s
    """,
        (
            data["user_id"],
            data["product_name"],
            data["selling_price"],
            data["last_request_date"],
            data["number_of_requests"],
            id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Restock request updated"}), 200


def delete_restock_request(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restock_requests WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Restock request deleted"}), 200


def get_update_products():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM trigger_log")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(products)


# def add_update_product():
#     data = request.json
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
#
#     cur.execute(
#         "INSERT INTO update_products (name, previous_shipping_cost, new_shipping_cost, seller_id) VALUES (%s, %s, %s, %s) RETURNING id",
#         (data['name'], data['previousShippingCost'], data['newShippingCost'], data['sellerId'])
#     )
#     product_id = cur.fetchone()["id"]
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     return jsonify({"message": "Product added", "id": product_id}), 201
#
#
# def update_product(id):
#     data = request.json
#     conn = get_db_connection()
#     cur = conn.cursor()
#
#     cur.execute(
#         "UPDATE update_products SET name=%s, previous_shipping_cost=%s, new_shipping_cost=%s WHERE id=%s",
#         (data['name'], data['previousShippingCost'], data['newShippingCost'], id)
#     )
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     return jsonify({"message": "Product updated"}), 200
#
#
# def delete_update_product(id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#
#     cur.execute("DELETE FROM update_products WHERE id=%s", (id,))
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     return jsonify({"message": "Product deleted"}), 200


def get_approved_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Filters
        brand = request.args.get("brand")
        category = request.args.get("category")
        sub_category = request.args.get("sub_category")
        sub_sub_category = request.args.get("sub_sub_category")
        search_term = request.args.get("search", "")

        query = """
        SELECT 
            p.PID, p.product_name, p.product_description, p.product_category, 
            p.sub_category, p.sub_sub_category, p.product_type, p.product_sku, 
            p.unit, p.unit_price, p.minimum_order_qty, p.current_stock_qty, 
            p.discount_type, p.discount_amount, p.tax_amount, p.tax_calculation, 
            p.shipping_cost, p.shipping_cost_multiply,ps.active_status, ps.is_featured
        FROM add_product p
        JOIN product_status ps ON p.PID = ps.pid
        WHERE ps.active_status = TRUE
        """

        params = []
        if brand:
            query += " AND p.product_name ILIKE %s"
            params.append(f"%{brand}%")
        if category:
            query += " AND p.product_category = %s"
            params.append(category)
        if sub_category:
            query += " AND p.sub_category = %s"
            params.append(sub_category)
        if sub_sub_category:
            query += " AND p.sub_sub_category = %s"
            params.append(sub_sub_category)
        if search_term:
            query += " AND p.product_name ILIKE %s"
            params.append(f"%{search_term}%")

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()

        # result = [dict(row) for row in products]

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "products": products}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def get_denied_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Filters
        brand = request.args.get("brand")
        category = request.args.get("category")
        sub_category = request.args.get("sub_category")
        sub_sub_category = request.args.get("sub_sub_category")
        search_term = request.args.get("search", "")

        query = """
            SELECT 
                p.PID, p.product_name, p.product_description, p.product_category, 
                p.sub_category, p.sub_sub_category, p.product_type, p.product_sku, 
                p.unit, p.unit_price, p.minimum_order_qty, p.current_stock_qty, 
                p.discount_type, p.discount_amount, p.tax_amount, p.tax_calculation, 
                p.shipping_cost, p.shipping_cost_multiply, ps.active_status, ps.is_featured
            FROM add_product p
            JOIN product_status ps ON p.PID = ps.pid
            WHERE ps.active_status = FALSE
            """

        params = []
        if brand:
            query += " AND p.product_name ILIKE %s"
            params.append(f"%{brand}%")
        if category:
            query += " AND p.product_category = %s"
            params.append(category)
        if sub_category:
            query += " AND p.sub_category = %s"
            params.append(sub_category)
        if sub_sub_category:
            query += " AND p.sub_sub_category = %s"
            params.append(sub_sub_category)
        if search_term:
            query += " AND p.product_name ILIKE %s"
            params.append(f"%{search_term}%")

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()

        # result = [dict(row) for row in products]

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "products": products}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
from datetime import datetime

ZOHO_EMAIL = "pclmart@zohomail.in"
ZOHO_PASSWORD = "Pcl@1245"


def read_emails():
    try:
        # Connect to mail server
        mail = imaplib.IMAP4_SSL("imap.zoho.in")
        mail.login(ZOHO_EMAIL, ZOHO_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        if status != "OK" or messages[0] == b"":
            return jsonify({"message": "No emails found"}), 200

        email_data = []
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        for num in messages[0].split():
            # Get the UID
            result, uid_data = mail.fetch(num, "(UID)")
            if result != "OK":
                continue
            uid = uid_data[0].decode().split()[2].split(")")[0]

            # Check if email with same UID already exists
            cursor.execute(
                "SELECT * FROM emails WHERE uid = %s AND type = 'received'", (uid,)
            )
            if cursor.fetchone():
                continue  # Skip duplicates

            # Fetch the full message
            status, msg_data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Decode subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    sender = msg.get("From")
                    sender_name = "Unknown"
                    sender_email = sender

                    # Extract name & email
                    match = re.match(r"(.+?)\s*<(.+?)>", sender)
                    if match:
                        sender_name = match.group(1).strip()
                        sender_email = match.group(2).strip()

                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if (
                                part.get_content_type() == "text/plain"
                                and "attachment"
                                not in str(part.get("Content-Disposition", ""))
                            ):
                                body = part.get_payload(decode=True).decode(
                                    errors="ignore"
                                )
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    # Insert into database
                    created_at = datetime.now()
                    try:
                        cursor.execute(
                            """
                            INSERT INTO emails (
                                uid, subject, sender, sender_name, sender_email,
                                body, type, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                uid,
                                subject,
                                sender,
                                sender_name,
                                sender_email,
                                body,
                                "received",
                                created_at,
                            ),
                        )
                        conn.commit()
                    except Exception as insert_err:
                        print(f"Insert error: {insert_err}")
                        conn.rollback()
                        continue

                    email_data.append(
                        {
                            "uid": uid,
                            "subject": subject,
                            "sender": sender,
                            "sender_name": sender_name,
                            "sender_email": sender_email,
                            "body": body,
                            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

        cursor.close()
        conn.close()
        mail.logout()

        return jsonify(email_data), 200

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"error": str(e)}), 500


def send_email(to_email, subject, body, original_uid=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = ZOHO_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP_SSL(
            "smtp.zoho.in", 465
        )  # Changed to SMTP_SSL with port 465
        server.login(ZOHO_EMAIL, ZOHO_PASSWORD)

        server.sendmail(ZOHO_EMAIL, to_email, msg.as_string())
        server.quit()

        # Store the sent email in the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user details for the recipient if they exist
        cursor.execute("SELECT id, name FROM users_login WHERE email = %s", (to_email,))
        user = cursor.fetchone()
        recipient_id = user[0] if user else None
        recipient_name = user[1] if user else to_email.split("@")[0]

        sent_at = datetime.now()

        # Store the sent email
        cursor.execute(
            """
                INSERT INTO emails (subject, recipient_email, recipient_name, body, type, created_at, related_uid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (subject, to_email, recipient_name, body, "sent", sent_at, original_uid),
        )

        # If this is a reply, update the original email's reply status
        if original_uid:
            cursor.execute(
                "UPDATE emails SET reply_status = 'Yes' WHERE uid = %s AND type = 'received'",
                (original_uid,),
            )

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Email sent successfully!"}, 200
    except Exception as e:
        return {"error": f"Error sending email: {str(e)}"}, 500


def delete_email(uid):
    try:
        # Connect to mail server
        mail = imaplib.IMAP4_SSL("imap.zoho.in")
        mail.login(ZOHO_EMAIL, ZOHO_PASSWORD)
        mail.select("inbox")

        # Find the message with UID
        status, msg_data = mail.uid("SEARCH", None, f"UID {uid}")
        if status != "OK" or not msg_data[0]:
            mail.logout()
            return jsonify({"error": f"Email with UID {uid} not found."}), 404

        # Delete the email
        mail.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
        mail.expunge()
        mail.logout()

        # Optional: Mark as deleted in the database (if you're storing emails)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE emails SET deleted = TRUE, deleted_at = %s WHERE uid = %s",
            (datetime.now(), uid),
        )
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        if rows_affected == 0:
            return (
                jsonify(
                    {
                        "warning": f"Email with UID {uid} deleted from server but not found in database."
                    }
                ),
                200,
            )

        return jsonify({"message": f"Email with UID {uid} deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"Error deleting email: {str(e)}"}), 500


# Function to get all emails (both received and sent)
def get_all_emails():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT * FROM emails 
            WHERE deleted = FALSE 
            ORDER BY created_at DESC
            """
        )

        emails = cursor.fetchall()
        cursor.close()
        conn.close()

        return emails
    except Exception as e:
        return f"Error retrieving emails: {str(e)}"


def create_review():
    data = request.json
    product_id = data.get("product_id")
    customer_id = data.get("customer_id")
    seller_id = data.get("seller_id")
    rating = data.get("rating")
    review_text = data.get("review_text")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO customer_reviews (product_id, customer_id, seller_id, rating, review_text) 
    VALUES (%s, %s, %s, %s, %s) RETURNING review_id;
    """
    cursor.execute(query, (product_id, customer_id, seller_id, rating, review_text))

    review_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return (
        jsonify({"message": "Review added successfully", "review_id": review_id}),
        201,
    )


def get_reviews_by_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT review_id, product_id, customer_id, seller_id, rating, review_text, created_at
    FROM customer_reviews WHERE product_id = %s;
    """
    cursor.execute(query, (product_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(reviews)


def get_reviews_by_seller(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    SELECT review_id, product_id, customer_id, rating, review_text, created_at
    FROM customer_reviews WHERE seller_id = %s;
    """
    cursor.execute(query, (seller_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(reviews)


def get_all_reviews():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM customer_reviews;"
    cursor.execute(query)
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(reviews)


def update_review(id):
    data = request.json
    rating = data.get("rating")
    review_text = data.get("review_text")

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    UPDATE customer_reviews SET rating = %s, review_text = %s WHERE review_id = %s;
    """
    cursor.execute(query, (rating, review_text, id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Review updated successfully"})


def delete_review(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "DELETE FROM customer_reviews WHERE review_id = %s;"
    cursor.execute(query, (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Review deleted successfully"})


def get_general_settings():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM general_settings ORDER BY id DESC LIMIT 1")
    settings = cursor.fetchone()
    cursor.close()
    conn.close()

    if settings:
        return jsonify(settings), 200
    return jsonify({"message": "No settings found"}), 404


def create_settings():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO general_settings (
            maintenance_mode, company_name, phone, email, 
            country, timezone, language, address, 
            latitude, longitude, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """,
        (
            data.get("maintenance_mode", False),
            data.get("company_name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("country", ""),
            data.get("timezone", ""),
            data.get("language", ""),
            data.get("address", ""),
            data.get("latitude", ""),
            data.get("longitude", ""),
            datetime.now(),
        ),
    )

    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Settings created successfully", "id": new_id}), 201


def update_settings():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the most recent settings record
    cursor.execute("SELECT id FROM general_settings ORDER BY id DESC LIMIT 1")
    last_setting = cursor.fetchone()

    if not last_setting:
        cursor.close()
        conn.close()
        return jsonify({"message": "Settings not found"}), 404

    cursor.execute(
        """
        UPDATE general_settings SET
            maintenance_mode = %s,
            company_name = %s,
            phone = %s,
            email = %s,
            country = %s,
            timezone = %s,
            language = %s,
            address = %s,
            latitude = %s,
            longitude = %s,
            updated_at = %s
        WHERE id = %s
    """,
        (
            data.get("maintenance_mode", False),
            data.get("company_name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("country", ""),
            data.get("timezone", ""),
            data.get("language", ""),
            data.get("address", ""),
            data.get("latitude", ""),
            data.get("longitude", ""),
            datetime.now(),
            last_setting[0],
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Settings updated successfully"}), 200


def get_payment_options():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT cash_on_delivery, digital_payment, offline_payment FROM payment_options ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return jsonify(
            {
                "cashOnDelivery": row[0],
                "digitalPayment": row[1],
                "offlinePayment": row[2],
            }
        )
    else:
        return jsonify(
            {"cashOnDelivery": False, "digitalPayment": False, "offlinePayment": False}
        )


def save_payment_options():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if there is already a row
    cur.execute("SELECT id FROM payment_options ORDER BY id DESC LIMIT 1")
    existing = cur.fetchone()

    if existing:
        # Update the existing record
        cur.execute(
            """
            UPDATE payment_options
            SET cash_on_delivery = %s,
                digital_payment = %s,
                offline_payment = %s
            WHERE id = %s
        """,
            (
                data["cashOnDelivery"],
                data["digitalPayment"],
                data["offlinePayment"],
                existing[0],
            ),
        )
    else:
        # Insert new record
        cur.execute(
            """
            INSERT INTO payment_options (cash_on_delivery, digital_payment, offline_payment)
            VALUES (%s, %s, %s)
        """,
            (data["cashOnDelivery"], data["digitalPayment"], data["offlinePayment"]),
        )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Payment options saved successfully"}), 201


def save_or_update_product_settings():
    data = request.json
    reorder_level = data.get("reorderLevel")  # Match frontend camelCase naming
    digital_product = data.get("digitalProduct")  # Match frontend camelCase naming
    show_brand = data.get("showBrand")  # Match frontend camelCase naming

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if there's already an entry
    cur.execute("SELECT id FROM product_settings LIMIT 1")
    existing = cur.fetchone()

    try:
        if existing:
            cur.execute(
                """
                UPDATE product_settings
                SET reorder_level = %s,
                    digital_product = %s,
                    show_brand = %s
                WHERE id = %s
            """,
                (reorder_level, digital_product, show_brand, existing[0]),
            )
        else:
            cur.execute(
                """
                INSERT INTO product_settings (reorder_level, digital_product, show_brand)
                VALUES (%s, %s, %s)
            """,
                (reorder_level, digital_product, show_brand),
            )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Product settings saved successfully"}), 201
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500


def get_product_settings():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT reorder_level, digital_product, show_brand FROM product_settings LIMIT 1"
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return jsonify(
                {
                    "reorderLevel": row[0],
                    "digitalProduct": row[1],
                    "showBrand": row[2],
                }
            )
        else:
            return jsonify(
                {"reorderLevel": 10, "digitalProduct": False, "showBrand": False}
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_priority():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Ensure at least one row exists
    cursor.execute("SELECT COUNT(*) FROM priority_sorting")
    count = cursor.fetchone()
    if count == 0:
        cursor.execute(
            "INSERT INTO priority_sorting (brand, category, vendor) VALUES (TRUE, TRUE, TRUE)"
        )
        conn.commit()

    # Fetch the row (assumes id=1 exists)
    cursor.execute("SELECT * FROM priority_sorting ORDER BY id LIMIT 1")
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(row)


def update_priority():
    data = request.json
    brand = data.get("brand", True)
    category = data.get("category", True)
    vendor = data.get("vendor", True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure at least one row exists
    cursor.execute("SELECT COUNT(*) FROM priority_sorting")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO priority_sorting (brand, category, vendor) VALUES (%s, %s, %s)",
            (brand, category, vendor),
        )
    else:
        cursor.execute(
            """
            UPDATE priority_sorting 
            SET brand = %s, category = %s, vendor = %s 
            WHERE id = (SELECT id FROM priority_sorting ORDER BY id LIMIT 1)
        """,
            (brand, category, vendor),
        )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Priority updated successfully."})


def get_order_settings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)  # Use dictionary cursor to return column names
    
    try:
        cur.execute("SELECT * FROM order_settings ORDER BY id DESC LIMIT 1;")
        row = cur.fetchone()
        for key in ["order_delivery_verification", "minimum_order_amount", 
                   "show_billing_address", "free_delivery", "guest_checkout"]:
            if key in row:
                row[key] = bool(row[key])
        
        return jsonify(row)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

def save_order_settings():
    data = request.json

    # Validate incoming data to ensure it has all the required fields
    required_fields = [
        "order_delivery_verification", "minimum_order_amount", "show_billing_address",
        "free_delivery", "guest_checkout", "refund_days", "delivery_responsibility", "free_delivery_over"
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if a record already exists
        cur.execute("SELECT id FROM order_settings LIMIT 1;")
        existing = cur.fetchone()

        if existing:
            # Update the existing record
            cur.execute(
                """
                UPDATE order_settings SET
                    order_delivery_verification = %s,
                    minimum_order_amount = %s,
                    show_billing_address = %s,
                    free_delivery = %s,
                    guest_checkout = %s,
                    refund_days = %s,
                    delivery_responsibility = %s,
                    free_delivery_over = %s
                WHERE id = %s;
                """,
                (
                    bool(data["order_delivery_verification"]),
                    bool(data["minimum_order_amount"]),
                    bool(data["show_billing_address"]),
                    bool(data["free_delivery"]),
                    bool(data["guest_checkout"]),
                    int(data["refund_days"]),
                    data["delivery_responsibility"],
                    float(data["free_delivery_over"]),
                    existing[0],
                ),
            )
        else:
            # Insert a new record
            cur.execute(
                """
                INSERT INTO order_settings (
                    order_delivery_verification,
                    minimum_order_amount,
                    show_billing_address,
                    free_delivery,
                    guest_checkout,
                    refund_days,
                    delivery_responsibility,
                    free_delivery_over
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    bool(data["order_delivery_verification"]),
                    bool(data["minimum_order_amount"]),
                    bool(data["show_billing_address"]),
                    bool(data["free_delivery"]),
                    bool(data["guest_checkout"]),
                    int(data["refund_days"]),
                    data["delivery_responsibility"],
                    float(data["free_delivery_over"]),
                ),
            )

        conn.commit()
        return jsonify({"message": "Settings saved successfully"}), 200
    
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

def get_vendor_settings():
    """Get all vendor settings"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM vendor_settings ORDER BY id DESC")
    settings = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify({"settings": [dict(row) for row in settings]}), 200

def save_vendor_settings():
    """Save new vendor settings"""
    data = request.json
    
    # Validate required fields
    required_fields = ['commission', 'enablePOS', 'vendorRegistration', 
                     'minimumOrder', 'vendorCanReply', 'forgotPasswordMethod',
                     'needProductApproval']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    try:
        # Ensure commission is a valid number
        commission = float(data['commission'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendor_settings (
                commission,
                enable_pos,
                vendor_registration,
                minimum_order,
                vendor_can_reply,
                forgot_password_method,
                need_approval_new_product,
                need_approval_product_shipping
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            commission,
            data['enablePOS'],
            data['vendorRegistration'],
            data['minimumOrder'],
            data['vendorCanReply'],
            data['forgotPasswordMethod'],
            data['needProductApproval']['newProduct'],
            data['needProductApproval']['productWiseShipping']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Settings saved successfully", "id": new_id}), 201
    
    except ValueError:
        return jsonify({"message": "Commission must be a valid number"}), 400
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    
def update_vendor_settings(setting_id):
    """Update vendor settings by ID"""
    data = request.json

    # Validate required fields
    required_fields = ['commission', 'enablePOS', 'vendorRegistration', 
                     'minimumOrder', 'vendorCanReply', 'forgotPasswordMethod',
                     'needProductApproval']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    try:
        # Ensure commission is a valid number
        commission = float(data['commission'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # First check if the record exists
        cur.execute("SELECT id FROM vendor_settings WHERE id = %s", (setting_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message": f"Settings with id {setting_id} not found"}), 404
        
        cur.execute("""
            UPDATE vendor_settings SET
                commission = %s,
                enable_pos = %s,
                vendor_registration = %s,
                minimum_order = %s,
                vendor_can_reply = %s,
                forgot_password_method = %s,
                need_approval_new_product = %s,
                need_approval_product_shipping = %s
            WHERE id = %s;
        """, (
            commission,
            data['enablePOS'],
            data['vendorRegistration'],
            data['minimumOrder'],
            data['vendorCanReply'],
            data['forgotPasswordMethod'],
            data['needProductApproval']['newProduct'],
            data['needProductApproval']['productWiseShipping'],
            setting_id
        ))

        rows_affected = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()

        if rows_affected > 0:
            return jsonify({"message": "Settings updated successfully"}), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except ValueError:
        return jsonify({"message": "Commission must be a valid number"}), 400
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    
def get_customer_settings():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM customer_settings LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        return jsonify(row)
    else:
        return jsonify({"error": "No settings found"}), 404


def update_customer_settings():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if any settings exist
    cursor.execute("SELECT COUNT(*) FROM customer_settings")
    count = cursor.fetchone()[0]
    
    try:
        if count > 0 and data.get("id"):  # Update if settings exist and ID is provided
            cursor.execute(
                """
                UPDATE customer_settings SET
                    customer_wallet = %s,
                    loyalty_point = %s,
                    referral_earning = %s,
                    add_refund_to_wallet = %s,
                    add_fund_to_wallet = %s,
                    max_add_fund_amount = %s,
                    min_add_fund_amount = %s,
                    equivalent_point = %s,
                    loyalty_point_earn_percentage = %s,
                    min_point_to_convert = %s,
                    referral_earnings = %s
                WHERE id = %s
                RETURNING id
                """,
                (
                    data["customerWallet"],
                    data["loyaltyPoint"],
                    data["referralEarning"],
                    data["addRefundToWallet"],
                    data["addFundToWallet"],
                    data["maxAddFundAmount"],
                    data["minAddFundAmount"],
                    data["equivalentPoint"],
                    data["loyaltyPointEarnPercentage"],
                    data["minPointToConvert"],
                    data["referralEarnings"],
                    data["id"],
                ),
            )
            result = cursor.fetchone()
            message = "Customer settings updated successfully"
        else:  # Insert if no settings exist or no ID provided
            # If there are existing settings but no ID provided, clear the table first
            if count > 0:
                cursor.execute("DELETE FROM customer_settings")
                
            cursor.execute(
                """
                INSERT INTO customer_settings (
                    customer_wallet,
                    loyalty_point,
                    referral_earning,
                    add_refund_to_wallet,
                    add_fund_to_wallet,
                    max_add_fund_amount,
                    min_add_fund_amount,
                    equivalent_point,
                    loyalty_point_earn_percentage,
                    min_point_to_convert,
                    referral_earnings
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data["customerWallet"],
                    data["loyaltyPoint"],
                    data["referralEarning"],
                    data["addRefundToWallet"],
                    data["addFundToWallet"],
                    data["maxAddFundAmount"],
                    data["minAddFundAmount"],
                    data["equivalentPoint"],
                    data["loyaltyPointEarnPercentage"],
                    data["minPointToConvert"],
                    data["referralEarnings"],
                ),
            )
            result = cursor.fetchone()
            message = "Customer settings created successfully"
            
        conn.commit()
        return jsonify({"message": message, "id": result[0]})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def delivery_settings():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM admin_delivery_settings LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return jsonify(result)
        else:
            return jsonify({"message": "No delivery settings found"}), 404
    
    elif request.method == 'POST':
        data = request.get_json()
        # Ensure we're getting the right format from the frontend
        upload_picture = data.get('uploadPicture', False)
        verification_method = data.get('verificationMethod', 'phone')
        
        # Insert only if settings don't exist
        cursor.execute("SELECT id FROM admin_delivery_settings LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            return jsonify({"message": "Settings already exist. Use PUT to update."}), 400
        
        cursor.execute("""
            INSERT INTO admin_delivery_settings (
                upload_picture_on_delivery,
                forgot_password_verification_method
            ) VALUES (%s, %s)
        """, (upload_picture, verification_method))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Delivery settings inserted successfully"})
    
    elif request.method == 'PUT':
        data = request.get_json()
        print(data)
        # Ensure we're getting the right format from the frontend
        upload_picture = data.get('uploadPicture', False)
        verification_method = data.get('verificationMethod', 'phone')
        
        cursor.execute("SELECT id FROM admin_delivery_settings LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE admin_delivery_settings
                SET upload_picture_on_delivery = %s,
                    forgot_password_verification_method = %s
                WHERE id = %s
            """, (upload_picture, verification_method, existing['id']))
            message = "Delivery settings updated successfully"
        else:
            cursor.execute("""
                INSERT INTO admin_delivery_settings (
                    upload_picture_on_delivery,
                    forgot_password_verification_method
                ) VALUES (%s, %s)
            """, (upload_picture, verification_method))
            message = "Delivery settings inserted (via PUT) successfully"
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": message})
    
    # Handle any other HTTP methods
    cursor.close()
    conn.close()
    return jsonify({"message": "Method not allowed"}), 405


def create_shipping_settings():
    data = request.get_json()
    shipping_type = data.get("shippingType", "inhouse")
    categories = data.get("categories", [])

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear previous settings before insert
    cursor.execute("DELETE FROM shipping_settings")

    for cat in categories:
        cursor.execute("""
            INSERT INTO shipping_settings (
                shipping_type, category_id, category_name, cost, status
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            shipping_type,
            cat["id"],
            cat["name"],
            cat["cost"],
            cat["status"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Shipping settings saved."}), 201

def get_shipping_settings():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT shipping_type, category_id, category_name, cost, status 
        FROM shipping_settings
    """)
    rows = cursor.fetchall()
    conn.close()

    categories = []
    for row in rows:
        categories.append({
            "id": row[1],
            "name": row[2],
            "cost": float(row[3]),
            "status": row[4]
        })

    return jsonify({
        "shippingType": rows[0][0] if rows else "inhouse",
        "categories": categories
    })

def update_shipping_settings():
    data = request.get_json()
    shipping_type = data.get("shippingType", "inhouse")
    categories = data.get("categories", [])

    conn = get_db_connection()
    cursor = conn.cursor()

    for cat in categories:
        cursor.execute("""
            UPDATE shipping_settings
            SET shipping_type = %s,
                cost = %s,
                status = %s
            WHERE category_id = %s
        """, (
            shipping_type,
            cat["cost"],
            cat["status"],
            cat["id"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Shipping settings updated."})

def get_delivery_restriction_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT country_enabled, zipcode_enabled FROM delivery_restriction_settings LIMIT 1")
    result = cursor.fetchone()

    if not result:
        response = {"countryEnabled": False, "zipCodeEnabled": False}
    else:
        response = {
            "countryEnabled": bool(result[0]),  # Ensure proper boolean conversion
            "zipCodeEnabled": bool(result[1])   # Ensure proper boolean conversion
        }

    cursor.close()
    conn.close()
    return jsonify(response)

def create_delivery_restriction_settings():
    data = request.get_json()
    country_enabled = bool(data.get("countryEnabled", False))  # Ensure proper boolean conversion
    zipcode_enabled = bool(data.get("zipCodeEnabled", False))  # Ensure proper boolean conversion

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM delivery_restriction_settings")
    cursor.execute("""
        INSERT INTO delivery_restriction_settings (country_enabled, zipcode_enabled)
        VALUES (%s, %s)
    """, (country_enabled, zipcode_enabled))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Settings saved"}), 201

def update_delivery_restriction_settings():
    data = request.get_json()
    country_enabled = bool(data.get("countryEnabled", False))  # Ensure proper boolean conversion
    zipcode_enabled = bool(data.get("zipCodeEnabled", False))  # Ensure proper boolean conversion

    conn = get_db_connection()
    cursor = conn.cursor()

    # If no row exists, insert
    cursor.execute("SELECT COUNT(*) FROM delivery_restriction_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO delivery_restriction_settings (country_enabled, zipcode_enabled)
            VALUES (%s, %s)
        """, (country_enabled, zipcode_enabled))
    else:
        cursor.execute("""
            UPDATE delivery_restriction_settings
            SET country_enabled = %s,
                zipcode_enabled = %s
        """, (country_enabled, zipcode_enabled))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Settings updated"}), 200

def invoice_settings():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM invoice_settings ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return jsonify({
                "terms": result[1],
                "business_identity_type": result[2],
                "business_identity_value": result[3],
                "logo_url": result[4],
                "is_active": bool(result[5])  # Convert to Python boolean
            })
        else:
            return jsonify({"message": "No invoice settings found."}), 404

    # For both POST and PUT
    terms = request.form.get("terms", "")
    identity_type = request.form.get("businessIdentityType", "")
    identity_value = request.form.get("businessIdentityValue", "")
    
    # Parse the is_active value from string to boolean
    is_active_str = request.form.get("isActive", "false")
    is_active = is_active_str.lower() == 'true'
    
    UPLOAD_FOLDER = os.path.join( r'uploads')
    logo_url = None
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            logo_folder = os.path.join(UPLOAD_FOLDER, 'invoice_logo')
            os.makedirs(logo_folder, exist_ok=True)
            file_path = os.path.join(logo_folder, filename)
            file.save(file_path)
            # Use URL style (forward slashes) for logo_url
            logo_url = f"/uploads/invoice_logo/{filename}"

    if request.method == "POST":
        # Clear old settings (if needed)
        cursor.execute("DELETE FROM invoice_settings")
        cursor.execute("""
            INSERT INTO invoice_settings (terms, business_identity_type, business_identity_value, logo_url, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """, (terms, identity_type, identity_value, logo_url, is_active))
    
    elif request.method == "PUT":
        # Update the most recent row
        cursor.execute("SELECT id FROM invoice_settings ORDER BY id DESC LIMIT 1")
        existing = cursor.fetchone()
        if existing:
            id = existing[0]
            if logo_url:
                cursor.execute("""
                    UPDATE invoice_settings
                    SET terms=%s, business_identity_type=%s, business_identity_value=%s, logo_url=%s, is_active=%s
                    WHERE id=%s
                """, (terms, identity_type, identity_value, logo_url, is_active, id))
            else:
                cursor.execute("""
                    UPDATE invoice_settings
                    SET terms=%s, business_identity_type=%s, business_identity_value=%s, is_active=%s
                    WHERE id=%s
                """, (terms, identity_type, identity_value, is_active, id))
        else:
            return jsonify({"message": "No existing invoice settings to update"}), 404

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Invoice settings saved successfully"})

def inhouse_settings_setup():
    # Create a single connection to be used in the function
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Define upload folder
        UPLOAD_FOLDER = os.path.join('uploads')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        if request.method == "GET":
            # Get shop settings
            cursor.execute("SELECT is_temporary_closed, min_order_amount, banner_image FROM inhouse_settings_setup WHERE shop_id = 1")
            data = cursor.fetchone()
            
            if data:
                return jsonify({
                    "shopId": 1,
                    "isTemporaryClosed": bool(data[0]),  # Ensure boolean value
                    "minOrderAmount": float(data[1]),
                    "bannerImage": data[2] if data[2] else ""
                })
            return jsonify({"error": "Business setup not found"}), 404
            
        # For POST and PUT methods
        # Check if content type is application/json or multipart/form-data
        content_type = request.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # Parse JSON data
            data = request.json
            is_temp_closed = bool(data.get("isTemporaryClosed"))
            min_order_amount = data.get("minOrderAmount")
            banner_image = None  # No file in JSON request
        else:
            # Parse form data
            is_temp_closed = request.form.get("isTemporaryClosed") == "true"
            min_order_amount = request.form.get("minOrderAmount")
            
            # Handle file upload
            banner_image = None
            if 'bannerImage' in request.files:
                file = request.files['bannerImage']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    banner_image_folder = os.path.join(UPLOAD_FOLDER, 'inhouse_banner')
                    os.makedirs(banner_image_folder, exist_ok=True)
                    file_path = os.path.join(banner_image_folder, filename)
                    file.save(file_path)
                    banner_image = f"/uploads/inhouse_banner/{filename}"
        
        # Check if record exists
        cursor.execute("SELECT COUNT(*) FROM inhouse_settings_setup WHERE shop_id = 1")
        exists = cursor.fetchone()[0] > 0
        
        if request.method == "POST" or (request.method == "PUT" and not exists):
            # For INSERT, include banner_image only if it exists
            if banner_image:
                cursor.execute(
                    "INSERT INTO inhouse_settings_setup (shop_id, is_temporary_closed, min_order_amount, banner_image) VALUES (1, %s, %s, %s)",
                    (is_temp_closed, min_order_amount, banner_image)
                )
            else:
                cursor.execute(
                    "INSERT INTO inhouse_settings_setup (shop_id, is_temporary_closed, min_order_amount) VALUES (1, %s, %s)",
                    (is_temp_closed, min_order_amount)
                )
            conn.commit()
            return jsonify({"message": "Business setup created successfully"})
            
        elif request.method == "PUT" and exists:
            # For UPDATE, only update banner_image if a new one is provided
            if banner_image:
                cursor.execute(
                    "UPDATE inhouse_settings_setup SET is_temporary_closed = %s, min_order_amount = %s, banner_image = %s WHERE shop_id = 1",
                    (is_temp_closed, min_order_amount, banner_image)
                )
            else:
                cursor.execute(
                    "UPDATE inhouse_settings_setup SET is_temporary_closed = %s, min_order_amount = %s WHERE shop_id = 1",
                    (is_temp_closed, min_order_amount)
                )
            conn.commit()
            return jsonify({"message": "Business setup updated successfully"})
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    
    finally:
        cursor.close()
        conn.close()

def handle_seo_settings():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if request.method == 'GET':
            cur.execute("SELECT * FROM seo_settings ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return jsonify({
                    "id": row[0],
                    "googleConsole": row[1],
                    "bingWebmaster": row[2],
                    "baiduWebmaster": row[3],
                    "yandexWebmaster": row[4]
                })
            else:
                return jsonify({"message": "No SEO settings found"}), 404

        data = request.get_json()
        google_console = data.get('googleConsole')
        bing_webmaster = data.get('bingWebmaster')
        baidu_webmaster = data.get('baiduWebmaster')
        yandex_webmaster = data.get('yandexWebmaster')

        if request.method == 'POST':
            cur.execute("""
                INSERT INTO seo_settings (google_console, bing_webmaster, baidu_webmaster, yandex_webmaster)
                VALUES (%s, %s, %s, %s)
            """, (google_console, bing_webmaster, baidu_webmaster, yandex_webmaster))
            conn.commit()
            message = "SEO settings created successfully"

        elif request.method == 'PUT':
            seo_id = data.get('id')
            if not seo_id:
                return jsonify({"error": "Missing 'id' for update"}), 400
            cur.execute("""
                UPDATE seo_settings
                SET google_console = %s,
                    bing_webmaster = %s,
                    baidu_webmaster = %s,
                    yandex_webmaster = %s
                WHERE id = %s
            """, (google_console, bing_webmaster, baidu_webmaster, yandex_webmaster, seo_id))
            conn.commit()
            message = "SEO settings updated successfully"

        cur.close()
        conn.close()
        return jsonify({"message": message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

