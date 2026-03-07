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
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Sending notification...")

            # Use --wait to block until notification is dismissed
            result = subprocess.run([
                "notify-send",
                "-u", "critical",  # Urgency level
                "-t", "0",         # Don't auto-expire (wait for user dismissal)
                "-a", "EyeLeo",    # App name
                "--wait",          # Wait for notification to be closed
                title,
                message
            ], check=True)

            # Log when notification was dismissed
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Notification dismissed by user")

        except subprocess.CalledProcessError as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Error sending notification: {e}")
        except FileNotFoundError:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Error: notify-send not found. Please install libnotify.")
    
    def is_paused(self):
        """Check if notifications are paused"""
        pause_file = self.state_file.parent / "paused"
        return pause_file.exists()
    
    def update_state_file(self, next_notification_time):
        """Update state file with PID, duration, and next notification time"""
        with open(self.state_file, 'w') as f:
            f.write(f"{os.getpid()}\n{self.duration // 60}\n{int(next_notification_time)}")

    def run(self):
        """Main loop - send notifications at specified intervals"""
        print(f"EyeLeo started - notifications every {self.duration // 60} minutes")
        print(f"State file: {self.state_file}")
        print("Press Ctrl+C to stop")

        try:
            while self.running:
                if not self.is_paused():
                    # Calculate next notification time
                    next_time = time.time() + self.duration
                    self.update_state_file(next_time)

                    # Wait first, then notify (not notify then wait)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    next_timestamp = datetime.fromtimestamp(next_time).strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] Next notification at {next_timestamp}")
                    time.sleep(self.duration)
                    self.send_notification()
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] Paused - checking again in 60 seconds...")
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
            lines = f.read().strip().split('\n')
            pid = lines[0]
            duration = lines[1] if len(lines) > 1 else "unknown"
            next_notification = float(lines[2]) if len(lines) > 2 else None

        # Check if process is actually running
        try:
            os.kill(int(pid), 0)
            paused_status = "PAUSED" if pause_file.exists() else "ACTIVE"

            status_msg = f"✓ EyeLeo is running (PID: {pid}) - Status: {paused_status} - Interval: {duration} minutes"

            # Add next notification time if available and not paused
            if next_notification and not pause_file.exists():
                now = time.time()
                if next_notification > now:
                    remaining_seconds = int(next_notification - now)
                    remaining_minutes = remaining_seconds // 60
                    remaining_secs = remaining_seconds % 60
                    next_time_str = datetime.fromtimestamp(next_notification).strftime("%H:%M:%S")
                    status_msg += f"\n  Next notification: {next_time_str} (in {remaining_minutes}m {remaining_secs}s)"
                else:
                    status_msg += "\n  Next notification: due now"

            print(status_msg)
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

