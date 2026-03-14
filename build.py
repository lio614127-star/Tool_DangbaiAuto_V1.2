import os
import subprocess
import sys

def build():
    print("🚀 Bắt đầu quá trình đóng gói ứng dụng...")
    
    # Define paths
    entry_point = "main.py"
    icon_path = "" # Add icon path if available
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon", "app_icon.ico",
        "--name", "DouyinDownloader",
        # Add scripts directory as data
        "--add-data", "src/scripts;src/scripts",
        # Add src/ui for styles etc
        "--add-data", "src/ui;src/ui",
        entry_point
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Đóng gói thành công! File .exe nằm trong thư mục 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Lỗi khi đóng gói: {e}")
    except FileNotFoundError:
        print("\n❌ Không tìm thấy PyInstaller. Vui lòng cài đặt bằng: pip install pyinstaller")

if __name__ == "__main__":
    build()
