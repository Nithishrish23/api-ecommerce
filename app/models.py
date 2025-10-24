from flask import jsonify
from app.database import get_db_connection
import os

UPLOAD_FOLDER = r'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_dashboard_data(userid):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the record exists for the userid
        cursor.execute('SELECT * FROM dashboard WHERE userid = %s', (userid,))
        result = cursor.fetchone()

        if not result:
            # If no data exists, insert default values for the userid
            insert_query = '''
            INSERT INTO dashboard (userid)
            VALUES (%s)
            '''
            cursor.execute(insert_query, (userid,))
            conn.commit()

            # Fetch the newly inserted row to return it
            cursor.execute('SELECT * FROM dashboard WHERE userid = %s', (userid,))
            result = cursor.fetchone()

        if result:
            # Convert the result tuple into a dictionary for better readability
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, result))
            return jsonify(data), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except Exception as e:
        print(f"Error in get_dashboard_data: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()