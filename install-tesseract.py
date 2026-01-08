"""
Helper script to download and install Tesseract OCR on Windows
"""
import os
import sys
import urllib.request
import subprocess


TESSERACT_INSTALLER_URL = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
INSTALLER_PATH = "tesseract-installer.exe"


def download_tesseract():
    """Download Tesseract installer"""
    print("📥 Downloading Tesseract OCR installer...")
    print(f"   URL: {TESSERACT_INSTALLER_URL}")
    
    try:
        urllib.request.urlretrieve(TESSERACT_INSTALLER_URL, INSTALLER_PATH)
        print(f"✅ Downloaded to: {INSTALLER_PATH}")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False


def install_tesseract():
    """Run Tesseract installer"""
    print("\n🔧 Running Tesseract installer...")
    print("   Please follow the installation wizard.")
    print("   ⚠️  IMPORTANT: Note the installation path (usually C:\\Program Files\\Tesseract-OCR)")
    
    try:
        subprocess.run([INSTALLER_PATH], check=True)
        print("✅ Installation completed!")
        return True
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def main():
    print(f"\n{'='*70}")
    print("Tesseract OCR Installer for Windows")
    print(f"{'='*70}\n")
    
    # Check if already downloaded
    if os.path.exists(INSTALLER_PATH):
        print(f"ℹ️  Installer already exists: {INSTALLER_PATH}")
        response = input("   Download again? (y/n): ").lower()
        if response == 'y':
            if not download_tesseract():
                return
    else:
        if not download_tesseract():
            return
    
    # Ask to install
    print("\n" + "="*70)
    response = input("Run installer now? (y/n): ").lower()
    if response == 'y':
        install_tesseract()
        
        print("\n" + "="*70)
        print("📝 Next Steps:")
        print("="*70)
        print("1. After installation, you need to add Tesseract to your PATH")
        print("2. The default installation path is: C:\\Program Files\\Tesseract-OCR")
        print("3. Add this to your system PATH environment variable")
        print("\nOR")
        print("\nSet the path in your Python script:")
        print("   import pytesseract")
        print("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        print("="*70)
    else:
        print("Installation cancelled. Run the installer manually when ready:")
        print(f"   {os.path.abspath(INSTALLER_PATH)}")


if __name__ == "__main__":
    main()

