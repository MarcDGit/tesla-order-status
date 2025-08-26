# 🚗 Tesla Order Status Tracker - Web Interface

A modern, user-friendly web application to track and monitor your Tesla order status with automatic change detection and detailed vehicle information display.

## 🌟 Overview

This tool provides a beautiful web interface to monitor your Tesla order status by connecting to Tesla's official API. It tracks changes over time, provides detailed vehicle configuration information, and offers an intuitive dashboard for easy monitoring.

### ✨ Key Features

- **🔐 Browser-Based Authentication**: Secure Tesla login with copy-paste workflow
- **📊 Interactive Dashboard**: Visual order status with real-time metrics
- **📈 Change History Visualization**: Interactive charts and timeline views
- **🔍 Searchable Option Code Database**: Comprehensive Tesla option code reference
- **💾 Privacy Controls**: Hide sensitive data for sharing screenshots
- **🔄 Auto-Refresh**: Automatic data updates and change detection
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **🎨 Modern UI**: Beautiful, intuitive interface built with Streamlit

## 📋 Requirements

- Python 3.7 or higher
- Internet connection for API access
- Tesla account with an active order
- Modern web browser

## 🚀 Quick Start

### 1. Download the Project

```bash
git clone https://github.com/MarcDGit/tesla-order-status.git
cd tesla-order-status
```

Or download as ZIP: https://github.com/MarcDGit/tesla-order-status/archive/refs/heads/main.zip

### 2. Launch the Application

**Simple one-command startup:**
```bash
python3 app.py
```

The application will:
- ✅ Check and install dependencies automatically
- 🚀 Launch the web interface in your browser
- 📱 Open at `http://localhost:8501`

**Alternative manual launch:**
```bash
# Install dependencies first (optional)
pip install -r requirements.txt

# Launch directly
streamlit run streamlit_app.py
```

### 3. Authenticate with Tesla

1. **Click "Open Tesla Login Page"** in the web interface
2. **Log in** with your Tesla account credentials
3. **Copy the redirect URL** from your browser (you'll see a "Page Not Found" - this is normal!)
4. **Paste the URL** into the Streamlit interface
5. **Click "Complete Authentication"**

🎉 You're ready to track your Tesla order!

## 📸 Screenshots

### 🏠 Welcome & Authentication
- Clean, guided authentication process
- Step-by-step instructions
- Visual feedback and progress indicators

### 📊 Order Dashboard
- Real-time order status overview
- Vehicle configuration details
- Delivery timeline and progress
- Interactive metrics and cards

### 📈 Change History
- Timeline visualization of order changes
- Interactive charts and graphs
- Detailed change logs with timestamps
- Recent changes highlighted

### 🔍 Option Codes Reference
- Searchable database of Tesla option codes
- Real-time filtering and search
- Comprehensive code descriptions
- Easy-to-browse interface

## 🔐 Security & Privacy

### 🛡️ Security Features
- **Direct Tesla Authentication**: Login happens directly with Tesla
- **No Credential Storage**: Your password never touches our application
- **Local Data Processing**: All data stays on your computer
- **Official Tesla API**: Uses only Tesla's official API endpoints
- **Token Security**: Authentication tokens stored locally and encrypted

### 🔒 Privacy Controls
- **Hide Sensitive Data**: Toggle to hide Order ID, VIN, and personal info
- **Local Storage**: No data sent to third parties
- **Data Control**: You control all stored data and can clear it anytime
- **Sharing Mode**: Privacy-friendly mode for screenshots

## 📊 Data Files

The application creates several files in your project directory:

- **`tesla_tokens.json`**: Stores authentication tokens (created after first login)
- **`tesla_orders.json`**: Caches current order information
- **`tesla_order_history.json`**: Maintains complete change history

These files are stored locally on your machine and never shared.

## ⚙️ Configuration

### Option Code Database
The `option-codes/` directory contains comprehensive Tesla option code definitions:
- **`000_teslahunt.json`**: Main option code database from TeslaHunt
- **`050_directlease.json`**: Direct lease specific codes
- **`100_options.json`**: Custom codes and community overrides

Files are loaded alphabetically, with later files overriding earlier ones for duplicate codes.

### Web Interface Settings
Access configuration through the "⚙️ Configuration" page:
- Privacy settings (show/hide sensitive data)
- Data refresh controls
- Authentication management
- File status overview

## 🛠️ Project Structure

### Core Application Files
- **`app.py`**: Main launcher script (use this to start!)
- **`streamlit_app.py`**: Complete web interface application
- **`tesla_order_status.py`**: Core order tracking functionality (deprecated CLI)
- **`requirements.txt`**: Python dependencies
- **`tesla_stores.py`**: Tesla store and delivery center database
- **`update_check.py`**: Automatic update checker

### Option Code Databases
- **`option-codes/`**: Directory containing Tesla option code definitions
  - Comprehensive database covering all Tesla models and configurations
  - Regular updates from community contributors
  - Searchable through the web interface

## 🆘 Troubleshooting

### Common Issues

**🌐 Web Interface**
- **Port in use**: Streamlit will automatically find an available port
- **Browser doesn't open**: Manually navigate to `http://localhost:8501`
- **Page won't load**: Check that Python and Streamlit are running

**🔐 Authentication**
- **"Page Not Found" error**: This is normal! Just copy the URL
- **Authentication fails**: Make sure you copied the complete redirect URL
- **Token expired**: Use "Sign Out" button and re-authenticate

**📦 Dependencies**
- **Missing modules**: Run `pip install -r requirements.txt`
- **Old Python version**: Upgrade to Python 3.7 or higher
- **Permission errors**: Try using `python3 -m pip install` instead

### Getting Help

If you need assistance:

1. **Check Issues**: [GitHub Issues](https://github.com/MarcDGit/tesla-order-status/issues)
2. **Create Issue**: Provide detailed information about your problem
3. **Community Support**: [Tesla Forum Discussion](https://tff-forum.de/u/chrisi51/summary)

When reporting issues, include:
- Operating system (Windows, macOS, Linux)
- Python version (`python3 --version`)
- Error messages (full stack trace if available)
- Steps to reproduce the problem

## 🤝 Credits & Acknowledgments

### Original Work
- **[niklaswa](https://github.com/niklaswa)** - Original [tesla-order-status](https://github.com/niklaswa/tesla-order-status) CLI script

### Enhanced Version
- **[chrisi51](https://github.com/chrisi51)** - Enhanced CLI version and previous maintainer
  - Enhanced option code database and change detection
  - Improved delivery center information and history tracking
  - Multiple output modes and clipboard integration
  - Advanced change history and formatting features
- **[MarcDGit](https://github.com/MarcDGit)** - Current maintainer with Streamlit web interface
  - Complete Streamlit web application and dashboard
  - Browser-based authentication workflow
  - Interactive visualizations and modern UI
- **Repository**: https://github.com/MarcDGit/tesla-order-status
- **Support**: [Tesla Forum Profile](https://tff-forum.de/u/chrisi51/summary)

### Data Sources
- **TeslaHunt**: Comprehensive option code database
- **Direct Lease**: Leasing-specific option codes
- **Community Contributors**: Ongoing option code updates and feature improvements

## 💝 Support the Project

If you find this tool helpful:

- **⭐ Star the Repository**: Help others discover this tool
- **🚗 Tesla Referral**: Use [MarcDGit's Tesla referral link](https://www.tesla.com/referral/marc79126) when ordering
- **🐛 Report Issues**: Help improve the tool by reporting bugs
- **💡 Suggest Features**: Share ideas for new functionality
- **🤝 Contribute**: Submit code improvements or option code updates

## 📄 License

This project is open source. Please respect Tesla's API terms of service and use responsibly.

## 🔄 Recent Updates

### 🆕 Web Interface Version (Current)
- **🌐 Complete Web Interface**: Beautiful, modern dashboard
- **🔐 Browser Authentication**: Streamlined Tesla login process
- **📊 Interactive Visualizations**: Charts, graphs, and timeline views
- **📱 Mobile Responsive**: Works on all devices
- **🎨 Modern Design**: Intuitive, user-friendly interface
- **⚡ Auto-Refresh**: Real-time updates and change detection
- **🔍 Advanced Search**: Searchable option code database
- **⚙️ Configuration UI**: Web-based settings management

### 📈 Enhanced Features
- Comprehensive Tesla store location database
- Advanced change detection and history tracking
- Privacy controls for sharing
- Automatic update checking
- Better error handling and user guidance
- Real-time data caching and refresh

---

## 🚨 Important Notes

- **No Tesla Affiliation**: This tool is not affiliated with Tesla, Inc.
- **Official API**: Uses Tesla's official API endpoints only
- **Your Credentials**: Requires your Tesla account for authentication
- **Terms of Service**: Use in accordance with Tesla's terms of service
- **At Your Own Risk**: Use at your own discretion

---

**🌟 Enjoy tracking your Tesla order with this modern, user-friendly interface!**