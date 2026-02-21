🚀 Light Forensic Imager (Linux)

A lightweight Linux-based Digital Forensics tool inspired by FTK Imager, built using C and Python, designed for disk imaging, RAM acquisition, and basic forensic analysis.

📌 Overview

Light Forensic Imager is a modular digital forensics tool developed for Linux environments.
It enables investigators to:

• Create forensic disk images (.dd)

• Capture volatile memory (RAM)

• Perform raw file recovery

• Explore disk structures using TSK

• Operate through a Python-based GUI

This tool focuses on lightweight performance, modular architecture, and forensic integrity.

🛠 Tech Stack

• C – Core forensic modules

• Python 3 – GUI Interface

• Linux System Calls – Low-level disk & memory access

• The Sleuth Kit (TSK) – File system exploration

• dd – Disk imaging


⚙️ Installation

1️⃣ Clone Repository:

    git clone https://github.com/DevKoshti28/light-forensic-imager-linux.git
    cd light-forensic-imager-linux

2️⃣ Run Setup Script:

    chmod +x install.sh
    ./install.sh

The script installs required dependencies and compiles C modules.

▶️ Run the Application

After installation:

    sudo python3 gui.py

⚠ Root privileges are required for disk and RAM acquisition.

🔍 Features

✔ Create forensic disk images using dd

✔ Capture system RAM safely

✔ Recover raw/deleted files

✔ Explore partitions and file systems

✔ Lightweight and modular design

✔ Linux compatible


🔐 Forensic Considerations

• Uses read-only acquisition where possible

• Maintains evidence integrity

• Designed for educational & research purposes

• Requires administrator privileges for acquisition

