#!/usr/bin/env python3
"""
Tesla Order Status Tracker - Main Application
Web-based Tesla order tracking with automatic browser authentication.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("🚗" * 30)
    print("🚗  TESLA ORDER STATUS TRACKER  🚗")
    print("🚗        Web Interface         🚗") 
    print("🚗" * 30)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import plotly
        import requests
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
            "--quiet"
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False

def launch_app():
    """Launch the Streamlit web application"""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    app_file = script_dir / "streamlit_app.py"
    if not app_file.exists():
        print("❌ Streamlit app not found!")
        return False
    
    print("🚀 Starting Tesla Order Status Tracker...")
    print("📱 Opening web interface at: http://localhost:8501")
    print("🔴 Press Ctrl+C to stop the application")
    print("-" * 50)
    print()
    
    try:
        # Launch Streamlit with optimized settings
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.address", "localhost",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--server.runOnSave", "true",
            "--server.allowRunOnSave", "true"
        ])
        return True
    except KeyboardInterrupt:
        print("\n🔴 Application stopped by user.")
        return True
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return False

def main():
    """Main application entry point"""
    print_banner()
    
    print("Welcome to Tesla Order Status Tracker!")
    print("This tool helps you monitor your Tesla order status and delivery updates")
    print("through an easy-to-use web interface.\n")
    
    # Check dependencies
    if not check_dependencies():
        print("⚠️  Some dependencies are missing.")
        install_choice = input("Would you like to install them now? (y/n): ").strip().lower()
        
        if install_choice == 'y':
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("pip install -r requirements.txt")
                return False
        else:
            print("❌ Cannot proceed without dependencies.")
            return False
    
    print("✅ All dependencies are available!")
    print()
    
    # Launch the application
    proceed = input("🚀 Ready to launch Tesla Order Status Tracker? (y/n): ").strip().lower()
    
    if proceed == 'y':
        return launch_app()
    else:
        print("👋 See you next time!")
        return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
