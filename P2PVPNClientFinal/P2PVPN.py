import subprocess
import time

class WireGuardVPNClient:
    def __init__(self, private_key, server_public_key, server_endpoint):
        self.private_key = private_key
        self.server_public_key = server_public_key
        self.server_endpoint = server_endpoint
        
    def generate_private_key(self):
        # Generate a private key using the 'wg genkey' command
        result = subprocess.run(["wg", "genkey"], capture_output=True, text=True)
        if result.returncode == 0:
            private_key = result.stdout.strip()
            # Write the private key to a file
            with open("private_key.txt", "w") as file:
                file.write(private_key)
            return private_key
        else:
            raise Exception(f"Failed to generate private key: {result.stderr}")
        
    def generate_public_key(self, private_key):
        # Generate a public key using the 'wg pubkey' command
        result = subprocess.run(["wg", "pubkey"], input=private_key, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
            # Write the Public key to a file
            with open("public_key.txt", "w") as file:
                file.write(public_key)
        else:
            raise Exception(f"Failed to generate public key: {result.stderr}")

    def configure_wireguard(self):
        # Configure WireGuard
        subprocess.run(["sudo", "ip", "link", "add", "dev", "wg0", "type", "wireguard"])
        subprocess.run(["sudo", "wg", "set", "wg0", "private-key", self.private_key])
        subprocess.run(["sudo", "ip", "addr", "add", "dev", "wg0", "10.0.0.2/24"])
        subprocess.run(["sudo", "wg", "set", "wg0", "peer", self.server_public_key, "endpoint", self.server_endpoint])
        subprocess.run(["sudo", "ip", "link", "set", "up", "dev", "wg0"])

    def start_vpn(self):
        # Start the WireGuard VPN
        subprocess.run(["sudo", "wg", "up", "wg0"])

    def stop_vpn(self):
        # Stop the WireGuard VPN
        subprocess.run(["sudo", "wg", "down", "wg0"])
        subprocess.run(["sudo", "ip", "link", "delete", "dev", "wg0"])
        
    def transfer_file(self, file_path):
        # Transfer a file using scp
        result = subprocess.run(["scp", file_path, f"{self.server_endpoint}:/path/on/server/"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to transfer file: {result.stderr}")
        else:
            print("File transferred successfully.")

if __name__ == "__main__":
    print("The Private key has been generated and is stored in the file: private_key.txt")
    
    # Get the server public key from the user
    server_public_key = input("Enter the server public key: ")
    
    # Exit if the server public key is not provided
    if not server_public_key:
        print("Server public key is required. Exiting.")
        exit()
        
    # Get the server endpoint from the user 
    server_endpoint = input("Enter the server endpoint (IP address:port): ")
    
    # Exit if the server endpoint is not provided
    if not server_endpoint:
        print("Server endpoint is required. Exiting.")
        exit()
        
    # Get user input for the file path to transfer 
    file_path = input("Enter the file path to transfer: ")

    # Exit if the file path is not provided
    if not file_path:
        print("File path is required. Exiting.")
        exit()
    
    vpn_client = WireGuardVPNClient(private_key=None, server_public_key=server_public_key, server_endpoint=server_endpoint)

    try:
        # Generate a private key
        vpn_client.private_key = vpn_client.generate_private_key()

        # Configure and start the VPN
        vpn_client.configure_wireguard()
        vpn_client.start_vpn()
        
        print("Connection established successfully.")

        # Keep the script running to maintain the VPN connection
        while True:
            time.sleep(60)
            
    except Exception as e:
        print(f"Error: {e}")
        # Stop the VPN on error
        vpn_client.stop_vpn()
        print("VPN Stopped.")

    except KeyboardInterrupt:
        # Stop the VPN on keyboard interrupt
        vpn_client.stop_vpn()
        print("VPN Stopped.")
