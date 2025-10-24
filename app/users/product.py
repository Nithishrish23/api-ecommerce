from flask import request, jsonify, session, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db_connection, verify_user, verify_admin_user
from datetime import datetime, timedelta
import os
from markupsafe import escape
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor
from app.authTokens import generate_token, validate_token
import json
import uuid
import random

def new_arrivals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id FROM product_selling 
            WHERE new_arrival >= %s
            """
        cursor.execute(query, (datetime.now() - timedelta(days=30),))
        product_selling_pids = cursor.fetchall()

        if not product_selling_pids:
            return jsonify({'new_arrivals': []}), 200

        # Extract pids into a list
        pids = [row['id'] for row in product_selling_pids]
        query = """
            SELECT * FROM add_product
            WHERE pid = ANY(%s)
            """
        cursor.execute(query, (pids,))
        products = cursor.fetchall()

        return jsonify({'new_arrivals': products}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch new arrivals'}), 500

    finally:
        if conn:
            conn.close()


def best_selling():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT id, best_selling FROM product_selling
        WHERE best_selling > 0
        ORDER BY best_selling DESC
        """
        cursor.execute(query)
        products = cursor.fetchall()

        return jsonify({'best_selling_products': products}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch best selling products'}), 500

    finally:
        if conn:
            conn.close()


def get_top_selling():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        three_months_ago = datetime.now() - timedelta(days=90)
        query = """
            SELECT id, top_selling FROM product_selling
            WHERE top_selling > 0 AND new_arrival >= %s
            ORDER BY top_selling DESC
            """
        cursor.execute(query, (three_months_ago,))
        products = cursor.fetchall()

        return jsonify({'top_selling_products': products}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch top-selling products'}), 500

    finally:
        if conn:
            conn.close()


def add_rating():
    try:
        data = request.json
        product_id = data.get('product_id')
        new_rating = data.get('rating')


        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch current rating and count
        cursor.execute("SELECT top_rating, rating_count FROM product_selling WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if product:
            current_rating = product[0] or 0
            rating_count = product[1] or 0

            # Calculate new average rating
            updated_count = rating_count + 1
            updated_rating = (current_rating * rating_count + new_rating) / updated_count

            # Update database
            cursor.execute(
                """
                UPDATE product_selling 
                SET top_rating = %s, rating_count = %s 
                WHERE id = %s
                """,
                (updated_rating, updated_count, product_id)
            )
            conn.commit()

            return jsonify({'message': 'Rating added successfully'}), 200
        else:
            return jsonify({'error': 'Product not found'}), 404

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to add rating'}), 500

    finally:
        if conn:
            conn.close()

def add_to_cart():
    try:

        data = request.json
        product_id = data.get('id')
        conn = get_db_connection()
        cursor = conn.cursor()

        # Increment best_selling count
        cursor.execute(
            "UPDATE product_selling SET best_selling = best_selling + 1 WHERE id = %s",
            (product_id,)
        )
        conn.commit()

        return jsonify({'message': 'Product added to cart'}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to add product to cart'}), 500

    finally:
        if conn:
            conn.close()


def get_featured_deals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM product_selling WHERE featured_deal = TRUE"
        cursor.execute(query)
        products = cursor.fetchall()

        return jsonify({'featured_deals': products}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch featured deals'}), 500

    finally:
        if conn:
            conn.close()

def set_featured():
    try:
        data = request.json
        product_id = data['id']
        is_featured = data['featured']

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE product_selling 
        SET featured_deal = %s 
        WHERE id = %s
        """
        cursor.execute(query, (is_featured, product_id))
        conn.commit()

        return jsonify({'message': 'Featured deal status updated'}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to update featured deal'}), 500

    finally:
        if conn:
            conn.close()


def get_user_orders():
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

        query = """
            SELECT o.order_id, o.product_id, o.order_date, o.quantity, o.total_price, 
                   p.product_name, p.product_description
            FROM orders o
            JOIN add_product p ON o.product_id = p.pid
            WHERE o.user_id = %s
            ORDER BY o.order_date DESC
        """
        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()

        if not orders:
            return jsonify({'message': 'No orders found for this user'}), 404

        return jsonify({'user_id': user_id, 'orders': orders}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Failed to fetch user orders'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def order_insert():
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

    data = request.json
    print(data)
    seller_id=data.get('seller_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    total_price=data.get('total_price')

    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO orders (user_id, seller_id,product_id, quantity, total_price)
        VALUES (%s, %s, %s, %s,%s)
        RETURNING order_id
    """

    cursor.execute(insert_query, (user_id,seller_id,product_id, quantity, total_price))

    order_id = cursor.fetchone()[0]

    conn.commit()

    return jsonify({'message': 'Order created successfully', 'order_id': order_id}), 201


def order_filter():

    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
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

    data=request.json
    status=data.get("filter")

    cursor.execute("select * from orders where user_id=%s and status=%s",(user_id,status))

    order=cursor.fetchall()
    cursor.close()
    conn.commit()
    return jsonify(order),200

