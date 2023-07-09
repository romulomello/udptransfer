import socket
import struct

def main():
    host = 'localhost'
    port = 12345
    server_address = (host, port)

    packet_size = 1024

    with open('file.test', 'rb') as file:
        data = file.read()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    file_size = len(data)
    client_socket.sendto(struct.pack('!Q', file_size), server_address)

    for packet_number in range(0, file_size, packet_size):
        packet = data[packet_number:packet_number+packet_size]

        packet_with_number = struct.pack('!I', packet_number // packet_size) + packet

        client_socket.sendto(packet_with_number, server_address)

        while True:
            try:
                response, _ = client_socket.recvfrom(4)

                if len(response) == 4:
                    confirmation_number = struct.unpack('!I', response)[0]

                    if confirmation_number == packet_number // packet_size:
                        print(f'Packet {packet_number // packet_size} delivered successfully.')
                        break
            except socket.timeout:
                client_socket.sendto(packet_with_number, server_address)

    client_socket.close()

if __name__ == '__main__':
    main()
