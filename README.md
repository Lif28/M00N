# M00N - WiFi Penetration Testing Tool

<div align="center">
  <br>
  <img width="1120" height="1120" alt="logo" src="https://github.com/user-attachments/assets/b81e91a4-6f18-4298-9445-af7399598dff" />
  <br>
</div>

M00N is a Swiss Army knife for WiFi penetration testing specifically designed for Raspberry Pi with compatible network interfaces. It provides an intuitive user interface for various WiFi security techniques.

## LEGAL WARNING AND DISCLAIMER

WARNING: This tool is developed exclusively for:
- Authorized security testing on owned networks
- Educational and research purposes
- Ethical penetration testing with explicit permission

USING THIS SOFTWARE ON NETWORKS WITHOUT AUTHORIZATION IS ILLEGAL AND PUNISHABLE BY LAW. The developers assume no responsibility for misuse of this tool.

## MAIN FEATURES

### Sniffing & Capture
- 4-Way Handshake Capture - Capture WPA/WPA2 handshake with automatic deauth
- AP Scan - WiFi network scanning with connected station detection
- Raw Sniff - Raw packet sniffing on specific networks

### Attacks
- Deauth Attack - Targeted deauthentication attacks:
  - Single Target (specific device)
  - Entire Network (entire network)
  - Both 5GHz-2.4GHz (multi-band attacks)
- Beacon Flood - Beacon flooding with different modes:
  - Common-networks (common SSIDs)
  - Personal-networks (customized SSIDs)
  - Random (random SSIDs)

### Integrated Tools
- Aircrack-ng Suite (airodump-ng, aireplay-ng, airmon-ng)
- MDK4 for advanced attacks
- Graphical interface optimized for 128x128 LCD display
- Network interface management with multi-country support

## HARDWARE REQUIREMENTS

### Main Device
- Raspberry Pi (Tested on Pi Zero WH, compatible with all models)
- Operating System: DietPi (recommended)
- Display: 1.44" LCD 128x128 pixels (integrated)

### Network Interface
- Compatible WiFi adapter with Monitor Mode and Packet Injection support
- Tested with: Alfa AWUS036AC (rtl8812au chipset)
- Requirements: Interface supporting monitor mode and packet injection

## COMPLETE INSTALLATION

### 1.0 Installing dietpi
Download DietPi
Download balenaEtcher
Flash Dietpi on your SD card
Start your Raspberrypi and configure the OS connecting the raspberry pi to your wifi and enabling ssh for convenience --> https://dietpi.com/docs/install/

### 1.1 Basic System Preparation
```
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git build-essential linux-headers-$(uname -r) -y
```
### ENABLE SPI INTERFACE ON DIETPI

### METHOD VIA DIETPI-CONFIG

- Open dietpi-config tool: ```dietpi-config```
- Navigate to: ```Advanced Options``` then press Enter
- Select SPI: ```SPI state```
- Enable SPI: ```Select Enable``` then Press Enter (dietpi might enable it automaticaly)
- Exit and reboot: Exit dietpi-config, the system will automatically reboot.

### 2. WiFi Interface Driver Installation (rtl8812au)
```
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
sudo make
sudo make install
sudo modprobe 88XXau
sudo dkms status
```

### 3. Penetration Testing Tools Installation
```
sudo apt install aircrack-ng -y
sudo apt install mdk4 -y
sudo apt install nmap wireless-tools net-tools -y
```

### 4. Python Dependencies Installation
```
sudo apt install python3-RPi.GPIO python3-pillow python3-psutil python3-spidev python3-numpy
```

### 5. M00N Project Setup
```
git clone https://github.com/Lif28/M00N.git
cd M00N
sudo mkdir -p /root/M00N/Logs /root/M00N/WpaHandshakes /root/M00N/AP_Scan /root/M00N/RawSniff
```

### 6. Interface Configuration
Edit Settings/settings.json:
```
{
    "interface": "wlan1",
    "country": "EU"
}
```
Supported interfaces:
- EU: Europe (channels 1-13 + 5GHz)
- US: United States (channels 1-11 + 5GHz)
- JP: Japan (channels 1-14 + 5GHz)
- CN: China (channels 1-13 + 5GHz)

## DETAILED USAGE

### Create the service file:
```
sudo nano /etc/systemd/system/moon.service
```

### Add this content:
```
[Unit]
Description=M00N Boot Executer
After=network.target

[Service]
ExecStart=/usr/bin/python /root/M00N/main.py
WorkingDirectory=/root/M00N/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

### Check status:
```
sudo systemctl enable moon.service
sudo systemctl start moon.service
sudo systemctl status moon.service
```

### Navigation Controls
- KEY_UP: Navigate up in menu
- KEY_DOWN: Navigate down in menu
- KEY_PRESS: Select option/Confirm
- KEY2: Secondary actions (details, stop scanning)
- KEY3: Back/Exit

### Specific Functionality Guides

#### 4-Way Handshake Capture
1. Main menu → Wifi → Sniffers → 4-way handshake
2. Select target network from list
3. Press KEY2 to see network details
4. Press KEY_PRESS to start capture
5. Choose deauth method:
   - aireplay-ng - Traditional deauthentication
   - mdk4 - Advanced deauthentication
6. Wait for handshake capture (timeout: 10 minutes)

#### Advanced AP Scanning
1. Wifi → Sniffers → AP scan → Default
2. Automatic scanning of available networks
3. Select network
4. Press KEY2 to see station list
5. Press KEY_PRESS on "Save" to export results

#### Raw Packet Sniffing
1. Wifi → Sniffers → Raw Sniff
2. Select target network
3. Raw packet sniffing on specified network
4. Files saved in /root/M00N/RawSniff/

#### Deauth Attacks
1. Wifi → Attacks → Deauth
2. Select target network
3. Choose attack mode:
   - Single Target: Deauth specific device
     - Scan connected stations
     - Select MAC target
   - Entire Network: Deauth entire network
   - Both 5ghz-4ghz: Multi-band attack
4. Use KEY3 to stop attack

#### Beacon Flood Attack
1. Wifi → Attacks → Beacon Flood
2. Select beacon type:
   - Common-networks: Common SSIDs (Facebook, Starbucks, etc.)
   - Personal-networks: Customized SSIDs
   - Random: Randomly generated SSIDs
3. Attack started automatically
4. KEY3 to stop

### Settings and Configuration

#### Interface Management
1. Main menu → Settings → Interface
2. List of available interfaces:
   - Select: Change primary interface
   - Restart: Restart interface

#### System Configuration
- Interface: WiFi interface selection
- SSH: Enable/Disable SSH access
- System: System options

## TROUBLESHOOTING

### Interface Not Detected
```
sudo iwconfig
sudo systemctl restart networking
sudo modprobe -r 88XXau && sudo modprobe 88XXau
```

### Monitor Mode Problems
```
sudo airmon-ng check kill
sudo airmon-ng start wlan1
sudo iwconfig
```

### Display Not Working
```
sudo i2cdetect -y 1
sudo systemctl restart display-manager
```

## FILE AND DIRECTORY STRUCTURE

M00N/
├── main.py                    # Main application
├── Libs/
│   ├── mojstd.py             # UI system, display, input
│   ├── netstd.py             # Networking functions and attacks
│   └── APScanner.py          # Advanced WiFi network scanner
├── Settings/
│   └── settings.json         # Global configuration
├── Images/                   # Graphic resources (logo, icons)
├── Logs/                     # Operation log files
│   ├── airodump.txt          # Airodump-ng logs
│   ├── aireplay.txt          # Aireplay-ng logs
│   └── mdk4.txt              # MDK4 logs
├── WpaHandshakes/            # Captured WPA handshakes
├── AP_Scan/                  # AP scan results
├── Beacons/                  # Beacon flood configuration files
├── pcap/                     # Packet capture (evil twin)
└── RawSniff/                 # Raw packet sniffing

## CONTRIBUTIONS AND SUPPORT

### Bug Reporting
1. Verify problem reproducibility
2. Provide detailed logs from /root/M00N/Logs/
3. Include configuration from Settings/settings.json

### Development Roadmap
- Additional interface support
- Performance optimizations
- New attack techniques
- Expanded documentation

### Support Channels
- Official documentation
- GitHub repository issues
- Dedicated community

---
Version: M00N v1.0
Platform: Raspberry Pi + DietPi
Status: Stable
Last Update: 2025

M00N - Illuminating WiFi network security
