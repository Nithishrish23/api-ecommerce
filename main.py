from app import create_app
from flask import Flask, request, make_response
from app.license_validator import license_validator
import sys
<<<<<<< HEAD
=======
import os
>>>>>>> 3e32fcab45e2833b65e20d6a3bf1cf24ce2d8a7a
from flask_cors import CORS

# Validate license before starting the server
# if not license_validator.validate_license("your-license-key"):
#     print("License validation failed. Server cannot start.")
#     sys.exit(1)

app = create_app()
<<<<<<< HEAD

# @app.before_request
# def handle_options_request():
#     if request.method == "OPTIONS":
#         response = make_response()
#         origin = request.headers.get("Origin")
#         # Only allow specific origins when using credentials
#         allowed_origins = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
#         if origin in allowed_origins:
#             response.headers["Access-Control-Allow-Origin"] = origin
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
#         response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Access-Control-Allow-Origin"
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         return response, 200

# @app.after_request
# def add_cors_headers(response):
#     origin = request.headers.get("Origin")
#     # Only allow specific origins when using credentials
#     allowed_origins = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]
#     if origin in allowed_origins:
#         response.headers["Access-Control-Allow-Origin"] = origin
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#     return response
=======
CORS(app)
>>>>>>> 3e32fcab45e2833b65e20d6a3bf1cf24ce2d8a7a

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
