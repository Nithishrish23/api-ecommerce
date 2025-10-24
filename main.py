from app import create_app
from flask import Flask, request, make_response
from app.license_validator import license_validator
import sys

# Validate license before starting the server
if not license_validator.validate_license("your-license-key"):
    print("License validation failed. Server cannot start.")
    sys.exit(1)

app = create_app()

@app.before_request
def handle_options_request():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Access-Control-Allow-Origin"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)