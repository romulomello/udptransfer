import socket
import struct

def main():
    host = 'localhost'
    port = 12345
    server_address = (host, port)

    packet_size = 1024
    window_size = 10

    with open('file.test', 'rb') as file:
        data = file.read()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)

    file_size = len(data)
    client_socket.sendto(struct.pack('!Q', file_size), server_address)

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
            print(f'Sent packet {packet_number}...')

        while True:
            try:
                response, _ = client_socket.recvfrom(4)

                if len(response) == 4:
                    confirmation_number = struct.unpack('!I', response)[0]

                    if confirmation_number == expected_ack:
                        print(f'Packet #{confirmation_number} delivered successfully.')
                        packets_acked += 1
                        expected_ack += 1
                        if expected_ack == last_packet:
                            break
                        packet_number = packets_acked + window_size - 1
                        packet = data[packet_number * packet_size:(packet_number + 1) * packet_size]

                        packet_with_number = struct.pack('!I', packet_number) + packet

                        client_socket.sendto(packet_with_number, server_address)
                        print(f'Sent packet #{packet_number}...')
                    elif confirmation_number < expected_ack:
                        print(f'Duplicate ACK {confirmation_number} received. Ignoring...')
                    else:
                        print(f'Out of order ACK {confirmation_number} received. Resending packets...')
                        break
            except socket.timeout:
                print(f'Packet #{expected_ack} timeout. Resending packets...')
                break

    client_socket.close()

if __name__ == '__main__':
    main()
