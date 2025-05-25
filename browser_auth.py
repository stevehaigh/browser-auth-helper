#!/usr/bin/env python3
"""
Browser Authentication Helper

This application opens a browser window, allows manual login, 
captures cookies and session data, then uses that data to make 
authenticated requests to download protected content.
"""

import requests
import time
import webbrowser
import os
import json
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class BrowserAuthenticator:
    def __init__(self, target_url, cookies_file="session_cookies.json"):
        """
        Initialize the browser authenticator.
        
        Args:
            target_url (str): The URL of the site that requires authentication
            cookies_file (str): File to save/load cookies from
        """
        self.target_url = target_url
        self.cookies_file = cookies_file
        self.driver = None
        self.session = requests.Session()
        
    def setup_browser(self, headless=False):
        """
        Set up the Chrome browser with appropriate options.
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument("--headless")
            
            # Essential options for better compatibility
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to appear more like a real browser
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Automatically download and install ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Browser setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up browser: {e}")
            print("💡 Make sure Chrome is installed and try again")
            raise

    def manual_login(self, login_url=None, wait_for_element=None, max_wait_time=300):
        """
        Open browser for manual login and wait for user to complete authentication.
        
        Args:
            login_url (str): Optional specific login URL (defaults to target_url)
            wait_for_element (str): Optional CSS selector to wait for after login
            max_wait_time (int): Maximum time to wait for login completion (seconds)
        """
        try:
            if not self.driver:
                self.setup_browser()
            
            login_url = login_url or self.target_url
            print(f"🌐 Opening browser to: {login_url}")
            self.driver.get(login_url)
            
            print("\n" + "="*60)
            print("📋 MANUAL LOGIN INSTRUCTIONS")
            print("="*60)
            print("1. Complete the login process in the browser window")
            print("2. Navigate to any protected page to verify login")
            print("3. When ready, press ENTER in this terminal to continue")
            print("4. Or type 'quit' to abort")
            print("="*60)
            
            # Wait for user to complete login
            start_time = time.time()
            while True:
                try:
                    user_input = input("\nPress ENTER when login is complete (or 'quit' to abort): ").strip().lower()
                    
                    if user_input == 'quit':
                        print("❌ Login aborted by user")
                        return False
                    
                    # Check if we've exceeded max wait time
                    if time.time() - start_time > max_wait_time:
                        print(f"⏰ Maximum wait time ({max_wait_time}s) exceeded")
                        return False
                    
                    # Show current URL for debugging
                    current_url = self.driver.current_url
                    print(f"📍 Current URL: {current_url}")
                    
                    # Optional: Wait for specific element that indicates successful login
                    if wait_for_element:
                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                            )
                            print(f"✅ Found expected element: {wait_for_element}")
                        except:
                            print(f"⚠️  Expected element not found: {wait_for_element}")
                            continue
                    
                    # Ask user to confirm login is complete
                    confirm = input("Is login complete and you're on a protected page? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        break
                    
                except (KeyboardInterrupt, EOFError):
                    print("\n❌ Login interrupted by user")
                    return False
            
            print("✅ Login process completed")
            return True
            
        except Exception as e:
            print(f"❌ Error during manual login: {e}")
            return False
    
    def capture_session_data(self):
        """
        Capture cookies and other session data from the browser.
        
        Returns:
            dict: Session data including cookies, headers, etc.
        """
        if not self.driver:
            print("❌ No browser session available")
            return None
        
        # Get all cookies
        cookies = self.driver.get_cookies()
        
        # Get current URL and domain
        current_url = self.driver.current_url
        parsed_url = urlparse(current_url)
        domain = parsed_url.netloc
        
        # Capture local storage and session storage
        local_storage = {}
        session_storage = {}
        
        try:
            local_storage = self.driver.execute_script("return window.localStorage;") or {}
        except:
            print("⚠️  Could not access localStorage")
        
        try:
            session_storage = self.driver.execute_script("return window.sessionStorage;") or {}
        except:
            print("⚠️  Could not access sessionStorage")
        
        session_data = {
            'cookies': cookies,
            'domain': domain,
            'current_url': current_url,
            'local_storage': local_storage,
            'session_storage': session_storage,
            'timestamp': time.time()
        }
        
        print(f"📦 Captured {len(cookies)} cookies from {domain}")
        return session_data
    
    def save_session_data(self, session_data):
        """
        Save session data to JSON file.
        
        Args:
            session_data (dict): Session data to save
        """
        if not session_data:
            print("❌ No session data to save")
            return False
            
        try:
            # Validate required fields
            required_fields = ['domain', 'current_url', 'timestamp', 'cookies']
            for field in required_fields:
                if field not in session_data:
                    print(f"❌ Missing required field in session data: {field}")
                    return False
            
            # Convert to a readable format
            readable_data = {
                'domain': session_data['domain'],
                'current_url': session_data['current_url'],
                'timestamp': session_data['timestamp'],
                'timestamp_readable': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session_data['timestamp'])),
                'cookies': [
                    {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie['path'],
                        'secure': cookie['secure'],
                        'httpOnly': cookie.get('httpOnly', False),
                        'sameSite': cookie.get('sameSite', 'None')
                    }
                    for cookie in session_data['cookies']
                ],
                'local_storage': session_data.get('local_storage', {}),
                'session_storage': session_data.get('session_storage', {})
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.cookies_file)), exist_ok=True)
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(readable_data, f, indent=2, ensure_ascii=False)
            
            # Verify the file was written
            if os.path.exists(self.cookies_file) and os.path.getsize(self.cookies_file) > 0:
                print(f"💾 Session data saved to: {self.cookies_file}")
                print(f"📊 Saved {len(readable_data['cookies'])} cookies")
                return True
            else:
                print(f"❌ Failed to write session data to: {self.cookies_file}")
                return False
            
        except Exception as e:
            print(f"❌ Error saving session data: {e}")
            import traceback
            print(f"🔍 Debug info: {traceback.format_exc()}")
            return False
    
    def load_session_data(self):
        """
        Load session data from JSON file.
        
        Returns:
            dict: Loaded session data or None if file doesn't exist
        """
        if not os.path.exists(self.cookies_file):
            print(f"⚠️  Session file not found: {self.cookies_file}")
            return None
        
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            print(f"📂 Session data loaded from: {self.cookies_file}")
            
            # Show when the session was saved
            if 'timestamp_readable' in session_data:
                print(f"📅 Session saved on: {session_data['timestamp_readable']}")
            
            return session_data
        except Exception as e:
            print(f"❌ Error loading session data: {e}")
            return None
    
    def configure_requests_session(self, session_data):
        """
        Configure the requests session with captured cookies and headers.
        
        Args:
            session_data (dict): Session data containing cookies
        """
        if not session_data:
            print("❌ No session data provided")
            return False
        
        # Add cookies to requests session
        for cookie in session_data['cookies']:
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie['domain'],
                path=cookie['path']
            )
        
        # Set essential headers to match browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        print(f"🔧 Requests session configured with {len(session_data['cookies'])} cookies")
        return True
    
    def test_authenticated_access(self, test_url=None):
        """
        Test if we can access a protected page using the captured session.
        
        Args:
            test_url (str): URL to test (defaults to target_url)
        
        Returns:
            requests.Response: Response object or None if failed
        """
        test_url = test_url or self.target_url
        print(f"🧪 Testing authenticated access to: {test_url}")
        
        try:
            response = self.session.get(test_url, timeout=30)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📏 Response Size: {len(response.content)} bytes")
            
            # Check for common indicators of successful authentication
            content_lower = response.text.lower()
            
            # Common signs of failed authentication
            auth_fail_indicators = [
                'login', 'sign in', 'unauthorized', 'access denied',
                'please log in', 'authentication required', 'session expired'
            ]
            
            # Check if response indicates auth failure
            auth_failed = any(indicator in content_lower for indicator in auth_fail_indicators)
            
            if response.status_code == 200 and not auth_failed:
                print("✅ Authentication appears successful!")
                return response
            elif response.status_code in [401, 403]:
                print("❌ Authentication failed (HTTP 401/403)")
                return None
            elif auth_failed:
                print("⚠️  Response contains login-related content (possible auth failure)")
                return response  # Return anyway for inspection
            else:
                print(f"⚠️  Unexpected response (Status: {response.status_code})")
                return response
                
        except Exception as e:
            print(f"❌ Error testing authenticated access: {e}")
            return None
    
    def download_protected_page(self, url, output_file="downloaded_page.html"):
        """
        Download a protected page using the authenticated session.
        
        Args:
            url (str): URL to download
            output_file (str): File to save content to
        
        Returns:
            str: Page content or None if failed
        """
        print(f"📥 Downloading protected page: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Page saved to: {output_file}")
                
                print(f"✅ Downloaded {len(content)} characters")
                return content
            else:
                print(f"❌ Download failed (Status: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading page: {e}")
            return None
    
    def open_page_in_browser(self, file_path):
        """
        Open a downloaded page in the default browser.
        
        Args:
            file_path (str): Path to the HTML file to open
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            abs_path = os.path.abspath(file_path)
            
            if not os.path.exists(abs_path):
                print(f"❌ File not found: {abs_path}")
                return False
            
            print(f"🌐 Opening page in browser: {abs_path}")
            file_url = f"file://{abs_path}"
            webbrowser.open(file_url)
            print("✅ Page opened in browser")
            return True
            
        except Exception as e:
            print(f"❌ Error opening page in browser: {e}")
            return False
    
    def close_browser(self):
        """Close the browser if it's open."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("🔒 Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure browser is closed."""
        self.close_browser()


def main():
    """
    Example usage of the BrowserAuthenticator.
    """
    print("🔐 Browser Authentication Helper")
    print("=" * 50)
    
    # Get target URL from user
    try:
        target_url = input("Enter the URL that requires authentication: ").strip()
        
        if not target_url:
            print("❌ No URL provided, exiting")
            return
        
        # Basic URL validation
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
            print(f"💡 Added https:// prefix: {target_url}")
        
    except (KeyboardInterrupt, EOFError):
        print("\n❌ Input interrupted, exiting")
        return
    
    # Initialize authenticator
    try:
        with BrowserAuthenticator(target_url) as auth:
            
            # Check if we have saved session data
            session_data = auth.load_session_data()
            
            if session_data:
                print(f"🔍 Found existing session data from {session_data['domain']}")
                try:
                    use_existing = input("Use existing session? (y/n): ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    print("\n❌ Input interrupted, exiting")
                    return
                
                if use_existing in ['y', 'yes']:
                    auth.configure_requests_session(session_data)
                    response = auth.test_authenticated_access()
                    
                    if response and response.status_code == 200:
                        print("✅ Existing session is still valid!")
                        
                        try:
                            test_url = input(f"Enter URL to download (or press ENTER for {target_url}): ").strip()
                            test_url = test_url or target_url
                        except (KeyboardInterrupt, EOFError):
                            print("\n❌ Input interrupted, exiting")
                            return
                        
                        content = auth.download_protected_page(test_url)
                        
                        if content:
                            try:
                                view_option = input("How would you like to view the page? (b)rowser / (t)ext preview: ").strip().lower()
                            except (KeyboardInterrupt, EOFError):
                                print("\n❌ Input interrupted, exiting")
                                return
                            
                            if view_option in ['b', 'browser']:
                                auth.open_page_in_browser("downloaded_page.html")
                            else:
                                print(f"📄 Page preview (first 500 chars):")
                                print("-" * 50)
                                print(content[:500])
                                if len(content) > 500:
                                    print("...")
                                print("-" * 50)
                        
                        return
                    else:
                        print("❌ Existing session is no longer valid, need to re-authenticate")
            
            # Perform manual login
            print("\n🚀 Starting manual login process...")
            
            if auth.manual_login():
                session_data = auth.capture_session_data()
                
                if session_data:
                    auth.save_session_data(session_data)
                    auth.configure_requests_session(session_data)
                    response = auth.test_authenticated_access()
                    
                    if response:
                        print("🎉 Authentication successful!")
                        
                        try:
                            test_url = input(f"Enter URL to download (or press ENTER for {target_url}): ").strip()
                            test_url = test_url or target_url
                        except (KeyboardInterrupt, EOFError):
                            print("\n❌ Input interrupted, exiting")
                            return
                        
                        content = auth.download_protected_page(test_url)
                        
                        if content:
                            try:
                                view_option = input("How would you like to view the page? (b)rowser / (t)ext preview: ").strip().lower()
                            except (KeyboardInterrupt, EOFError):
                                print("\n❌ Input interrupted, exiting")
                                return
                            
                            if view_option in ['b', 'browser']:
                                auth.open_page_in_browser("downloaded_page.html")
                            else:
                                print(f"📄 Page preview (first 500 chars):")
                                print("-" * 50)
                                print(content[:500])
                                if len(content) > 500:
                                    print("...")
                                print("-" * 50)
                    else:
                        print("❌ Authentication test failed")
                else:
                    print("❌ Failed to capture session data")
            else:
                print("❌ Manual login failed or was cancelled")
                
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Try running the script again or check your internet connection")


if __name__ == "__main__":
    main()
