#!/bin/bash
# EyeLeo installation script

set -e

echo "Installing EyeLeo..."

# Make the script executable
chmod +x eyeleo.py

# Create symlink in ~/.local/bin
mkdir -p ~/.local/bin
ln -sf "$(pwd)/eyeleo.py" ~/.local/bin/eyeleo
echo "✓ Created symlink in ~/.local/bin/eyeleo"

# Install systemd service
mkdir -p ~/.config/systemd/user
cp eyeleo.service ~/.config/systemd/user/
echo "✓ Installed systemd service"

# Reload systemd
systemctl --user daemon-reload
echo "✓ Reloaded systemd"

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  eyeleo start -duration 20    # Start with 20-minute intervals"
echo "  eyeleo pause                 # Pause notifications (for meetings)"
echo "  eyeleo resume                # Resume notifications"
echo "  eyeleo status                # Check if running"
echo "  eyeleo stop                  # Stop the daemon"
echo ""
echo "To enable auto-start on login:"
echo "  systemctl --user enable eyeleo.service"
echo "  systemctl --user start eyeleo.service"
echo ""
echo "To check service status:"
echo "  systemctl --user status eyeleo.service"

