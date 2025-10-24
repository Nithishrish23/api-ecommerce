from flask import request, jsonify, session, redirect, make_response
from app.database import get_db_connection, verify_user, verify_admin_user
from markupsafe import escape
from psycopg2.extras import RealDictCursor

def address():
    data=request.json
    print(data)
    token_payload = getattr(request, 'token_payload', None)
    if token_payload:
        userid = token_payload.get('user_id')
    elif session.get('user'):
        userid = session.get('user')
    else:
        userid = escape(data.get('user'))

    if not userid:
        return jsonify({"error": "User ID not found"}), 401

    name=data.get('name')
    phoneNumber=data.get('phone_number')
    pinCode=data.get('pincode')
    locality=data.get('locality')
    address=data.get('address')
    state=data.get('state')
    landmark=data.get('landmark')
    alternatephone=data.get('alternate_phone')
    addresstype=data.get('address_type')
    latitude=data.get('latitude')
    longitude=data.get('longitude')
    addressPurpose=data.get('addresspurpose')

    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("""Insert into user_address(userid,name, phone_number, pincode, locality, address, state, landmark, alternate_phone, address_type,addresspurpose,latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            RETURNING *; 
        """,(userid,name,phoneNumber,pinCode,locality,address,state,landmark,alternatephone,addresstype,addressPurpose,latitude,longitude))
    new_address_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Address added successfully",
        "address_id": new_address_id
    }), 201

def address_view():
    token_payload = getattr(request, 'token_payload', None)
    if token_payload:
        userid = token_payload.get('user_id')
    elif session.get('user'):
        userid = session.get('user')

    if not userid:
        return jsonify({"error": "User ID not found"}), 401

    conn=get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT * FROM user_address
        WHERE userid = %s;
    """, (userid,))
    existing_address = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "address":existing_address
    }), 201


def address_delete(id):
    token_payload = getattr(request, 'token_payload', None)

    if token_payload:
        userid = token_payload.get('user_id')
    elif session.get('user'):
        userid = session.get('user')

    if not userid:
        return jsonify({"error": "User ID not found"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:

        cursor.execute("""
            DELETE FROM user_address
            WHERE userid = %s AND id = %s
            RETURNING *; 
        """, (userid, id))

        deleted_address = cursor.fetchone()
        conn.commit()

        if not deleted_address:
            return jsonify({"error": "Address not found"}), 404

        return jsonify({
            "message": "Address deleted successfully",
            "address": deleted_address
        }), 200

    except Exception as e:
        print("Error:", str(e))
        if conn:
            conn.rollback()
        return jsonify({"error": "Failed to delete address"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def edit_address(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    token_payload = getattr(request, 'token_payload', None)

    if token_payload:
        userid = token_payload.get('user_id')
    elif session.get('user'):
        userid = session.get('user')

    if not userid:
        return jsonify({"error": "User ID not found"}), 401

    try:
        update_data = data
        set_clauses = []
        values = []

        print("userid, id, data:", userid, id, data)

        for column, value in update_data.items():
            if column not in ['pid', 'userid']:  # Exclude 'pid' and 'userid' from update
                set_clauses.append(f"{column} = %s")
                values.append(value)

        values.append(id)
        values.append(userid)

        query = f"""
            UPDATE user_address
            SET {', '.join(set_clauses)}
            WHERE id = %s and userid = %s
            RETURNING *;
        """

        print("Executing query:", query)
        print("Values:", values)

        cursor.execute(query, tuple(values))
        updated_address = cursor.fetchone()

        conn.commit()

        if not updated_address:
            return jsonify({"error": "Failed to update address"}), 500

        return jsonify({
            "message": "Address updated successfully",
            "address": updated_address
        }), 200

    except Exception as e:
        print("Error:", str(e))
        if conn:
            conn.rollback()
        return jsonify({"error": "Failed to update address"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
