import socket
import logging
import os
import sys
import time
from scapy.all import IP, UDP, Raw
import config

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/sender.log", mode='w'),
        logging.StreamHandler()
    ]
)

def send_file(filename):
    if not os.path.exists(filename):
        logging.error(f"File {filename} does not exist.")
        return False
    
    file_size = os.path.getsize(filename)
    logging.info(f"Sending file: {filename} ({file_size} bytes)")
    logging.info(f"Target Encrypter: {config.ENCRYPTER_HOST}:{config.ENCRYPTER_PORT}")
    logging.info(f"Final Destination: {config.DESTINATION_HOST}:{config.DESTINATION_PORT}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # max udp payload is around 65k but we stick to 8kb chunks
    # keeps cpu usage sane and packets manageable
    chunk_size = config.CHUNK_SIZE
    bytes_sent = 0
    
    try:
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # wrap the data in a raw IP packet so the encrypter knows what to do with it
                # encrypter needs IP, decrypter expects IP/UDP structure
                pkt = IP(dst=config.DESTINATION_HOST)/UDP(dport=config.DESTINATION_PORT)/Raw(load=chunk)
                data_to_send = bytes(pkt)

                # Send to encrypter
                sock.sendto(data_to_send, (config.ENCRYPTER_HOST, config.ENCRYPTER_PORT))
                bytes_sent += len(chunk)
                
                # Progress update
                if bytes_sent % config.PROGRESS_INTERVAL_BYTES < chunk_size:
                    logging.info(f"Sent {bytes_sent}/{file_size} bytes ({100*bytes_sent//file_size}%)")
                
                # tiny sleep to prevent packet loss on the other end
                time.sleep(0.005)
        
        logging.info(f"File transfer complete: {bytes_sent} bytes sent")
        logging.info("Waiting 5 seconds before closing to ensure all packets arrive...")
        time.sleep(5)
        return True
        
    except Exception as e:
        logging.error(f"Error sending file: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python file_sender.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    send_file(filename)
