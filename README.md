# Light Forensic Imaging Tool (Linux)

A lightweight forensic imaging and analysis tool for Linux systems.
Inspired by FTK Imager, this tool supports:

- Disk Imaging (SSD, HDD, USB) using dd
- RAM Capture
- Raw File Recovery
- Basic TSK-based File Explorer
- GUI Interface (Python)

## Tech Stack
- C (Core imaging modules)
- Python (GUI)
- GTK (Optional)
- Linux System Calls

## Features
- Create forensic disk images (.dd)
- Capture system memory (RAM)
- Recover deleted/raw files
- Explore disk structures using TSK

## Installation

```bash
sudo apt update
sudo apt install build-essential python3 python3-pip