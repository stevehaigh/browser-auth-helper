# Browser Authentication Helper

A Python application that automates the process of capturing authentication data from websites that require manual login, then uses that data to make authenticated requests and download protected content.

## 🚀 Features

- **Automated Browser Setup**: Automatically downloads and configures ChromeDriver
- **Manual Login Support**: Opens a browser window for manual authentication
- **Session Data Capture**: Captures cookies, localStorage, and sessionStorage
- **Session Persistence**: Saves and reloads authentication data for future use
- **Authenticated Requests**: Uses captured session data to make authenticated HTTP requests
- **Content Download**: Downloads protected pages using authenticated sessions
- **Page Preview**: View downloaded content in browser or text preview
- **Cross-Platform**: Works on macOS, Windows, and Linux

## 📋 Requirements

- Python 3.7+
- Chrome browser installed
- Internet connection

## 🛠️ Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd browser-auth-helper
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install requests selenium webdriver-manager
   ```

3. **Verify Chrome is installed:**
   The script will automatically download the appropriate ChromeDriver version.

## 🎯 Quick Start

### Example: Accessing GitHub Profile Settings

Here's a practical example using GitHub's protected profile settings page:

1. **Run the script:**
   ```bash
   python browser_auth.py
   ```

2. **Enter the target URL:**
   ```
   Enter the URL of the site requiring authentication: https://github.com/settings/profile
   ```
   - The script will open GitHub's login page
   - This page requires authentication to access

3. **Complete manual login:**
   - A Chrome browser window will open to GitHub's login page
   - Log in with your GitHub credentials
   - Navigate to your profile settings to verify login worked
   - Press ENTER in the terminal when ready

4. **Download protected content:**
   - Enter the URL: `https://github.com/settings/profile`
   - Choose to view in browser or as text preview
   - The tool will download your authenticated profile settings page

### General Usage Steps

1. **Run the script:**
   ```bash
   python browser_auth.py
   ```

2. **Enter the target URL:**
   - Provide the URL of the site requiring authentication
   - The script will add `https://` if not provided

3. **Complete manual login:**
   - A Chrome browser window will open
   - Log in manually through the website's interface
   - Navigate to a protected page to verify login
   - Press ENTER in the terminal when ready

4. **Download protected content:**
   - Enter the URL of the content you want to download
   - Choose to view in browser or as text preview

## 🔧 Advanced Usage

### Using as a Python Module

```python
from browser_auth import BrowserAuthenticator

# Initialize the authenticator
with BrowserAuthenticator("https://example.com") as auth:
    # Perform manual login
    if auth.manual_login():
        # Capture session data
        session_data = auth.capture_session_data()
        
        # Save for future use
        auth.save_session_data(session_data)
        
        # Configure requests session
        auth.configure_requests_session(session_data)
        
        # Test authentication
        response = auth.test_authenticated_access()
        
        # Download protected content
        content = auth.download_protected_page("https://example.com/protected")
```

### Headless Mode

```python
# Run browser in headless mode (no UI)
auth.setup_browser(headless=True)
```

### Custom Configuration

```python
# Custom session file location
auth = BrowserAuthenticator(
    target_url="https://example.com",
    cookies_file="custom_session.json"
)

# Wait for specific element after login
auth.manual_login(
    wait_for_element="[data-test='dashboard']",
    max_wait_time=600  # 10 minutes
)
```

## 📁 File Structure

```
browser-auth-helper/
├── browser_auth.py              # Main application
├── requirements.txt             # Package dependencies
├── session_cookies.json        # Saved authentication data
├── downloaded_page.html         # Downloaded content
└── README.md                   # This file
```

## 🔒 Session Data

The application captures and stores:

- **Cookies**: All cookies from the authenticated session
- **Local Storage**: Browser localStorage data
- **Session Storage**: Browser sessionStorage data
- **Domain Information**: Target domain and current URL
- **Timestamps**: When the session was captured

Session data is stored in JSON format with human-readable timestamps for easy inspection.

## 🛡️ Security Considerations

- **Sensitive Data**: Session files contain authentication tokens and cookies
- **File Permissions**: Ensure session files have appropriate access restrictions
- **Clean Up**: Regularly clean up old session files
- **HTTPS Only**: Use only with HTTPS websites for security
- **Private Networks**: Be cautious when using on shared or public networks

## 🔍 Troubleshooting

### Debug Mode

Add debug output to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚨 Error Handling

The application includes comprehensive error handling for:

- Network connectivity issues
- Browser setup failures
- Authentication timeouts
- File I/O operations
- Invalid URLs
- User interruptions (Ctrl+C)

### Session Data Validation

The `save_session_data()` method includes robust validation:

- **Input Validation**: Checks for required fields (domain, current_url, timestamp, cookies)
- **File Verification**: Confirms session file was written successfully
- **Error Recovery**: Provides detailed error messages and debug information
- **Return Values**: Returns `True` for success, `False` for failure for programmatic use

Example validation output:
```
✅ Session data saved to: session_cookies.json
📊 Saved 15 cookies
```

Or if validation fails:
```
❌ Missing required field in session data: cookies
❌ Failed to write session data to: session_cookies.json
```

## 📊 Use Cases

- **Web Scraping**: Access protected content after authentication
- **API Testing**: Capture session tokens for API testing
- **Content Archival**: Download protected documents or pages
- **Automation**: Integrate with larger automation workflows
- **Research**: Access gated content for legitimate research purposes

## ⚡ Performance Tips

- **Reuse Sessions**: Save and reuse session data to avoid repeated logins
- **Batch Operations**: Download multiple pages in a single session
- **Headless Mode**: Use headless mode for better performance
- **Connection Pooling**: The requests session automatically handles connection pooling

## 🤝 Contributing

Contributions are welcome! Please consider:

- Adding support for other browsers (Firefox, Safari)
- Implementing proxy support
- Adding rate limiting features
- Improving error handling
- Adding unit tests

## 📄 License

This project is intended for educational and legitimate testing purposes. Users are responsible for complying with website terms of service and applicable laws.

## 🔗 Dependencies

- **[requests](https://requests.readthedocs.io/)**: HTTP library for making authenticated requests
- **[selenium](https://selenium-python.readthedocs.io/)**: Web browser automation
- **[webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)**: Automatic ChromeDriver management

## 📝 Changelog

### v1.0
- **🚀 Initial Release**: Core authentication and download features
- Support for Chrome browser automation
- Session data persistence
- Protected content download
- Browser and text preview options

---

## 🤖 AI Development Disclosure

This code was developed with assistance from AI tools:
- **GitHub Copilot with Claude Sonnet 4 (Agent mode)**: Used for code generation, debugging, and documentation

While AI tools assisted in development, all code has been reviewed, tested, and validated for functionality and security.

---

**⚠️ Disclaimer**: This tool is for educational and testing purposes only. Users must comply with website terms of service and applicable laws. The authors are not responsible for misuse of this software.
