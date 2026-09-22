# Network-Packet-Sniffer 🕵️‍♂️🐍

> A low-level network packet analyzer built entirely from scratch using Python's built-in `socket` and `struct` libraries. No high-level abstractions like Scapy—just raw bytes, kernel-level sockets, and bitwise operations.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Networking](https://img.shields.io/badge/TCP%2FIP-000000?style=for-the-badge&logo=wireshark&logoColor=white)

## 📌 About The Project

**Network-Packet-Sniffer** intercepts raw network traffic directly from the Network Interface Card (NIC). It binds a raw socket (`AF_PACKET`) to bypass the operating system's network stack, allowing it to capture and decode every single byte that flows through the wire. 

Instead of relying on third-party libraries, this project manually parses the network encapsulation layers (Ethernet -> IP -> TCP/UDP -> Payload) step-by-step, handling Network Byte Order (Big-Endian) conversions and bitwise masking natively.

### ✨ Key Features
- **Zero External Dependencies:** Built entirely with Python's standard library.
- **Deep Packet Inspection:** Extracts MAC addresses, IP addresses, TTL, Ports, Sequence/Acknowledgment numbers, and dynamic header lengths.
- **Bit-Level Masking:** Uses bitwise shifts (`>>`) and logical ANDs (`&`) to extract sub-byte fields like IP Version, IHL, DSCP, and TCP Flags (URG, ACK, PSH, RST, SYN, FIN).
- **Payload Extraction:** Dynamically calculates header sizes to perfectly isolate the Application Layer payload (e.g., HTTP text, TLS encrypted bytes).
- **Terminal UI:** Displays a color-coded, aligned output of captured packets and safely formats raw hex data for readability.

---

## 🚀 How It Works

1. The script creates a raw socket using `socket.AF_PACKET` and `ETH_P_ALL` (to capture all protocols).
2. It receives a raw binary byte array (up to 65,535 bytes) from the network adapter.
3. **Layer 2 (Data Link):** Parses the first 14 bytes to extract the Ethernet Frame (Destination MAC, Source MAC, EtherType).
4. **Layer 3 (Network):** If the EtherType is `0x0800` (IPv4), it parses the IP header to find routing details and the underlying protocol (TCP/UDP).
5. **Layer 4 (Transport):** Parses the TCP or UDP header based on the IP protocol field.
6. **Application Layer:** Calculates total header lengths to slice the remaining bytes, revealing the final payload.

---

## 💻 Installation & Usage

**Note:** Raw sockets require low-level hardware access. This project must be run on a **Linux** environment with **root (sudo)** privileges.

1. Clone the repository:
   ```bash
   git clone https://github.com/furyxGG/Network-Packet-Sniffer.git
   cd Network-Packet-Sniffer
   ```

2. Run the sniffer:
   ```bash
   sudo python3 main.py
   ```

3. Generate some test traffic:
   Open another terminal and use `curl` to send a plain-text HTTP request, or just browse the web to see background TLS/HTTPS traffic.
   ```bash
   curl http://neverssl.com
   ```

---

## 🧠 Architecture & Protocol Parsing

The script strips away headers like a Russian nesting doll using Python's `struct.unpack`. Here are the blueprints used for parsing:

### 1. Ethernet Frame (Layer 2)
The first 14 bytes of every packet. We check the 2-byte EtherType to ensure the encapsulated data is IPv4 (`0x0800`).

![Ethernet Frame](https://www.gatevidyalay.com/wp-content/uploads/2018/10/Ethernet-Frame-Format-IEEE-802.3.png)
*Parsed using struct format: `!6s6sH`*

### 2. IPv4 Header (Layer 3)
Since fields like `Version` (4 bits) and `IHL` (4 bits) share a single byte, the script isolates them using bitwise right shifts (`>> 4`) and masks (`& 0x0F`).

![IPv4 Header](https://media.geeksforgeeks.org/wp-content/uploads/20251001101428862998/don_t_fragment.webp)
*Parsed using struct format: `!BBHHHBBHII`*

### 3. Transport Layer (Layer 4)
#### TCP Header
TCP is highly complex due to its dynamic length and control flags. The script reads a 16-bit block containing the Data Offset, Reserved bits, and Flags, isolating boolean states like SYN and ACK.

![TCP Header](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh5H6oD8rBTqw9zgr76AaPdmOrdMYNciX9D_7XgmtCuf_Vod5DUOvj748&s=10)
*Parsed using struct format: `!HHIIHHHH`*

#### UDP Header
A lightweight protocol with a fixed 8-byte header.

![UDP Header](https://d8wojkg2185gh.cloudfront.net/strapi/UDP_Header_Structure_5fc68ec626.webp)
*Parsed using struct format: `!HHHH`*

---

## 🔬 What I Learned
Building a packet sniffer from scratch is the ultimate way to understand the OSI model. When you rely on high-level tools like Wireshark or Scapy, you miss out on the crucial low-level mechanics: Network Byte Order (Big-Endian vs. Little-Endian), casting raw electric signals into 8-bit or 16-bit integers, and extracting boolean flags using bitwise operations. It connects abstract networking concepts directly to C-style memory management and hardware architecture.