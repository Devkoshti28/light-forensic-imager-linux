import sys
import os
import subprocess
import re
import hashlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QStackedWidget, QProgressBar, QFileDialog, QMessageBox,
                             QComboBox, QTreeWidget, QTreeWidgetItem, QSplitter, 
                             QTabWidget, QTextEdit)
from PyQt5.QtCore import QProcess, Qt

STYLESHEET = """
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', Arial; font-size: 14px; }
QPushButton { background-color: #89b4fa; color: #11111b; border-radius: 8px; padding: 10px 20px; font-weight: bold; }
QPushButton:hover { background-color: #b4befe; }
QPushButton:disabled { background-color: #45475a; color: #6c7086; }
QPushButton#btnRecover { background-color: #a6e3a1; color: #11111b;}
QPushButton#btnRecover:hover { background-color: #94e2d5; }
QPushButton#btnExplore { background-color: #f9e2af; color: #11111b;}
QPushButton#btnExplore:hover { background-color: #f38ba8; }
QLineEdit, QComboBox { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; padding: 8px; color: #cdd6f4; }
QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #45475a; }
QTreeWidget { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; color: #cdd6f4; }
QHeaderView::section { background-color: #45475a; color: #cdd6f4; padding: 4px; border: none; font-weight: bold; }
QProgressBar { border: 2px solid #45475a; border-radius: 5px; text-align: center; background-color: #313244; }
QProgressBar::chunk { background-color: #a6e3a1; width: 20px; }
QLabel#title { font-size: 24px; font-weight: bold; color: #89b4fa; }
QSplitter::handle { background-color: #45475a; width: 3px; border-radius: 1px; }
QTabWidget::pane { border: 1px solid #45475a; border-radius: 6px; background-color: #1e1e2e; }
QTabBar::tab { background-color: #313244; color: #cdd6f4; padding: 8px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px;}
QTabBar::tab:selected { background-color: #89b4fa; color: #11111b; font-weight: bold; }
QTextEdit { background-color: #11111b; color: #a6e3a1; border: none; font-family: 'Courier New', Courier, monospace; font-size: 13px; padding: 10px;}
"""

class LiteImagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteImager - Forensic Acquisition & Recovery (Modular)")
        self.resize(1150, 750) 
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.dir_nodes = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.bin_disk = os.path.join(self.base_dir, "build", "img_disk")
        self.bin_ram = os.path.join(self.base_dir, "build", "img_ram")
        self.bin_recover = os.path.join(self.base_dir, "build", "recover_raw")
        self.bin_tsk = os.path.join(self.base_dir, "build", "tsk_explorer")
        
        self.build_page_home()
        self.build_page_action()
        self.build_page_explorer()
        
        self.process = None
        self.mode = ""

    def build_page_home(self):
        page = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Select Operation Mode")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        btn_disk = QPushButton("Disk Imaging (.dd)")
        btn_disk.setFixedSize(300, 50)
        btn_disk.clicked.connect(lambda: self.setup_action_page("disk"))
        
        btn_ram = QPushButton("Live RAM Capture")
        btn_ram.setFixedSize(300, 50)
        btn_ram.clicked.connect(lambda: self.setup_action_page("ram"))

        btn_recover = QPushButton("Signature Carving (Raw Recovery)")
        btn_recover.setObjectName("btnRecover")
        btn_recover.setFixedSize(300, 50)
        btn_recover.clicked.connect(lambda: self.setup_action_page("recover"))
        
        btn_explore = QPushButton("Autopsy-Style File Explorer")
        btn_explore.setObjectName("btnExplore")
        btn_explore.setFixedSize(300, 50)
        btn_explore.clicked.connect(self.setup_explorer_page)
        
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(btn_disk, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(btn_ram, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(btn_recover, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(btn_explore, alignment=Qt.AlignCenter)
        layout.addStretch()
        page.setLayout(layout)
        self.stack.addWidget(page)

    def build_page_action(self):
        self.page_action = QWidget()
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.lbl_action_title = QLabel("Action Title")
        self.lbl_action_title.setObjectName("title")
        top_layout.addWidget(btn_back)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_action_title)
        top_layout.addStretch()
        
        self.src_widget = QWidget()
        src_layout = QHBoxLayout(self.src_widget)
        src_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_src = QLabel("Source:")
        self.combo_src = QComboBox()
        self.combo_src.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        self.btn_refresh_src = QPushButton("↻ Refresh")
        self.btn_refresh_src.clicked.connect(self.populate_drives)
        self.btn_browse_src = QPushButton("Browse Image")
        self.btn_browse_src.clicked.connect(self.browse_src_file)
        self.btn_browse_src.hide()

        src_layout.addWidget(self.lbl_src)
        src_layout.addWidget(self.combo_src, stretch=1)
        src_layout.addWidget(self.btn_refresh_src)
        src_layout.addWidget(self.btn_browse_src)
        
        dst_layout = QHBoxLayout()
        self.lbl_dst = QLabel("Destination:")
        self.input_dst = QLineEdit()
        self.btn_browse_dst = QPushButton("Browse")
        self.btn_browse_dst.clicked.connect(self.browse_dest)
        dst_layout.addWidget(self.lbl_dst)
        dst_layout.addWidget(self.input_dst)
        dst_layout.addWidget(self.btn_browse_dst)
        
        self.btn_start = QPushButton("Start Process")
        self.btn_start.clicked.connect(self.start_process)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.lbl_status = QLabel("Ready.")
        
        layout.addLayout(top_layout)
        layout.addSpacing(20)
        layout.addWidget(self.src_widget)
        layout.addLayout(dst_layout)
        layout.addSpacing(20)
        layout.addWidget(self.btn_start)
        layout.addSpacing(20)
        layout.addWidget(self.progress)
        layout.addWidget(self.lbl_status)
        layout.addStretch()
        self.page_action.setLayout(layout)
        self.stack.addWidget(self.page_action)

    def build_page_explorer(self):
        self.page_explorer = QWidget()
        layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        lbl_title = QLabel("File System Explorer")
        lbl_title.setObjectName("title")
        top_layout.addWidget(btn_back)
        top_layout.addStretch()
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        
        src_layout = QHBoxLayout()
        lbl_exp_src = QLabel("Disk Image:")
        self.combo_exp_src = QComboBox()
        self.combo_exp_src.setEditable(True)
        btn_exp_browse = QPushButton("Browse")
        btn_exp_browse.clicked.connect(lambda: self.browse_src_for_explorer())
        
        lbl_part = QLabel("Partition:")
        self.combo_exp_part = QComboBox()
        self.combo_exp_part.addItem("Raw Image (Offset: 0)", "0")
        
        self.btn_exp_scan = QPushButton("Scan Filesystem")
        self.btn_exp_scan.clicked.connect(self.start_explorer_scan)
        
        src_layout.addWidget(lbl_exp_src)
        src_layout.addWidget(self.combo_exp_src, stretch=2)
        src_layout.addWidget(btn_exp_browse)
        src_layout.addWidget(lbl_part)
        src_layout.addWidget(self.combo_exp_part, stretch=1)
        src_layout.addWidget(self.btn_exp_scan)
        
        self.splitter = QSplitter(Qt.Horizontal)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Status", "Inode", "File / Folder Name"])
        self.file_tree.setColumnWidth(0, 80)
        self.file_tree.setColumnWidth(1, 100)
        self.file_tree.itemSelectionChanged.connect(self.on_tree_select)
        
        self.preview_tabs = QTabWidget()
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_hex = QTextEdit()
        self.txt_hex.setReadOnly(True)
        self.txt_text = QTextEdit()
        self.txt_text.setReadOnly(True)
        self.txt_meta = QTextEdit()
        self.txt_meta.setReadOnly(True)
        
        self.preview_tabs.addTab(self.txt_info, "File Info")
        self.preview_tabs.addTab(self.txt_hex, "Hex View")
        self.preview_tabs.addTab(self.txt_text, "Text View")
        self.preview_tabs.addTab(self.txt_meta, "MFT/Inode Meta")
        
        self.splitter.addWidget(self.file_tree)
        self.splitter.addWidget(self.preview_tabs)
        self.splitter.setSizes([500, 650]) 
        
        ext_layout = QHBoxLayout()
        lbl_ext = QLabel("Extract to Folder:")
        self.input_ext_dst = QLineEdit()
        btn_ext_browse = QPushButton("Browse")
        btn_ext_browse.clicked.connect(lambda: self.input_ext_dst.setText(QFileDialog.getExistingDirectory(self, "Output Folder")))
        self.btn_ext_run = QPushButton("Extract Selected File")
        self.btn_ext_run.clicked.connect(self.extract_selected_file)
        
        ext_layout.addWidget(lbl_ext)
        ext_layout.addWidget(self.input_ext_dst, stretch=1)
        ext_layout.addWidget(btn_ext_browse)
        ext_layout.addWidget(self.btn_ext_run)
        
        self.lbl_exp_status = QLabel("Ready.")
        
        layout.addLayout(top_layout)
        layout.addSpacing(10)
        layout.addLayout(src_layout)
        layout.addWidget(self.splitter, stretch=1)
        layout.addLayout(ext_layout)
        layout.addWidget(self.lbl_exp_status)
        
        self.page_explorer.setLayout(layout)
        self.stack.addWidget(self.page_explorer)

    def on_tree_select(self):
        selected = self.file_tree.selectedItems()
        if not selected: return
        
        item = selected[0]
        inode = item.text(1)
        filename = item.text(2)
        
        if not inode:
            self.txt_info.setText("Virtual Folder - No data available.")
            self.txt_hex.setText("No Inode associated with this virtual structure.")
            self.txt_text.setText("No Data")
            self.txt_meta.setText("No Metadata")
            return
            
        src = self.combo_exp_src.currentText()
        offset = self.combo_exp_part.currentData() or "0"
        
        self.txt_meta.setText("Fetching metadata...")
        meta_run = subprocess.run([self.bin_tsk, "--meta", src, offset, inode], capture_output=True, text=True)
        
        meta_text = meta_run.stdout
        if "META_START" in meta_text and "META_END" in meta_text:
            meta_text = meta_text.split("META_START\n")[1].split("\nMETA_END")[0]
        self.txt_meta.setText(meta_text.strip() or "No metadata available.")
        
        size_str = "Unknown"
        match = re.search(r"Size:\s+(\d+)", meta_text)
        if match: size_str = f"{match.group(1)} bytes"
        
        self.txt_hex.setText("Loading...")
        self.txt_text.setText("Loading...")
        self.txt_info.setText("Analyzing file...")
        
        temp_preview = "/tmp/liteimager_preview.tmp"
        if os.path.exists(temp_preview): os.remove(temp_preview)
            
        subprocess.run([self.bin_tsk, "--preview", src, offset, inode, temp_preview])
        
        if os.path.exists(temp_preview):
            with open(temp_preview, "rb") as f:
                data = f.read()
                
            if data:
                file_magic = "Unknown"
                magic_run = subprocess.run(["file", "-b", temp_preview], capture_output=True, text=True)
                if magic_run.returncode == 0: file_magic = magic_run.stdout.strip()
                
                md5_hash = hashlib.md5(data).hexdigest()
                
                info_text = f"File Name: {filename}\n"
                info_text += f"Inode: {inode}\n"
                info_text += f"Reported Size: {size_str}\n\n"
                info_text += f"--- Forensic Analysis ---\n"
                info_text += f"Detected File Type:\n{file_magic}\n\n"
                info_text += f"Preview Block MD5 Hash (First 4KB):\n{md5_hash}\n"
                self.txt_info.setText(info_text)

                hex_lines = []
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_str = " ".join(f"{b:02X}" for b in chunk)
                    ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                    hex_lines.append(f"{i:08X}  {hex_str:<47}  {ascii_str}")
                self.txt_hex.setText("\n".join(hex_lines))
                
                text_str = "".join(chr(b) if 32 <= b <= 126 or b in (9, 10, 13) else "." for b in data)
                self.txt_text.setText(text_str)
            else:
                self.txt_info.setText(f"File: {filename}\nStatus: Empty or Directory")
                self.txt_hex.setText("File is empty or is a directory.")
                self.txt_text.setText("File is empty or is a directory.")
        else:
            self.txt_info.setText("Failed to read file from disk image.")
            self.txt_hex.setText("Failed to generate preview.")

    def populate_drives(self):
        self.combo_src.clear()
        try:
            result = subprocess.run(['lsblk', '-p', '-n', '-o', 'NAME,SIZE,TYPE,MODEL'], capture_output=True, text=True, check=True)
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                parts = line.split()
                if len(parts) >= 3:
                    dev_path, size, dev_type = parts[0], parts[1], parts[2]
                    model = " ".join(parts[3:]) if len(parts) > 3 else "Unknown Model"
                    if dev_type in ['disk', 'part', 'loop', 'nvme']:
                        display_text = f"{dev_path}  —  {size}  [{dev_type.upper()}]  {model}"
                        self.combo_src.addItem(display_text, dev_path)
        except Exception:
            self.combo_src.addItem("Error loading drives", "")

    def setup_action_page(self, mode):
        self.mode = mode
        self.input_dst.clear()
        self.progress.setValue(0)
        self.lbl_status.setText("Ready.")
        self.btn_start.setEnabled(True)

        if mode == "disk":
            self.lbl_action_title.setText("Bit-by-Bit Disk Imaging")
            self.src_widget.setVisible(True)
            self.btn_refresh_src.show()
            self.btn_browse_src.hide()
            self.combo_src.setEditable(False)
            self.lbl_dst.setText("Destination File:")
            self.input_dst.setPlaceholderText("Save as .dd or .img")
            self.populate_drives()
        elif mode == "ram":
            self.lbl_action_title.setText("Live RAM Capture")
            self.src_widget.setVisible(False)
            self.lbl_dst.setText("Destination File:")
            self.input_dst.setPlaceholderText("Save as .lime")
        elif mode == "recover":
            self.lbl_action_title.setText("Raw Signature Carving")
            self.src_widget.setVisible(True)
            self.btn_refresh_src.hide()
            self.btn_browse_src.show()
            self.combo_src.clear()
            self.combo_src.setEditable(True)
            self.combo_src.setCurrentText("Select or paste path to .dd image...")
            self.lbl_dst.setText("Output Folder:")
            self.input_dst.setPlaceholderText("Select an empty folder to save files")

        self.stack.setCurrentIndex(1)

    def setup_explorer_page(self):
        self.mode = "list"
        self.file_tree.clear()
        self.dir_nodes = {}
        self.combo_exp_part.clear()
        self.combo_exp_part.addItem("Raw Image (Offset: 0)", "0")
        self.txt_info.clear()
        self.txt_hex.clear()
        self.txt_text.clear()
        self.txt_meta.clear()
        self.lbl_exp_status.setText("Ready.")
        self.btn_exp_scan.setEnabled(True)
        self.btn_ext_run.setEnabled(True)
        self.stack.setCurrentIndex(2)

    def browse_src_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Disk Image File", "", "Image Files (*.dd *.img *.raw);;All Files (*)")
        if fname: self.combo_src.setCurrentText(fname)

    def browse_src_for_explorer(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Disk Image File", "", "Image Files (*.dd *.img *.raw);;All Files (*)")
        if fname: 
            self.combo_exp_src.setCurrentText(fname)
            self.detect_partitions(fname)

    def detect_partitions(self, src):
        self.combo_exp_part.clear()
        self.combo_exp_part.addItem("Raw Image (Offset: 0)", "0")
        
        result = subprocess.run([self.bin_tsk, "--partitions", src], capture_output=True, text=True)
        output = result.stdout
        
        if "PARTITION_START" in output:
            part_data = output.split("PARTITION_START\n")[1].split("\nPARTITION_END")[0]
            for line in part_data.split('\n'):
                parts = line.split()
                if len(parts) >= 5 and parts[2].isdigit():
                    start_offset = parts[2]
                    description = " ".join(parts[5:])
                    if description != "Unallocated":
                        self.combo_exp_part.addItem(f"{description} (Offset: {start_offset})", start_offset)
            
            if self.combo_exp_part.count() > 1:
                self.combo_exp_part.setCurrentIndex(1)

    def browse_dest(self):
        if self.mode == "recover":
            folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if folder: self.input_dst.setText(folder)
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Save Destination File")
            if fname: self.input_dst.setText(fname)

    def start_process(self):
        dst = self.input_dst.text()
        if not dst:
            QMessageBox.warning(self, "Error", "Destination is required.")
            return

        lime_path = os.path.join(self.base_dir, "lime.ko")
        cmd = []
        
        if self.mode == "disk":
            src = self.combo_src.currentData()
            if not src: return
            cmd = [self.bin_disk, src, dst]
        elif self.mode == "ram":
            if not os.path.exists(lime_path): 
                QMessageBox.critical(self, "Error", f"Could not find lime.ko!\nPlease place it here: {lime_path}")
                return
            cmd = [self.bin_ram, dst, lime_path]
        elif self.mode == "recover":
            src = self.combo_src.currentText()
            cmd = [self.bin_recover, src, dst]

        if not cmd: return

        self.btn_start.setEnabled(False)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.start(cmd[0], cmd[1:])

    def start_explorer_scan(self):
        src = self.combo_exp_src.currentText()
        offset = self.combo_exp_part.currentData() or "0"
        
        if not os.path.exists(src) or os.path.isdir(src):
            QMessageBox.warning(self, "Error", "Valid source image file is required.")
            return
            
        self.file_tree.clear()
        self.dir_nodes = {}
        self.txt_info.clear()
        self.txt_hex.clear()
        self.txt_text.clear()
        self.txt_meta.clear()
        self.lbl_exp_status.setText("Scanning filesystem with TSK... (This may take a moment)")
        self.btn_exp_scan.setEnabled(False)
        
        self.mode = "list"
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.errorOccurred.connect(self.handle_process_error)
        self.process.start(self.bin_tsk, ["--list", src, offset])

    def extract_selected_file(self):
        selected = self.file_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a file to extract from the tree.")
            return
            
        item = selected[0]
        inode = item.text(1)
        filename = item.text(2)
        
        if not inode:
            QMessageBox.warning(self, "Error", "Selected item does not have a valid Inode.")
            return
            
        safe_filename = filename.replace("$", "_").replace("`", "_").replace(";", "_").replace("&", "_")
        
        out_folder = self.input_ext_dst.text()
        if not os.path.isdir(out_folder):
            QMessageBox.warning(self, "Error", "Please select a valid output folder first.")
            return
            
        out_path = os.path.join(out_folder, safe_filename)
        src = self.combo_exp_src.currentText()
        offset = self.combo_exp_part.currentData() or "0"
        
        self.lbl_exp_status.setText(f"Extracting {safe_filename}...")
        self.btn_ext_run.setEnabled(False)
        
        self.mode = "extract"
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.start(self.bin_tsk, ["--extract", src, offset, inode, out_path])

    def handle_process_error(self, error):
        self.btn_start.setEnabled(True)
        self.btn_exp_scan.setEnabled(True)
        self.btn_ext_run.setEnabled(True)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode().strip()
        for line in data.split('\n'):
            if line.startswith("PROGRESS:"):
                try: self.progress.setValue(int(float(line.split(":")[1])))
                except ValueError: pass
            
            elif line.startswith("STATUS:"):
                status_msg = line.split(":", 1)[1].strip()
                self.lbl_status.setText(status_msg)
                self.lbl_exp_status.setText(status_msg)
                
            elif line.startswith("HASH:"):
                self.lbl_status.setText(line.split("HASH:")[1].strip())
                
            elif line.startswith("FILE_ENTRY:"):
                raw_entry = line[len("FILE_ENTRY:"):].strip()
                tokens = raw_entry.split()
                if not tokens: continue
                
                is_deleted = '*' in tokens
                status = "Deleted" if is_deleted else "Allocated"
                is_dir = tokens[0].startswith('d')
                
                inode, full_path = "", ""
                for i, token in enumerate(tokens):
                    if token.endswith(':'):
                        inode = token[:-1] 
                        full_path = " ".join(tokens[i+1:])
                        break
                
                if inode and full_path:
                    path_parts = full_path.split('/')
                    filename = path_parts[-1]
                    
                    parent_item = self.file_tree.invisibleRootItem()
                    current_path = ""
                    
                    for i in range(len(path_parts) - 1):
                        folder_name = path_parts[i]
                        current_path = current_path + "/" + folder_name if current_path else folder_name
                        
                        if current_path not in self.dir_nodes:
                            dir_node = QTreeWidgetItem(["", "", folder_name])
                            font = dir_node.font(2)
                            font.setBold(True)
                            dir_node.setFont(2, font)
                            parent_item.addChild(dir_node)
                            self.dir_nodes[current_path] = dir_node
                        
                        parent_item = self.dir_nodes[current_path]
                    
                    current_path = full_path
                    if current_path in self.dir_nodes:
                        node = self.dir_nodes[current_path]
                        node.setText(0, status)
                        node.setText(1, inode)
                    else:
                        node = QTreeWidgetItem([status, inode, filename])
                        if is_dir:
                            font = node.font(2)
                            font.setBold(True)
                            node.setFont(2, font)
                        parent_item.addChild(node)
                        self.dir_nodes[current_path] = node
                        
                    if is_deleted:
                        node.setForeground(0, Qt.red)
                        node.setForeground(2, Qt.red)
                    
            elif line.startswith("ERROR:"):
                QMessageBox.critical(self, "Execution Error", line)
                self.btn_start.setEnabled(True)
                self.btn_exp_scan.setEnabled(True)
                self.btn_ext_run.setEnabled(True)
                
            elif "DONE" in line:
                self.btn_start.setEnabled(True)
                self.btn_exp_scan.setEnabled(True)
                self.btn_ext_run.setEnabled(True)
                self.progress.setValue(100)

    def handle_stderr(self):
        err = self.process.readAllStandardError().data().decode().strip()
        if err: print(f"Backend Error: {err}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Please run this script with sudo.")
        sys.exit(1)
        
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = LiteImagerGUI()
    window.show()
    sys.exit(app.exec_())
