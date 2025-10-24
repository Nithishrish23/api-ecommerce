import psycopg2
from config.settings import Config
from werkzeug.security import check_password_hash
import bcrypt


def get_db_connection():
    return psycopg2.connect(
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )


def verify_user(username, password):
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "SELECT id, password FROM seller_users WHERE email = %s ",
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


def verify_admin_user(email, password):
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id, password FROM admin_users WHERE email = %s", (email,))
            result = cur.fetchone()
            if result:
                user_id, hashed_password = result
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return user_id
            return None
    finally:
        con.close()


def create():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seller_users(
        id SERIAL PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name  TEXT Default NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT Default 'password',
        phone_number Text default null,
        profile_path Text default null,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        
    );

   Create table if not exists dashboard(
   userid int not null,
   FOREIGN KEY (userid) REFERENCES seller_users(id) ON DELETE CASCADE,
   total_order Int Default Null,
   Total_stores Int  Default Null,
   Total_products Int  Default Null,
   Total_customers Int  Default Null,
   Pending Int  Default Null,
   confirmed Int  Default Null,                                                                                                                                                                                                                                                                                                        
   Packaging Int  Default Null,
   out_of_delivery Int  Default Null,
   Delivered Int  Default Null,
   Canceled Int  Default Null,
   Returned Int  Default Null,
   Failed_to_delivery Int  Default Null,
   in_house_earning decimal(20,2)  Default Null,
   commision_earned decimal(20,2)  Default Null,
   delivery_charge_earned decimal(20,2)  Default Null,
   Total_tax_collected decimal(20,2)  Default Null,
   pending_amount decimal(20,2)  Default Null
   );
   
Create table if not exists Seller_Registation(
    userid int not null,
    FOREIGN KEY (userid) REFERENCES seller_users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    dob DATE,
    country VARCHAR(100),
    state VARCHAR(100),
    place VARCHAR(100),
    mobile_no VARCHAR(50),
    email VARCHAR(255),
    profile_picture_path TEXT,
    company_name VARCHAR(255),
    official_mobile_no VARCHAR(15),
    official_email VARCHAR(255),
    certificate_path TEXT,
    bank_name VARCHAR(255),
    branch_ifsc_code VARCHAR(20),
    account_holder_name VARCHAR(255),
    account_number VARCHAR(100),
    swift_bic VARCHAR(100),
    upi_id VARCHAR(100),
    paypal_email VARCHAR(255),
    payment_terms_accepted BOOLEAN,
    ie_code VARCHAR(50),
    ie_certificate_path TEXT,
    exporter_terms_accepted BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    
    
CREATE TABLE IF NOT EXISTS add_product (
    pid SERIAL PRIMARY KEY,
    userid INT NOT NULL,                  
    product_name VARCHAR(255) DEFAULT NULL,           
    product_description TEXT DEFAULT NULL,            
    product_category VARCHAR(255) DEFAULT NULL,       
    sub_category VARCHAR(255) DEFAULT NULL,           
    sub_sub_category VARCHAR(255) DEFAULT NULL,          
    product_type VARCHAR(255) DEFAULT NULL,           
    product_sku VARCHAR(100) DEFAULT NULL,            
    unit VARCHAR(50) DEFAULT NULL,                                
    unit_price DECIMAL(10, 2) DEFAULT NULL,           
    minimum_order_qty INT DEFAULT NULL,               
    current_stock_qty INT DEFAULT NULL,               
    discount_type VARCHAR(50) DEFAULT NULL,           
    discount_amount DECIMAL(10, 2) DEFAULT NULL,      
    tax_amount DECIMAL(10, 2) DEFAULT NULL,           
    tax_calculation VARCHAR(50) DEFAULT NULL,         
    shipping_cost DECIMAL(10, 2) DEFAULT NULL,        
    shipping_cost_multiply BOOLEAN DEFAULT NULL,    
    product_thumbnail TEXT DEFAULT NULL,              
    additional_images TEXT DEFAULT NULL,                    

    meta_title VARCHAR(255) DEFAULT NULL,             
    meta_description TEXT DEFAULT NULL,  
    tem_close Boolean Default False,

    FOREIGN KEY (userid) REFERENCES seller_users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_users(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT Default 'password'
    );
CREATE TABLE IF NOT EXISTS users_login(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        mobile_number VARCHAR(50),
        password TEXT Default 'password',
        profile_path Text,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
CREATE TABLE IF NOT EXISTS customer_ticket (
   pid SERIAL PRIMARY KEY,
   user_id INT NOT NULL,
   FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE,
   subject TEXT NOT NULL,
   type TEXT,
   priority TEXT,
   description TEXT,
   attachment TEXT,
   status TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS product_selling (
    pid SERIAL PRIMARY KEY,
    id INT NOT NULL,
    FOREIGN KEY (id) REFERENCES add_product(pid) ON DELETE CASCADE,
    featured_deal BOOLEAN DEFAULT FALSE,
    best_selling INT DEFAULT 0, -- Number of times added to cart
    top_selling INT DEFAULT 0,  -- Number of times sold in the last 3 months
    top_rating NUMERIC(2, 1) DEFAULT 0, -- Average rating (e.g., 4.5 out of 5)
    rating_count INT DEFAULT 0, -- Total number of ratings
    new_arrival DATE DEFAULT CURRENT_DATE
);

Create table if not exists brands(
    id SERIAL PRIMARY KEY,
    Brand_name varchar(255) unique,
    image_alt_name text,
    image_filename text
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    priority INTEGER DEFAULT 1,
    image TEXT,
    home_category BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS sub_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    priority INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sub_sub_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sub_category_id INT NOT NULL,
    category_id INT NOT NULL,
    priority INTEGER DEFAULT 1,
    FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE if not exists attributes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT,
    count INTEGER DEFAULT 1,
    status BOOLEAN DEFAULT TRUE
);
    
CREATE TABLE IF NOT EXISTS push_notifications (
    id SERIAL PRIMARY KEY,
    notification_id INTEGER REFERENCES notifications(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL CHECK (language IN ('en', 'ar', 'bd', 'hi')),
    notification_type TEXT NOT NULL,
    message TEXT NOT NULL,
    enabled BOOLEAN DEFAULT FALSE
);

CREATE TABLE if not exists announcements (
    id SERIAL PRIMARY KEY,
    status VARCHAR(10) NOT NULL,
    background_color VARCHAR(10) NOT NULL,
    text_color VARCHAR(10) NOT NULL,
    announcement_text TEXT NOT NULL
);


        
                   

CREATE TABLE IF NOT EXISTS product_status (
    pid INT PRIMARY KEY,
    userid INT,
    active_status BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (pid) REFERENCES add_product(pid) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION public.sync_product_selling() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO product_selling (id)
        VALUES (NEW.pid);
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE product_selling
        SET id = NEW.pid
        WHERE id = OLD.pid;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM product_selling
        WHERE id = OLD.pid;
    END IF;
    RETURN NULL;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_sync_product_selling'
    ) THEN
        EXECUTE 'CREATE TRIGGER trg_sync_product_selling
                 AFTER INSERT OR UPDATE OR DELETE ON public.add_product
                 FOR EACH ROW EXECUTE FUNCTION public.sync_product_selling()';
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION public.sync_product_status_on_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM product_status WHERE pid = OLD.pid;
    RETURN OLD;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_sync_product_status_on_delete'
    ) THEN
        EXECUTE 'CREATE TRIGGER trg_sync_product_status_on_delete
                 AFTER DELETE ON public.add_product
                 FOR EACH ROW EXECUTE FUNCTION public.sync_product_status_on_delete()';
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION public.sync_product_status_on_insert_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO product_status (pid, userid, active_status, is_featured)
    VALUES (NEW.pid, NEW.userid, FALSE, FALSE)
    ON CONFLICT (pid) DO UPDATE
    SET
        userid = EXCLUDED.userid,
        active_status = TRUE,
        is_featured = TRUE;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_sync_product_status_on_insert_update'
    ) THEN
        EXECUTE 'CREATE TRIGGER trg_sync_product_status_on_insert_update
                 AFTER INSERT OR UPDATE ON public.add_product
                 FOR EACH ROW EXECUTE FUNCTION public.sync_product_status_on_insert_update()';
    END IF;
END;
$$;


INSERT INTO product_status (pid, userid, active_status, is_featured)
SELECT pid, userid, FALSE, FALSE FROM add_product
ON CONFLICT (pid) DO NOTHING;

-- Policy Tables
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

-- Social Media Table
CREATE TABLE IF NOT EXISTS social_media (
    id SERIAL PRIMARY KEY,
    facebook TEXT,
    instagram TEXT,
    X TEXT,
    linkedin TEXT,
    pinterest TEXT,
    whatsapp TEXT
);

-- Banner Setup Table
CREATE TABLE IF NOT EXISTS banner_setup (
    id SERIAL PRIMARY KEY,
    image TEXT,
    banner_type VARCHAR(50),
    published BOOLEAN DEFAULT FALSE
);

-- Coupons Table
CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    coupon_type VARCHAR(50),
    coupon_title VARCHAR(255),
    coupon_code VARCHAR(100) UNIQUE,
    coupon_Bearer VARCHAR(100),
    vendor VARCHAR(255),
    customer VARCHAR(255),
    usage_limit INT,
    discount_type VARCHAR(50),
    discount_amount DECIMAL(10, 2),
    minimum_purchase DECIMAL(10, 2),
    start_date DATE,
    expiry_date DATE
);

-- Flash Deals Table
CREATE TABLE IF NOT EXISTS flash_deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    duration VARCHAR(100),
    status VARCHAR(50),
    active_products INT DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    image TEXT
);

-- Deals of the Day Table
CREATE TABLE IF NOT EXISTS deals_of_the_day (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    product VARCHAR(255),
    status VARCHAR(50)
);

-- Feature Deals Table
CREATE TABLE IF NOT EXISTS feature_deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    is_active BOOLEAN DEFAULT FALSE
);

-- Vendors Table
CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    user_id INT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    password TEXT,
    shop_name VARCHAR(255),
    shop_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Review Table
CREATE TABLE IF NOT EXISTS product_review (
    id SERIAL PRIMARY KEY,
    product_id INT,
    user_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

-- Cart Table
CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT,
    seller_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    total_price DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES seller_users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

-- Seller Wallet Table
CREATE TABLE IF NOT EXISTS seller_wallet (
    id SERIAL PRIMARY KEY,
    seller_id INT UNIQUE,
    balance DECIMAL(15, 2) DEFAULT 0,
    pending_withdraw DECIMAL(15, 2) DEFAULT 0,
    already_withdrawn DECIMAL(15, 2) DEFAULT 0,
    tax_given DECIMAL(15, 2) DEFAULT 0,
    commission_given DECIMAL(15, 2) DEFAULT 0,
    delivery_charge_earned DECIMAL(15, 2) DEFAULT 0,
    FOREIGN KEY (seller_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

-- Products Table (for aggregated product data)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    seller_id INT,
    total_sales INT DEFAULT 0,
    FOREIGN KEY (seller_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

-- Restock Requests Table
CREATE TABLE IF NOT EXISTS restock_requests (
    id SERIAL PRIMARY KEY,
    user_id INT,
    product_name VARCHAR(255),
    selling_price DECIMAL(10, 2),
    last_request_date DATE,
    number_of_requests INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

-- Trigger Log Table (for product update tracking)
CREATE TABLE IF NOT EXISTS trigger_log (
    id SERIAL PRIMARY KEY,
    product_id INT,
    action VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE
);

-- Email Management Table
CREATE TABLE IF NOT EXISTS emails (
    uid VARCHAR(255) PRIMARY KEY,
    to_email VARCHAR(255),
    from_email VARCHAR(255),
    subject TEXT,
    body TEXT,
    original_uid VARCHAR(255),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer Reviews Table
CREATE TABLE IF NOT EXISTS customer_reviews (
    id SERIAL PRIMARY KEY,
    product_id INT,
    seller_id INT,
    user_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES add_product(pid) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES seller_users(id) ON DELETE CASCADE
);

-- General Settings Table
CREATE TABLE IF NOT EXISTS general_settings (
    id SERIAL PRIMARY KEY,
    maintenance_mode BOOLEAN DEFAULT FALSE,
    company_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    country VARCHAR(100),
    timezone VARCHAR(100),
    language VARCHAR(50),
    address TEXT,
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);

-- Customer Settings Table
CREATE TABLE IF NOT EXISTS customer_settings (
    id SERIAL PRIMARY KEY,
    customer_verification BOOLEAN DEFAULT FALSE,
    customer_wallet BOOLEAN DEFAULT FALSE,
    customer_loyalty_point BOOLEAN DEFAULT FALSE,
    customer_referral_earning BOOLEAN DEFAULT FALSE,
    add_funds_to_wallet BOOLEAN DEFAULT FALSE,
    minimum_add_fund_amount DECIMAL(10, 2) DEFAULT 0
);

-- Payment Options Table
CREATE TABLE IF NOT EXISTS payment_options (
    id SERIAL PRIMARY KEY,
    cash_on_delivery BOOLEAN DEFAULT FALSE,
    digital_payment BOOLEAN DEFAULT FALSE,
    offline_payment BOOLEAN DEFAULT FALSE
);

-- Product Settings Table
CREATE TABLE IF NOT EXISTS product_settings (
    id SERIAL PRIMARY KEY,
    reorderLevel INT DEFAULT 10,
    digitalProduct BOOLEAN DEFAULT FALSE,
    showBrand BOOLEAN DEFAULT TRUE
);

-- Priority Settings Table
CREATE TABLE IF NOT EXISTS priority_settings (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255),
    priority INT DEFAULT 1
);

-- Order Settings Table
CREATE TABLE IF NOT EXISTS order_settings (
    id SERIAL PRIMARY KEY,
    order_verification BOOLEAN DEFAULT FALSE,
    minimum_order_amount DECIMAL(10, 2) DEFAULT 0,
    free_delivery_over DECIMAL(10, 2) DEFAULT 0,
    free_delivery_responsibility VARCHAR(50)
);

-- Vendor Settings Table
CREATE TABLE IF NOT EXISTS vendor_settings (
    id SERIAL PRIMARY KEY,
    vendor_registration BOOLEAN DEFAULT TRUE,
    vendor_pos_permission BOOLEAN DEFAULT FALSE,
    new_product_approval BOOLEAN DEFAULT TRUE,
    product_wise_shipping_cost BOOLEAN DEFAULT FALSE,
    minimum_order_amount DECIMAL(10, 2) DEFAULT 0
);

-- Delivery Settings Table
CREATE TABLE IF NOT EXISTS delivery_settings (
    id SERIAL PRIMARY KEY,
    self_delivery BOOLEAN DEFAULT FALSE,
    third_party_delivery BOOLEAN DEFAULT FALSE
);

-- Shipping Settings Table
CREATE TABLE IF NOT EXISTS shipping_settings (
    id SERIAL PRIMARY KEY,
    shipping_method VARCHAR(100),
    shipping_cost DECIMAL(10, 2),
    duration VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

-- Delivery Restriction Settings Table
CREATE TABLE IF NOT EXISTS delivery_restriction_settings (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    zipcode VARCHAR(20),
    restriction_type VARCHAR(50)
);

-- Invoice Settings Table
CREATE TABLE IF NOT EXISTS invoice_settings (
    id SERIAL PRIMARY KEY,
    invoice_logo TEXT,
    company_name VARCHAR(255),
    company_email VARCHAR(255),
    company_phone VARCHAR(20),
    company_address TEXT
);

-- Inhouse Settings Table
CREATE TABLE IF NOT EXISTS inhouse_settings (
    id SERIAL PRIMARY KEY,
    shop_name VARCHAR(255),
    shop_logo TEXT,
    shop_banner TEXT,
    vacation_mode BOOLEAN DEFAULT FALSE,
    vacation_start_date DATE,
    vacation_end_date DATE,
    temporary_close BOOLEAN DEFAULT FALSE
);

-- SEO Settings Table
CREATE TABLE IF NOT EXISTS seo_settings (
    id SERIAL PRIMARY KEY,
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    canonical_url TEXT,
    meta_image TEXT
);

-- Environment Settings Table
CREATE TABLE IF NOT EXISTS environment_settings (
    id SERIAL PRIMARY KEY,
    app_name VARCHAR(255),
    app_debug BOOLEAN DEFAULT FALSE,
    app_mode VARCHAR(50),
    db_connection VARCHAR(100),
    db_host VARCHAR(255),
    db_port VARCHAR(10),
    buyer_username VARCHAR(255),
    purchase_code VARCHAR(255)
);

-- App Settings Table
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    android_min_customer_version VARCHAR(50),
    android_customer_download_url TEXT,
    ios_min_customer_version VARCHAR(50),
    ios_customer_download_url TEXT,
    android_min_vendor_version VARCHAR(50),
    android_vendor_download_url TEXT,
    ios_min_vendor_version VARCHAR(50),
    ios_vendor_download_url TEXT
);

-- Languages Table
CREATE TABLE IF NOT EXISTS languages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    code VARCHAR(10) UNIQUE,
    status BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE
);

-- Currencies Table
CREATE TABLE IF NOT EXISTS currencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    symbol VARCHAR(10),
    code VARCHAR(10) UNIQUE,
    exchange_rate DECIMAL(10, 4) DEFAULT 1.0,
    is_default BOOLEAN DEFAULT FALSE
);

-- Cookie Settings Table
CREATE TABLE IF NOT EXISTS cookie_settings (
    id SERIAL PRIMARY KEY,
    strictly_necessary BOOLEAN DEFAULT TRUE,
    performance_analytics BOOLEAN DEFAULT FALSE,
    functional BOOLEAN DEFAULT FALSE,
    targeting_advertising BOOLEAN DEFAULT FALSE
);

-- Login Settings Table
CREATE TABLE IF NOT EXISTS login_settings (
    id SERIAL PRIMARY KEY,
    manual_login BOOLEAN DEFAULT TRUE,
    otp_login BOOLEAN DEFAULT FALSE,
    social_media_login BOOLEAN DEFAULT FALSE
);

-- Payment Methods Table
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    method_name VARCHAR(100),
    is_active BOOLEAN DEFAULT FALSE,
    api_key TEXT,
    secret_key TEXT,
    mode VARCHAR(50)
);

-- User Address Table
CREATE TABLE IF NOT EXISTS user_addresses (
    id SERIAL PRIMARY KEY,
    user_id INT,
    address_type VARCHAR(50),
    contact_person_name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users_login(id) ON DELETE CASCADE
);

-- Priority Sorting Table
CREATE TABLE IF NOT EXISTS priority_sorting (
    id SERIAL PRIMARY KEY,
    brand BOOLEAN DEFAULT TRUE,
    category BOOLEAN DEFAULT TRUE,
    vendor BOOLEAN DEFAULT TRUE
);

-- Emails Table (with additional fields)
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(255) UNIQUE,
    subject TEXT,
    sender VARCHAR(255),
    sender_name VARCHAR(255),
    sender_email VARCHAR(255),
    recipient_email VARCHAR(255),
    recipient_name VARCHAR(255),
    body TEXT,
    type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    reply_status VARCHAR(20) DEFAULT 'No',
    related_uid VARCHAR(255)
);

-- Admin Delivery Settings Table
CREATE TABLE IF NOT EXISTS admin_delivery_settings (
    id SERIAL PRIMARY KEY,
    upload_picture_on_delivery BOOLEAN DEFAULT FALSE,
    forgot_password_verification_method VARCHAR(50) DEFAULT 'phone'
);

-- Shipping Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS shipping_settings (
    id SERIAL PRIMARY KEY,
    shipping_type VARCHAR(50),
    category_id INT,
    category_name VARCHAR(255),
    cost DECIMAL(10, 2),
    status BOOLEAN DEFAULT TRUE
);

-- Delivery Restriction Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS delivery_restriction_settings (
    id SERIAL PRIMARY KEY,
    country_enabled BOOLEAN DEFAULT FALSE,
    zipcode_enabled BOOLEAN DEFAULT FALSE
);

-- Invoice Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS invoice_settings (
    id SERIAL PRIMARY KEY,
    terms TEXT,
    business_identity_type VARCHAR(100),
    business_identity_value VARCHAR(255),
    logo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Inhouse Settings Setup Table
CREATE TABLE IF NOT EXISTS inhouse_settings_setup (
    id SERIAL PRIMARY KEY,
    shop_id INT DEFAULT 1,
    is_temporary_closed BOOLEAN DEFAULT FALSE,
    min_order_amount DECIMAL(10, 2) DEFAULT 0,
    banner_image TEXT
);

-- SEO Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS seo_settings (
    id SERIAL PRIMARY KEY,
    google_console TEXT,
    bing_webmaster TEXT,
    baidu_webmaster TEXT,
    yandex_webmaster TEXT
);

-- Software Updates Table
CREATE TABLE IF NOT EXISTS software_updates (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    purchase_code VARCHAR(255),
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin Login Settings Table
CREATE TABLE IF NOT EXISTS admin_login_settings (
    id SERIAL PRIMARY KEY,
    manual_login BOOLEAN DEFAULT TRUE,
    otp_login BOOLEAN DEFAULT FALSE,
    email_verification BOOLEAN DEFAULT FALSE,
    phone_verification BOOLEAN DEFAULT FALSE,
    max_otp_attempts INT DEFAULT 5,
    otp_resend_time INT DEFAULT 30,
    otp_block_time INT DEFAULT 120,
    max_login_attempts INT DEFAULT 10,
    login_block_time INT DEFAULT 120,
    login_url VARCHAR(255) DEFAULT '/login'
);

-- Payment Methods Table (enhanced)
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    status BOOLEAN DEFAULT FALSE,
    access_token TEXT,
    public_key TEXT,
    private_key TEXT,
    gateway_title VARCHAR(255),
    logo TEXT,
    mode VARCHAR(50),
    payment_info TEXT,
    required_info TEXT[]
);

-- Customer Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS customer_settings (
    id SERIAL PRIMARY KEY,
    customer_wallet BOOLEAN DEFAULT FALSE,
    loyalty_point BOOLEAN DEFAULT FALSE,
    referral_earning BOOLEAN DEFAULT FALSE,
    add_refund_to_wallet BOOLEAN DEFAULT FALSE,
    add_fund_to_wallet BOOLEAN DEFAULT FALSE,
    max_add_fund_amount DECIMAL(10, 2) DEFAULT 0,
    min_add_fund_amount DECIMAL(10, 2) DEFAULT 0,
    equivalent_point INT DEFAULT 0,
    loyalty_point_earn_percentage DECIMAL(5, 2) DEFAULT 0,
    min_point_to_convert INT DEFAULT 0,
    referral_earnings DECIMAL(10, 2) DEFAULT 0
);

-- Order Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS order_settings (
    id SERIAL PRIMARY KEY,
    order_delivery_verification BOOLEAN DEFAULT FALSE,
    minimum_order_amount BOOLEAN DEFAULT FALSE,
    show_billing_address BOOLEAN DEFAULT FALSE,
    free_delivery BOOLEAN DEFAULT FALSE,
    guest_checkout BOOLEAN DEFAULT FALSE,
    refund_days INT DEFAULT 0,
    delivery_responsibility VARCHAR(100),
    free_delivery_over DECIMAL(10, 2) DEFAULT 0
);

-- Vendor Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS vendor_settings (
    id SERIAL PRIMARY KEY,
    commission DECIMAL(5, 2) DEFAULT 0,
    enable_pos BOOLEAN DEFAULT FALSE,
    vendor_registration BOOLEAN DEFAULT TRUE,
    minimum_order DECIMAL(10, 2) DEFAULT 0,
    vendor_can_reply BOOLEAN DEFAULT FALSE,
    forgot_password_method VARCHAR(50) DEFAULT 'email',
    need_approval_new_product BOOLEAN DEFAULT TRUE,
    need_approval_product_shipping BOOLEAN DEFAULT FALSE
);

-- Cookie Settings Table (enhanced)
CREATE TABLE IF NOT EXISTS cookie_settings (
    id SERIAL PRIMARY KEY,
    cookie_text TEXT,
    status BOOLEAN DEFAULT FALSE
);

-- Create view for seller product information
CREATE OR REPLACE VIEW seller_product_view AS
SELECT
    sr.userid,
    sr.name AS seller_name,
    sr.email AS seller_email,
    sr.mobile_no AS seller_mobile,
    sr.company_name,
    sr.bank_name,
    sr.branch_ifsc_code,
    sr.profile_picture_path,
    ap.product_name,
    ap.product_category,
    ap.sub_category,
    ap.product_description,
    ap.unit_price,
    ap.current_stock_qty,
    ap.product_thumbnail
FROM
    Seller_Registation sr
JOIN
    add_product ap ON sr.userid = ap.userid;

''')
    con.commit()

create()