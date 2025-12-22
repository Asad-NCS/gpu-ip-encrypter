import socket
import logging
import os
import sys

import config

# windows needs this for cuda to work
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64')

from gpu_aes import AESGpu
from scapy.all import IP

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/encrypter.log", mode='w'),
        logging.StreamHandler()
    ]
)

def ip_to_bytes(ip):
    return socket.inet_aton(ip)

#this new code added later to convert bytes to ip address
def bytes_to_ip(b):
    return socket.inet_ntoa(b)

#this new code added later to convert bytes to hex dump for display
def hex_dump(data, max_bytes=64):
    """Return hex dump of data for logging"""
    snippet = data[:max_bytes]
    hex_str = ' '.join(f'{b:02x}' for b in snippet)
    if len(data) > max_bytes:
        hex_str += f' ... ({len(data)} bytes total)'
    return hex_str

def start_encrypter():
    print("Initializing Encrypter...", flush=True)
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
        
        sock.bind((config.ENCRYPTER_HOST, config.ENCRYPTER_PORT))
        logging.info(f"Encrypter listening on {config.ENCRYPTER_HOST}:{config.ENCRYPTER_PORT}")
        
        packet_count = 0
        while True:
            # We expect to receive the raw IP packet as payload from Injector
            # Or does Injector send a UDP packet with the IP packet as payload?
            # Yes, Injector "tunnels" the IP packet.
            data, addr = sock.recvfrom(65535)
            packet_count += 1
            
            # dont log every single packet or console will explode
            should_log = (packet_count % 1000 == 0) or (packet_count < 5)

            if should_log:
                logging.info(f"Received {len(data)} bytes from {addr} (Packet #{packet_count})")
            
            try:
                # Parse the inner IP packet to get Src/Dst/Payload
                # We can use Scapy to parse the bytes
                pkt = IP(data)
                
                src_ip = pkt.src
                dst_ip = pkt.dst
                # Payload of IP (includes UDP/TCP header)
                payload = bytes(pkt.payload)
                
                if should_log:
                    logging.info(f"Encrypting packet: {src_ip} -> {dst_ip}")
                
                # Serialize: SrcIP (4) + DstIP (4) + Payload
                data_to_encrypt = ip_to_bytes(src_ip) + ip_to_bytes(dst_ip) + payload
                
                if should_log:
                    logging.info(f"Plaintext: {hex_dump(data_to_encrypt)}")
                
                # Encrypt
                encrypted_data = aes.encrypt(data_to_encrypt)
                
                if should_log:
                    logging.info(f"Encrypted: {hex_dump(encrypted_data)}")
                
                # Send to Decrypter
                sock.sendto(encrypted_data, (config.DECRYPTER_HOST, config.DECRYPTER_PORT))
                if should_log:
                    logging.info(f"Sent encrypted data to {config.DECRYPTER_HOST}:{config.DECRYPTER_PORT}")

            except Exception as e:
                logging.error(f"Processing failed: {e}")

    except Exception as e:
        logging.error(f"Socket error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_encrypter()
