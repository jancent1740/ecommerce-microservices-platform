import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Flask API is running in Docker!",
        "status": "success",
        "version": "1.0"
    })

@app.route('/api/products')
def get_products():
    response = requests.get('http://host.docker.internal:8000/api/products/')
    products = response.json()
    return jsonify(products)

@app.route('/api/orders')
def get_orders():
    try:
        response = requests.get('http://host.docker.internal:8000/api/placed-orders/')
        if response.status_code == 200:
            orders = response.json()
            return jsonify(orders)
        else:
            return jsonify({"error": "Failed to fetch orders"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Connection error: {str(e)}"}), 500

@app.route('/api/revenue-by-category')
def get_revenue_per_product():
    try:
        response = requests.get('http://host.docker.internal:8000/api/revenue-by-category/')
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/highest-selling-product')
def get_highest_selling():
    try:
        response = requests.get('http://host.docker.internal:8000/api/highest-selling-product/')
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/least-desirable-product')
def get_least_desirable():
    try:
        response = requests.get('http://host.docker.internal:8000/api/least-desirable-product/')
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)