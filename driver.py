import os
import threading
import time

import chrome_version
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import tkinter as tk
import json


def make_driver(path: str, name: str) -> webdriver.Chrome:
    chrome_prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Disable notifications (still okay)
        "profile.managed_default_content_settings.cookies": 1,  # Allow cookies (essential for sessions)
        "profile.managed_default_content_settings.javascript": 1,  # Allow JavaScript (critical for Instagram)
        "profile.managed_default_content_settings.plugins": 1,  # Allow plugins
        "profile.managed_default_content_settings.popups": 2,  # Block popups (standard practice)
        "profile.managed_default_content_settings.geolocation": 2,  # Block geolocation (optional, depends on need)
        # "profile.managed_default_content_settings.media_stream": 1,  # Allow media stream (needed for Stories/Reels)
        # "profile.managed_default_content_settings.images": 1,  # Enable images (critical for Instagram)
        "profile.managed_default_content_settings.stylesheets": 1,  # Enable CSS (critical for proper page rendering)
        "profile.managed_default_content_settings.fonts": 1,  # Enable fonts (important for proper text rendering)
        "profile.managed_default_content_settings.background_sync": 1,  # Allow background sync (important for notifications and session state)
        "profile.managed_default_content_settings.automatic_downloads": 2,  # Block automatic downloads (standard practice)
        "profile.managed_default_content_settings.sound": 2,  # Disable sound (optional, based on preference)
    }

    user_data_dir = os.path.normpath(path)
    profile_dir = name

    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # options.add_argument("--blink-settings=imagesEnabled=false")

    options.add_experimental_option("prefs", chrome_prefs)

    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_dir}")

    chrome_ver = chrome_version.get_chrome_version()

    chrome_ver = chrome_ver.split(".")[0]  # type: ignore

    driver = uc.Chrome(options=options, version_main=int(chrome_ver))

    driver.set_network_conditions(
        offline=False,
        latency=3,  # minimal latency
        download_throughput=100 * 1024 * 1024,  # fast download speed
        upload_throughput=100 * 1024 * 1024,
    )

    return driver


def element_text(driver: webdriver.Chrome, css_selector: str) -> str:
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        return element.text

    except Exception as e:
        print(e)
        return "lol"


def safe_click(driver: webdriver.Chrome, css_selector: str):
    # print(f"looking for {css_selector}")
    try:
        element = find_element(driver, css_selector)
    except Exception as e:
        print(f"could not find {css_selector} because {e}")
        return
    try:
        # print(f"trying to click {css_selector}")
        element.click()
    except ElementClickInterceptedException:
        if element is not None:
            # print(f"trying to click {css_selector} with js")
            driver.execute_script("arguments[0].click();", element)


def find_element(driver: webdriver.Chrome, css_selector: str):
    return WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def get_post_count(driver: webdriver.Chrome) -> int:
    posts_count_css = "ul > li > div > span"
    return int(element_text(driver, posts_count_css))


def click_first_post(driver):
    first_post_css = (
        "div[style*='display: flex'] > div:nth-of-type(1) > div:nth-of-type(1) > a"
    )
    safe_click(driver, first_post_css)


def comment(driver):
    comment_css = "textarea[placeholder='Add a comment…']"
    while True:
        try:
            comment = find_element(driver, comment_css)
            comment.send_keys("s\n")
            break
        except Exception as e:
            print(f"message failed cuz{e}")
            pass


def add_cookies(driver: webdriver.Chrome):
    cookies = [
        {"name": "ps_n", "value": "1"},
        {"name": "datr", "value": "hE8oZoNobLlvHHsqkuUnRn5A"},
        {"name": "ig_nrcb", "value": "1"},
        {
            "name": "shbts",
            "value": '"1725111200\\05453282054993\\0541756647200:01f719d25294f4cb86b3eb22e24bc25e59dd3d7b1f3417bfc8bce37252a4d91f2fe610b5"',
        },
        {"name": "ds_user_id", "value": "68589703012"},
        {
            "name": "shbid",
            "value": '"5688\\05453282054993\\0541756647200:01f74f6827fecbfc0dd7518c4a72a7e019f06831ab041808fc997ac41187a33e17cd34ac"',
        },
        {"name": "csrftoken", "value": "POgpK9ZH6ySQvLPEu1VkMWhcWZCOOkH2"},
        {"name": "ig_did", "value": "0131AC64-B7F2-4371-BB6F-EDB55F9B113B"},
        {"name": "ps_l", "value": "1"},
        {"name": "wd", "value": "2560x1355"},
        {"name": "mid", "value": "ZihPhQALAAFrZdYSHSxbb7ERARyf"},
        {
            "name": "sessionid",
            "value": "68589703012%3AKQ0QuXgg0s7z7g%3A23%3AAYcs5SCuKkDRdC_8dqDrYiWmAjIzM9G-5kA-xS2XBA",
        },
        {
            "name": "rur",
            "value": '"CCO\\05468589703012\\0541756746016:01f7ad72126d3ea6c18c459b4aeefbb364a053e93de730b32035ac4c51e9fab7819c3463"',
        },
    ]

    for cookie in cookies:
        driver.add_cookie(cookie)


def tkinter_input():
    root = tk.Tk()
    root.geometry("200x200")

    def submit():
        def save_config(config: dict):
            with open("config.json", "w") as file:
                json.dump(config, file)

        config = {
            "link": link_entry.get(),
            "profile_path": profile_path_entry.get(),
            "profile_name": profile_name_entry.get(),
        }

        save_config(config)
        threading.Thread(
            target=catcher,
            args=(config,),
        ).start()
        root.destroy()  # Close the window after getting the input

    link_label = tk.Label(root, text="Link:")
    link_label.pack()
    link_entry = tk.Entry(root)
    link_entry.pack()

    profile_path_label = tk.Label(root, text="Profile Path:")
    profile_path_label.pack()
    profile_path_entry = tk.Entry(root)
    profile_path_entry.pack()

    profile_name_label = tk.Label(root, text="Profile Name:")
    profile_name_label.pack()
    profile_name_entry = tk.Entry(root)
    profile_name_entry.pack()

    button = tk.Button(root, text="Submit", command=submit)
    button.pack()

    if os.path.exists("config.json"):
        with open("config.json", "r") as file:
            config = json.load(file)
            link_entry.insert(0, config.get("link", ""))
            profile_path_entry.insert(0, config.get("profile_path", ""))
            profile_name_entry.insert(0, config.get("profile_name", ""))

    root.mainloop()


def catcher(config: dict):
    driver = make_driver(config["profile_path"], config["profile_name"])
    target_link = config["link"]
    driver.get(target_link)
    add_cookies(driver)
    driver.refresh()
    # print("went to insta")

    prev_post_count = get_post_count(driver)

    # start_time = datetime.datetime.now()

    while prev_post_count >= get_post_count(driver):
        # duration = datetime.datetime.now() - start_time
        # print(f"Time taken to refresh: {duration.total_seconds():.2f} seconds")

        # print(f"curr post count is {prev_post_count}")
        prev_post_count = get_post_count(driver)

        # time.sleep(random.uniform(0, 0.5))
        # start_time = datetime.datetime.now()
        driver.refresh()

    # start_time = datetime.datetime.now()
    # print("new post detected")
    click_first_post(driver)

    # print("commenting")
    comment(driver)
    # print("done")
    # duration = datetime.datetime.now() - start_time
    # print(f"Time taken: {duration.total_seconds():.2f} seconds")
    time.sleep(1000)


def main():
    tkinter_input()


if __name__ == "__main__":
    main()
