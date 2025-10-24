
from flask import request, jsonify, session, redirect, make_response
from app.database import get_db_connection, verify_user, verify_admin_user
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename




def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch all categories
    cursor.execute("SELECT id, name, priority FROM categories ORDER BY priority")
    categories = cursor.fetchall()

    category_list = []
    for category in categories:
        category_id = category[0]

        # Fetch subcategories for each category
        cursor.execute("SELECT id, name, priority FROM sub_categories WHERE category_id = %s ORDER BY priority", (category_id,))
        subcategories = cursor.fetchall()

        subcategory_list = []
        for subcategory in subcategories:
            sub_category_id = subcategory[0]

            # Fetch subsubcategories for each subcategory
            cursor.execute("SELECT id, name, priority FROM sub_sub_categories WHERE sub_category_id = %s ORDER BY priority", (sub_category_id,))
            subsubcategories = cursor.fetchall()

            subcategory_list.append({
                "id": sub_category_id,
                "name": subcategory[1],
                "priority": subcategory[2],
                "subSubCategories": [{"id": subsub[0], "name": subsub[1], "priority": subsub[2]} for subsub in subsubcategories]
            })

        category_list.append({
            "id": category_id,
            "name": category[1],
            "priority": category[2],
            "subCategories": subcategory_list
        })

    cursor.close()
    conn.close()

    return jsonify(category_list)