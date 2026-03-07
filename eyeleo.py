#!/usr/bin/env python3
"""
EyeLeo - Eye care reminder tool for Sway/Wayland
Reminds you to take breaks and blink to prevent eye strain
"""

import argparse
import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from datetime import datetime

class EyeLeo:
    def __init__(self, duration=20, state_file=None):
        self.duration = duration * 60  # Convert minutes to seconds
        self.state_file = state_file or Path.home() / ".config" / "eyeleo" / "state"
        self.running = True
        self.paused = False
        
        # Ensure config directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutting down EyeLeo...")
        self.running = False
        sys.exit(0)
    
    def send_notification(self):
        """Send eye care notification using notify-send"""
        title = "👁️ Eye Care Reminder"
        message = (
            "Time to take a break!\n\n"
            "• Look away from the screen\n"
            "• Blink several times\n"
            "• Look at something 20 feet away for 20 seconds"
        )
        
        try:
            subprocess.run([
                "notify-send",
                "-u", "critical",  # Urgency level
                "-t", "10000",     # Display for 10 seconds
                "-a", "EyeLeo",    # App name
                title,
                message
            ], check=True)
            
            # Log the notification
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Notification sent")
            
        except subprocess.CalledProcessError as e:
            print(f"Error sending notification: {e}")
        except FileNotFoundError:
            print("Error: notify-send not found. Please install libnotify.")
            sys.exit(1)
    
    def is_paused(self):
        """Check if notifications are paused"""
        pause_file = self.state_file.parent / "paused"
        return pause_file.exists()
    
    def run(self):
        """Main loop - send notifications at specified intervals"""
        print(f"EyeLeo started - notifications every {self.duration // 60} minutes")
        print(f"State file: {self.state_file}")
        print("Press Ctrl+C to stop")
        
        # Write PID to state file
        with open(self.state_file, 'w') as f:
            f.write(str(os.getpid()))
        
        try:
            while self.running:
                if not self.is_paused():
                    self.send_notification()
                    time.sleep(self.duration)
                else:
                    print("Paused - checking again in 60 seconds...")
                    time.sleep(60)
        finally:
            # Cleanup state file
            if self.state_file.exists():
                self.state_file.unlink()


def pause():
    """Pause notifications"""
    pause_file = Path.home() / ".config" / "eyeleo" / "paused"
    pause_file.parent.mkdir(parents=True, exist_ok=True)
    pause_file.touch()
    print("✓ EyeLeo notifications paused")


def resume():
    """Resume notifications"""
    pause_file = Path.home() / ".config" / "eyeleo" / "paused"
    if pause_file.exists():
        pause_file.unlink()
        print("✓ EyeLeo notifications resumed")
    else:
        print("EyeLeo was not paused")


def status():
    """Check if EyeLeo is running and paused status"""
    state_file = Path.home() / ".config" / "eyeleo" / "state"
    pause_file = Path.home() / ".config" / "eyeleo" / "paused"
    
    if state_file.exists():
        with open(state_file, 'r') as f:
            pid = f.read().strip()
        
        # Check if process is actually running
        try:
            os.kill(int(pid), 0)
            paused_status = "PAUSED" if pause_file.exists() else "ACTIVE"
            print(f"✓ EyeLeo is running (PID: {pid}) - Status: {paused_status}")
        except (OSError, ValueError):
            print("✗ EyeLeo is not running (stale state file)")
            state_file.unlink()
    else:
        print("✗ EyeLeo is not running")


def stop():
    """Stop the running EyeLeo daemon"""
    state_file = Path.home() / ".config" / "eyeleo" / "state"
    
    if state_file.exists():
        with open(state_file, 'r') as f:
            pid = f.read().strip()
        
        try:
            os.kill(int(pid), signal.SIGTERM)
            print(f"✓ Stopped EyeLeo (PID: {pid})")
        except (OSError, ValueError) as e:
            print(f"Error stopping EyeLeo: {e}")
    else:
        print("✗ EyeLeo is not running")


def main():
    parser = argparse.ArgumentParser(
        description="EyeLeo - Eye care reminder for Sway/Wayland",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  eyeleo.py start -duration 20    # Start with 20-minute intervals
  eyeleo.py pause                 # Pause notifications (for meetings)
  eyeleo.py resume                # Resume notifications
  eyeleo.py status                # Check if running
  eyeleo.py stop                  # Stop the daemon
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start EyeLeo daemon')
    start_parser.add_argument('-duration', type=int, default=20,
                            help='Notification interval in minutes (default: 20)')
    
    # Control commands
    subparsers.add_parser('pause', help='Pause notifications')
    subparsers.add_parser('resume', help='Resume notifications')
    subparsers.add_parser('status', help='Check status')
    subparsers.add_parser('stop', help='Stop daemon')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        eyeleo = EyeLeo(duration=args.duration)
        eyeleo.run()
    elif args.command == 'pause':
        pause()
    elif args.command == 'resume':
        resume()
    elif args.command == 'status':
        status()
    elif args.command == 'stop':
        stop()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

