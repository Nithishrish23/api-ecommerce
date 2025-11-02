from app import create_app
from flask import Flask, request, make_response
# from app.license_validator import license_validator
import sys
import os
from flask_cors import CORS

# Validate license before starting the server
# if not license_validator.validate_license("your-license-key"):
#     print("License validation failed. Server cannot start.")
#     sys.exit(1)

app = create_app()
CORS(app, supports_credentials=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
