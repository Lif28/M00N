import json
import subprocess
import re

# Initialize WiFi adapter

class wifi_info():
    def __init__(self):
        self.INTERFACE = json.load(open("/root/M00N/Settings/settings.json", "r"))["interface"]
        with open("/root/M00N/Settings/settings.json", 'r') as cou:
            data = json.load(cou)
        self.country = data['country']

    def process(self):       
        try:
            out =subprocess.check_output(["sudo", "iw", "dev", self.INTERFACE, "scan"], text=True)
            return out
        except Exception as e:
            print(f"ERROR {e}")
    
    def split(self, data):
        blocks = re.split(r'\nBSS\s', data)
        wifi_data = []

        for i in blocks:
            # Checks if i is empty or not
            if not i.strip():
                continue
            wifi_data.append(i)
        return wifi_data
    
    def final(self):
        Final_dict = []
        wifi_chans = {
            "US": {
                2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5,
                2437: 6, 2442: 7, 2447: 8, 2452: 9, 2457: 10,
                2462: 11, 5180: 36, 5200: 40, 5220: 44, 5240: 48,
                5260: 52, 5280: 56, 5300: 60, 5320: 64,
                5500: 100, 5520: 104, 5540: 108, 5560: 112,
                5580: 116, 5600: 120, 5620: 124, 5640: 128,
                5660: 132, 5680: 136, 5700: 140, 5745: 149,
                5765: 153, 5785: 157, 5805: 161, 5825: 165
            },
            "EU": {
                2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5,
                2437: 6, 2442: 7, 2447: 8, 2452: 9, 2457: 10,
                2462: 11, 2467: 12, 2472: 13, 5180: 36, 5200: 40,
                5220: 44, 5240: 48, 5260: 52, 5280: 56, 5300: 60,
                5320: 64, 5500: 100, 5520: 104, 5540: 108, 5560: 112,
                5580: 116, 5600: 120, 5620: 124, 5640: 128,
                5660: 132, 5680: 136, 5700: 140, 5720: 144,
                5745: 149, 5765: 153, 5785: 157, 5805: 161, 5825: 165
            },
            "JP": {
                2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5,
                2437: 6, 2442: 7, 2447: 8, 2452: 9, 2457: 10,
                2462: 11, 2467: 12, 2472: 13, 2484: 14, 5180: 36,
                5200: 40, 5220: 44, 5240: 48, 5260: 52, 5280: 56,
                5300: 60, 5320: 64, 5500: 100, 5520: 104, 5540: 108,
                5560: 112, 5580: 116, 5600: 120, 5620: 124, 5640: 128,
                5660: 132, 5680: 136, 5700: 140
            },
            "CN": {
                2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5,
                2437: 6, 2442: 7, 2447: 8, 2452: 9, 2457: 10,
                2462: 11, 2467: 12, 2472: 13, 5180: 36, 5200: 40,
                5220: 44, 5240: 48, 5260: 52, 5280: 56, 5300: 60,
                5320: 64, 5500: 100, 5520: 104, 5540: 108, 5560: 112,
                5580: 116, 5600: 120, 5620: 124, 5640: 128,
                5660: 132, 5680: 136, 5700: 140, 5720: 144,
                5745: 149, 5765: 153, 5785: 157, 5805: 161, 5825: 165
            }
        }

        
        data = self.process()
        blocks = self.split(data)
        for i in blocks:
            BSSID = re.search(r'([0-9a-fA-F:]{17})', i).group(0)


            SSID_match = re.search(r'SSID:\s*(.*)', i)
            SSID = ("HIDDEN NETWORK" if (SSID_match.group(1).strip() == "" or "Supported" in SSID_match.group(1).strip()) else SSID_match.group(1).strip())

            CHAN = wifi_chans[self.country][int(re.search(r'freq:\s*(\d+)', i).group(1))]

            SIGNAL = re.search(r'signal:\s*([-0-9.]+) dBm', i)
            SIGNAL = float(SIGNAL.group(1)) if SIGNAL else None

            SECURITY = None
            if 'WPA3' in i or 'SAE' in i:
                SECURITY = 'WPA3'
            elif 'WPA2' in i or 'RSN:' in i:
                SECURITY = 'WPA2'
            elif 'WPA' in i:
                SECURITY = 'WPA'
            else:
                SECURITY = 'OPEN'

            dict = {
                "Bssid":str(BSSID),
                "Ssid": str(SSID),
                "Chan": str(CHAN),
                "Signal": str(SIGNAL),
                "Security": str(SECURITY)
            }

            Final_dict.append(dict)
              
        with open("wifiinfo.json", mode="w") as a:
            json.dump(Final_dict, a, indent=2)
   
    def main(self):
        self.final()
