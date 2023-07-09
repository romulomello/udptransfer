import socket
import struct
from collections import defaultdict

def main():
    host = 'localhost'
    port = 12345
    server_address = (host, port)

    packet_size = 1024
    window_size = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print('Server waiting for connections...')

    file_size, client_address = server_socket.recvfrom(1024)
    file_size = struct.unpack('!Q', file_size)[0]
    print(f'File size: {file_size} bytes')

    received_packets = defaultdict(bool)
    expected_sequence_number = 0

    cwnd = 1
    ssthresh = float('inf')

    while True:
        packet_with_number, client_address = server_socket.recvfrom(packet_size + 4)
        packet_number = struct.unpack('!I', packet_with_number[:4])[0]
        packet = packet_with_number[4:]

        if len(packet) < packet_size:
            packet = packet[:len(packet)]

        if packet_number >= expected_sequence_number:
            received_packets[packet_number] = packet

            print(f'Received packet {packet_number}...')

            server_socket.sendto(struct.pack('!I', packet_number), client_address)
            print(f'Delivery confirmation for packet {packet_number} sent.')

            if len(received_packets) == file_size // packet_size + 1:
                break

            if packet_number == expected_sequence_number:
                expected_sequence_number += 1

                if expected_sequence_number % window_size == 0 or expected_sequence_number not in received_packets:
                    if cwnd < ssthresh:
                        cwnd *= 2
                    else:
                        cwnd += 1 / cwnd

                    server_socket.sendto(struct.pack('!I', expected_sequence_number) + str(int(cwnd)).encode(),
                                         client_address)

        else:
            server_socket.sendto(struct.pack('!I', expected_sequence_number - 1), client_address)

            for i in range(packet_number, expected_sequence_number):
                if i not in received_packets:
                    server_socket.sendto(struct.pack('!I', i), client_address)

    received_data = b''.join(received_packets[i] for i in range(len(received_packets)))

    with open('received_file.test', 'wb') as file:
        file.write(received_data)

    print('File received and saved.')

    server_socket.close()

if __name__ == '__main__':
    main()
