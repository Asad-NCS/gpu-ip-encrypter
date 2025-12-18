import logging
from scapy.all import rdpcap, IP
import socket
import time
import config
import os

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/injector.log", mode='w'),
        logging.StreamHandler()
    ]
)

PCAP_FILE = "test_traffic.pcap"

def run_injector():
    logging.info(f"Loading {PCAP_FILE}...")
    packets = rdpcap(PCAP_FILE)
    logging.info(f"Loaded {len(packets)} packets.")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i, pkt in enumerate(packets):
        if IP in pkt:
            # send the whole ip packet as data
            # scapy makes this easy with bytes(pkt[IP])
            print(pkt[IP])
            data = bytes(pkt[IP])
            
            sock.sendto(data, (config.ENCRYPTER_HOST, config.ENCRYPTER_PORT))
            logging.info(f"Injected packet {i+1}/{len(packets)}")
            
            # chill for a sec so we dont crash anything
            time.sleep(0.01)
            
    logging.info("Injection complete.")

if __name__ == "__main__":
    run_injector()
