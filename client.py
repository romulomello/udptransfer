import socket
import struct
import logging

logging.basicConfig(level=logging.INFO, filename='client.log', filemode='w', format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

def main():
    host = 'localhost'
    port = 12345
    server_address = (host, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)

    with open('file.test', 'rb') as file:
        data = file.read()

    file_size = len(data)
    client_socket.sendto(struct.pack('!Q', file_size), server_address)

    packet_size, _ = client_socket.recvfrom(1024)
    packet_size = struct.unpack('!Q', packet_size)[0]
    logger.info(f'Packet size: {packet_size} bytes')

    window_size, _ = client_socket.recvfrom(1024)
    window_size = struct.unpack('!Q', window_size)[0]
    logger.info(f'Window size: {window_size} packets')

    packets_acked = 0
    expected_ack = 0
    last_packet = file_size // packet_size + 1

    while packets_acked < last_packet:
        window_start = packets_acked
        window_end = min(packets_acked + window_size, last_packet)

        for packet_number in range(window_start, window_end):
            packet = data[packet_number * packet_size:(packet_number + 1) * packet_size]

            packet_with_number = struct.pack('!I', packet_number) + packet

            client_socket.sendto(packet_with_number, server_address)
            logger.info(f'Sent packet {packet_number}...')

        while True:
            try:
                response, _ = client_socket.recvfrom(4)

                if len(response) == 4:
                    confirmation_number = struct.unpack('!I', response)[0]

                    if confirmation_number == expected_ack:
                        logger.info(f'Packet #{confirmation_number} delivered successfully.')
                        packets_acked += 1
                        expected_ack += 1
                        if expected_ack == last_packet:
                            break
                        packet_number = packets_acked + window_size - 1
                        packet = data[packet_number * packet_size:(packet_number + 1) * packet_size]

                        packet_with_number = struct.pack('!I', packet_number) + packet

                        client_socket.sendto(packet_with_number, server_address)
                        logger.info(f'Sent packet #{packet_number}...')
                    elif confirmation_number < expected_ack:
                        logger.info(f'Duplicate ACK {confirmation_number} received. Ignoring...')
                    else:
                        logger.info(f'Out of order ACK {confirmation_number} received. Resending packets...')
                        break
            except socket.timeout:
                logger.info(f'Packet #{expected_ack} timeout. Resending packets...')
                break

    client_socket.close()

if __name__ == '__main__':
    main()
