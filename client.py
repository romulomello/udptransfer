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

    packets_sent = 0
    packets_acked = 0

    while packets_acked < file_size // packet_size + 1:
        window_start = packets_sent
        window_end = min(packets_sent + window_size, file_size // packet_size + 1)

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

                    if confirmation_number >= packets_acked and confirmation_number == window_end - 1:
                        print(f'Packets {window_start} to {confirmation_number} delivered successfully.')
                        packets_acked = confirmation_number + 1
                        break
            except socket.timeout:
                client_socket.sendto(packet_with_number, server_address)

        packets_sent += window_size

    client_socket.close()

if __name__ == '__main__':
    main()
