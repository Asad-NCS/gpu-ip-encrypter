import socket
import logging
import config
import os 
# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/destination.log", mode='w'),
        logging.StreamHandler()
    ]
)

def hex_dump(data, max_bytes=64):
    """Return hex dump of data for logging"""
    snippet = data[:max_bytes]
    hex_str = ' '.join(f'{b:02x}' for b in snippet)
    if len(data) > max_bytes:
        hex_str += f' ... ({len(data)} bytes total)'
    return hex_str

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Bind to 0.0.0.0 to receive from any interface
        bind_host = "0.0.0.0"
        sock.bind((bind_host, config.DESTINATION_PORT))
        logging.info(f"Destination listening on {bind_host}:{config.DESTINATION_PORT}")
        
        while True:
            data, addr = sock.recvfrom(65535)
            logging.info(f"Received packet from {addr}: {len(data)} bytes")
            logging.info(f"Payload: {hex_dump(data)}")
            # We expect raw payload here? Or the full packet?
            # The Decrypter sends "IP(src=OriginalSrc, dst=OriginalDst) / UDP / Payload"
            # If Decrypter uses raw socket or scapy send, it sends a full IP packet.
            # If Destination is a standard UDP socket, it receives the PAYLOAD of the UDP packet destined to it.
            # If Decrypter sends a UDP packet to 127.0.0.1:12345, the OS stack handles IP/UDP headers
            # and gives the payload to this socket.
            
            

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()
