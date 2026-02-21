#!/bin/bash

echo "[*] Installing System Dependencies (Sleuth Kit, Compilers, Git, Python)..."
sudo apt update
sudo apt install -y sleuthkit build-essential libssl-dev linux-headers-$(uname -r) python3 python3-pip git

echo "[*] Installing Python Dependencies..."
pip3 install -r requirements.txt

echo "[*] Compiling C Backend Modules..."
mkdir -p build
gcc img_disk.c -o build/img_disk -lssl -lcrypto
gcc img_ram.c -o build/img_ram
gcc recover_raw.c -o build/recover_raw
gcc tsk_explorer.c -o build/tsk_explorer

echo "[*] Fetching and Compiling LiME for RAM Capture..."
# Only build LiME if it doesn't already exist
if [ ! -f "lime.ko" ]; then
    git clone https://github.com/504ensicsLabs/LiME.git
    cd LiME/src
    make
    # Copy the newly built module to the main folder as 'lime.ko'
    cp lime-*.ko ../../lime.ko
    cd ../../
    # Clean up the downloaded source code to keep the folder neat
    rm -rf LiME
    echo "[+] LiME compiled successfully!"
else
    echo "[+] lime.ko already exists, skipping build."
fi

echo "[*] Setup Complete! You can now run: sudo python3 gui.py"