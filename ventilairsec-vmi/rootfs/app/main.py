"""
Ventilairsec VMI Monitor - Main Application
Addon Home Assistant pour monitorer la VMI Purevent via EnOcean
"""

import json
import logging
import os
import sys
import argparse
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

from enocean_handler import EnOceanHandler
from data_parser import DataParser
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Global variables
config = None
db = None
enocean_handler = None
data_parser = None


def load_config(config_path):
    """Load configuration from JSON file"""
    logger.info(f"Loading config from {config_path}")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)


def init_app(config_data, db_path, logs_path):
    """Initialize the application"""
    global config, db, enocean_handler, data_parser
    
    config = config_data
    
    # Set log level
    log_level = config.get('log_level', 'info').upper()
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Initialize database
    db = Database(db_path)
    db.initialize()
    
    # Initialize data parser
    data_parser = DataParser(config)
    
    # Initialize EnOcean handler
    enocean_handler = EnOceanHandler(
        port=config.get('serial_port', '/dev/ttyAMA0'),
        config=config,
        callback=on_enocean_message
    )
    
    logger.info("Application initialized successfully")


def on_enocean_message(data):
    """Callback for EnOcean message reception"""
    try:
        # Parse the message
        parsed_data = data_parser.parse(data)
        
        if parsed_data:
            # Store in database
            db.insert_reading(parsed_data)
            
            # Log for debugging
            logger.debug(f"Received and stored: {parsed_data}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


# REST API Endpoints
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'enocean_connected': enocean_handler.is_connected() if enocean_handler else False
    })


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of configured devices"""
    devices = []
    
    if 'vmi' in config.get('devices', {}):
        devices.append({
            'id': config['devices']['vmi']['id'],
            'name': config['devices']['vmi']['name'],
            'type': config['devices']['vmi']['type']
        })
    
    if 'assistant' in config.get('devices', {}):
        devices.append({
            'id': config['devices']['assistant']['id'],
            'name': config['devices']['assistant']['name'],
            'type': config['devices']['assistant']['type']
        })
    
    # Add sensors
    for sensor in config.get('devices', {}).get('sensors', []):
        devices.append({
            'id': sensor['id'],
            'name': sensor['name'],
            'type': sensor['type']
        })
    
    return jsonify(devices)


@app.route('/api/current', methods=['GET'])
def get_current():
    """Get current readings for all devices"""
    try:
        readings = db.get_latest_readings()
        return jsonify(readings)
    except Exception as e:
        logger.error(f"Error getting current readings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<device_id>', methods=['GET'])
def get_history(device_id):
    """Get historical readings for a device"""
    try:
        hours = request.args.get('hours', 24, type=int)
        readings = db.get_readings_history(device_id, hours)
        return jsonify(readings)
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reading/<device_id>/<metric>', methods=['GET'])
def get_metric(device_id, metric):
    """Get specific metric for a device"""
    try:
        hours = request.args.get('hours', 24, type=int)
        data = db.get_metric_history(device_id, metric, hours)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting metric: {e}")
        return jsonify({'error': str(e)}), 500


# Web Interface Routes
@app.route('/', methods=['GET'])
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/settings', methods=['GET'])
def settings():
    """Settings page"""
    return render_template('settings.html')


def run_server(port):
    """Run Flask server"""
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


def daemon_enocean():
    """Run EnOcean handler in background"""
    try:
        logger.info("Starting EnOcean handler")
        enocean_handler.start()
    except Exception as e:
        logger.error(f"EnOcean handler error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Ventilairsec VMI Monitor')
    parser.add_argument('--config', required=True, help='Path to config.json')
    parser.add_argument('--db', required=True, help='Path to database directory')
    parser.add_argument('--logs', required=True, help='Path to logs directory')
    
    args = parser.parse_args()
    
    # Create directories if they don't exist
    Path(args.db).mkdir(parents=True, exist_ok=True)
    Path(args.logs).mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    config_data = load_config(args.config)
    
    # Initialize application
    init_app(config_data, args.db, args.logs)
    
    # Start EnOcean handler in background thread
    enocean_thread = threading.Thread(target=daemon_enocean, daemon=True)
    enocean_thread.start()
    
    # Give EnOcean time to initialize
    time.sleep(2)
    
    # Start web server
    web_port = config.get('web_port', 5000)
    run_server(web_port)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        if enocean_handler:
            enocean_handler.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
