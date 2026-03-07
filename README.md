# EyeLeo 👁️

Eye care reminder tool for Sway/Wayland on Linux. Sends periodic notifications to remind you to take breaks and blink.

## Features

- ⏰ Customizable notification intervals (default: 20 minutes)
- ⏸️ Pause/resume functionality when you need to focus
- 🔔 Native Wayland notifications (works with mako, dunst, etc.)
- 🚀 Systemd integration for auto-start
- 💾 Lightweight Python script

## Requirements

- **Python 3**
- **libnotify** - Provides `notify-send` command (usually pre-installed)
- **SwayNC** (Sway Notification Center) - Notification daemon for Sway

### Installing Dependencies

```bash
# Install SwayNC (notification daemon)
sudo pacman -S swaync

# Install libnotify if not already installed (provides notify-send)
sudo pacman -S libnotify
```

Add to your `~/.config/sway/config`:
```
exec swaync
```

Then reload Sway or start swaync manually:
```bash
swaync &
```

## Installation

```bash
chmod +x install.sh
./install.sh
```

This will:
- Make the script executable
- Create a symlink in `~/.local/bin/eyeleo`
- Install the systemd service

## Usage

**⚠️ IMPORTANT:** Choose either Manual Mode OR Systemd Service - **DO NOT run both at the same time!**

### Option 1: Systemd Service (Recommended - Auto-start)

This is the recommended way. The service runs in the background and starts automatically on login.

```bash
# Enable auto-start on login
systemctl --user enable eyeleo.service

# Start the service now
systemctl --user start eyeleo.service

# Check service status
systemctl --user status eyeleo.service

# Stop the service
systemctl --user stop eyeleo.service

# Disable auto-start
systemctl --user disable eyeleo.service
```

**To change the duration when using systemd:**
1. Edit `~/.config/systemd/user/eyeleo.service`
2. Change `-duration 20` to your preferred interval
3. Run: `systemctl --user daemon-reload && systemctl --user restart eyeleo.service`

### Option 2: Manual Mode (One-time use)

**⚠️ Only use this if the systemd service is NOT running!**

Check first: `systemctl --user status eyeleo.service` (should show "inactive")

```bash
# Start with 20-minute intervals (runs in foreground)
eyeleo start -duration 20

# Start with 30-minute intervals
eyeleo start -duration 30

# Stop with Ctrl+C
```

### Pause/Resume

**Works with both systemd service and manual mode:**

```bash
# Pause notifications
eyeleo pause

# Resume notifications
eyeleo resume

# Check current status
eyeleo status
```

The daemon keeps running in the background when paused, it just won't show notifications.

## Sway Integration

You can bind keyboard shortcuts in your Sway config (`~/.config/sway/config`):

```
# Pause/resume EyeLeo
bindsym $mod+Shift+e exec eyeleo pause
bindsym $mod+Shift+r exec eyeleo resume
```

## Customization

Edit `eyeleo.service` to change the default duration:

```ini
ExecStart=%h/Apps/eyeleo/eyeleo.py start -duration 25
```

Then reload:
```bash
systemctl --user daemon-reload
systemctl --user restart eyeleo.service
```

## Uninstall

```bash
systemctl --user stop eyeleo.service
systemctl --user disable eyeleo.service
rm ~/.config/systemd/user/eyeleo.service
rm ~/.local/bin/eyeleo
systemctl --user daemon-reload
```

## The 20-20-20 Rule

Every 20 minutes, look at something 20 feet away for 20 seconds. This helps reduce eye strain from prolonged screen time.

