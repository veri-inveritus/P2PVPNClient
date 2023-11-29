use hex::decode;
use std::{collections::HashMap, collections::HashSet, net::SocketAddr, str::FromStr, time::Duration};
use tokio::net::UdpSocket;
use tokio::time;
use dialoguer::{Input, Password};
use wiretun::{DeviceConfig, PeerConfig, Cidr};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Prompt user for private key
    let private_key_hex: String = Password::new()
        .with_prompt("Enter your private key")
        .interact()?;

    // Convert the entered private key to bytes using the hex crate
    let private_key_bytes = hex::decode(&private_key_hex)?;

    // Ensure the byte array has the expected length
    if private_key_bytes.len() != 32 {
        eprintln!("Private key must be 32 bytes long");
        std::process::exit(1);
    }

    // Convert the Vec<u8> to [u8; 32]
    let mut private_key: [u8; 32] = [0; 32];
    private_key.copy_from_slice(&private_key_bytes);

    // Configure WireGuard device
    let port: u16 = Input::<String>::new()
        .with_prompt("Enter the listen port")
        .interact_text()?
        .parse()?;

    let peer_public_key: String = Input::new()
        .with_prompt("Enter the peer's public key")
        .interact_text()?;

    // Convert peer_public_key to [u8; 32]
    let decoded_public_key = match decode(&peer_public_key) {
        Ok(bytes) => {
            let mut key = [0; 32];
            key.copy_from_slice(&bytes);
            key
        }
        Err(e) => {
            eprintln!("Error decoding public key: {}", e);
            std::process::exit(1);
        }
    };

    let peer_endpoint: String = Input::new()
        .with_prompt("Enter the peer's endpoint")
        .interact_text()?;

    let endpoint = peer_endpoint.parse::<SocketAddr>()?;

    // Definition for allowed_ips_set
    let allowed_ips: HashSet<Cidr> = vec!["192.168.0.1/24".parse().unwrap()].into_iter().collect();

    // Convert the set of allowed IPs to a set of Cidr
    let allowed_ips_set: HashSet<Cidr> = allowed_ips
        .into_iter()
        .map(|cidr| Cidr::from_str(&cidr.to_string()).expect("Failed to parse Cidr"))
        .collect();

    let mut peers = HashMap::new();
    peers.insert(
        decoded_public_key,
        PeerConfig {
            public_key: decoded_public_key,
            endpoint: Some(endpoint),
            allowed_ips: allowed_ips_set,
            persistent_keepalive: Some(Duration::from_secs(15)),
            ..Default::default()
        },
    );

    let config = DeviceConfig {
        private_key,
        listen_port: port,
        peers,
        ..Default::default()
    };

    struct Device {
        socket: UdpSocket,
    }

    impl Device {
        async fn send(
            &self,
            peer_public_key: Vec<u8>,
            peer_endpoint: SocketAddr,
            data: &[u8],
        ) -> Result<(), Box<dyn std::error::Error>> {
            self.socket.send_to(data, peer_endpoint).await?;
            Ok(())
        }

        async fn native(interface: &str, config: DeviceConfig) -> Result<Self, Box<dyn std::error::Error>> {
            let socket = UdpSocket::bind("0.0.0.0:0").await?;
            Ok(Device { socket })
        }
    }

    let device = Device::native("wg0", config).await?;
    let data_to_send = b"Hello, Peer!";
    device.send(peer_public_key, endpoint, data_to_send).await?;

    // Keep the program running
    loop {
        time::sleep(Duration::from_secs(1)).await;
    }
}

async fn receive_data(device: Device) -> Result<(), Box<dyn std::error::Error>> {
    let mut buf = vec![0u8; 1024];

    loop {
        match device.socket.recv_from(&mut buf).await {
            Ok((size, peer)) => {
                let received_data = &buf[..size];
                println!("Received data from {}: {:?}", peer, received_data);
            }
            Err(e) => {
                eprintln!("Error receiving data: {:?}", e);
            }
        }
    }
}
