P2PVPNClient

Created under the Apache 2.0 Open Source License

## WireGuard VPN Setup Documentation

This documentation provides information on the dependencies required to run the WireGuard VPN setup code and instructions on how to execute the code successfully.

### Dependencies:

The WireGuard VPN setup code relies on the following dependencies:

1. **WireGuard Tools:**
   - Ensure that the WireGuard tools (`wg`, `wg-quick`) are installed on your system. These tools are used for key generation, VPN configuration, and management.
   - Installation methods vary based on the operating system:
     - For Debian/Ubuntu: `sudo apt-get install wireguard-tools`
     - For Red Hat/Fedora: `sudo dnf install wireguard-tools`
     - For macOS: `brew install wireguard-tools`
     - For Windows: Download the installer from the [official WireGuard website](https://www.wireguard.com/install/).

2. **SSH and SCP:**
   - The code uses the `scp` command for secure file transfer over SSH. Ensure that your system has SSH and SCP installed.

3. **Python Environment:**
   - The code is written in Python. Ensure you have Python installed on your system. The code is compatible with Python 3.

### Running the Code:

Follow these steps to run the WireGuard VPN setup code:

1. **Clone the Repository:**
   - Clone or download the repository containing the WireGuard VPN setup code from the source.

2. **Navigate to the Directory:**
   - Open a terminal and navigate to the directory where the code is located.

3. **Install Python Dependencies:**
   - The code does not have external Python dependencies. The standard Python library is sufficient.

4. **Run the Code:**
   - Execute the code by running the following command in the terminal:
     ```bash
     python wireguard_vpn_setup.py
     ```
     - The script will prompt you to specify whether you are the client or the host.
     - Follow the on-screen instructions to provide the necessary input, including public keys and endpoints.

5. **File Transfer:**
   - If you choose to transfer a file, the script will prompt you for the file path.
   - Enter the path of the file you want to transfer, and the script will securely transfer the file over the established VPN connection.

6. **Maintaining the VPN Connection:**
   - The script will keep running in a loop to maintain the VPN connection.
   - To stop the VPN, you can interrupt the script using a keyboard interrupt (`Ctrl + C`). The script will then gracefully stop the VPN and exit.

### Conclusion:

The provided WireGuard VPN setup code simplifies the process of establishing a secure VPN connection between two peers. By following the instructions in this documentation, users can quickly configure the VPN and transfer files securely. Ensure that the necessary dependencies are installed on your system before running the code.