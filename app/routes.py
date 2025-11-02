from flask import Blueprint, request, send_from_directory, jsonify
from app.auth import (
    register,
    login,
    admin_login,
    check_session,
    user,
    handle_seller_registration,
    add_product,
    logout,
)
from app.auth import get_seller_dashboard_data,get_admin_dashboard_data
from app.auth import (
    edit_product,
    delete_product,
    admin_product_details,
    product_details,
    product_detail_id,
    admin_manufacture_list,
    get_seller_orders,
    get_seller_order_by_status,
    update_order_status,
    get_seller_order_stats
)
from flask_cors import cross_origin
from app.authTokens import token_required
from app.users.login import (
    user_login,
    user_login_id,
    user_register,
    user_product_details,
    get_single_product_details,
    update_tem_close,
)
from app.users.login import (
    user_profile_edit,
    create_ticket,
    view_ticket,
    delete_ticket,
    get_tem_close_status,
    admin_view_ticket,
)
from app.users.address import address, address_view, address_delete, edit_address
import os
from app.admin.auth2 import (
    create_restock_request,
    get_restock_requests,
    update_restock_request,
    delete_restock_request,
    get_update_products,
    get_approved_products,
    get_denied_products,
)
from app.admin.auth import (
    toggle_product_status,
    toggle_product_featured,
    get_product_status,
    add_policy,
    show_policy,
    social_media,
    show_media,
    add_new_vendor,
    get_vendor,
    get_vendors,
    update_vendor,
    delete_vendor,
    create_sub_sub_category,
    get_all_sub_sub_categories,
    update_sub_sub_category,
    delete_sub_sub_category,
)
from app.admin.auth import (
    banner_setup,
    get_banners,
    delete_banner,
    update_banner,
    add_coupon,
    get_coupons,
    update_coupon,
    delete_coupon,
    product_review,
    cart,
    upload_file,
    list_files,
    get_attributes,
    add_attribute,
    delete_attribute,
    update_attribute,
    get_notifications,
    add_notification,
    delete_notification,
    update_notification,
)
from app.admin.auth import (
    add_brands,
    get_brands,
    delete_brand,
    edit_brand,
    get_category,
    edit_category,
    delete_category,
    add_category,
    add_subcategory,
    get_subcategories,
    update_subcategory,
    delete_subcategory,
)
from app.admin.auth import (
    add_feature_deal,
    get_feature_deal,
    delete_feature_deal,
    update_feature_deal,
    create_push_notification,
    get_push_notifications,
    delete_push_notification,
    update_push_notification,
    create_announcement,
    get_announcements,
    update_announcement,
    delete_announcement,
    get_admin_orders,
    get_admin_order_details,
    update_admin_order_status,
    get_admin_order_stats,
)
from app.admin.auth import (
    get_flash_deals,
    add_flash_deal,
    delete_flash_deal,
    update_flash_deal,
    get_day_deals,
    update_day_deal,
    delete_day_deal,
    add_day_deal,
    filter_customers,
    get_customers,
)
from app.users.product import (
    new_arrivals,
    best_selling,
    get_top_selling,
    add_rating,
    add_to_cart,
    get_featured_deals,
    set_featured,
    get_user_orders,
)
from app.users.product import order_insert
from werkzeug.utils import safe_join

from app.admin.auth2 import (
    read_emails,
    send_email,
    create_review,
    update_review,
    delete_review,
    get_reviews_by_product,
    get_reviews_by_seller,
    get_all_reviews,
    delete_email,
)

from app.admin.auth2 import (
    get_general_settings,
    get_customer_settings,
    update_settings,
    update_customer_settings,
    create_settings,
    get_payment_options,
    save_payment_options,
    save_or_update_product_settings,
    get_product_settings,
    get_priority,
    update_priority,
    save_order_settings,
    get_order_settings,
    get_vendor_settings,
    save_vendor_settings,
    update_vendor_settings,
    delivery_settings,
    get_shipping_settings,
    update_shipping_settings,
    create_shipping_settings,
    get_delivery_restriction_settings,
    create_delivery_restriction_settings,
    update_delivery_restriction_settings,
    invoice_settings,
    inhouse_settings_setup,
    handle_seo_settings,
)

from app.admin.auth3 import (
    get_environment_settings,
    update_environment_settings,
    get_app_settings,
    update_app_settings,
    get_languages,
    add_language,
    update_language,
    get_currencies,
    add_currency,
    set_default_currency,
    get_cookie_settings,
    update_cookie_settings,
    clean_database,
    software_update,
    login_settings,
    payment_methods_handler,
)
from app.payments import create_payment_intent, handle_stripe_webhook
from app.payments import create_checkout_session
blueprint = Blueprint("routes", __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), r"uploads")

@blueprint.route("/", methods=["GET","POST"])
def home_page():
    import bcrypt
    import os
    import psycopg2
    
    def create_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    # Example usage:
    password = "Admin@123"
    hashed_password = create_password(password)
    print(hashed_password)

    return f"<h1>Welcome {hashed_password}</h1>"

@blueprint.route("/uploads/media", methods=["GET", "POST"])
def media_files_route():
    if request.method == "GET":
        return list_files()
    elif request.method == "POST":
        return upload_file()


@blueprint.route("/uploads/media/<path:folderName>", methods=["GET"])
def get_folder_files(folderName):
    folder_path = os.path.join(UPLOAD_FOLDER, folderName)

    if not os.path.exists(folder_path):
        return jsonify({"error": "Folder not found"}), 404

    files = [
        os.path.join(folderName, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    return jsonify(files)


@blueprint.route("/uploads/<path:filepath>", methods=["GET"])
def serve_uploads(filepath):
    # Securely join the upload folder path with the requested file path
    safe_path = safe_join(os.path.abspath(UPLOAD_FOLDER), filepath)

    if not safe_path or not os.path.exists(safe_path):
        return jsonify({"error": "File not found"}), 404

    if os.path.isdir(safe_path):
        return jsonify({"error": "This is a folder, not a file"}), 400

    directory = os.path.dirname(safe_path)
    filename = os.path.basename(safe_path)
    return send_from_directory(directory, filename)


@blueprint.route("/register", methods=["GET", "POST"])
def register_route():
    return register()


@blueprint.route("/login", methods=["POST"])
def login_route():
    return login()


# Seller Dashboard API
@blueprint.route("/seller_dashboard/<int:userid>", methods=["GET"])
def seller_dashboard_route(userid):
    return get_seller_dashboard_data(userid)

# Admin Dashboard API
@blueprint.route("/admin_dashboard", methods=["GET"])
def admin_dashboard_route():
    return get_admin_dashboard_data()


@blueprint.route("/check_session", methods=["GET", "POST"])
def check_session_route():
    return check_session()


@blueprint.route("/user/<int:user_id>", methods=["GET", "POST"])
@cross_origin()
def user_route(user_id):
    return user(user_id)


@blueprint.route("/register-seller", methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def seller_register():
    return handle_seller_registration()


@blueprint.route("/seller-add-new-product", methods=["GET", "POST"])
@cross_origin()
@token_required
def seller_add_new_product():
    return add_product()


@blueprint.route("/admin_product_details", methods=["GET","POST"])
def admin_product_detail_route():
    return admin_product_details()


@blueprint.route("/product_details/", methods=["GET","POST"])
@token_required
@cross_origin()
def get_product_detail():
    return product_details()


@blueprint.route("/product_detail/<int:pid>", methods=["GET", "POST"])
@token_required
@cross_origin()
def product_detail_route(pid):
    return product_detail_id(pid)


@blueprint.route("/delete_product/<int:pid>", methods=["DELETE"])
def delete_product_route(pid):
    return delete_product(pid)


@blueprint.route("/edit-product/<int:pid>", methods=["PATCH"])
@cross_origin()
@token_required
def edit_product_route(pid):
    return edit_product(pid)


@blueprint.route("/admin_login", methods=["POST", "GET"])
def admin_login_route():
    return admin_login()


@blueprint.route("/user_login", methods=["POST"])
def user_login_id_route():
    return user_login()


@blueprint.route("/user_login/<int:user_id>", methods=["GET", "POST"])
@token_required
@cross_origin()
def user_login_route(user_id):
    return user_login_id(user_id)


@blueprint.route("/user_register", methods=["GET", "POST"])
def user_register_route():
    return user_register()


@blueprint.route("/logout", methods=["GET", "POST"])
def logout_route():
    return logout()


@blueprint.route("/admin_manufacture_list", methods=["GET", "POST"])
def admin_manufacture_list_route():
    return admin_manufacture_list()


@blueprint.route("/active_products", methods=["GET", "POST"])
def user_product_detail_route():
    return user_product_details()


@blueprint.route("/user_active_product/<int:pid>", methods=["GET"])
def single_product_detail_route(pid):
    return get_single_product_details(pid)


@blueprint.route("/product_status/<int:product_id>", methods=["GET", "POST"])
def toggle_product_status_route(product_id):
    return toggle_product_status(product_id)


@blueprint.route("/product_featured/<int:product_id>", methods=["GET", "POST"])
def toggle_product_featured_route(product_id):
    return toggle_product_featured(product_id)


@blueprint.route("/get_product_status", methods=["GET"])
def status_route():
    return get_product_status()


@blueprint.route("/update-profile", methods=["POST", "GET", "PATCH", "PUT"])
@cross_origin()
@token_required
def user_profile_edit_route():
    return user_profile_edit()


@blueprint.route("/create-ticket", methods=["GET", "POST"])
@cross_origin()
@token_required
def create_ticket_route():
    return create_ticket()


@blueprint.route("/view-ticket", methods=["GET", "POST"])
@cross_origin()
@token_required
def view_ticket_route():
    return view_ticket()

@blueprint.route("/admin_view_ticket", methods=["GET", "POST"])
def admin_view_ticket_route():
    return admin_view_ticket()


@blueprint.route("/delete-ticket", methods=["GET", "POST"])
@cross_origin()
def delete_ticket_route():
    return delete_ticket()


@blueprint.route("/add-address", methods=["GET", "POST"])
@cross_origin()
@token_required
def add_address_route():
    return address()


@blueprint.route("/user-address", methods=["GET", "POST"])
@cross_origin()
@token_required
def user_address_id_route():
    return address_view()


@blueprint.route("/delete-address/<int:id>", methods=["GET", "POST"])
@cross_origin()
def delete_address_route(id):
    return address_delete(id)


@blueprint.route("/edit-address/<int:id>", methods=["GET", "POST"])
@cross_origin()
@token_required
def edit_address_route(id):
    return edit_address(id)


@blueprint.route("/new_arrivals", methods=["GET", "POST"])
def new_arrivals_route():
    return new_arrivals()


@blueprint.route("/best_selling", methods=["GET", "POST"])
def best_selling_route():
    return best_selling()


@blueprint.route("/top_selling", methods=["GET", "POST"])
def top_selling_route():
    return get_top_selling()


@blueprint.route("/add_rating", methods=["POST"])
def add_rating_route():
    return add_rating()


@blueprint.route("/add_to_cart", methods=["POST"])
def add_to_cart_route():
    return add_to_cart()


@blueprint.route("/get_featured_deals", methods=["GET"])
def get_featured_deals_route():
    return get_featured_deals()


@blueprint.route("/set_featured", methods=["POST"])
def set_featured_route():
    return set_featured()


@blueprint.route("/orders", methods=["GET", "POST"])
@token_required
@cross_origin()
def get_user_orders_route():
    return get_user_orders()


@blueprint.route("/insert_order", methods=["GET", "POST"])
@token_required
@cross_origin()
def order_insert_route():
    return order_insert()


# Seller Order Routes
@blueprint.route("/seller/orders", methods=["GET"])
@token_required
@cross_origin()
def get_seller_orders_route():
    return get_seller_orders()


@blueprint.route("/seller/orders/<status>", methods=["GET"])
@token_required
@cross_origin()
def get_seller_order_by_status_route(status):
    return get_seller_order_by_status(status)


@blueprint.route("/seller/orders/update_status", methods=["PUT"])
@token_required
@cross_origin()
def update_order_status_route():
    return update_order_status()


@blueprint.route("/seller/orders/stats", methods=["GET"])
@token_required
@cross_origin()
def get_seller_order_stats_route():
    return get_seller_order_stats()


@blueprint.route("/terms&conditions/<policy>", methods=["GET", "POST"])
@cross_origin()
def termsandconditions_route(policy):
    return add_policy(policy)


@blueprint.route("/show_terms/<policy>", methods=["GET", "POST"])
@cross_origin()
def show_terms_route(policy):
    return show_policy(policy)


@blueprint.route("/social_media", methods=["GET", "POST"])
@cross_origin()
def social_media_route():
    return social_media()


@blueprint.route("/show_media", methods=["GET", "POST"])
@cross_origin()
def show_media_route():
    return show_media()


@blueprint.route("/banner", methods=["GET", "POST"])
@cross_origin()
def banner_route():
    return banner_setup()


@blueprint.route("/show_banner", methods=["GET"])
@cross_origin()
def show_banner_route():
    return get_banners()


@blueprint.route("/update_banner/<int:id>", methods=["PUT"])
@cross_origin()
def update_banner_route(id):
    return update_banner(id)


@blueprint.route("/delete_banner/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_banner_route(id):
    return delete_banner(id)


@blueprint.route("/add_coupon", methods=["POST"])
@cross_origin()
def add_coupon_route():
    return add_coupon()


@blueprint.route("/show_coupon", methods=["GET"])
@cross_origin()
def show_coupon_route():
    return get_coupons()


@blueprint.route("/update_coupon/<int:id>", methods=["PUT"])
@cross_origin()
def update_coupon_route(id):
    return update_coupon(id)


@blueprint.route("/delete_coupon/<int:id>", methods=["PUT"])
@cross_origin()
def delete_coupon_route(id):
    return delete_coupon(id)


@blueprint.route("/flash-deals", methods=["GET"])
@cross_origin()
def get_deals():
    return get_flash_deals()


@blueprint.route("/flash-deals", methods=["POST"])
@cross_origin()
def add_deals():
    return add_flash_deal()


@blueprint.route("/flash-deals/<int:deal_id>", methods=["PUT"])
@cross_origin()
def update_deals(deal_id):
    return update_flash_deal(deal_id)


@blueprint.route("/flash-deals/<int:deal_id>", methods=["DELETE"])
@cross_origin()
def del_deals(deal_id):
    return delete_flash_deal(deal_id)


@blueprint.route("/day_deals", methods=["GET"])
@cross_origin()
def get_day_deals_route():
    return get_day_deals()


@blueprint.route("/day_deals", methods=["POST"])
@cross_origin()
def add_day_deal_route():
    return add_day_deal()


@blueprint.route("/day_deals/<int:deal_id>", methods=["PUT"])
@cross_origin()
def update_day_deal_route(deal_id):
    return update_day_deal(deal_id)


@blueprint.route("/day_deals/<int:deal_id>", methods=["DELETE"])
@cross_origin()
def delete_day_deal_route(deal_id):
    return delete_day_deal(deal_id)


@blueprint.route("/feature_deal", methods=["GET"])
@cross_origin()
def get_feature_deal_route():
    return get_feature_deal()


@blueprint.route("/feature_deal", methods=["POST"])
@cross_origin()
def add_feature_deals_route():
    return add_feature_deal()


@blueprint.route("/feature_deal/<int:id>", methods=["PUT"])
@cross_origin()
def update_feature_deals_route(id):
    return update_feature_deal(id)


@blueprint.route("/feature_deal/<int:id>", methods=["DELETE"])
@cross_origin()
def delete_feature_deals_route(id):
    return delete_feature_deal(id)


@blueprint.route("/customer_list", methods=["GET"])
@cross_origin()
def customer_list_route():
    return get_customers()


@blueprint.route("/filter_customer_list", methods=["POST"])
@cross_origin()
def filter_list_route():
    return filter_customers()


@blueprint.route("/update_tem_close", methods=["GET", "POST"])
@token_required
@cross_origin()
def update_tem_close_route():
    return update_tem_close()


@blueprint.route("/get_tem_close_status", methods=["GET"])
@token_required
@cross_origin()
def get_tem_close_status_route():
    return get_tem_close_status()


@blueprint.route("/add_new_vendor", methods=["GET", "POST"])
@token_required
@cross_origin()
def add_new_vendor_route():
    return add_new_vendor()


@blueprint.route("/get_vendors", methods=["GET", "POST"])
@token_required
@cross_origin()
def get_new_vendors_route():
    return get_vendors()


@blueprint.route("/get_vendor/<int:vendor_id>", methods=["GET", "POST"])
@token_required
@cross_origin()
def get_new_vendor_route(vendor_id):
    return get_vendor(vendor_id)


@blueprint.route("/update_vendor/<int:vendor_id>", methods=["GET", "POST"])
@token_required
@cross_origin()
def update_vendor_route(vendor_id):
    return update_vendor(vendor_id)


@blueprint.route("/delete_vendor/<int:vendor_id>", methods=["GET", "POST"])
@token_required
@cross_origin()
def delete_vendor_route(vendor_id):
    return delete_vendor(vendor_id)


@blueprint.route("/product_review", methods=["GET", "POST", "PUT", "DELETE"])
@token_required
@cross_origin()
def product_review_route():
    return product_review()


@blueprint.route("/add_cart", methods=["GET", "POST", "PUT", "DELETE"])
@token_required
@cross_origin()
def add_to_cart__route():
    return cart()


@blueprint.route("/brands", methods=["GET"])
def get_brands_route():
    return get_brands()


@blueprint.route("/brands", methods=["POST"])
def add_brand_route():
    return add_brands()


@blueprint.route("/brands/<int:brand_id>", methods=["PUT"])
def edit_brand_route(brand_id):
    return edit_brand(brand_id)


@blueprint.route("/brands/<int:brand_id>", methods=["DELETE"])
def delete_brand_route(brand_id):
    return delete_brand(brand_id)


@blueprint.route("/category", methods=["GET"])
def get_category_route():
    return get_category()


@blueprint.route("/category", methods=["POST"])
def add_category_route():
    return add_category()


@blueprint.route("/edit_category/<int:category_id>", methods=["PUT"])
def edit_category_route(category_id):
    return edit_category(category_id)


@blueprint.route("/delete_category/<int:category_id>", methods=["DELETE"])
def delete_category_route(category_id):
    return delete_category(category_id)


@blueprint.route("/add_sub_category", methods=["POST"])
def add_sub_category_route():
    return add_subcategory()


@blueprint.route("/get_sub_category", methods=["GET"])
def get_sub_category_route():
    return get_subcategories()


@blueprint.route("/edit_sub_category/<int:id>", methods=["PUT"])
def edit_sub_category_route(id):
    return update_subcategory(id)


@blueprint.route("/delete_sub_category/<int:id>", methods=["DELETE"])
def delete_sub_category_route(id):
    return delete_subcategory(id)


@blueprint.route("/add_sub_sub_category", methods=["POST"])
def add_sub_sub_category_route():
    return create_sub_sub_category()


@blueprint.route("/get_sub_sub_category", methods=["GET"])
def get_sub_sub_category_route():
    return get_all_sub_sub_categories()


@blueprint.route("/update_sub_sub_categories/<int:id>", methods=["PUT"])
def update_sub_sub_category_route():
    return update_sub_sub_category(id)


@blueprint.route("/delete_sub_sub_category/<int:id>", methods=["DELETE"])
def delete_sub_sub_category_route(id):
    return delete_sub_sub_category(id)


@blueprint.route("/get_product_attributes", methods=["GET"])
def get_product_attributes_route():
    return get_attributes()


@blueprint.route("/add_product_attributes", methods=["POST"])
def add_product_attributes_route():
    return add_attribute()


@blueprint.route("/update_product_attributes/<int:id>", methods=["PUT"])
def update_product_attributes_route(id):
    return update_attribute(id)


@blueprint.route("/delete_product_attributes/<int:id>", methods=["DELETE"])
def del_product_attributes_route(id):
    return delete_attribute(id)


@blueprint.route("/get_notifications", methods=["GET"])
def get_notification_route():
    return get_notifications()


@blueprint.route("/add_notifications", methods=["POST"])
def add_notification_route():
    return add_notification()


@blueprint.route("/del_notifications/<int:id>", methods=["DELETE"])
def del_notification_route():
    return delete_notification(id)


@blueprint.route("/edit_notifications/<int:id>", methods=["DELETE"])
def edit_notification_route():
    return update_notification(id)


@blueprint.route("/add_push_notification", methods=["POST"])
def add_push_notification_route():
    return create_push_notification()


@blueprint.route("/get_push_notification", methods=["GET"])
def get_push_notification_route():
    return get_push_notifications()


@blueprint.route("/edit_push_notification/<int:id>", methods=["PUT"])
def edit_push_notification_route(id):
    return update_push_notification(id)


@blueprint.route("/delete_push_notification/<int:id>", methods=["DELETE"])
def delete_push_notification_route(id):
    return delete_push_notification(id)


@blueprint.route("/create_announcement", methods=["POST"])
def create_announcement_route():
    return create_announcement()


@blueprint.route("/get_announcement", methods=["GET"])
def get_announcements_route():
    return get_announcements()


@blueprint.route("/edit_announcement/<int:id>", methods=["PUT"])
def edit_announcements_route(id):
    return update_announcement(id)


@blueprint.route("/delete_announcement/<int:id>", methods=["DELETE"])
def del_announcements_route(id):
    return delete_announcement(id)


@blueprint.route("/add_request_stocks", methods=["POST"])
@token_required
@cross_origin()
def create_restock_request_route():
    return create_restock_request()


@blueprint.route("/get_request_stocks", methods=["GET"])
def get_restock_requests_route():
    return get_restock_requests()


@blueprint.route("/restock_requests", methods=["GET"])
def restock_requests_route():
    # alias for older helpers or direct frontend calls
    return get_restock_requests()


# @blueprint.route('/seller_get_request_stock', methods=['GET'])
# @token_required
# @cross_origin()
# def get_restock_request_seller_route():
#     return get_restock_request_seller()


@blueprint.route("/update_restock_request/<int:id>", methods=["PUT"])
def update_restock_request_route(id):
    return update_restock_request(id)


@blueprint.route("/delete_restock_request/<int:id>", methods=["DELETE"])
def delete_restock_request_route(id):
    return delete_restock_request(id)


# @blueprint.route('/add_update_product', methods=['POST'])
# def add_update_product_route():
#     return add_update_product()


@blueprint.route("/get_update_product", methods=["GET"])
def get_update_product_route():
    return get_update_products()


#
# @blueprint.route('/update_products/<int:id>', methods=['PUT'])
# def update_product_route(id):
#     return update_product(id)
#
#
# @blueprint.route('/delete_update_products/<int:id>', methods=['PUT'])
# def delete_update_product_route(id):
#     return delete_update_product(id)


@blueprint.route("/approved_products_list", methods=["GET"])
def approved_products_route():
    return get_approved_products()


@blueprint.route("/denied_products_list", methods=["GET"])
def denied_products_route():
    return get_denied_products()


@blueprint.route("/send_email", methods=["POST"])
def send_email_route():
    data = request.get_json()
    to_email = data.get("to_email")
    subject = data.get("subject")
    body = data.get("body")
    original_uid = data.get("original_uid")

    return send_email(to_email, subject, body, original_uid)


@blueprint.route("/read_emails", methods=["GET"])
def read_emails_route():
    return read_emails()


@blueprint.route("/delete_emails/<uid>", methods=["DELETE"])
def delete_email_route(uid):
    return delete_email(uid)


@blueprint.route("/customer_review", methods=["POST"])
def insert_customer_review():
    return create_review()


@blueprint.route("/get_customer_review", methods=["GET"])
def get_customer_review_route():
    return get_all_reviews()


@blueprint.route("/get_customer_review/<int:product_id>", methods=["GET"])
def get_customer_review_product(product_id):
    return get_reviews_by_product(product_id)


@blueprint.route("/get_customer_review/<int:seller_id>", methods=["GET"])
def get_customer_review_seller_route(seller_id):
    return get_reviews_by_seller(seller_id)


@blueprint.route("/update_customer_review/<int:id>", methods=["PUT"])
def update_customer_review(id):
    return update_review(id)


@blueprint.route("/delete_customer_review/<int:id>", methods=["DELETE"])
def delete_customer_review(id):
    return delete_review(id)


@blueprint.route("/general_settings", methods=["GET"])
def general_settings_route():
    return get_general_settings()


@blueprint.route("/customer_settings", methods=["POST"])
def create_setting_route():
    return create_settings()


@blueprint.route("/update_settings", methods=["PUT"])
def update_settings_route():
    return update_settings()


@blueprint.route("/get_payment", methods=["GET"])
def get_payment_options_route():
    return get_payment_options()


@blueprint.route("/save_payment", methods=["POST", "PUT"])
def save_payment_options_route():
    return save_payment_options()


@blueprint.route("/save_product_settings", methods=["POST", "PUT"])
def save_product_settings_route():
    return save_or_update_product_settings()


@blueprint.route("/get_product_settings", methods=["GET"])
def get_product_settings_route():
    return get_product_settings()


@blueprint.route("/get_priority", methods=["GET", "POST"])
@cross_origin()
def get_priority_route():
    return get_priority()


@blueprint.route("/update_priority", methods=["PUT"])
@cross_origin()
def update_priority_route():
    return update_priority()


@blueprint.route("/get_order_settings", methods=["GET"])
def get_order_settings_route():
    return get_order_settings()


@blueprint.route("/save_order_settings", methods=["POST", "PUT"])
def save_order_settings_route():
    return save_order_settings()


@blueprint.route("/vendor_settings", methods=["GET", "POST"])
def vendor_settings_route():
    if request.method == "GET":
        return get_vendor_settings()
    else:
        return save_vendor_settings()


@blueprint.route("/update_vendor_settings/<int:setting_id>", methods=["PUT"])
def update_vendor_settings_route(setting_id):
    return update_vendor_settings(setting_id)


@blueprint.route("/customer_settings", methods=["GET"])
def customer_settings_route():
    return get_customer_settings()


@blueprint.route("/update_customer_settings", methods=["PUT"])
def update_customer_settings_route():
    return update_customer_settings()


@blueprint.route("/delivery_settings", methods=["GET", "POST", "PUT"])
def delivery_settings_route():
    return delivery_settings()


@blueprint.route("/get_shipping_settings", methods=["GET"])
def shipping_settings_route():
    return get_shipping_settings()


@blueprint.route("/update_shipping_settings", methods=["PUT"])
def update_shipping_settings_route():
    return update_shipping_settings()


@blueprint.route("/create_shipping_settings", methods=["POST"])
def create_shipping_settings_route():
    return create_shipping_settings()

@blueprint.route("/delivery_restriction_setting", methods=["GET", "POST", "PUT"])
def delivery_restriction_settings_route():
    if request.method == "GET":
        return get_delivery_restriction_settings()  
    elif request.method == "POST":
        return create_delivery_restriction_settings()
    elif request.method == "PUT":
        return update_delivery_restriction_settings()
    
@blueprint.route("/invoice_settings",methods=["GET", "POST", "PUT"])
def invoice_settings_route():
    if request.method == "GET":
        return invoice_settings()
    elif request.method == "POST":
        return invoice_settings()
    elif request.method == "PUT":
        return invoice_settings()
    
@blueprint.route("/inhouse-settings-setup",methods=["GET", "POST", "PUT"])
def inhouse_settings_setup_route():
    return inhouse_settings_setup()

@blueprint.route("/seo_settings",methods=["GET", "POST", "PUT"])
def seo_settings_route():
    if request.method == "GET":
        return handle_seo_settings()
    elif request.method == "POST":
        return handle_seo_settings()
    elif request.method == "PUT":
        return handle_seo_settings()
    
@blueprint.route("/environment-settings", methods=["GET"])
def get_environment_settings_route():
    return get_environment_settings()

@blueprint.route("/environment-settings", methods=["POST", "PUT"])
def update_environment_settings_route():
    return update_environment_settings()

@blueprint.route("/app-settings", methods=["GET"])
def get_app_settings_route():
    return get_app_settings()

@blueprint.route("/app-settings", methods=["POST", "PUT"])
def update_app_settings_route():
    return update_app_settings()

@blueprint.route("/languages", methods=["GET"])
def get_languages_route():
    return get_languages()

@blueprint.route("/languages", methods=["POST"])
def add_language_route():
    return add_language()

@blueprint.route("/languages/<int:lang_id>", methods=["PUT"])
def update_language_route(lang_id):
    return update_language(lang_id)

@blueprint.route("/currencies", methods=["GET"])
def get_currencies_route():
    return get_currencies()

@blueprint.route("/currencies", methods=["POST"])
def add_currency_route():
    return add_currency()

@blueprint.route("/currencies/<int:currency_id>/set-default", methods=["PUT"])
def set_default_currency_route(currency_id):
    return set_default_currency(currency_id)

@blueprint.route("/cookie-settings", methods=["GET"])
def get_cookie_settings_route():
    return get_cookie_settings()

@blueprint.route("/cookie-settings", methods=["POST", "PUT"])
def update_cookie_settings_route():
    return update_cookie_settings()

@blueprint.route("/clean-database/<string:target>", methods=["DELETE"])
def clean_database_route(target):
    return clean_database(target)

@blueprint.route("/software_update", methods=["GET", "POST", "PUT", "DELETE"])
def software_update_route():
    return software_update()

@blueprint.route("/login_settings", methods=["GET","POST","PUT"])
def login_settings_route():
   return login_settings()

@blueprint.route("/payment_methods_handler", methods=["POST","GET","PUT"])
def payment_methods_handler_route():
    return payment_methods_handler()


# Create a Stripe PaymentIntent and return client_secret
@blueprint.route('/create_payment_intent', methods=['POST'])
def create_payment_intent_route():
    try:
        data = request.json or {}
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        metadata = data.get('metadata', {})

        if amount is None:
            return jsonify({'error': 'Amount is required'}), 400

        # amount expected in major currency (e.g., dollars); convert to cents
        amount_cents = int(round(float(amount) * 100))

        intent = create_payment_intent(amount_cents, currency=currency, metadata=metadata)

        return jsonify({'client_secret': intent.client_secret, 'id': intent.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Stripe webhook endpoint
@blueprint.route('/stripe_webhook', methods=['POST'])
def stripe_webhook_route():
    return handle_stripe_webhook(request)


@blueprint.route('/create_stripe_session', methods=['POST'])
def create_stripe_session_route():
    try:
        data = request.json or {}
        items = data.get('items', [])
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')

        if not items or not success_url or not cancel_url:
            return jsonify({'error': 'items, success_url and cancel_url are required'}), 400

        # Build line_items for Stripe (expects price_data or price id); we'll use simple price_data
        line_items = []
        for it in items:
            # amount in cents
            unit_amount = int(round(float(it.get('unit_price', 0)) * 100))
            qty = int(it.get('quantity', 1))
            line_items.append({
                'price_data': {
                    'currency': data.get('currency', 'usd'),
                    'product_data': {'name': it.get('product_name', 'Item')},
                    'unit_amount': unit_amount,
                },
                'quantity': qty
            })

        session = create_checkout_session(line_items, success_url, cancel_url, metadata=data.get('metadata'))
        return jsonify({'url': session.url, 'id': session.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Admin Order Management Routes
@blueprint.route("/admin/orders", methods=["GET"])
def admin_orders_route():
    return get_admin_orders()

@blueprint.route("/admin/orders/<int:order_id>", methods=["GET"])
def admin_order_details_route(order_id):
    return get_admin_order_details(order_id)

@blueprint.route("/admin/orders/update_status", methods=["PUT"])
def admin_update_order_status_route():
    return update_admin_order_status()

@blueprint.route("/admin/orders/stats", methods=["GET"])
def admin_order_stats_route():
    return get_admin_order_stats()
