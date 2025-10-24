from app.database import get_db_connection

def create():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_address (
    id SERIAL PRIMARY KEY,
    userid INT NOT NULL,
    FOREIGN KEY (userid) REFERENCES users_login(id) ON DELETE CASCADE,
    name text,
    phone_number text,
    pincode text,
    locality text,
    address text,
    state text,
    landmark text,
    alternate_phone text,
    address_type text,
    addressPurpose text,
    latitude text,
    longitude text
    );
    
    
    CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    seller_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    total_price NUMERIC(10, 2),
    status Text,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES seller_users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

''')
    con.commit()

create()