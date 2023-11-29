import subprocess
import time

class WireGuardVPNPeer:
    def __init__(self, private_key, public_key, peer_public_key, peer_endpoint):
        self.private_key = private_key
        self.public_key = public_key
        self.peer_public_key = peer_public_key
        self.peer_endpoint = peer_endpoint

    def generate_private_key(self):
        # Generate a private key using the 'wg genkey' command
        result = subprocess.run(["wg", "genkey"], capture_output=True, text=True)
        if result.returncode == 0:
            private_key = result.stdout.strip()
        else:
            raise Exception(f"Failed to generate private key: {result.stderr}")

    def generate_public_key(self, private_key):
        # Generate a public key using the 'wg pubkey' command
        result = subprocess.run(["wg", "pubkey"], input=private_key, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(f"Failed to generate public key: {result.stderr}")

    def configure_wireguard(self):
        # Configure WireGuard
        subprocess.run(["sudo", "ip", "link", "add", "dev", "wg0", "type", "wireguard"])
        subprocess.run(["sudo", "wg", "set", "wg0", "private-key", self.private_key])
        subprocess.run(["sudo", "ip", "addr", "add", "dev", "wg0", "10.0.0.2/24"])
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", self.peer_public_key, "endpoint", self.peer_endpoint])
        subprocess.run(["sudo", "ip", "link", "set", "up", "dev", "wg0"])
        
        # Add routing to ensure traffic goes through the VPN
        subprocess.run(["sudo", "ip", "route", "add", "10.0.0.0/24", "dev", "wg0"])

    def start_vpn(self):
        # Start the WireGuard VPN
        subprocess.run(["sudo", "wg", "up", "wg0"])

    def stop_vpn(self):
        # Stop the WireGuard VPN
        subprocess.run(["sudo", "wg", "down", "wg0"])
        subprocess.run(["sudo", "ip", "link", "delete", "dev", "wg0"])
        
        # Remove the added route when stopping the VPN
        subprocess.run(["sudo", "ip", "route", "del", "10.0.0.0/24"])

    def transfer_file(self, file_path):
        # Transfer a file using scp
        result = subprocess.run(["scp", file_path, f"{self.peer_endpoint}:/path/on/peer/"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to transfer file: {result.stderr}")
        else:
            print("File transferred successfully.")

if __name__ == "__main__":
    print("WireGuard VPN Setup")

    # Ask the user if they are the client or the host
    user_role = input("Are you the client or the host? (client/host): ").lower()

    if user_role not in ["client", "host"]:
        print("Invalid choice. Exiting.")
        exit()

    # If the user is the host, generate a private key and print the public key
    if user_role == "host":
        host_peer = WireGuardVPNPeer(private_key=None, public_key=None, peer_public_key=None, peer_endpoint=None)

        # Generate a private key and public key
        host_peer.private_key = host_peer.generate_private_key()
        host_peer.public_key = host_peer.generate_public_key(host_peer.private_key)

        print(f"Host Private Key: {host_peer.private_key}")
        print(f"Host Public Key: {host_peer.public_key}")

        # Get user input for the client's public key and endpoint
        client_public_key = input("Enter the client's public key: ")
        client_endpoint = input("Enter the client's endpoint (IP address:port): ")

        # Configure and start the VPN
        host_peer.configure_wireguard()
        host_peer.start_vpn()

        print("Connection established successfully.")

        # Keep the script running to maintain the VPN connection
        while True:
            time.sleep(60)

    # If the user is the client, get the server public key and endpoint
    client_peer = WireGuardVPNPeer(private_key=None, public_key=None, peer_public_key=None, peer_endpoint=None)

    # Generate a private key and public key
    client_peer.private_key = client_peer.generate_private_key()
    client_peer.public_key = client_peer.generate_public_key(client_peer.private_key)

    # Get user input for the server's public key and endpoint
    server_public_key = input("Enter the server's public key: ")
    server_endpoint = input("Enter the server's endpoint (IP address:port): ")

    # Exit if the server public key or endpoint is not provided
    if not server_public_key or not server_endpoint:
        print("Server public key and endpoint are required. Exiting.")
        exit()

    # Configure and start the VPN
    client_peer.peer_public_key = server_public_key
    client_peer.peer_endpoint = server_endpoint

    client_peer.configure_wireguard()
    client_peer.start_vpn()

    print("Connection established successfully.")

    # Keep the script running to maintain the VPN connection
    while True:
        time.sleep(60)
