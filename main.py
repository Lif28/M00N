import RPi.GPIO as GPIO
import time
import subprocess
import json
import re
from Libs.APScanner import *
from Libs.mojstd import *
from Libs.netstd import *

version = "M00N v1.0"
Handshake_capture = 1
INTERFACE = json.load(open("/root/M00N/Settings/settings.json", "r"))["interface"]
selected_index = 0

# Menus
MENUS = {
    'main': ["Wifi", "Bluetooth", "Settings", "Reboot", "Shutdown"],
    'wifi': ["Sniffers", "Attacks", "Connect"],
    'sniffers': ["4-way handshake", "AP scan", "Raw Sniff"],
    'apscan': ["Default"],
    'attacks': ["Deauth", "Beacon Flood"],
    'beacon_flood': ["Common-networks", "Personal-networks", "Random"],
    'deauth_methods': ["Single Target", "Entire Network", "Both 5ghz-4ghz"],
    'settings': ["Interface"],
    'ssh': ["Enable", "Disable"],
    'interface': ["Restart", "Select"]
}

def nav(menu_options, selected_index):
    if GPIO.input(KEY_UP_PIN) == 0:
        time.sleep(0.1)
        selected_index = (selected_index - 1) % len(menu_options)
    elif GPIO.input(KEY_DOWN_PIN) == 0:
        selected_index = (selected_index + 1) % len(menu_options)
        time.sleep(0.1)
    return selected_index

# MAX visible len messages = 18 letters

def draw_menu(menu, selected_index=0, color=(100, 40, 237), offset=20):
    # Clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    draw.text((5, 0), version, font=font, fill=(255, 0, 0))
    draw.rectangle((0, 12, width, 14), outline=0, fill=(2, 92, 72)) # Bottom bar

    # Importat
    max_visible_options = 6

    # Offset
    scroll_offset = max(0, min(selected_index - max_visible_options + 1, len(menu) - max_visible_options))

    # Important
    visible_options = menu[scroll_offset:scroll_offset + max_visible_options]

    # Draw Option
    menu_offset = 16  # Offset
    for i, option in enumerate(visible_options):
        y = (i * 20) + menu_offset  # Space

        # Highlight
        if scroll_offset + i == selected_index:
            text_size = draw.textbbox((0, 0), option, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]
            draw.rectangle((0, y, width, y + text_height+5), fill=color) # Highlight
            draw.text((1, y), option, font=font, fill=(0, 0, 0))  # Black text
        else:
            draw.text((1, y), option, font=font, fill=(255,255,255))# White text

    # Display the updated image
    disp.LCD_ShowImage(image, 0, 0)

def wifi_det(data, selected_ssid):
    for dict in data:
        if dict['Ssid'] == selected_ssid:
            return {
                "Bssid": dict['Bssid'],
                "Ssid": dict['Ssid'],
                "Chan": dict['Chan'],
                "Signal": dict['Signal'],
                "Security": dict['Security']
            }
        
def station_scan(TEMP_MENU, bssid, chan, Obj, airo=0):
    
    elements = []
    macs_ = set()
    # Gets only the 2 mac --> STATION
    ui_print("Checking interface", "unset")
    if Obj.interface_select() == -1: ui_print(ui_print("""[ERR] Interface\n not Found. Try to\n reboot M00N if the\n problem persist."""))
    else:
        Obj.interface_start()
        ui_print(f"{INTERFACE} ready!", color=(0,255,142))
        ui_print("Press KEY_2 to\nstop scanning...", "unset")
        process = Obj.start_airodump1(bssid, chan)

        
        for line in process:
            # find all macs in the line
            if airo == 0:
                macs = re.findall(r'[0-9A-Fa-f:]{17}', line)
                # The second macs is the STATION one
                if len(macs) > 1:
                    for station in macs[1:]:
                        if station not in TEMP_MENU:
                            TEMP_MENU.append(station)
            else:
                macs = re.findall(r'[0-9A-Fa-f:]{17}', line)
                macs_.update(macs[1:])
                if line.strip():
                    # lines --> AP: BSSID + PWR + Beacons + Data
                    ap_match = re.search(r'([0-9A-Fa-f:]{17})\s+(-?\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
                    
                    if ap_match:
                        elements.clear()
                        elements.extend([
                                    f'Beacons: {ap_match.group(4)}',
                                    f'Data: {ap_match.group(5)} packets', 
                                    f'Data/s: {ap_match.group(6)}',
                                    f'RXQ: {ap_match.group(3)}%',
                                    '---'
                                ])
        TEMP_MENU.extend(elements)
        del elements
        if airo == 0: 
            Obj.interface_stop()
            return TEMP_MENU
        else:
            Obj.interface_stop()
            return list(macs_)

# Main Functions

def load_wifi_data():
    # Load WiFi networks data from JSON file with error handling
    try:
        with open("wifiinfo.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        ui_print("[ERR] wifiinfo.json\nnot found", 2, (255, 0, 0))
        return []
    except:
        ui_print("[ERR] Invalid JSON\nfile", 2, (255, 0, 0))
        return []

def create_wifi_menu(data):
    # Create menu items from WiFi data with index
    return [f"{item['Ssid']} [{idx}]" for idx, item in enumerate(data)]

def get_wifi_details_from_menu_item(menu_item, data):
    # Extract WiFi details from selected menu item
    try:
        idx = int(menu_item.split("[")[-1].strip("]"))
        return data[idx]
    except:
        ui_print("[ERR] Invalid\nselection", 2, (255, 0, 0))
        return None

def create_wifi_details_menu(wifi_details):
    # Create standardized WiFi details menu
    return [
        'Ssid:', wifi_details["Ssid"],
        'Bssid:', wifi_details["Bssid"],
        f'Channel: {wifi_details["Chan"]}',
        f'Signal: {wifi_details["Signal"]}',
        f'Security: {wifi_details["Security"]}'
    ]

def wait_for_key_release(pin, timeout=0.2):
    # Wait for key to be released with timeout
    start = time.time()
    while GPIO.input(pin) == 0 and (time.time() - start) < timeout:
        time.sleep(0.01)

def display_wifi_details(wifi_details):
    # Display WiFi details in a sub-menu
    details_menu = create_wifi_details_menu(wifi_details)
    inner_index = 0
    
    while GPIO.input(KEY3_PIN) != 0:
        inner_index = nav(details_menu, inner_index)
        draw_menu(details_menu, inner_index)
        time.sleep(0.05)  # Prevent excessive CPU usage
    
    wait_for_key_release(KEY3_PIN)

def start_interface_safe(Obj):
    """
    Start interface with proper error handling
    Returns: True if success, False if failed
    """

    ui_print("Checking interface...", "unset")
    if Obj.interface_select() == -1:
        ui_print("""[ERR] Interface\nnot Found. Try to\nreboot M00N if the\nproblem persist.""", 3)
        return False
    
    if Obj.interface_start() == 1:
        ui_print("[ERR] Interface\nstart failed", 3)
        return False
    
    ui_print(f"{INTERFACE} ready!", color=(0, 255, 142))
    return True

# ==========================================
#               4 WAY HANDSHAKE             
# ==========================================

def handle_4way_handshake(Obj):
    """
    Handle 4-way handshake capture - REFACTORED
    - Removed code duplication
    - Better error handling
    - Cleaner flow
    """
    time.sleep(0.2)
    ui_print("Loading...", "unset")
    wifi_info().main()

    # Load WiFi data --> wifi_details dictionary
    data = load_wifi_data()
    if not data:
        return
    
    # Create menu
    wifi_menu = create_wifi_menu(data)
    selected_index = 0
    
    # Main navigation loop
    while GPIO.input(KEY_PRESS_PIN) != 0:
        selected_index = nav(wifi_menu, selected_index)
        draw_menu(wifi_menu, selected_index)
        
        # Exit on KEY3
        if GPIO.input(KEY3_PIN) == 0:
            wait_for_key_release(KEY3_PIN)
            return
        
        # Show details on KEY2
        if GPIO.input(KEY2_PIN) == 0:
            wait_for_key_release(KEY2_PIN)
            wifi_details = get_wifi_details_from_menu_item(wifi_menu[selected_index], data)
            if wifi_details:
                display_wifi_details(wifi_details)
        
        time.sleep(0.05)
    
    # Key press detected - start handshake capture
    wait_for_key_release(KEY_PRESS_PIN)
    wifi_details = get_wifi_details_from_menu_item(wifi_menu[selected_index], data)
    if not wifi_details:
        return
    
    # Select deauth method
    deauth_methods = ["aireplay-ng", "mdk4"]
    selected_index = 0
    
    while True:
        selected_index = nav(deauth_methods, selected_index)
        draw_menu(deauth_methods, selected_index)
        
        if GPIO.input(KEY3_PIN) == 0:
            wait_for_key_release(KEY3_PIN)
            return
        
        if GPIO.input(KEY_PRESS_PIN) == 0:
            wait_for_key_release(KEY_PRESS_PIN)
            deauth_choice = deauth_methods[selected_index]
            
            # Start interface with error handling
            if not start_interface_safe(Obj):
                return
            
            ui_print("Loading...", "unset")
            
            # Check for  exit
            if GPIO.input(KEY3_PIN) == 0:
                Obj.interface_stop()
                return
            
            # Start handshake capture
            result = Obj.handshake_capture(
                wifi_details["Chan"],
                wifi_details["Ssid"],
                wifi_details["Bssid"],
                deauth_choice
            )
            
            # stops interface after operation
            Obj.interface_stop()
            
            # Handle result
            time.sleep(0.5)
            if result == 2:
                ui_print("[ERR] Timeout", 5)
            
            return

# ==================================
#               AP SCAN             
# ==================================

def handle_ap_scan(Obj):
    """
    Handle AP scanning - REFACTORED
    - Cleaner structure
    - Better station handling
    - Improved save functionality
    """
    time.sleep(0.2)
    selected_index = 0
    
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(MENUS['apscan'], selected_index)
        draw_menu(MENUS['apscan'], selected_index)
        
        if GPIO.input(KEY_PRESS_PIN) == 0:
            wait_for_key_release(KEY_PRESS_PIN)
            selected_option = MENUS['apscan'][selected_index]
            
            if selected_option == "Default":
                _handle_default_ap_scan(Obj)
            
        time.sleep(0.05)


def _handle_default_ap_scan(Obj):
    """Handle default AP scan mode - INTERNAL FUNCTION"""
    ui_print("Scanning APs...", "unset")
    subprocess.run(f"sudo iwconfig {INTERFACE} mode managed", shell=True)
    time.sleep(2)
    Obj.interface_stop()
    wifi_info().main()
    
    # Load scan results
    data = load_wifi_data()
    if not data:
        return
    
    # Create and display AP menu
    ap_menu = create_wifi_menu(data)
    selected_index = 0
    
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(ap_menu, selected_index)
        draw_menu(ap_menu, selected_index)
        
        if GPIO.input(KEY_PRESS_PIN) == 0:
            wait_for_key_release(KEY_PRESS_PIN)
            wifi_details = get_wifi_details_from_menu_item(ap_menu[selected_index], data)
            
            if wifi_details:
                _display_ap_with_stations(wifi_details, Obj)
        
        time.sleep(0.05)

def _display_station_list(stations):
    """Display detected stations - INTERNAL FUNCTION"""
    inner_index = 0
    while GPIO.input(KEY3_PIN) != 0:
        inner_index = nav(stations, inner_index)
        draw_menu(stations, inner_index)
        time.sleep(0.05)
    wait_for_key_release(KEY3_PIN)


def _save_ap_results(wifi_details, stations):
    """Save AP scan results to file - INTERNAL FUNCTION"""
    try:
        # Create directory if not exists
        subprocess.run("mkdir -p /root/M00N/AP_Scan", shell=True)
        
        filename = f'/root/M00N/AP_Scan/{wifi_details["Ssid"]}.txt'
        with open(filename, "w") as f:
            f.write(f"SSID: {wifi_details['Ssid']}\n")
            f.write(f"BSSID: {wifi_details['Bssid']}\n")
            f.write(f"Channel: {wifi_details['Chan']}\n")
            f.write(f"Signal: {wifi_details['Signal']}\n")
            f.write(f"Security: {wifi_details['Security']}\n")
            f.write(f"\nStations ({len(stations)}):\n")
            for station in stations:
                f.write(f"  {station}\n")
        
        ui_print("File saved.", 2, (0, 255, 142))
    except:
        ui_print("[ERR] Save failed", 2, (255, 0, 0))

def _display_ap_with_stations(wifi_details, Obj):
    """Display AP details with station scanning - INTERNAL FUNCTION"""
    # Base menu with AP details
    details_menu = create_wifi_details_menu(wifi_details)
    
    # Scan for stations (in background, non-blocking)
    stations = station_scan(
        details_menu,  # Appends to existing menu
        wifi_details["Bssid"],
        wifi_details["Chan"],
        Obj=Obj,
        airo=1
    )
    
    # Add save option
    details_menu.append('Save')
    selected_index = 0
    
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(details_menu, selected_index)
        draw_menu(details_menu, selected_index)
        
        # Save on PRESS
        if GPIO.input(KEY_PRESS_PIN) == 0 and details_menu[selected_index] == "Save":
            wait_for_key_release(KEY_PRESS_PIN)
            _save_ap_results(wifi_details, stations)
            break
        
        # View stations on KEY2
        elif GPIO.input(KEY2_PIN) == 0:
            wait_for_key_release(KEY2_PIN)
            if not stations:
                ui_print("No station found!", color=(255, 0, 0))
            else:
                _display_station_list(stations)
        
        time.sleep(0.05)

# =====================================
#               RAW SNIFF                
# =====================================

def handle_raw_sniff(Obj):
    time.sleep(0.2)
    ui_print("Loading...", "unset")

    wifi_info().main()

    # Load WiFi data --> wifi_details dictionary
    data = load_wifi_data()
    if not data:
        return
    
    raw_sniff_menu = create_wifi_menu(data)
    selected_index = 0
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(raw_sniff_menu, selected_index)
        draw_menu(raw_sniff_menu, selected_index)

        if GPIO.input(KEY_PRESS_PIN) == 0:
            # Key press detected - start raw sniff
            wait_for_key_release(KEY_PRESS_PIN)
            wifi_details = get_wifi_details_from_menu_item(raw_sniff_menu[selected_index], data)
            if not wifi_details:
                return

            # Start interface with error handling
            if not start_interface_safe(Obj):
                return
            
            ui_print("Loading...", "unset")

            Obj.raw_sniff(
                wifi_details["Ssid"], 
                wifi_details["Bssid"], 
                wifi_details["Chan"]
            ) 
            
            time.sleep(0.1)

            Obj.interface_stop()
        
        if GPIO.input(KEY2_PIN) == 0:
            wait_for_key_release(KEY2_PIN)
            wifi_details = get_wifi_details_from_menu_item(raw_sniff_menu[selected_index], data)
            if wifi_details:
                display_wifi_details(wifi_details)

            time.sleep(0.05)
    time.sleep(0.1)

# =====================================
#               DEAUTH                
# =====================================

def handle_deauth(Obj):
    """
    Handle deauth attacks - REFACTORED
    - Single Target: Deauth specific client
    - Entire Network: Deauth all clients on AP
    """
    time.sleep(0.2)
    ui_print("Loading...", "unset")
    wifi_info().main()
    
    # Load WiFi data
    data = load_wifi_data()
    if not data:
        return
    
    # Create menu
    deauth_menu = create_wifi_menu(data)
    selected_index = 0
    
    # Main navigation loop
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(deauth_menu, selected_index)
        draw_menu(deauth_menu, selected_index)
        
        # Show details on KEY2
        if GPIO.input(KEY2_PIN) == 0:
            wait_for_key_release(KEY2_PIN)
            wifi_details = get_wifi_details_from_menu_item(deauth_menu[selected_index], data)
            if wifi_details:
                display_wifi_details(wifi_details)
        
        # Select network on KEY_PRESS
        elif GPIO.input(KEY_PRESS_PIN) == 0:
            wait_for_key_release(KEY_PRESS_PIN)
            wifi_details = get_wifi_details_from_menu_item(deauth_menu[selected_index], data)
            if not wifi_details:
                continue
            
            # Select deauth method (Single Target or Entire Network)
            method_index = 0
            while GPIO.input(KEY3_PIN) != 0:
                method_index = nav(MENUS['deauth_methods'], method_index)
                draw_menu(MENUS['deauth_methods'], method_index)
                
                if GPIO.input(KEY_PRESS_PIN) == 0:
                    wait_for_key_release(KEY_PRESS_PIN)
                    selected_method = MENUS['deauth_methods'][method_index]
                    
                    ui_print("Loading...", "unset")
                    
                    # SINGLE TARGET - Select specific client
                    if selected_method == "Single Target":
                        # Scan for stations
                        stations = []
                        station_scan(stations, wifi_details['Bssid'], wifi_details['Chan'], Obj=Obj)
                        
                        if not stations:
                            ui_print("No station found!", 2, color=(255, 0, 0))
                            Obj.interface_stop()
                            break
                        
                        # Start interface
                        if not start_interface_safe(Obj):
                            return
                        
                        # Display stations menu
                        station_index = 0
                        while GPIO.input(KEY3_PIN) != 0:
                            station_index = nav(stations, station_index)
                            draw_menu(stations, station_index)
                            
                            if GPIO.input(KEY_PRESS_PIN) == 0:
                                wait_for_key_release(KEY_PRESS_PIN)
                                selected_station = stations[station_index]
                                ui_print(f"Deauthing\n{selected_station}\non {wifi_details['Ssid']}", "unset")
                                
                                # Start deauth attack
                                Obj.deauth(wifi_details["Bssid"], wifi_details["Chan"], selected_station)
                                Obj.cleanup_process()
                                break
                        
                        Obj.interface_stop()
                        time.sleep(0.1)
                    
                    # ENTIRE NETWORK - Deauth all clients
                    elif selected_method == "Entire Network":
                        # Start interface
                        if not start_interface_safe(Obj):
                            return
                        ui_print(f"Deauthing\nEntire Network\non {wifi_details['Ssid']}", "unset")
                        Obj.start_mdk4_deauth(wifi_details["Bssid"], wifi_details["Chan"])
                        
                        # Wait for KEY3 to stop
                        while GPIO.input(KEY3_PIN) != 0:
                            time.sleep(0.15)
                        
                        Obj.cleanup_process()
                        Obj.interface_stop()
                        return
                    
                    else:
                        selected_ssid = wifi_details["Ssid"]
                        # Start interface
                        if not start_interface_safe(Obj):
                            return
                        
                        channels = []
                        
                        for dic in data:
                            if selected_ssid in dic["Ssid"]:
                                channels.append(int(dic["Chan"]))
                        
                        ui_print("Loading ...", "unset")
                        Obj.start_mdk4_deauth1(selected_ssid, channels)
                        ui_print(f"Deauthing:\n{selected_ssid}\non {channels}", "unset")
                        while GPIO.input(KEY3_PIN) != 0:
                            time.sleep(0.15)
                        
                        Obj.stop_mdk4_deauth1()
                        Obj.interface_stop()

                time.sleep(0.05)
            time.sleep(0.05)
        time.sleep(0.05)


# ==========================================
#               BEACON FLOOD                                
# ==========================================

def handle_beacon_flood(Obj):
    """
    Handle beacon flood attack - REFACTORED
    - Common-networks: Flood with common SSIDs
    - Personal-networks: Flood with personal SSIDs
    - Random: Flood with random SSIDs
    """
    time.sleep(0.2)
    selected_index = 0
    
    # Select beacon flood mode
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(MENUS['beacon_flood'], selected_index)
        draw_menu(MENUS['beacon_flood'], selected_index)
        
        if GPIO.input(KEY_PRESS_PIN) == 0:
            wait_for_key_release(KEY_PRESS_PIN)
            selected_mode = MENUS['beacon_flood'][selected_index]
            
            # Start interface
            if not start_interface_safe(Obj):
                return
            
            Obj.start_mdk4_beacon_flood(selected_mode)
            ui_print("Beacon Flooding ...",  "unset", color=(0,255,142))

            while GPIO.input(KEY3_PIN) != 0:
                time.sleep(0.1)

            Obj.stop_mdk4_beacon_flood_process()
            time.sleep(0.1)
            Obj.interface_stop()
            time.sleep(0.1)
    time.sleep(0.1)

# ======================================
#               SHUTDOWN                             
# ======================================

def handle_shutdown():
    safe = time.time()
    while GPIO.input(KEY3_PIN) != 0:
        ui_print("""Hold KEY2\nfor 3 sec to\nshutdown.""", "unset")
        if GPIO.input(KEY2_PIN) == 0:
            start_time = time.time()
            while GPIO.input(KEY2_PIN) == 0:
                if time.time() - start_time >= 3:
                    ui_print("Shutting down...", 1.5)
                    show_image(r"Images/logo.png", "unset")
                    subprocess.run("sudo shutdown now", shell=True)
                    time.sleep(10)
                    break
        elif time.time() - safe >= 10:
            ui_print("Timeout", 2 , (255, 0, 0))
            safe = None
            break

def handle_reboot():
    safe = time.time()
    while GPIO.input(KEY3_PIN) != 0:
        ui_print("""Hold KEY2\nfor 3 sec to\nreboot.""", "unset")
        if GPIO.input(KEY2_PIN) == 0:
            start_time = time.time()
            while GPIO.input(KEY2_PIN) == 0:
                if time.time() - start_time >= 3:
                    subprocess.run("sudo reboot", shell=True)
                    ui_print("Rebooting...", 1.5)
                    show_image(r"Images/logo.png", "unset")
                    time.sleep(10)
                    break

        elif time.time() - safe >= 10:
            ui_print("Timeout", 2 , (255, 0, 0))
            safe = None
            break


# ======================================
#               SETTINGS                                             
# ======================================

def handle_settings():
    
    selected_index = 0
    time.sleep(0.20)
    
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(MENUS['settings'], selected_index)
        draw_menu(MENUS['settings'], selected_index)

        if GPIO.input(KEY_PRESS_PIN) == 0:
            selected_option = MENUS['settings'][selected_index]

            if selected_option == "Interface":
                handle_interface_settings()
                selected_index = 0
                time.sleep(0.2)
    
    time.sleep(0.1)


def handle_interface_settings():
    
    global INTERFACE
    
    # Network interfaces
    sys_class_net_ = subprocess.run(["ls", "/sys/class/net/"], text=True, capture_output=True)
    
    if sys_class_net_.returncode != 0:
        ui_print("[ERR] Unable to\nfind ANY network\ninterfaces")
        time.sleep(2)
        return
    
    # Lists of network interfaces
    interface = sys_class_net_.stdout.splitlines()
    selected_index = 0
    time.sleep(0.20)
    TEMP_MENU = interface
    
    while GPIO.input(KEY3_PIN) != 0:
        selected_index = nav(TEMP_MENU, selected_index)
        draw_menu(TEMP_MENU, selected_index)

        if GPIO.input(KEY_PRESS_PIN) == 0:
            selected_interface = TEMP_MENU[selected_index]
            selected_index = 0
            time.sleep(0.2)

            # Menu
            while GPIO.input(KEY3_PIN) != 0:
                selected_index = nav(MENUS['interface'], selected_index)
                draw_menu(MENUS['interface'], selected_index)

                if GPIO.input(KEY_PRESS_PIN) == 0:
                    selected_option = MENUS['interface'][selected_index]
                    
                    if selected_option == "Select":
                        # select and save configurations (interface) 
                        INTERFACE = selected_interface
                        ui_print("Wait please...", 0.5)
                        
                        try:
                            with open("Settings/settings.json", "r+") as file:
                                data = json.load(file)
                                data["interface"] = INTERFACE
                                file.seek(0)  # Start from the beginning of the file
                                json.dump(data, file, indent=2)
                                file.truncate()  # Remove any leftover data
                            
                            ui_print(f"Selected Interface:\n{selected_interface}", 2, (0, 255, 142))
                        except Exception as e:
                            ui_print(f"[ERR] Failed to save:\n{str(e)[:18]}", 2, (255, 0, 0))
                        
                        break
                    
                    else:
                        # Restart interface
                        restart_interface(selected_interface)
                        break
            
            time.sleep(0.2)
    
    del TEMP_MENU


def restart_interface(interface_name):
    ui_print("Restarting\ninterface...", "unset")
    
    commands = [
        f"sudo airmon-ng stop {interface_name}",
        "sudo modprobe -r 88XXau",
        "sudo modprobe 88XXau",
        f"sudo ifconfig {interface_name} up"
        f"sudo iwconfig {interface_name} mode managed"
    ]
    
    try:
        for command in commands:
            subprocess.run(command, shell=True)
            time.sleep(0.25)
        
        ui_print(f"{interface_name} restarted", 1, (0, 255, 142))
    except Exception as e:
        ui_print(f"[ERR] Restart failed:\n{str(e)[:18]}", 2, (255, 0, 0))

# Main Part
show_image(r"/root/M00N/Images/logo.png")
try:
    subprocess.run("sudo rm -rf /root/M00N/Logs/*", shell=True)
    subprocess.run(f"sudo ifconfig {INTERFACE} up", shell=True)
except:
    ui_print("""[ERR] Interface
not starting!""", (255,0,0))

while True:
    draw_menu(MENUS['main'], selected_index)
    if GPIO.input(KEY_UP_PIN) == 0:
        selected_index = (selected_index - 1) % len(MENUS['main'])
        draw_menu(MENUS['main'], selected_index)
    elif GPIO.input(KEY_DOWN_PIN) == 0:
        selected_index = (selected_index + 1) % len(MENUS['main'])
        draw_menu(MENUS['main'], selected_index)
    elif GPIO.input(KEY_PRESS_PIN) == 0:
        selected_option = MENUS['main'][selected_index]
        if selected_option == "Wifi":
            
            # WIFI
            time.sleep(0.20)
            while True:
                Handshake_capture = 1
                selected_index = nav(MENUS['wifi'], selected_index)
                draw_menu(MENUS['wifi'], selected_index)
                if GPIO.input(KEY3_PIN) == 0:
                    break
                elif GPIO.input(KEY_PRESS_PIN) == 0:
                    selected_option = MENUS['wifi'][selected_index]
                    
                    # SNIFFERS
                    if selected_option == "Sniffers":
                        time.sleep(0.20)
                        while GPIO.input(KEY3_PIN) != 0:
                            selected_index = nav(MENUS['sniffers'], selected_index)
                            draw_menu(MENUS['sniffers'], selected_index)
                            if GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = MENUS['sniffers'][selected_index]
                                handshake = 1

                                # 4-WAY HANDSHAKE
                                if selected_option == "4-way handshake":
                                    handle_4way_handshake(netstd(INTERFACE))
                                    time.sleep(0.1)
                                    
                                # AP SCAN
                                elif selected_option == "AP scan":
                                    handle_ap_scan(netstd(INTERFACE))
                                    time.sleep(0.1)

                                            
                                # RAW SNIFF
                                elif selected_option == "Raw Sniff":
                                    handle_raw_sniff(netstd(INTERFACE))
                                    time.sleep(0.1)
                    
                    # ATTACKS
                    elif selected_option == "Attacks":
                        Obj = netstd(INTERFACE)
                        time.sleep(0.2)
                        selected_index = 0
                        while GPIO.input(KEY3_PIN) != 0:
                            selected_index = nav(MENUS['attacks'], selected_index)
                            draw_menu(MENUS['attacks'], selected_index)
                            if GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = MENUS['attacks'][selected_index]
                                
                                # Deauth
                                if selected_option == "Deauth":
                                    handle_deauth(Obj)
                                    time.sleep(0.1)

                                else:
                                    handle_beacon_flood(Obj)

                        time.sleep(0.1)

#REBOOT
        elif selected_option == "Reboot":
            handle_reboot()
            time.sleep(0.1)

#SHUTDOWN
        elif selected_option == "Shutdown":
            handle_shutdown()
            time.sleep(0.1)

#SETTINGS --> To improve
        elif selected_option == "Settings":
            handle_settings()
            time.sleep(0.1)
