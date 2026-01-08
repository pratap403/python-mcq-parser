"""
Helper script to download and setup Poppler for Windows
Poppler is required by pdf2image to convert PDF pages to images
"""
import os
import sys
import urllib.request
import zipfile
import shutil


POPPLER_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
POPPLER_ZIP = "poppler.zip"
POPPLER_DIR = "poppler"


def download_poppler():
    """Download Poppler for Windows"""
    print("📥 Downloading Poppler for Windows...")
    print(f"   URL: {POPPLER_URL}")
    print("   This may take a few minutes...")
    
    try:
        urllib.request.urlretrieve(POPPLER_URL, POPPLER_ZIP)
        print(f"✅ Downloaded to: {POPPLER_ZIP}")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False


def extract_poppler():
    """Extract Poppler zip file"""
    print(f"\n📦 Extracting Poppler...")
    
    try:
        with zipfile.ZipFile(POPPLER_ZIP, 'r') as zip_ref:
            zip_ref.extractall(POPPLER_DIR)
        print(f"✅ Extracted to: {POPPLER_DIR}")
        
        # Find the bin directory
        for root, dirs, files in os.walk(POPPLER_DIR):
            if 'bin' in dirs:
                bin_path = os.path.join(root, 'bin')
                print(f"✅ Poppler binaries found at: {os.path.abspath(bin_path)}")
                return bin_path
        
        return None
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        return None


def main():
    print(f"\n{'='*70}")
    print("Poppler Installer for Windows")
    print(f"{'='*70}\n")
    
    # Check if already exists
    if os.path.exists(POPPLER_DIR):
        print(f"ℹ️  Poppler directory already exists: {POPPLER_DIR}")
        response = input("   Re-download and extract? (y/n): ").lower()
        if response != 'y':
            print("Installation cancelled.")
            return
        shutil.rmtree(POPPLER_DIR)
    
    # Download
    if os.path.exists(POPPLER_ZIP):
        print(f"ℹ️  Poppler zip already exists: {POPPLER_ZIP}")
        response = input("   Re-download? (y/n): ").lower()
        if response == 'y':
            if not download_poppler():
                return
    else:
        if not download_poppler():
            return
    
    # Extract
    bin_path = extract_poppler()
    
    if bin_path:
        print("\n" + "="*70)
        print("✅ Installation Complete!")
        print("="*70)
        print("\n📝 Next Steps:")
        print("="*70)
        print("\n1. Poppler is now installed locally in this directory")
        print(f"2. Binary path: {os.path.abspath(bin_path)}")
        print("\n3. The pdf-auto-ocr-parser.py script will automatically detect it")
        print("\nOR you can set it manually in your Python script:")
        print(f"   poppler_path = r'{os.path.abspath(bin_path)}'")
        print("="*70)
        
        # Clean up zip
        try:
            os.remove(POPPLER_ZIP)
            print(f"\n🗑️  Cleaned up: {POPPLER_ZIP}")
        except:
            pass
    else:
        print("\n❌ Installation failed. Please try again or install manually.")


if __name__ == "__main__":
    main()

