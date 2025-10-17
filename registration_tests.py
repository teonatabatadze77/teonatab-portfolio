import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_and_click_register():
	"""Open https://invu.ge/thenn and click the //a[@href="/register"] element.

	Uses webdriver-manager to obtain a matching ChromeDriver. Prints status to stdout.
	"""
	# Create a Chrome webdriver (will download driver if needed)
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
	wait = WebDriverWait(driver, 15)
	try:
		print("Opening https://invu.ge/thenn")
		driver.get("https://invu.ge/thenn")

		# Wait until the link with href=/register is clickable and click it
		print("Waiting for register link (//a[@href='/register'])...")
		register_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/register']")))
		print("Clicking register link...")
		register_link.click()

		# Wait for navigation (URL contains /register) so we know click worked
		wait.until(EC.url_contains("/register"))
		print("Navigation complete. Current URL:", driver.current_url)

		# Now try to fill the registration form. We'll try several locator strategies
		# because different sites use different attributes (name, id, type, placeholder).
		def try_find(driver, by, value, timeout=5):
			try:
				return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
			except Exception:
				return None

		def fill_field(field_name, value):
			# Try common locator patterns for a logical field name like 'firstName'
			candidates = [
				(lambda: try_find(driver, By.NAME, field_name)),
				(lambda: try_find(driver, By.ID, field_name)),
				# Some pages (or the user's input) use @type to carry semantic names
				(lambda: try_find(driver, By.XPATH, f"//input[@type='{field_name}']")),
				# Try common placeholder-based heuristics
				(lambda: try_find(driver, By.XPATH, f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{field_name.lower()}')]") ),
				# try label for attribute
				(lambda: try_find(driver, By.XPATH, f"//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{field_name.lower()}')]/following::input[1]")),
			]
			el = None
			for cand in candidates:
				try:
					el = cand()
				except Exception:
					el = None
				if el:
					break
			if not el:
				print(f"Could not find field for '{field_name}' using fallback locators")
				return False
			try:
				el.clear()
			except Exception:
				pass
			try:
				el.send_keys(value)
				print(f"Filled '{field_name}' with '{value}'")
				return True
			except Exception as exc:
				print(f"Failed to send keys to '{field_name}':", exc)
				return False

		# Field values from user request
		fields = [
			('firstName', 'tamari'),
			('lastName', 'gagoshidze'),
			('email', 'gagoshidzetam55@gmail.com'),
			('password', 'tamarAR77'),
			('confirmPassword', 'tamarAR77'),
		]

		for name, val in fields:
			# small sleep to allow any dynamic form rendering
			time.sleep(0.5)
			ok = fill_field(name, val)
			if not ok:
				# continue trying other fields even if one fails
				print(f"Warning: field '{name}' may not have been filled.")

		# Try to find and click the submit button
		print("Looking for submit button...")
		submit_candidates = [
			(By.XPATH, "//button[@type='submit']"),
			(By.CSS_SELECTOR, "button[type='submit']"),
			(By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'register') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign up') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]")
		]
		sub_el = None
		for by, val in submit_candidates:
			try:
				sub_el = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((by, val)))
				if sub_el:
					break
			except Exception:
				continue
		if sub_el:
			print("Clicking submit button...")
			sub_el.click()
			# Wait briefly for any result
			try:
				WebDriverWait(driver, 10).until(EC.staleness_of(sub_el))
			except Exception:
				pass
			print("Submit clicked — current URL:", driver.current_url)
		else:
			print("Could not find a submit button using common locators.")

		# Keep browser open briefly so user can see result
		time.sleep(2)
	except Exception as exc:
		print("Error while trying to click register link:", exc)
	finally:
		driver.quit()


if __name__ == '__main__':
	open_and_click_register()

