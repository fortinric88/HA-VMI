"""
Data Parser - Parse EnOcean protocol messages
Based on Jeedom OpenEnocean plugin specifications
"""

import logging
import struct
from datetime import datetime

logger = logging.getLogger(__name__)


class DataParser:
    """Parse EnOcean protocol messages for supported devices"""
    
    # Device type mappings
    DEVICE_TYPES = {
        'd1079-01-00': 'VMI Purevent',
        'd1079-00-00': 'Assistant Ventilairsec',
        'a5-09-04': 'Sensor CO2',
        'a5-04-01': 'Sensor Temp/Humidity',
        'a5-04-02': 'Sensor Temp/Humidity Extended'
    }
    
    def __init__(self, config):
        """Initialize parser with configuration"""
        self.config = config
        self.devices = self._build_device_map(config)
    
    def _build_device_map(self, config):
        """Build mapping of device IDs to types"""
        devices = {}
        
        # Add VMI and assistant
        if 'vmi' in config.get('devices', {}):
            vmi = config['devices']['vmi']
            devices[vmi['id']] = vmi['type']
        
        if 'assistant' in config.get('devices', {}):
            asst = config['devices']['assistant']
            devices[asst['id']] = asst['type']
        
        # Add sensors
        for sensor in config.get('devices', {}).get('sensors', []):
            devices[sensor['id']] = sensor['type']
        
        return devices
    
    def parse(self, raw_data):
        """
        Parse raw EnOcean message
        
        Args:
            raw_data: Dictionary with packet data from EnOceanHandler
        
        Returns:
            Dictionary with parsed data or None
        """
        try:
            sender_id = raw_data.get('sender_id')
            rorg = raw_data.get('rorg')
            data = raw_data.get('data', [])
            
            # Find device type
            device_type = self.devices.get(sender_id)
            
            if not device_type:
                logger.debug(f"Unknown device: {sender_id}")
                return None
            
            # Parse according to device type
            if device_type == 'd1079-01-00':
                return self._parse_vmi_purevent(sender_id, data, raw_data)
            
            elif device_type == 'd1079-00-00':
                return self._parse_assistant(sender_id, data, raw_data)
            
            elif device_type == 'a5-09-04':
                return self._parse_co2_sensor(sender_id, data, raw_data)
            
            elif device_type in ['a5-04-01', 'a5-04-02']:
                return self._parse_temp_humidity_sensor(sender_id, data, raw_data)
            
            else:
                logger.warning(f"Unsupported device type: {device_type}")
                return None
                
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _parse_vmi_purevent(self, sender_id, data, raw_data):
        """Parse VMI Purevent (D1079-01-00) message"""
        try:
            parsed = {
                'device_id': sender_id,
                'device_type': 'd1079-01-00',
                'device_name': 'VMI Purevent',
                'timestamp': datetime.now().isoformat(),
                'raw_data': data.hex() if isinstance(data, bytes) else ''.join(f'{b:02x}' for b in data)
            }
            
            # Message structure based on Jeedom plugin
            # The VMI sends telemetry in specific byte patterns
            
            if len(data) >= 4:
                # Parse temperature values (scaled)
                # Temperature external
                if len(data) > 10:
                    temp_ext = (data[10] - 200) / 2.0
                    parsed['temperature_exterior'] = round(temp_ext, 1)
                
                # Heating power (percentage)
                if len(data) > 8:
                    parsed['heating_power'] = data[8]
                
                # Air flow output (m3/h)
                if len(data) > 9:
                    parsed['air_flow_output'] = data[9] * 2
            
            logger.debug(f"Parsed VMI data: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing VMI data: {e}")
            return None
    
    def _parse_assistant(self, sender_id, data, raw_data):
        """Parse Assistant Ventilairsec (D1079-00-00) message"""
        try:
            parsed = {
                'device_id': sender_id,
                'device_type': 'd1079-00-00',
                'device_name': 'Assistant Ventilairsec',
                'timestamp': datetime.now().isoformat(),
                'raw_data': data.hex() if isinstance(data, bytes) else ''.join(f'{b:02x}' for b in data)
            }
            
            logger.debug(f"Parsed Assistant data: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing Assistant data: {e}")
            return None
    
    def _parse_co2_sensor(self, sender_id, data, raw_data):
        """Parse CO2 Sensor (A5-09-04) message"""
        try:
            parsed = {
                'device_id': sender_id,
                'device_type': 'a5-09-04',
                'device_name': 'CO2 Sensor',
                'timestamp': datetime.now().isoformat()
            }
            
            if len(data) >= 4:
                # A5-09-04 format: CO2 concentration in ppm
                # Scale: 0-2500 ppm = 0-255 (bytes 0-1)
                co2_raw = (data[0] << 8) | data[1]
                parsed['co2_ppm'] = int((co2_raw / 255.0) * 2500)
            
            logger.debug(f"Parsed CO2 sensor: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing CO2 sensor: {e}")
            return None
    
    def _parse_temp_humidity_sensor(self, sender_id, data, raw_data):
        """Parse Temperature/Humidity Sensor (A5-04-01) message"""
        try:
            parsed = {
                'device_id': sender_id,
                'device_type': 'a5-04-01',
                'device_name': 'Temp/Humidity Sensor',
                'timestamp': datetime.now().isoformat()
            }
            
            if len(data) >= 4:
                # A5-04-01 format:
                # Byte 0: Temperature (0-255 = -20°C to +60°C)
                # Byte 1: Humidity (0-255 = 0-100%)
                temp_raw = data[0]
                humidity_raw = data[1]
                
                # Convert temperature: -20°C to +60°C range
                temp_celsius = -20 + (temp_raw / 255.0) * 80
                
                # Convert humidity: 0-100%
                humidity_percent = (humidity_raw / 255.0) * 100
                
                parsed['temperature'] = round(temp_celsius, 1)
                parsed['humidity'] = round(humidity_percent, 1)
            
            logger.debug(f"Parsed Temp/Humidity sensor: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing Temp/Humidity sensor: {e}")
            return None
