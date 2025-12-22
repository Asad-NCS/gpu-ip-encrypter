import socket
import logging
import os
import sys

import config

# windows needs this for cuda to work
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64')

from gpu_aes import AESGpu
from scapy.all import IP, UDP, send

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/decrypter.log", mode='w'),
        logging.StreamHandler()
    ]
)

def bytes_to_ip(b):
    return socket.inet_ntoa(b)

def hex_dump(data, max_bytes=64):
    """Return hex dump of data for logging"""
    snippet = data[:max_bytes]
    hex_str = ' '.join(f'{b:02x}' for b in snippet)
    if len(data) > max_bytes:
        hex_str += f' ... ({len(data)} bytes total)'
    return hex_str

def start_decrypter():
    # Initialize GPU AES
    print("Initializing Decrypter...", flush=True)
    try:
        print("Creating AESGpu instance...", flush=True)
        aes = AESGpu(config.AES_KEY)
        logging.info("GPU AES initialized.")
    except Exception as e:
        logging.error(f"Failed to init GPU AES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Increase receive buffer size to prevent packet loss during bursts
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, config.SOCKET_BUFFER_SIZE)
        
        sock.bind((config.DECRYPTER_HOST, config.DECRYPTER_PORT))
        logging.info(f"Decrypter listening on {config.DECRYPTER_HOST}:{config.DECRYPTER_PORT}")
        
        packet_count = 0
        while True:
            encrypted_data, addr = sock.recvfrom(65535)
            packet_count += 1
            
            # Only log every 1000th packet to avoid console spam/packet loss
            should_log = (packet_count % 1000 == 0) or (packet_count < 5)

            if should_log:
                logging.info(f"Received {len(encrypted_data)} bytes from {addr} (Packet #{packet_count})")
                logging.info(f"Encrypted: {hex_dump(encrypted_data)}")
            
            try:
                # Decrypt
                decrypted_data = aes.decrypt(encrypted_data)
                
                if should_log:
                    logging.info(f"Decrypted: {hex_dump(decrypted_data)}")
                
                # Parse: SrcIP (4) + DstIP (4) + Payload
                if len(decrypted_data) < 8:
                    # This might happen if decryption failed or padding was wrong
                    # logging.error("Decrypted data too short.") 
                    continue
                    
                original_src_bytes = decrypted_data[:4]
                original_dst_bytes = decrypted_data[4:8]
                original_payload = decrypted_data[8:]
                
                original_src = bytes_to_ip(original_src_bytes)
                original_dst = bytes_to_ip(original_dst_bytes)
                
                if should_log:
                    logging.info(f"Decrypted: Src={original_src}, Dst={original_dst}, PayloadLen={len(original_payload)}")
                
                # forward to destination
                # cant spoof source ip easily on windows so we just send it normally
                
                # original_payload has the UDP header + data
                # we need to strip the 8 byte header since we're sending via a fresh socket
                # otherwise we get double headers
                
                if len(original_payload) > 8:
                    real_payload = original_payload[8:]
                    # We assume destination port is 12345 as per destination.py
                    # In a real scenario, we would extract the destination port from the UDP header in original_payload.
                    # UDP Header: Source Port (2), Dest Port (2), Length (2), Checksum (2)
                    
                    # Let's parse the UDP header to be correct
                    udp_header = original_payload[:8]
                    
                    # Send the REAL payload to the destination
                    sock.sendto(real_payload, (config.DESTINATION_HOST, config.DESTINATION_PORT))
                    
                    if should_log:
                        logging.info(f"Forwarded {len(real_payload)} bytes to {config.DESTINATION_HOST}:{config.DESTINATION_PORT}")
                else:
                    if should_log:
                        logging.warning("Payload too short to contain UDP header")

            except Exception as e:
                logging.error(f"Processing failed: {e}")

    except Exception as e:
        logging.error(f"Socket error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_decrypter()
