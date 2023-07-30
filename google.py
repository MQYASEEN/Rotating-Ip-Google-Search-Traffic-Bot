import os
import time
import random
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

def click_random_titles(driver, titles_filename):
    with open(titles_filename, 'r') as file:
        titles = [line.strip() for line in file if line.strip()]

    if not titles:
        print("No titles found in the file.")
        return

    # Wait for 3 seconds before starting to click on titles
    time.sleep(3)

    # Click on a random title from the list
    random_title = random.choice(titles)
    print(f"Clicking on title: {random_title}")

    try:
        title_elements = driver.find_elements(By.XPATH, f'//div[@class="data"]//h3/a[contains(text(), "{random_title}")]')
        if not title_elements:
            print(f"Title not found: {random_title}")
            return

        # Click on the first element from the matched titles
        title_elements[0].click()

        # Wait for 5 seconds to ensure the website is completely loaded
        WebDriverWait(driver, 5).until(EC.title_contains(random_title))

        # Now, you can perform any further actions on the website related to the clicked title
        # For example, extract information, perform interactions, etc.
    except Exception as e:
        print(f"Failed to click on the title: {random_title} - {e}")

def is_proxy_working(proxy):
    try:
        response = requests.get('https://www.google.com/', proxies={'http': proxy, 'https': proxy}, timeout=10)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def create_webdriver(proxy=None):
    chrome_options = webdriver.ChromeOptions()

    # Set the proxy for the webdriver if provided
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    # Optional: Add other options to the Chrome driver, e.g., headless mode
    # chrome_options.add_argument('--headless')

    # Add the preferences to handle the cookies popup
    prefs = {
        'profile.default_content_setting_values.cookies': 2,  # 2: Block all cookies
        'profile.block_third_party_cookies': True
    }
    chrome_options.add_experimental_option('prefs', prefs)
    # Create the webdriver with the proxy and options
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_proxies_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            proxies = [line.strip() for line in file]
        return proxies
    else:
        return []

def get_keywords_from_file(filename):
    keywords_dict = {}
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                keyword, link = line.strip().split(':', 1)
                keywords_dict[keyword] = link.strip()
    return keywords_dict

def find_link_by_class_name(driver, website_link):
    # Find the URL elements by class name
    url_elements = driver.find_elements(By.CSS_SELECTOR, '.tF2Cxc')

    for element in url_elements:
        url = element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        if website_link in url:
            return url

    return None

def click_on_anchor_link(driver):
    try:
        # Find the anchor link element by ID
        anchor_link_element = driver.find_element(By.ID, 'menu-item-2056')
        # Highlight and click on the anchor link
        highlight_element(driver, anchor_link_element)

        # Get the main window handle before clicking the link
        main_window_handle = driver.current_window_handle

        # Click on the anchor link to open in a new tab
        anchor_link_element.click()

        # Wait for a few seconds to let the new tab load (adjust the wait time as needed)
        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

        # Switch back to the main window
        driver.switch_to.window(main_window_handle)

    except NoSuchElementException:
        # If the element is not found, click anywhere on the screen 5 times and then try again
        for _ in range(5):
            try:
                # Perform the click anywhere on the screen
                driver.execute_script("document.elementFromPoint(arguments[0], arguments[1]).click();", 100, 100)
            except Exception:
                pass
            time.sleep(1)
        try:
            # Find the anchor link element by ID again after clicking 5 times
            anchor_link_element = driver.find_element(By.ID, 'menu-item-2056')
            # Highlight and click on the anchor link
            highlight_element(driver, anchor_link_element)
        except NoSuchElementException:
            # If the element is still not found, click anywhere on the screen 3 times and then try again
            for _ in range(3):
                try:
                    # Perform the click anywhere on the screen
                    driver.execute_script("document.elementFromPoint(arguments[0], arguments[1]).click();", 100, 100)
                except Exception:
                    pass
                time.sleep(1)
            try:
                # Find the anchor link element by ID again after clicking 3 times
                anchor_link_element = driver.find_element(By.ID, 'menu-item-2056')
                # Highlight and click on the anchor link
                highlight_element(driver, anchor_link_element)
            except NoSuchElementException:
                print("Anchor link element not found after multiple attempts. Unable to proceed.")
                return

    # Wait for 5 seconds after clicking the anchor link
    time.sleep(5)

    # Click anywhere on the screen 3 times
    for _ in range(3):
        try:
            # Perform the click anywhere on the screen
            driver.execute_script("document.elementFromPoint(arguments[0], arguments[1]).click();", 100, 100)
        except Exception:
            pass
        time.sleep(1)

    # Switch back to the main window/tab
    driver.switch_to.window(main_window_handle)

def google_search_with_proxies(search_query, website_link, proxies=None):
    results = []

    # If proxies is not provided or is None, set it to an empty list
    if proxies is None:
        proxies = []

    for proxy in proxies:
        if is_proxy_working(proxy):
            try:
                driver = create_webdriver(proxy)
                driver.get('https://www.google.com/')

                # Find the search box and submit the query
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'q'))
                )
                search_box.send_keys(search_query)
                search_box.submit()

                # Wait for 3 seconds to allow the search page to load completely
                time.sleep(3)

                # Check the search results for the website link in the first 10 pages
                url = None
                for _ in range(10):  # Loop through the first 10 pages of search results
                    url = find_link_by_class_name(driver, website_link)
                    if url:
                        break  # Exit the loop if link found
                    try:
                        next_page_button = driver.find_element(By.ID, 'pnnext')
                        next_page_button.click()
                        time.sleep(5)  # Adding a delay to ensure page loads completely
                    except:
                        break  # Exit loop if the next page button is not found (no more pages)

                if url:
                        print(f"URL found in search results: {url}")
                        driver.get(url)  # Click on the URL

                        # Wait for 5 seconds to ensure the website is completely loaded
                        time.sleep(5)

                        click_on_anchor_link(driver)

                        # Wait for 5 seconds before proceeding to click on random titles
                        time.sleep(5)

                        try:
                            click_random_titles(driver, "titles.txt")
                        except NoSuchElementException:
                            # If the element is not found, click anywhere on the screen 5 times and then try again
                            for _ in range(5):
                                try:
                                    # Perform the click anywhere on the screen
                                    driver.execute_script("document.elementFromPoint(arguments[0], arguments[1]).click();", 100, 100)
                                except Exception:
                                    pass
                                time.sleep(1)

                else:
                 print(f"URL not found in the top 10 pages of search results: {website_link}")

                # Wait for 60-70 seconds before closing the webdriver
                time.sleep(60 + 10 * random.random())  # Adding random delay between 10 and 20 seconds

                # Close the webdriver
                driver.quit()

                # Return early if successful
                return results
            except Exception as e:
                print(f"Proxy {proxy} failed: {e}")
                continue
        else:
            print(f"Proxy {proxy} is not working. Skipping to the next proxy.")

    print("No working proxies found.")
    return results

def highlight_element(driver, element):
    # Create an instance of ActionChains
    action_chains = ActionChains(driver)

    # Move the mouse to the element to highlight it
    action_chains.move_to_element(element)

    # Perform the action to move the mouse
    action_chains.perform()

    # Add some highlight effect (e.g., changing the border color)
    original_style = element.get_attribute("style")
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "border: 2px solid red;")

    # Wait for a short time (e.g., 0.5 seconds) to show the highlight effect
    time.sleep(0.5)

    # Remove the highlight effect by restoring the original style
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original_style)

    # Perform the action to click on the element
    action_chains.click(element)

    # Execute the ActionChains
    action_chains.perform()


if __name__ == "__main__":
    # Get user input for keywords file name
    keywords_filename = input("Enter the keywords file name: ")

    # Get proxies from the user-provided file name
    proxies = get_proxies_from_file("proxies.txt")

    # Get keywords and their corresponding website links from the file
    keywords = get_keywords_from_file(keywords_filename)

    for keyword, website_link in keywords.items():
        # Perform Google search with the keyword and check if the link is in the top 10 pages
        google_search_with_proxies(keyword, website_link, proxies)

    if not proxies:
        print("No proxies found. Using default IP.")
        for keyword, website_link in keywords.items():
            google_search_with_proxies(keyword, website_link, None)