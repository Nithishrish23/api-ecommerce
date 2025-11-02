import os.path

from flask import request, jsonify, session, redirect, make_response, send_from_directory
from app.database import get_db_connection, verify_user, verify_admin_user
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename

def get_product_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT pid,active_status, is_featured FROM product_status")
        status_record = cursor.fetchall()

        if not status_record:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify({'status': status_record}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        cursor.close()
        conn.close()


def toggle_product_status(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT active_status FROM product_status WHERE pid = %s", (product_id,))
        status_record = cursor.fetchone()

        if not status_record:
            return jsonify({'error': 'Product not found'}), 404

        current_status = status_record['active_status']
        new_status = not current_status

        cursor.execute(
            "UPDATE product_status SET active_status = %s WHERE pid = %s",
            (new_status, product_id)
        )
        conn.commit()

        return jsonify({'success': True, 'active_status': new_status}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        cursor.close()
        conn.close()


def toggle_product_featured(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT is_featured FROM product_status WHERE pid = %s", (product_id,))
        featured_record = cursor.fetchone()

        if not featured_record:
            return jsonify({'error': 'Product not found'}), 404

        current_featured = featured_record['is_featured']
        new_featured = not current_featured

        # Update the featured status
        cursor.execute(
            "UPDATE product_status SET is_featured = %s WHERE pid = %s",
            (new_featured, product_id)
        )
        conn.commit()

        return jsonify({'success': True, 'is_featured': new_featured}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        cursor.close()
        conn.close()


def add_policy(policy):
    table_mapping = {
        "terms": ("terms_and_conditions", "terms"),
        "refund": ("refund_policy", "refund"),
        "privacy": ("privacy_policy", "privacy"),
        "return": ("return_policy", "return"),
        "cancellation": ("cancellation_policy", "cancellation"),
        "shipping": ("shipping_policy", "shipping"),
        "about": ("about_us", "about"),
        "faq": ("faq", "faq"),
        "reliability": ("company_reliability", "reliability")
    }

    if policy not in table_mapping:
        return jsonify({"error": "Invalid policy type"}), 400

    table_name, column_name = table_mapping[policy]
    try:
        con = get_db_connection()
        cur = con.cursor(cursor_factory=RealDictCursor)
        data = request.json
        text = data.get(column_name)

        cur.execute(f"SELECT id FROM {table_name} LIMIT 1")
        existing_record = cur.fetchone()

        if existing_record:
            cur.execute(f"UPDATE {table_name} SET {column_name} = %s WHERE id = %s", (text, existing_record[0]))
            message = f"{policy.replace('_', ' ').title()} updated successfully"
        else:
            cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (%s)", (text,))
            message = f"{policy.replace('_', ' ').title()} added successfully"

        con.commit()
        cur.close()
        con.close()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def show_policy(policy):
    table_mapping = {
        "terms": ("terms_and_conditions", "terms"),
        "refund": ("refund_policy", "refund"),
        "privacy": ("privacy_policy", "privacy"),
        "return": ("return_policy", "return"),
        "cancellation": ("cancellation_policy", "cancellation"),
        "shipping": ("shipping_policy", "shipping"),
        "about": ("about_us", "about"),
        "faq": ("faq", "faq"),
        "reliability": ("company_reliability", "reliability")
    }

    if policy not in table_mapping:
        return jsonify({"error": "Invalid policy type"}), 400

    table_name, column_name = table_mapping[policy]

    try:
        con = get_db_connection()
        cur = con.cursor(cursor_factory=RealDictCursor)

        cur.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
        record = cur.fetchone()

        cur.close()
        con.close()

        if record:
            return jsonify(record), 200
        else:
            return jsonify({"message": "No data found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def social_media():
    try:
        data = request.json
        social_fields = ["facebook", "instagram", "X", "linkedin", "pinterest", "whatsapp"]
        filled_fields = {key: value for key, value in data.items() if value and key in social_fields}

        if len(filled_fields) != 1:
            return jsonify({"error": "Only one social media field should be filled at a time"}), 400
        column_name, column_value = next(iter(filled_fields.items()))

        con = get_db_connection()
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"UPDATE social_media SET {column_name} = %s WHERE {column_name} IS NOT NULL", (column_value,))

        if cur.rowcount == 0:
            cur.execute(f"INSERT INTO social_media ({column_name}) VALUES (%s)", (column_value,))

        con.commit()
        cur.close()
        con.close()

        return jsonify({"message": f"{column_name} updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def show_media():
    con = get_db_connection()
    cur = con.cursor(cursor_factory=RealDictCursor)

    cur.execute(f"SELECT * FROM social_media")
    record = cur.fetchall()

    if record:
        return jsonify({"media": record}), 200
    else:
        return jsonify({"message": "No data found"}), 404


def banner_setup():
    con = get_db_connection()
    cur = con.cursor(cursor_factory=RealDictCursor)

    data = request.form.to_dict()
    files = request.files

    banner_image = files.get('banner_image')
    banner_type = data.get('banner_type')
    published = data.get('published')

    if banner_image and banner_image.filename:
        file_name = secure_filename(banner_image.filename)
        file_path = os.path.join('./uploads/banner', file_name)
        os.makedirs('./uploads/banner', exist_ok=True)
        banner_image.save(file_path)

    cur.execute('''
    Insert into banner_setup (image,banner_type,published) values (%s,%s,%s) RETURNING id
    ''', (file_path, banner_type, published))
    banner_id = cur.fetchone()['id']
    con.commit()
    cur.close()
    con.close()
    return jsonify({"message": "Banner added", "id": banner_id})


def get_banners():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM banner_setup;")
    banners = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(banners)


def update_banner(id):
    data = request.json
    banner_image = data.get('image')
    banner_type = data.get('banner_type')
    published = data.get('published')

    if banner_image and banner_image.filename:
        file_name = secure_filename(banner_image.filename)
        file_path = os.path.join('./uploads/banner', file_name)
        os.makedirs('./uploads/banner', exist_ok=True)
        banner_image.save(file_path)

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "UPDATE banner_setup SET image=%s, banner_type=%s, published=%s WHERE id=%s RETURNING id;",
        (file_path, banner_type, published, id)
    )
    updated_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_id:
        return jsonify({"message": "Banner updated", "id": id})
    else:
        return jsonify({"error": "Banner not found"}), 404


def delete_banner(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("DELETE FROM banner_setup WHERE id=%s RETURNING id;", (id,))
    deleted_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted_id:
        return jsonify({"message": "Banner deleted", "id": id})
    else:
        return jsonify({"error": "Banner not found"}), 404


def add_coupon():
    data = request.json
    keys = ["coupon_type", "coupon_title", "coupon_code", "coupon_Bearer", "vendor",
            "customer", "usage_limit", "discount_type", "discount_amount", "minimum_purchase",
            "start_date", "expiry_date"]

    values = [data.get(k) for k in keys]

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        f"INSERT INTO coupons ({', '.join(keys)}) VALUES ({', '.join(['%s'] * len(keys))}) RETURNING id;",
        values
    )
    coupon_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Coupon added", "id": coupon_id}), 201


def get_coupons():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM coupons;")
    coupons = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(coupons)


def update_coupon(id):
    data = request.json
    update_fields = [f"{key}=%s" for key in data.keys()]
    values = list(data.values()) + [id]

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        f"UPDATE coupons SET {', '.join(update_fields)} WHERE id=%s RETURNING id;",
        values
    )
    updated_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_id:
        return jsonify({"message": "Coupon updated", "id": id})
    else:
        return jsonify({"error": "Coupon not found"}), 404


def delete_coupon(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("DELETE FROM coupons WHERE id=%s RETURNING id;", (id,))
    deleted_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted_id:
        return jsonify({"message": "Coupon deleted", "id": id})
    else:
        return jsonify({"error": "Coupon not found"}), 404


def get_flash_deals():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id, title, duration, status, active_products, is_published FROM flash_deals")
    deals = cursor.fetchall()
    conn.close()
    return jsonify(deals)


def add_flash_deal():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    data = request.json
    files = request.files
    flash_image = files.get("image")
    if flash_image and flash_image.filename:
        file_name = secure_filename(flash_image.filename)
        file_path = os.path.join('./uploads/flash', file_name)
        os.makedirs('./uploads/flash', exist_ok=True)
        flash_image.save(file_path)

    cursor.execute(
        "INSERT INTO flash_deals (title, duration, status, active_products, is_published) VALUES (%s, %s, %s, %s, %s)",
        (data["title"], data["duration"], data["status"], data["activeProducts"], data["isPublished"]))
    conn.commit()
    conn.close()
    return {"message": "Flash deal added successfully!"}, 201


def update_flash_deal(deal_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    data = request.json
    print(data)
    cursor.execute(
        "UPDATE flash_deals SET title=%s, duration=%s, status=%s, active_products=%s, is_published=%s WHERE id=%s",
        (data["title"], data["duration"], data["status"], data["activeProducts"], data["isPublished"], deal_id))
    conn.commit()
    conn.close()
    return {"message": "Flash deal updated successfully!"}


def delete_flash_deal(deal_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("DELETE FROM flash_deals WHERE id=%s", (deal_id,))
    conn.commit()
    conn.close()
    return {"message": "Flash deal deleted successfully!"}


def get_day_deals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, title, product, status FROM deals_of_the_day")
        deals = cursor.fetchall()
        cursor.close()
        return jsonify({"success": True, "deals": deals}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def add_day_deal():
    try:
        data = request.json
        print(data)
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO deals_of_the_day (title, product, status) VALUES (%s, %s, %s) RETURNING id",
            (data["title"], data["product"], data["status"]),
        )
        deal_id = cursor.fetchone()
        # deal_id = "success"
        conn.commit()
        cursor.close()
        return jsonify({"success": True, "deal_id": deal_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def update_day_deal(deal_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "UPDATE deals_of_the_day SET title=%s, product=%s, status=%s WHERE id=%s",
            (data["title"], data["product"], data["status"], deal_id),
        )
        conn.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Deal updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def delete_day_deal(deal_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("DELETE FROM deals_of_the_day WHERE id = %s", (deal_id,))
        conn.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Deal deleted"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_feature_deal():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM feature_deals ORDER BY id ASC")
    deals = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(deals)


def add_feature_deal():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
    INSERT INTO feature_deals (title, start_date, end_date, status, is_active)
    VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(query, (data['title'], data['start_date'], data['end_date'], data['status'], data['is_active']))
    new_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Feature deal added successfully!", "id": new_id}), 201


def update_feature_deal(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    UPDATE feature_deals 
    SET title = %s, start_date = %s, end_date = %s, status = %s, is_active = %s 
    WHERE id = %s;
    """
    cursor.execute(query, (data['title'], data['start_date'], data['end_date'], data['status'], data['is_active'], id))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Feature deal updated successfully!"})


def delete_feature_deal(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feature_deals WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Feature deal deleted successfully!"})


def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""SELECT u.id, u.name, u.email,o.quantity,u.mobile_number,  
                      TO_CHAR(u.created_at, 'DD/MM/YYYY') AS created_at
               FROM users_login u
               FULL JOIN orders o ON u.id = o.user_id
            """)
    customers = cursor.fetchall()
    conn.close()
    return jsonify(customers)


def filter_customers():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT u.id, u.name, u.email, o.quantity, u.mobile_number,  
               TO_CHAR(u.created_at, 'DD/MM/YYYY') AS created_at 
        FROM users_login u
        FULL JOIN orders o ON u.id = o.user_id
    """

    params = []
    conditions = []

    if 'searchTerm' in data and data['searchTerm']:
        conditions.append("u.name ILIKE %s OR u.email ILIKE %s OR u.mobile_number ILIKE %s")
        search_term = f"%{data['searchTerm']}%"
        params.extend([search_term, search_term, search_term])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY u.id LIMIT %s"
    params.append(data.get('limit', 100))

    cursor.execute(query, params)
    customers = cursor.fetchall()
    conn.close()
    return jsonify(customers)


def add_new_vendor():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        token_payload = getattr(request, 'token_payload', None)

        if token_payload:
            user_id = token_payload.get('user_id')
        else:
            user_id = session.get('user_id')

        first_name = data.get("firstName")
        last_name = data.get("lastName")
        phone = data.get("phone")
        email = data.get("email")
        password = data.get("password")
        shop_name = data.get("shopName")
        shop_address = data.get("shopAddress")

        if not (first_name and last_name and phone and email and password and shop_name and shop_address):
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM vendors WHERE email = %s", (email,))
        existing_vendor = cursor.fetchone()
        if existing_vendor:
            return jsonify({"error": "Vendor with this email already exists"}), 409

        # Insert vendor into the database
        cursor.execute("""
            INSERT INTO vendors (user_id,first_name, last_name, phone, email, password, shop_name, shop_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, first_name, last_name, phone, email, password, shop_name, shop_address))
        vendor_id = cursor.fetchone()["id"]
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Vendor added successfully", "vendor_id": vendor_id}), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500


def get_vendors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM vendors;")
        vendors = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(vendors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_vendor(vendor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM vendors WHERE id = %s;", (vendor_id,))
        vendor = cursor.fetchone()

        cursor.close()
        conn.close()

        if vendor:
            return jsonify(vendor), 200
        else:
            return jsonify({"message": "Vendor not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_vendor(vendor_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE vendors 
        SET first_name = %s, last_name = %s, phone = %s, email = %s, shop_name = %s, shop_address = %s
        WHERE id = %s;
        """
        cursor.execute(query, (
            data['firstName'], data['lastName'], data['phone'], data['email'],
            data['shopName'], data['shopAddress'], vendor_id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Vendor updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_vendor(vendor_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM vendors WHERE id = %s;", (vendor_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Vendor deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def product_review():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM product_review")
        reviews = cursor.fetchall()
        conn.close()
        return jsonify(reviews)

    elif request.method == 'POST':
        data = request.json
        cursor.execute("""
            INSERT INTO product_review (seller_user_id, product_id, user_login_id, content, Rating)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (data['seller_user_id'], data['product_id'], data['user_login_id'], data.get('content'), data['Rating']))
        review_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({"message": "Review added", "review_id": review_id}), 201

    elif request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE product_review
            SET content = %s, Rating = %s
            WHERE id = %s
        """, (data['content'], data['Rating'], data['id']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Review updated"})

    elif request.method == 'DELETE':
        data = request.json
        cursor.execute("DELETE FROM product_review WHERE id = %s", (data['id'],))
        conn.commit()
        conn.close()
        return jsonify({"message": "Review deleted"})


def cart():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        user_id = request.args.get('user_id')
        cursor.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
        cart_items = cursor.fetchall()
        conn.close()
        return jsonify(cart_items)

    elif request.method == 'POST':
        data = request.json
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, product_id) DO UPDATE 
            SET quantity = cart.quantity + EXCLUDED.quantity
            RETURNING id
        """, (data['user_id'], data['product_id'], data.get('quantity', 1)))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item added to cart"}), 201

    elif request.method == 'PUT':
        data = request.json
        cursor.execute("""
            UPDATE cart SET quantity = %s WHERE id = %s
        """, (data['quantity'], data['id']))
        conn.commit()
        conn.close()
        return jsonify({"message": "Cart updated"})

    elif request.method == 'DELETE':
        data = request.json
        cursor.execute("DELETE FROM cart WHERE id = %s", (data['id'],))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item removed from cart"})


def add_brands():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.form.to_dict()
        files = request.files

        brand_name = data.get("Brand_name")
        image_alt_name = data.get("image_alt_name")
        image_file = files.get("image_filename")

        if not brand_name:
            return jsonify({"error": "Brand name is required"}), 400

        image_filename = None
        if image_file:
            image_filename = f"{brand_name}_{image_file.filename}"
            image_path = os.path.join('./uploads/brands_image', image_filename)
            os.makedirs('./uploads/brands_image', exist_ok=True)
            image_file.save(image_path)
        cursor.execute(
            """
            INSERT INTO brands (Brand_name, image_alt_name, image_filename)
            VALUES (%s, %s, %s)
            ON CONFLICT (Brand_name) 
            DO UPDATE SET image_alt_name = EXCLUDED.image_alt_name, 
            image_filename = EXCLUDED.image_filename
            """,
            (brand_name, image_alt_name, image_filename)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Brand saved successfully", "brand": brand_name}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_brands():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM brands")
        brands = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"brands": brands}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def edit_brand(brand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.form.to_dict()
        files = request.files

        brand_name = data.get("Brand_name")
        image_alt_name = data.get("image_alt_name")
        image_file = files.get("image_filename")

        if not brand_name:
            return jsonify({"error": "Brand name is required"}), 400

        image_filename = None

        if image_file:
            image_filename = f"{brand_name}_{image_file.filename}"
            image_path = os.path.join('./uploads/brands_image', image_filename)
            image_file.save(image_path)

        # Update database
        cursor.execute(
            "UPDATE brands SET Brand_name = %s, image_alt_name = %s, image_filename = %s WHERE id = %s",
            (brand_name, image_alt_name, image_filename, brand_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Brand updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_brand(brand_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if brand exists
        cursor.execute("SELECT image_filename FROM brands WHERE id = %s", (brand_id,))
        brand = cursor.fetchone()

        if not brand:
            return jsonify({"error": "Brand not found"}), 404

        if brand[0]:
            image_path = os.path.join('./uploads/brands_image', brand[0])
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete brand from database
        cursor.execute("DELETE FROM brands WHERE id = %s", (brand_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Brand deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_category():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        search_term = request.args.get('search', '')

        if search_term:
            cursor.execute("SELECT * FROM categories WHERE name ILIKE %s ORDER BY priority ASC", (f"%{search_term}%",))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY priority ASC")

        categories = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({"categories": categories}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def add_category():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        data = request.form.to_dict()
        files = request.files
        name = data.get("name")
        priority = data.get("priority", 1)
        home_category = data.get("home_category", "false").lower() == "true"
        if not name:
            return jsonify({"error": "Category name is required"}), 400

        image_path = None

        if 'image' in files:
            image_file = files['image']
            image_filename = f"{name.replace(' ', '_')}_{image_file.filename}"
            image_path = os.path.join("./uploads/category", image_filename)
            os.makedirs("./uploads/category", exist_ok=True)
            image_file.save(image_path)

        # Insert into database
        cursor.execute(
            "INSERT INTO categories (name, priority, image, home_category) VALUES (%s, %s, %s, %s)",
            (name, priority, image_path, home_category)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def edit_category(category_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.form.to_dict()
        files = request.files

        name = data.get("name")
        priority = data.get("priority", 1)
        home_category = data.get("home_category", "false").lower() == "true"

        if not name:
            return jsonify({"error": "Category name is required"}), 400

        image_filename = None

        if 'image' in files:
            image_file = files['image']
            image_filename = f"{name.replace(' ', '_')}_{image_file.filename}"
            image_path = os.path.join("./uploads/category", image_filename)
            os.makedirs("./uploads/category", exist_ok=True)
            image_file.save(image_path)

        cursor.execute(
            "UPDATE categories SET name = %s, priority = %s, image = %s, home_category = %s WHERE id = %s",
            (name, priority, image_filename, home_category, category_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Category updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_category(category_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT image FROM categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()

        if not category:
            return jsonify({"error": "Category not found"}), 404

        if category[0]:
            image_path = os.path.join("./uploads/category", category[0])
            if os.path.exists(image_path):
                os.remove(image_path)

        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Category deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def add_subcategory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        data = request.form.to_dict()

        name = data.get("name")
        category_id = data.get("category_id")
        priority = int(data.get("priority", 1))

        if not name or not category_id:
            return jsonify({"error": "Subcategory name and category_id are required"}), 400

        cursor.execute(
            "INSERT INTO sub_categories (name, category_id, priority) VALUES (%s, %s, %s) RETURNING *",
            (name, category_id, priority)
        )
        new_subcategory = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(new_subcategory), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_subcategories():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM sub_categories")
        subcategories = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(subcategories), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_subcategory(id):
    """Update an existing subcategory."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        data = request.json
        name = data.get("name")
        category_id = data.get("category_id")
        priority = int(data.get("priority", 1))

        if not name or not category_id:
            return jsonify({"error": "Subcategory name and category_id are required"}), 400

        cursor.execute("SELECT id FROM sub_categories WHERE id = %s", (id,))
        subcategory = cursor.fetchone()
        if not subcategory:
            return jsonify({"error": "Subcategory not found"}), 404

        cursor.execute(
            "UPDATE sub_categories SET name = %s, category_id = %s, priority = %s WHERE id = %s RETURNING *",
            (name, category_id, priority, id)
        )
        updated_subcategory = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(updated_subcategory), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_subcategory(id):
    """Delete a subcategory."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM sub_categories WHERE id = %s", (id,))
        subcategory = cursor.fetchone()

        if not subcategory:
            return jsonify({"error": "Subcategory not found"}), 404

        cursor.execute("DELETE FROM sub_categories WHERE id = %s RETURNING id", (id,))
        deleted = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Subcategory deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_sub_sub_category():
    data = request.json
    name = data.get("name")
    sub_category_id = data.get("sub_category_id")
    category_id = data.get("category_id")
    priority = data.get("priority", 1)

    if not name or not sub_category_id or not category_id:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sub_sub_categories (name, sub_category_id, category_id, priority) VALUES (%s, %s, %s, %s) RETURNING id",
        (name, sub_category_id, category_id, priority),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "SubSubCategory created successfully", "id": new_id}), 201


def get_all_sub_sub_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, sub_category_id, category_id, priority FROM sub_sub_categories ORDER BY priority")
    sub_sub_categories = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([
        {"id": sub[0], "name": sub[1], "sub_category_id": sub[2], "category_id": sub[3], "priority": sub[4]}
        for sub in sub_sub_categories
    ])


def get_sub_sub_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, sub_category_id, category_id, priority FROM sub_sub_categories WHERE id = %s",
                   (id,))
    sub_sub_category = cursor.fetchone()
    cursor.close()
    conn.close()

    if sub_sub_category:
        return jsonify({"id": sub_sub_category[0], "name": sub_sub_category[1], "sub_category_id": sub_sub_category[2],
                        "category_id": sub_sub_category[3], "priority": sub_sub_category[4]})
    else:
        return jsonify({"error": "SubSubCategory not found"}), 404


def update_sub_sub_category(id):
    data = request.json
    name = data.get("name")
    sub_category_id = data.get("sub_category_id")
    category_id = data.get("category_id")
    priority = data.get("priority", 1)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE sub_sub_categories SET name = %s, sub_category_id = %s, category_id = %s, priority = %s WHERE id = %s RETURNING id",
        (name, sub_category_id, category_id, priority, id),
    )

    if cursor.rowcount == 0:
        return jsonify({"error": "SubSubCategory not found"}), 404

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "SubSubCategory updated successfully"}), 200


def delete_sub_sub_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sub_sub_categories WHERE id = %s RETURNING id", (id,))

    if cursor.rowcount == 0:
        return jsonify({"error": "SubSubCategory not found"}), 404

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify("Deleted Successfully"), 200


def list_files():
    UPLOAD_FOLDER = os.path.join(r'uploads')
    file_structure = []
    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        relative_path = os.path.relpath(root, UPLOAD_FOLDER)
        if relative_path == ".":
            relative_path = ""
        folder_content = {
            "folder": relative_path,
            "subfolders": dirs,
            "files": [os.path.join(relative_path, file) for file in files]
        }
        file_structure.append(folder_content)
    return jsonify(file_structure)


def upload_file():
    UPLOAD_FOLDER = os.path.join(r'uploads')
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    folder = request.form.get('folder', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Secure the filename and create full path
        filename = secure_filename(file.filename)
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(folder_path, exist_ok=True)
        full_path = os.path.join(folder_path, filename)

        # Save the file
        file.save(full_path)
        return jsonify({"message": "File uploaded successfully"}), 201


def get_attributes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attributes")
    attributes = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{"id": attr[0], "name": attr[1]} for attr in attributes])


def add_attribute():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Attribute name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attributes (name) VALUES (%s) RETURNING id", (name,))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"id": new_id, "name": name}), 201


def update_attribute(id):
    data = request.json
    name = data.get("name")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE attributes SET name = %s WHERE id = %s RETURNING id", (name, id))
    updated_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if updated_id:
        return jsonify({"id": id, "name": name})
    else:
        return jsonify({"error": "Attribute not found"}), 404


def delete_attribute(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attributes WHERE id = %s RETURNING id", (id,))
    deleted_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if deleted_id:
        return jsonify({"message": "Attribute deleted successfully"})
    else:
        return jsonify({"error": "Attribute not found"}), 404


def get_notifications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications ORDER BY id DESC")
    notifications = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(notifications)


def add_notification():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    image = data.get('image', '')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO notifications (title, description, image) VALUES (%s, %s, %s) RETURNING id",
                (title, description, image))
    new_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Notification added", "id": new_id}), 201


def get_notifications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM push_notifications")
    notifications = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(notifications)


def update_notification(id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications
        SET title=%s, description=%s, image=%s, count=%s, status=%s
        WHERE id=%s
    """, (
        data['title'], data['description'], data.get('image', ''), data.get('count', 1), data.get('status', True), id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Notification updated successfully"})


def delete_notification(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notifications WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Notification deleted"}), 200


def create_push_notification():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO push_notifications (notification_id, language, notification_type, message, enabled)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (data['notification_id'], data['language'], data['notification_type'], data['message'], data['enabled']))

        notification_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Notification created", "id": notification_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_push_notifications():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM push_notifications")
        notifications = cur.fetchall()
        cur.close()
        conn.close()

        notifications_list = []
        for row in notifications:
            notifications_list.append({
                "id": row[0],
                "notification_id": row[1],
                "language": row[2],
                "notification_type": row[3],
                "message": row[4],
                "enabled": row[5]
            })
        return jsonify(notifications_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_push_notification(id):
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE push_notifications
            SET language=%s, notification_type=%s, message=%s, enabled=%s
            WHERE id=%s
        """, (data['language'], data['notification_type'], data['message'], data['enabled'], id))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Notification updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def delete_push_notification(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM push_notifications WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Notification deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_announcement():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO announcements (status, background_color, text_color, announcement_text)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (data['status'], data['backgroundColor'], data['textColor'], data['announcementText']))

        announcement_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Announcement created", "id": announcement_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_announcements():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("select * from announcements")
        announcements = cur.fetchall()
        cur.close()
        conn.close()

        announcements_list = [
            {
                "id": row["id"],  #
                "status": row["status"],
                "backgroundColor": row["background_color"],
                "textColor": row["text_color"],
                "announcementText": row["announcement_text"]
            }
            for row in announcements
        ]

        return jsonify(announcements_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_announcement(id):
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE announcements
            SET status=%s, background_color=%s, text_color=%s, announcement_text=%s
            WHERE id=%s
        """, (data['status'], data['backgroundColor'], data['textColor'], data['announcementText'], id))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Announcement updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_announcement(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM announcements WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Announcement deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Admin Order Management Functions
def get_admin_orders():
    """Get all orders for admin with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get filter parameters
        order_type = request.args.get('order_type', 'all')
        store = request.args.get('store', 'all')
        status = request.args.get('status', 'all')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search', '')

        query = """
            SELECT
                o.order_id,
                o.user_id,
                o.seller_id,
                o.product_id,
                o.quantity,
                o.total_price,
                o.status,
                o.order_date,
                u.name as customer_name,
                u.email as customer_email,
                u.mobile_number as customer_phone,
                p.product_name,
                s.name as seller_name,
                s.company_name as store_name
            FROM orders o
            LEFT JOIN users_login u ON o.user_id = u.id
            LEFT JOIN add_product p ON o.product_id = p.pid
            LEFT JOIN seller_users s ON o.seller_id = s.id
            WHERE 1=1
        """

        params = []

        if status != 'all':
            query += " AND o.status = %s"
            params.append(status)

        if store != 'all':
            query += " AND s.company_name ILIKE %s"
            params.append(f"%{store}%")

        if date_from:
            query += " AND o.order_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND o.order_date <= %s"
            params.append(date_to)

        if search:
            query += " AND (u.name ILIKE %s OR u.email ILIKE %s OR o.order_id::text ILIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        query += " ORDER BY o.order_date DESC"

        cursor.execute(query, params)
        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "orders": orders, "count": len(orders)}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_admin_order_details(order_id):
    """Get detailed information about a specific order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                o.*,
                u.name as customer_name,
                u.email as customer_email,
                u.mobile_number as customer_phone,
                p.product_name,
                p.product_description,
                p.product_thumbnail,
                s.name as seller_name,
                s.company_name as store_name,
                s.email as seller_email
            FROM orders o
            LEFT JOIN users_login u ON o.user_id = u.id
            LEFT JOIN add_product p ON o.product_id = p.pid
            LEFT JOIN seller_users s ON o.seller_id = s.id
            WHERE o.order_id = %s
        """, (order_id,))

        order = cursor.fetchone()
        cursor.close()
        conn.close()

        if order:
            return jsonify({"success": True, "order": order}), 200
        else:
            return jsonify({"success": False, "error": "Order not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def update_admin_order_status():
    """Admin updates order status"""
    try:
        data = request.json
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE orders
            SET status = %s
            WHERE order_id = %s
            RETURNING order_id
        """, (new_status, order_id))

        updated = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if updated:
            return jsonify({"success": True, "message": "Order status updated"}), 200
        else:
            return jsonify({"success": False, "error": "Order not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_admin_order_stats():
    """Get order statistics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_orders,
                COUNT(CASE WHEN status = 'Confirmed' THEN 1 END) as confirmed_orders,
                COUNT(CASE WHEN status = 'Packaging' THEN 1 END) as packaging_orders,
                COUNT(CASE WHEN status = 'Out for Delivery' THEN 1 END) as out_for_delivery_orders,
                COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_orders,
                COUNT(CASE WHEN status = 'Returned' THEN 1 END) as returned_orders,
                COUNT(CASE WHEN status = 'Failed to Deliver' THEN 1 END) as failed_orders,
                COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancelled_orders,
                SUM(total_price) as total_revenue,
                SUM(CASE WHEN status = 'Delivered' THEN total_price ELSE 0 END) as delivered_revenue
            FROM orders
        """)

        stats = cursor.fetchone()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "stats": stats}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
