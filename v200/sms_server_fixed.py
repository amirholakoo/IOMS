#!/usr/bin/env python3
"""
SMS Server for HomayOMS
Handles SMS sending via SIM800C module
"""

import os
import time
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import serial
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sms_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SIM800CController:
    def __init__(self, port=None, baudrate=9600, timeout=10):
        # Auto-detect SIM800C port
        if port is None:
            port = self._detect_sim800c_port()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
    
    def _detect_sim800c_port(self):
        """Auto-detect SIM800C port"""
        import glob
        import subprocess
        
        # Common SIM800C ports (GPIO first, then USB)
        possible_ports = [
            '/dev/ttyAMA0',  # GPIO serial (Raspberry Pi)
            '/dev/ttyS0',    # Alternative GPIO serial
            '/dev/ttyUSB0',  # USB connection
            '/dev/ttyUSB1', 
            '/dev/ttyACM0',
            '/dev/ttyACM1'
        ]
        
        # Check which ports exist
        existing_ports = []
        for port in possible_ports:
            if os.path.exists(port):
                existing_ports.append(port)
        
        if not existing_ports:
            logger.warning("No serial ports found. SIM800C may not be connected.")
            return '/dev/ttyAMA0'  # Default to GPIO
        
        # Try to connect to each port and test AT command
        for port in existing_ports:
            try:
                logger.info(f"Testing port: {port}")
                test_conn = serial.Serial(port, 9600, timeout=2)
                test_conn.write(b'AT\r\n')
                time.sleep(1)
                response = test_conn.read_all().decode('utf-8', errors='ignore')
                test_conn.close()
                
                if 'OK' in response:
                    logger.info(f"SIM800C detected on {port}")
                    return port
            except Exception as e:
                logger.debug(f"Port {port} test failed: {e}")
                continue
        
        # If no port responds to AT command, use GPIO as default
        logger.warning(f"No SIM800C detected. Using GPIO port: {existing_ports[0]}")
        return existing_ports[0]
        
    def connect(self):
        """Establish connection to SIM800C module"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Connected to SIM800C on {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SIM800C: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn:
            self.serial_conn.close()
            logger.info("Disconnected from SIM800C")
    
    def send_command(self, command, wait_time=1):
        """Send AT command and get response"""
        if not self.serial_conn:
            return None
            
        try:
            # Clear buffer
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
            # Send command
            self.serial_conn.write(f"{command}\r\n".encode())
            time.sleep(wait_time)
            
            # Read response
            response = ""
            while self.serial_conn.in_waiting:
                response += self.serial_conn.read().decode('utf-8', errors='ignore')
            
            logger.debug(f"Command: {command}, Response: {response}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error sending command {command}: {e}")
            return None
    
    def check_signal_strength(self):
        """Check signal strength"""
        response = self.send_command("AT+CSQ")
        if response and "CSQ:" in response:
            try:
                csq = response.split("CSQ:")[1].split(",")[0].strip()
                return int(csq)
            except:
                return 0
        return 0
    
    def check_network_registration(self):
        """Check network registration status"""
        response = self.send_command("AT+CREG?")
        if response and "CREG:" in response:
            try:
                status = response.split("CREG:")[1].split(",")[1].strip()
                return int(status)
            except:
                return 0
        return 0
    
    def send_sms(self, phone_number, message):
        """Send SMS message"""
        # For testing without SIM800C, just log the message
        if not self.serial_conn:
            logger.info(f"FAKE SMS - To: {phone_number}, Message: {message}")
            return True, "SMS logged (SIM800C not connected)"
        
        try:
            # Set SMS text mode
            self.send_command("AT+CMGF=1")
            
            # Set phone number
            self.send_command(f'AT+CMGS="{phone_number}"')
            time.sleep(1)
            
            # Send message content
            self.serial_conn.write(f"{message}\x1A".encode())
            time.sleep(5)
            
            # Read response
            response = ""
            while self.serial_conn.in_waiting:
                response += self.serial_conn.read().decode('utf-8', errors='ignore')
            
            logger.info(f"SMS sent to {phone_number}: {response}")
            
            # FIXED: Handle different response formats
            if "OK" in response:
                return True, "SMS sent successfully"
            elif "ERROR" in response:
                return False, "SMS sending failed"
            elif any(char.isdigit() for char in response.strip()):
                # If response contains numbers (like message ID), consider it successful
                return True, f"SMS sent successfully (ID: {response.strip()})"
            else:
                # If we got any response but no clear success/error, assume success
                return True, f"SMS sent successfully (Response: {response.strip()})"
                
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False, str(e)

# Initialize SIM800C controller
sms_controller = SIM800CController()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if not sms_controller.serial_conn:
            sms_controller.connect()
        
        if sms_controller.serial_conn:
            signal = sms_controller.check_signal_strength()
            network = sms_controller.check_network_registration()
            
            return jsonify({
                'status': 'healthy',
                'signal': signal,
                'network': network,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': 'SIM800C not connected',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/verify/send', methods=['POST'])
def send_sms():
    """Send SMS endpoint"""
    try:
        # Check API key
        api_key = request.headers.get('X-API-Key')
        expected_key = config('SMS_API_KEY', default='ioms_sms_server_2025')
        
        if api_key != expected_key:
            return jsonify({
                'success': False,
                'message': 'Invalid API key'
            }), 401
        
        # Get request data
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({
                'success': False,
                'message': 'Missing phone_number or message'
            }), 400
        
        # Connect to SIM800C if not connected
        if not sms_controller.serial_conn:
            if not sms_controller.connect():
                return jsonify({
                    'success': False,
                    'message': 'SIM800C connection failed'
                }), 500
        
        # Send SMS
        success, result = sms_controller.send_sms(phone_number, message)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully',
                'phone_number': phone_number,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'SMS sending failed: {result}',
                'phone_number': phone_number,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"SMS sending error: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Get SMS server status"""
    try:
        if not sms_controller.serial_conn:
            sms_controller.connect()
        
        signal = sms_controller.check_signal_strength()
        network = sms_controller.check_network_registration()
        
        return jsonify({
            'connected': sms_controller.serial_conn is not None,
            'signal_strength': signal,
            'network_registration': network,
            'port': sms_controller.port,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'connected': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Load configuration
    port = config('SMS_SERVER_PORT', default=5003, cast=int)
    host = config('SMS_SERVER_HOST', default='0.0.0.0')
    debug = config('SMS_SERVER_DEBUG', default=False, cast=bool)
    
    logger.info(f"Starting SMS server on {host}:{port}")
    
    # Try to connect to SIM800C
    if sms_controller.connect():
        logger.info("SIM800C connected successfully")
    else:
        logger.warning("SIM800C connection failed - server will start but SMS may not work")
    
    # Start Flask server
    app.run(host=host, port=port, debug=debug) 