# main config file

# pick your mode here
# LOCAL = testing on one machine
# LAN = two different computers
MODE = 'LOCAL' 

# lan settings (only matters if MODE is LAN)
# put the real ips here
LAN_SENDER_IP   = "192.168.1.10"  # device A
LAN_RECEIVER_IP = "192.168.1.20"  # device B

# auto setup stuff (dont touch this part)
if MODE == 'LOCAL':
    ENCRYPTER_HOST = "127.0.0.100" 
    DECRYPTER_HOST = "127.0.0.200"
    DESTINATION_HOST = "127.0.0.1"
else:
    ENCRYPTER_HOST = LAN_SENDER_IP
    DECRYPTER_HOST = LAN_RECEIVER_IP
    DESTINATION_HOST = LAN_RECEIVER_IP

ENCRYPTER_PORT = 9999
DECRYPTER_PORT = 9999
DESTINATION_PORT = 12345

# Encryption Configuration
AES_KEY = b'thisisasecretkey' # Must be 16, 24, or 32 bytes
#by default set to 16 bytes for AES-128

# File Transfer Configuration
CHUNK_SIZE = 8192#set to 8kb safe spot on udp
PROGRESS_INTERVAL_BYTES = 10 * 1024 * 1024 # 10 MB #just tells how often terminal says "sent 1"
SOCKET_BUFFER_SIZE = 16 * 1024 * 1024 # 16 MB buffer to prevent packet loss
