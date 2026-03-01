#!/bin/bash

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo "Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "Tailscale already installed"
fi

# Connect to headscale
echo "Connecting to headscale.right-api.com..."
tailscale up --login-server https://headscale.right-api.com --authkey $(cat /tmp/headscale_key 2>/dev/null || echo "No key found")

echo "Done!"
