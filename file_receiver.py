import socket
import logging
import sys
import os
import config

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/receiver.log", mode='w'),
        logging.StreamHandler()
    ]
)

def receive_file(output_filename):
    # make sure we have somewhere to put the file
    output_dir = "decrypted_output"
    if not os.path.dirname(output_filename):
        # default to decrypted_output if they didn't give a path
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_filename = os.path.join(output_dir, output_filename)
    else:
        # If directory specified, ensure it exists
        dir_name = os.path.dirname(output_filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to 0.0.0.0 to receive from any interface, or use specific config host
    bind_host = "0.0.0.0" 
    bind_port = config.DESTINATION_PORT

    try:
        sock.bind((bind_host, bind_port))
        # Set timeout to 5 seconds to automatically close when transfer finishes
        sock.settimeout(5.0)
        
        logging.info(f"File receiver listening on {bind_host}:{bind_port}")
        logging.info(f"Writing to: {output_filename}")
        
        bytes_received = 0
        
        with open(output_filename, 'wb') as f:
            while True:
                try:
                    data, addr = sock.recvfrom(65535)
                    
                    if not data:
                        break
                    
                    f.write(data)
                    bytes_received += len(data)
                    
                    # Progress update
                    if bytes_received % config.PROGRESS_INTERVAL_BYTES < 65535:
                        logging.info(f"Received {bytes_received} bytes")
                except socket.timeout:
                    logging.info("Timeout reached (no data for 5s). Assuming transfer complete.")
                    break
        
    except KeyboardInterrupt:
        logging.info(f"Transfer interrupted. Received {bytes_received} bytes total")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        sock.close()
        logging.info(f"File saved: {output_filename} ({bytes_received} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Usage: python file_receiver.py <output_filename>")
        sys.exit(1)
    
    output_filename = sys.argv[1]
    receive_file(output_filename)
