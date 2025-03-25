import threading
import logging
import random
import string
import time
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('token-refresh-worker-logger')


def generate_random_text(length=100):
    """Generate a random string of specified length."""
    if length <= 0:
        return ""

    # Define the character pool (letters, digits, and punctuation if needed)
    char_pool = string.ascii_letters + string.digits + string.punctuation

    # Generate random text of given length
    random_text = ''.join(random.choices(char_pool, k=length))
    return random_text


class TokenRefreshWorker():
    def __init__(self):
        self.refresh_interval = 55
        self.access_token = None
        self.token_expiry = None
        self.token_thread = None
        self._stop_token_refresh = threading.Event()
        self.get_token()
        self.start_token_refresh()


    def get_token(self):
        """
        Set dummy token
        """

        try:
            
            self.access_token = generate_random_text(100)
            print('random access token',self.access_token)
            # Calculate token expiry time (default is 1 minute = 60 seconds)
            expires_in = 10
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info(f"Token refreshed successfully. Expires in {expires_in} seconds.")
            return self.access_token
            
        except Exception as e:
            # Handle any exception that occurs
            return {"error": f"Failed to get token: {str(e)}"}
    
    def start_token_refresh(self):
        """
        Start the token refresh background thread.
        """
        if self.token_thread is None or not self.token_thread.is_alive():
            self._stop_token_refresh.clear()
            self.token_thread = threading.Thread(target=self._token_refresh_worker)
            self.token_thread.daemon = True
            self.token_thread.start()
            logger.info("Token refresh thread started")

    def _token_refresh_worker(self):
        """
        Background worker that refreshes the token periodically.
        """
        logger.info('Token refresh worker block')
        while not self._stop_token_refresh.is_set():
            logger.info('Token refresh worker block checking')
            # Check if token needs refresh (if it's expired or about to expire)
            if self.token_expiry and datetime.now() > (self.token_expiry - timedelta(seconds=5)):
                try:
                    self.get_token()
                except Exception as e:
                    logger.error(f"Failed to refresh token in background thread: {str(e)}")
            
            # Sleep for a short period before checking again
            time.sleep(1)

    def stop_token_refresh(self):
        """
        Stop the token refresh background thread.
        """
        if self.token_thread and self.token_thread.is_alive():
            self._stop_token_refresh.set()
            self.token_thread.join(timeout=2)
            logger.info("Token refresh thread stopped")

if __name__ == "__main__":
    client = TokenRefreshWorker()
    try:
        # Execute the query
        result = client.get_token()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down client...")
        client.stop_token_refresh()
    # client.get_token()