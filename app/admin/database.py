from app.database import get_db_connection


def create():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """
    
CREATE TABLE IF NOT EXISTS product_status (
        id SERIAL PRIMARY KEY,
        pid INT NOT NULL,
        userid INT NOT NULL,
        active_status BOOLEAN DEFAULT TRUE,
        is_featured BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pid) REFERENCES add_product(PID) ON DELETE CASCADE,
        FOREIGN KEY (userid) REFERENCES seller_users(id) ON DELETE CASCADE
        );
    
CREATE TABLE IF NOT EXISTS terms_and_conditions (
        id SERIAL PRIMARY KEY,
        terms TEXT
        );
CREATE TABLE IF NOT EXISTS refund_policy (
        id SERIAL PRIMARY KEY,
        refund TEXT
        );
CREATE TABLE IF NOT EXISTS privacy_policy (
        id SERIAL PRIMARY KEY,
        privacy TEXT
        );
CREATE TABLE IF NOT EXISTS return_policy (
        id SERIAL PRIMARY KEY,
        return TEXT
        );
CREATE TABLE IF NOT EXISTS cancellation_policy (
        id SERIAL PRIMARY KEY,
        cancellation TEXT
        );
CREATE TABLE IF NOT EXISTS shipping_policy (
        id SERIAL PRIMARY KEY,
        shipping TEXT
        );
CREATE TABLE IF NOT EXISTS about_us (
        id SERIAL PRIMARY KEY,
        about TEXT
        );
CREATE TABLE IF NOT EXISTS faq (
        id SERIAL PRIMARY KEY,
        faq TEXT
        );
CREATE TABLE IF NOT EXISTS company_reliability (
        id SERIAL PRIMARY KEY,
        reliability TEXT
        );
Create table if not exists social_media(
       facebook text,
       instagram text,
       X text,
       linkedin text,
       pinterest text,
       whatsapp text
   );
   
CREATE TABLE IF NOT EXISTS banner_setup (
       id SERIAL PRIMARY KEY,
       image TEXT,
       banner_type TEXT,
       published BOOLEAN DEFAULT FALSE
    );

CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    coupon_type TEXT,
    coupon_title TEXT,
    coupon_code TEXT UNIQUE,
    coupon_Bearer TEXT,  
    vendor TEXT,
    customer TEXT,  
    usage_limit INT,
    discount_type TEXT,
    discount_amount INT,
    minimum_purchase INT,
    start_date DATE,
    expiry_date DATE  
    );
CREATE TABLE IF NOT EXISTS flash_deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    image_path text,
    duration VARCHAR(255),
    status VARCHAR(50),
    active_products INT,
    is_published BOOLEAN
    );
CREATE TABLE if not exists deals_of_the_day (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT TRUE
    );
    
CREATE TABLE if not exists feature_deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Active', 'Expired')) NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE TABLE if not exists vendors (
    id SERIAL PRIMARY KEY,
    user_id int not null,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    shop_name VARCHAR(100),
    shop_address TEXT,
    FOREIGN KEY (user_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

CREATE TABLE if not exists product_review (
   id SERIAL PRIMARY KEY,
   seller_user_id int not null,
   product_id int not null,
   user_login_id int not null,
   content text,
   Rating float,
   FOREIGN KEY (seller_user_id) REFERENCES seller_users(id) ON DELETE CASCADE,
   FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE,
   FOREIGN KEY (user_login_id) REFERENCES users_login(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

CREATE TABLE if not exists restock_requests (
    id SERIAL PRIMARY KEY,
    user_id Int not null,
    product_name VARCHAR(255) NOT NULL,
    selling_price NUMERIC(10,2) NOT NULL,
    last_request_date DATE NOT NULL,
    number_of_requests INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE
);

CREATE TABLE if not exists update_products (
    id SERIAL PRIMARY KEY,
    seller_id Int Not Null,
    name VARCHAR(255) NOT NULL,
    previous_shipping_cost DECIMAL(10,2),
    new_shipping_cost DECIMAL(10,2),
    FOREIGN KEY(seller_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

CREATE TABLE if not exists customer_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    seller_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL,
    status BOOLEAN DEFAULT False,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES add_product(PID),
    FOREIGN KEY (customer_id) REFERENCES users_login(id),
    FOREIGN KEY (seller_id) REFERENCES seller_users(id)
);


CREATE TABLE IF NOT EXISTS emails(
    id SERIAL PRIMARY KEY,
    uid TEXT,  -- Only for received emails
    subject TEXT NOT NULL,
    sender TEXT,  -- Full sender string for received emails
    sender_name TEXT,  -- Extracted name for received emails
    sender_email TEXT,  -- Extracted email for received emails
    recipient_name TEXT,  -- For sent emails
    recipient_email TEXT,  -- For sent emails
    body TEXT,
    type TEXT NOT NULL,  -- 'received', 'sent'
    reply_status TEXT DEFAULT 'No',  -- 'Yes', 'No'
    related_uid TEXT,  -- To link replies with original emails
    deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);      

CREATE TABLE IF NOT EXISTS general_settings (
    id SERIAL PRIMARY KEY,
    maintenance_mode BOOLEAN DEFAULT FALSE,
    company_name TEXT,
    phone TEXT,
    email TEXT,
    country TEXT,
    timezone TEXT,
    language TEXT,
    address TEXT,
    latitude TEXT,
    longitude TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS payment_options (
id SERIAL PRIMARY KEY,
cash_on_delivery BOOLEAN NOT NULL,
digital_payment BOOLEAN NOT NULL,
offline_payment BOOLEAN NOT NULL
);

CREATE TABLE if not exists product_settings (
    id SERIAL PRIMARY KEY,
    reorder_level INTEGER NOT NULL,
    digital_product BOOLEAN DEFAULT FALSE,
    show_brand BOOLEAN DEFAULT FALSE
);

CREATE TABLE if not exists priority_sorting (
    id SERIAL PRIMARY KEY,
    brand BOOLEAN DEFAULT TRUE,
    category BOOLEAN DEFAULT TRUE,
    vendor BOOLEAN DEFAULT TRUE
);

CREATE TABLE if not exists order_settings (
    id SERIAL PRIMARY KEY,
    order_delivery_verification BOOLEAN NOT NULL,
    minimum_order_amount BOOLEAN NOT NULL,
    show_billing_address BOOLEAN NOT NULL,
    free_delivery BOOLEAN NOT NULL,
    guest_checkout BOOLEAN NOT NULL,
    refund_days INTEGER NOT NULL,
    delivery_responsibility VARCHAR(20) NOT NULL,
    free_delivery_over NUMERIC(10, 2) NOT NULL
);

CREATE TABLE if not exists vendor_settings (
    id SERIAL PRIMARY KEY,
    commission NUMERIC,
    enable_pos BOOLEAN,
    vendor_registration BOOLEAN,
    minimum_order BOOLEAN,
    vendor_can_reply BOOLEAN,
    forgot_password_method VARCHAR(10),
    need_approval_new_product BOOLEAN,
    need_approval_product_shipping BOOLEAN
);

CREATE TABLE if not exists customer_settings (
    id SERIAL PRIMARY KEY,
    customer_wallet BOOLEAN,
    loyalty_point BOOLEAN,
    referral_earning BOOLEAN,
    add_refund_to_wallet BOOLEAN,
    add_fund_to_wallet BOOLEAN,
    max_add_fund_amount VARCHAR(50),
    min_add_fund_amount VARCHAR(50),
    equivalent_point VARCHAR(50),
    loyalty_point_earn_percentage VARCHAR(50),
    min_point_to_convert VARCHAR(50),
    referral_earnings VARCHAR(50)
);
CREATE TABLE if not exists admin_delivery_settings (
    id SERIAL PRIMARY KEY,
    upload_picture_on_delivery BOOLEAN NOT NULL,
    forgot_password_verification_method VARCHAR(10) NOT NULL
);

CREATE TABLE if not exists shipping_settings (
    id SERIAL PRIMARY KEY,
    shipping_type VARCHAR(50) NOT NULL,
    category_id INTEGER NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    cost NUMERIC(10, 2) DEFAULT 0,
    status BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS delivery_restriction_settings (
    id SERIAL PRIMARY KEY,
    country_enabled BOOLEAN DEFAULT FALSE,
    zipcode_enabled BOOLEAN DEFAULT FALSE
);

CREATE TABLE if not exists invoice_settings (
    id Serial PRIMARY KEY,
    terms TEXT,
    business_identity_type VARCHAR(50),
    business_identity_value VARCHAR(255),
    logo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE if not exists inhouse_settings_setup (
    id SERIAL PRIMARY KEY,
    shop_id INTEGER UNIQUE NOT NULL,
    is_temporary_closed BOOLEAN DEFAULT FALSE,
    min_order_amount NUMERIC(10, 2) DEFAULT 0.00,
    banner_image TEXT  -- Stores image URL or path
);

CREATE TABLE if not exists seo_settings (
    id SERIAL PRIMARY KEY,
    google_console TEXT,
    bing_webmaster TEXT,
    baidu_webmaster TEXT,
    yandex_webmaster TEXT
);

CREATE TABLE IF NOT EXISTS environment_settings (
    id SERIAL PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    app_debug BOOLEAN DEFAULT FALSE,
    app_mode VARCHAR(50) DEFAULT 'Live',
    db_connection VARCHAR(255),
    db_host VARCHAR(255),
    db_port VARCHAR(10),
    buyer_username VARCHAR(255),
    purchase_code VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    android_min_customer_version VARCHAR(20),
    android_customer_download_url VARCHAR(255),
    ios_min_customer_version VARCHAR(20),
    ios_customer_download_url VARCHAR(255),
    android_min_vendor_version VARCHAR(20),
    android_vendor_download_url VARCHAR(255),
    ios_min_vendor_version VARCHAR(20),
    ios_vendor_download_url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS languages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS currencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    code VARCHAR(10) NOT NULL,
    exchange_rate DECIMAL(10, 6) DEFAULT 1,
    status BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS cookie_settings (
    id SERIAL PRIMARY KEY,
    cookie_text TEXT,
    status BOOLEAN DEFAULT TRUE
);

CREATE TABLE if not exists software_updates (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    purchase_code TEXT NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists admin_login_settings (
    id SERIAL PRIMARY KEY,
    manual_login BOOLEAN DEFAULT TRUE,
    otp_login BOOLEAN DEFAULT FALSE,
    email_verification BOOLEAN DEFAULT FALSE,
    phone_verification BOOLEAN DEFAULT FALSE,
    max_otp_attempts INTEGER DEFAULT 5,
    otp_resend_time INTEGER DEFAULT 30,
    otp_block_time INTEGER DEFAULT 120,
    max_login_attempts INTEGER DEFAULT 10,
    login_block_time INTEGER DEFAULT 120,
    login_url TEXT DEFAULT '/login'
);
CREATE TABLE if not exists payment_methods (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('digital', 'offline')) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    access_token TEXT,
    public_key TEXT,
    private_key TEXT,
    gateway_title TEXT,
    logo TEXT,
    mode TEXT,
    payment_info TEXT,
    required_info TEXT[]
);

"""
    )

    con.commit()


create()