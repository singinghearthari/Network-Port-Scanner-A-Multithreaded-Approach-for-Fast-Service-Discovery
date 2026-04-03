import sys
import time
import argparse
import threading
import queue
from port_scanner.core import PortScanner

def run_cli():
    parser = argparse.ArgumentParser(description="Network Port Scanner - CLI")
    parser.add_argument("target", help="Target IP or Hostname")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("-t", "--timeout", type=float, default=0.5, help="Timeout in seconds (default: 0.5)")
    parser.add_argument("-w", "--workers", type=int, default=500, help="Max threads (default: 500)")

    args = parser.parse_args()

    if not (0 <= args.start <= 65535 and 0 <= args.end <= 65535 and args.start <= args.end):
        print("Error: Port range must be within 0-65535 and start <= end")
        sys.exit(1)

    scanner = PortScanner(args.target, args.start, args.end, timeout=args.timeout, max_workers=args.workers)

    try:
        resolved_ip = scanner.resolve_target()
        print(f"Target: {args.target} ({resolved_ip})")
        print(f"Range: {args.start}-{args.end}")
        print("Starting scan...\n")
    except Exception as e:
        print(f"Failed to resolve target '{args.target}'. {e}")
        sys.exit(1)

    start_time = time.time()
    
    scanner_thread = threading.Thread(target=scanner.run, daemon=True)
    scanner_thread.start()

    last_progress = 0
    while scanner_thread.is_alive() or not scanner.result_queue.empty():
        try:
            msg = scanner.result_queue.get(timeout=0.1)
            msg_type = msg[0]
            if msg_type == 'open':
                port, service, banner = msg[1], msg[2], msg[3]
                banner_info = f" [Banner: {banner}]" if banner else ""
                print(f"\n[+] Port {port} ({service}) is open{banner_info}")
            elif msg_type == 'progress':
                # msg[1] is a (scanned count), msg[2] is b (total)
                a, b = msg[1], msg[2]
                pct = int((a / b) * 10)
                if pct > last_progress:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    last_progress = pct
            elif msg_type == 'done':
                break
        except queue.Empty:
            continue
        except KeyboardInterrupt:
            print("\nStopping scan...")
            scanner.stop()
            break

    scanner_thread.join()
    
    elapsed = time.time() - start_time
    print(f"\n\nScan complete in {elapsed:.2f}s.")
    print(f"Open ports found: {len(scanner.open_ports)}")

    if scanner.open_ports:
        print("\nSummary of open ports:")
        for port, service, banner in sorted(scanner.open_ports, key=lambda x: x[0]):
            banner_info = f" | Banner: {banner}" if banner else ""
            print(f"  - {port}: {service}{banner_info}")
