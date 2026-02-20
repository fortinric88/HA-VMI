"""
EnOcean Handler - Communication with EnOcean GPIO module
"""

import logging
import threading
import time
from queue import Queue

from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean import utils

logger = logging.getLogger(__name__)


class EnOceanHandler:
    """Handle EnOcean communication via serial port"""
    
    def __init__(self, port, config, callback=None):
        """
        Initialize EnOcean handler
        
        Args:
            port: Serial port (e.g., /dev/ttyAMA0)
            config: Configuration dictionary
            callback: Callback function for received messages
        """
        self.port = port
        self.config = config
        self.callback = callback
        self.communicator = None
        self.running = False
        self.receive_thread = None
        
    def start(self):
        """Start EnOcean communication"""
        try:
            logger.info(f"Initializing EnOcean on port {self.port}")
            
            # Create serial communicator
            self.communicator = SerialCommunicator(
                port=self.port,
                baudrate=57600,
                timeout=1
            )
            
            # Start communicator
            self.communicator.start()
            self.running = True
            
            # Get base ID
            time.sleep(1)
            if self.communicator.base_id:
                base_id_hex = utils.to_hex_string(self.communicator.base_id)
                logger.info(f"EnOcean Base ID: {base_id_hex}")
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            logger.info("EnOcean handler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start EnOcean handler: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop EnOcean communication"""
        try:
            logger.info("Stopping EnOcean handler")
            self.running = False
            
            if self.communicator:
                self.communicator.stop()
            
            # Wait for receive thread
            if self.receive_thread:
                self.receive_thread.join(timeout=5)
            
            logger.info("EnOcean handler stopped")
        except Exception as e:
            logger.error(f"Error stopping EnOcean handler: {e}")
    
    def is_connected(self):
        """Check if EnOcean is connected"""
        return self.running and self.communicator and self.communicator.is_alive()
    
    def _receive_loop(self):
        """Loop to receive messages from EnOcean"""
        logger.info("Starting message receive loop")
        
        while self.running:
            try:
                # Get packet from queue with timeout
                packet = self.communicator.receive.get(block=True, timeout=1)
                
                if packet:
                    self._process_packet(packet)
                    
            except Exception as e:
                # Queue timeout is normal, don't log it
                if "Empty" not in str(type(e)):
                    logger.debug(f"Receive loop exception: {e}")
                continue
        
        logger.info("Message receive loop stopped")
    
    def _process_packet(self, packet):
        """Process received EnOcean packet"""
        try:
            if isinstance(packet, RadioPacket):
                # Extract basic packet info
                sender_id = utils.to_hex_string(packet.sender_id).replace(':', '').upper()
                sender_id_int = int.from_bytes(packet.sender_id, 'big')
                
                logger.debug(f"Received packet from: {sender_id}")
                
                # Build data dictionary
                data = {
                    'sender_id': sender_id,
                    'sender_id_int': sender_id_int,
                    'rorg': packet.rorg,
                    'data': packet.data,
                    'status': packet.status,
                    'repeater_level': packet.repeater_level,
                    'timestamp': time.time()
                }
                
                # Call callback if configured
                if self.callback:
                    self.callback(data)
                    
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    def send_packet(self, receiver_id, data, rorg='F6'):
        """
        Send EnOcean packet
        
        Args:
            receiver_id: Target device ID (hex string)
            data: Payload data (bytes)
            rorg: Radio organization type
        """
        try:
            if not self.is_connected():
                logger.error("EnOcean not connected, cannot send packet")
                return False
            
            logger.info(f"Sending packet to {receiver_id}")
            
            # Create and send packet
            packet = RadioPacket(
                rorg=rorg,
                data=data,
                receiver=bytes.fromhex(receiver_id.replace(':', '')),
                learn=False
            )
            
            self.communicator.send(packet)
            return True
            
        except Exception as e:
            logger.error(f"Error sending packet: {e}")
            return False
