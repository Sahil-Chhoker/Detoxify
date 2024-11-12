import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from contextlib import suppress
import psutil
from bot.database_manager import DatabaseManager

class YoutubeCrawler:
    def __init__(self, user_id):
        """
        Initialize crawler with database integration
        :param user_id: UUID of the user from users table
        """
        self.user_id = user_id
        self.db = DatabaseManager()

        # Initialize undetected ChromeDriver
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")

        # Initialize the undetected chromedriver
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def check_login_status(self):
        """Check if user is already logged in to YouTube"""
        try:
            self.driver.get("https://www.youtube.com")
            time.sleep(3)

            avatar = self.driver.find_elements(By.CSS_SELECTOR, "button#avatar-btn")
            return len(avatar) > 0
        except Exception as e:
            print(f"Error checking login status: {str(e)}")
            return False

    def manual_login(self):
        """Allow user to manually log in and save session to database"""
        try:
            print("\nManual Login Instructions:")
            print("1. A browser window will open")
            print("2. Please log in with your Google account")
            print("3. After successful login, you'll be redirected to YouTube")
            print(
                "4. Once you see your avatar in the top right, press Enter in this console"
            )

            self.driver.get(
                "https://accounts.google.com/signin/v2/identifier?service=youtube"
            )
            input("\nPress Enter after you have successfully logged in...")

            if self.check_login_status():
                print("Login successful!")
                # Save session to database
                cookies = self.driver.get_cookies()
                user_agent = self.driver.execute_script("return navigator.userAgent")
                if self.db.save_session(self.user_id, cookies, user_agent):
                    print("Session saved to database!")
                return True
            else:
                print("Login verification failed. Please try again.")
                return False

        except Exception as e:
            print(f"Manual login failed: {str(e)}")
            return False

    def load_session(self):
        """Load session from database"""
        try:
            cookies, user_agent = self.db.load_session(self.user_id)
            if cookies:
                # Visit YouTube first (cookies need a matching domain)
                self.driver.get("https://www.youtube.com")

                # Add the cookies to the current session
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception:
                        continue

                # Refresh to apply cookies
                self.driver.refresh()
                time.sleep(3)

                # Verify login status
                if self.check_login_status():
                    return True
                else:
                    # Invalidate session if login failed
                    self.db.invalidate_session(self.user_id)
            return False
        except Exception as e:
            print(f"Error loading session: {str(e)}")
            return False

    def search_query(self, query):
        """Search for a given query on YouTube"""
        try:
            self.driver.get("https://www.youtube.com")
            time.sleep(2)

            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )

            # Type with random delays
            search_box.clear()
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))

            time.sleep(random.uniform(0.5, 1.0))
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            return True
        except Exception as e:
            print(f"Search failed: {str(e)}")
            return False

    def watch_videos(self, num_videos=5, watch_time_range=(30, 120)):
        """Watch a specified number of videos from search results"""
        try:
            video_links = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a#video-title"))
            )

            for i in range(min(num_videos, len(video_links))):
                time.sleep(random.uniform(1, 3))
                video_links[i].click()

                watch_time = random.randint(watch_time_range[0], watch_time_range[1])
                print(f"Watching video {i+1} for {watch_time} seconds...")

                for _ in range(watch_time // 10):
                    time.sleep(10)
                    if random.random() < 0.3:
                        self.driver.execute_script(
                            f"window.scrollTo(0, {random.randint(100, 500)});"
                        )

                self.driver.back()
                time.sleep(random.uniform(2, 4))

                video_links = self.wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "a#video-title")
                    )
                )

            return True
        except Exception as e:
            print(f"Video watching failed: {str(e)}")
            return False

    def _force_kill_chrome_processes(self):
        """Force kill any remaining Chrome processes"""
        chrome_process_names = ["chrome.exe", "chromedriver.exe", "chromium.exe"]

        try:
            # Windows specific process killing
            if os.name == "nt":  
                with suppress(Exception):
                    os.system("taskkill /f /im chrome.exe")
                    os.system("taskkill /f /im chromedriver.exe")

            # Cross-platform process killing using psutil
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if (
                        proc.info["name"]
                        and proc.info["name"].lower() in chrome_process_names
                    ):
                        proc.kill()
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue
                except Exception as e:
                    print(f"Warning: Error killing process: {str(e)}")

            # Unix-like systems (Linux/Mac)
            if os.name != "nt":
                with suppress(Exception):
                    os.system("pkill -f chrome")
                    os.system("pkill -f chromedriver")

        except Exception as e:
            print(f"Warning: Error during force kill: {str(e)}")

    def _graceful_close(self):
        """Attempt to close the browser gracefully"""
        try:
            # Close all windows first
            if self.driver.window_handles:
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                    time.sleep(0.5)  

            # Execute quit JavaScript
            with suppress(Exception):
                self.driver.execute_script("window.onbeforeunload = null;")

            # Quit the driver
            self.driver.quit()
            return True
        except Exception as e:
            print(f"Warning: Graceful close failed: {str(e)}")
            return False

    def close(self):
        """
        Close the browser using multiple fallback methods to ensure clean shutdown
        """
        if not hasattr(self, "driver") or not self.driver:
            return

        try:
            print("Attempting to close browser...")

            # Step 1: Try graceful shutdown with retry
            for attempt in range(3):
                try:
                    if self._graceful_close():
                        print("Browser closed successfully")
                        break
                except Exception:
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(1)

            # Step 2: If driver still exists, try force quit
            if hasattr(self, "driver") and self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    print(f"Warning: Force quit failed: {str(e)}")

            # Step 3: Kill any remaining Chrome processes
            self._force_kill_chrome_processes()

            # Step 4: Clear all references
            time.sleep(1)  

        except Exception as e:
            print(f"Warning: Error during cleanup: {str(e)}")

        finally:
            try:
                # Clear the driver reference
                self.driver = None

                # Optional: Garbage collection
                import gc

                gc.collect()

                print("Cleanup completed")
            except Exception as e:
                print(f"Warning: Final cleanup error: {str(e)}")
