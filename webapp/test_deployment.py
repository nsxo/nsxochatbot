#!/usr/bin/env python3
"""
Simple test script to verify Flask API deployment.
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Admin Dashboard API is working!',
        'status': 'success',
        'service': 'flask-admin-api',
        'working_directory': os.getcwd(),
        'files': os.listdir('.'),
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'unknown')
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'admin-dashboard-api',
        'message': 'Flask API is running correctly'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print(f"🚀 Starting test Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 