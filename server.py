import socket
import struct
from collections import defaultdict
import random
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w', format='%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

def main():
    host = 'localhost'
    port = 12345
    server_address = (host, port)

    # Server socket config
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    logger.info('Server waiting for connections...')

    # Receive file size from the client
    file_size, client_address = server_socket.recvfrom(1024)
    file_size = struct.unpack('!Q', file_size)[0]
    logger.info(f'File size: {file_size} bytes')

    # Send packet size to the server
    packet_size = 1024
    server_socket.sendto(struct.pack('!Q', packet_size), client_address)

    # Send window size to the server
    window_size = 10
    server_socket.sendto(struct.pack('!Q', window_size), client_address)

    received_packets = defaultdict(bool) # Track received packets using a dictionary
    expected_sequence_number = 0

    cwnd = 1 # Congestion window size
    ssthresh = float('inf')  # Slow-start threshold
    loss_prob = 0.01 # Probability of random packet loss

    while True:
        # Receive packet with number from the client
        packet_with_number, client_address = server_socket.recvfrom(packet_size + 4)
        packet_number = struct.unpack('!I', packet_with_number[:4])[0]
        packet = packet_with_number[4:]

        # Introduce random packet loss with a probability of loss_prob
        if random.random() < loss_prob:
            logger.info('Random packet loss!')
            ssthresh = cwnd/2
            packet_number += 1

        # If the received packet is smaller than packet_size, trim it
        if len(packet) < packet_size:
            packet = packet[:len(packet)]

        # Check if the received packet's number matches the expected sequence number
        if packet_number == expected_sequence_number:
            # Store the received packet
            received_packets[packet_number] = packet

            logger.info(f'Received packet #{packet_number}...')

            # Send acknowledgment to the client for the received packet
            server_socket.sendto(struct.pack('!I', packet_number), client_address)
            logger.info(f'Delivery confirmation for packet #{packet_number} sent.')

            # Check if all packets have been received
            if len(received_packets) == file_size // packet_size + 1:
                break

            expected_sequence_number += 1

            # Perform congestion control and window management
            if expected_sequence_number % window_size == 0 or expected_sequence_number not in received_packets:
                if cwnd < ssthresh:
                    cwnd *= 2 # Slow-start phase
                else:
                    cwnd += 1 / cwnd # Congestion avoidance phase

        else:
            # Send repeated ACK with the last recognized packet number
            logger.info(f'Unexpected sequence number #{packet_number}. Resending ACK {expected_sequence_number}.')
            server_socket.sendto(struct.pack('!I', expected_sequence_number - 1), client_address)

    # Concatenate the received packets to reconstruct the file
    received_data = b''.join(received_packets[i] for i in range(len(received_packets)))

    # Save the reconstructed file
    with open('received_file.test', 'wb') as file:
        file.write(received_data)

    logger.info('File received and saved.')

    server_socket.close()

if __name__ == '__main__':
    main()
