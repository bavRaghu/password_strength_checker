import threading
import unittest

from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import app, assess_password


class PasswordCheckerSeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.server = make_server("127.0.0.1", 5003, app)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://127.0.0.1:5003"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()
        if hasattr(cls, "server"):
            cls.server.shutdown()
        if hasattr(cls, "server_thread"):
            cls.server_thread.join(timeout=5)

    def setUp(self):
        self.driver.get(self.base_url)

    def test_homepage_loads(self):
        self.assertIn("Password", self.driver.title)
        self.assertTrue(self.driver.find_element(By.ID, "password").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "toggle").is_displayed())

    def test_all_three_pages_load(self):
        for path in ("/", "/tips", "/about"):
            response = self.driver.get(self.base_url + path)
            self.assertIn("PassCheck", self.driver.page_source)

    def test_weak_password(self):
        self.driver.find_element(By.ID, "password").send_keys("password")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        result = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "result")))
        self.assertIn("Weak", result.text)

    def test_strong_password(self):
        self.driver.find_element(By.ID, "password").send_keys("R!ver-Maple-Cloud-739")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        result = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "result")))
        self.assertIn("Strong", result.text)

    def test_show_hide_password(self):
        password = self.driver.find_element(By.ID, "password")
        toggle = self.driver.find_element(By.ID, "toggle")
        self.assertEqual(password.get_attribute("type"), "password")
        toggle.click()
        self.assertEqual(password.get_attribute("type"), "text")
        self.assertEqual(toggle.text, "Hide")
        toggle.click()
        self.assertEqual(password.get_attribute("type"), "password")
        self.assertEqual(toggle.text, "Show")

    def test_password_assessment(self):
        self.assertEqual(assess_password("password")["label"], "Weak")
        self.assertEqual(assess_password("R!ver-Maple-Cloud-739")["label"], "Strong")


if __name__ == "__main__":
    unittest.main(verbosity=2)
