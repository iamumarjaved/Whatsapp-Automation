import base64
import os
import re
import time
import platform
import webbrowser
import pyautogui
from urllib.parse import quote
from django.conf import settings
import win32clipboard
from io import BytesIO
from PIL import Image
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from . import exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

WIDTH, HEIGHT = pyautogui.size()
file_dir = os.path.dirname(__file__)
filepath = os.path.join(file_dir, 'smile1.png')
search = os.path.join(file_dir, 'search_box.png')

# Keep track of open tabs
open_tabs = {}



def check_number(number: str) -> bool:
    return "+" in number or "_" in number

def _web(receiver: str, message: str) -> None:
    if check_number(number=receiver):
        driver.get("https://web.whatsapp.com/send?phone=" + receiver + "&text=" + quote(message))
    else:
        driver.get("https://web.whatsapp.com/accept?code=" + receiver)

    # Wait for the page to load
    time.sleep(10)


def close_tab(wait_time: int = 2) -> None:
    time.sleep(wait_time)
    # _system = platform.system().lower()
    # if _system in ("windows", "linux"):
    #     pyautogui.hotkey("ctrl", "w")
    # elif _system == "darwin":
    #     pyautogui.hotkey("command", "w")
    # else:
    #     raise exceptions.TabCloseException(f"System not supported!")
    # pyautogui.press("enter")
    time.sleep(2)
    driver.quit()

def clickTextBox() -> None:
    location = pyautogui.locateOnScreen(filepath)
    print(location)
    print("clicking textbox")
    try:
        try:
            pyautogui.moveTo(location[0] + 150, location[1] + 5)
        except Exception as e:
            if str(e) == "NoneType' object is not subscriptable":
                raise exceptions.WhatsAppNotFoundException(
                    "Seems the WhatsApp Web Window was closed or moved to another Tab!"
                )
        pyautogui.click()
    except Exception:
        location = pyautogui.locateOnScreen("smile.png")
        try:
            pyautogui.moveTo(location[0] + 150, location[1] + 5)
        except Exception as e:
            if str(e) == "NoneType' object is not subscriptable":
                raise exceptions.WhatsAppNotFoundException(
                    "Seems the WhatsApp Web Window was closed or moved to another Tab!"
                )
        pyautogui.click()

def send_message(message, receiver, wait_time, image=None) -> None:
    print("before _web line")
    _web(receiver=receiver, message=message)
    time.sleep(2)
    pyautogui.click(WIDTH / 2, HEIGHT / 2 + 15)
    time.sleep(wait_time - 7)

    if image:
        print("\naccessing image loop\n")
        # Save the base64 encoded image as a temporary file
        img_data = base64.b64decode(image)
        with open("temp_image.png", "wb") as img_file:
            img_file.write(img_data)

        # Convert image to BMP format
        image = Image.open("temp_image.png")
        output = BytesIO()
        image.save(output, format="BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        print("\n\nimage copied\n\n")
        # Paste the image in the WhatsApp chat
        messagebox_xpath = "/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]"
        messagebox_xpath = "//div[@role='textbox'][@spellcheck='true'][@contenteditable='true']"
        message_box = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, messagebox_xpath)))
        message_box.click()
        message_box = driver.find_element(By.XPATH, messagebox_xpath)
        message_box.click()
        time.sleep(2)
        action_chain = ActionChains(driver)
        action_chain.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        os.remove("temp_image.png")
        print("\n\nimage sent\n\n")
        time.sleep(2)
        # message_box.send_keys(Keys.ENTER)
        print("\n\n1\n\n")
        time.sleep(2)
    time.sleep(2)
    # send_button_xpath = "//span[@data-testid='send']"
    # send_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, send_button_xpath)))
    #
    # try:
    #     WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, send_button_xpath)))
    # except TimeoutException:
    #     print("Warning: Send button did not become invisible within the given timeout.")


    # if not check_number(number=receiver):
    #     print("message sent", message)
    #     for char in message:
    #         if char == "\n":
    #             pyautogui.hotkey("shift", "enter")
    #         else:
    #             pyautogui.typewrite(char)
    print("\n\n2\n\n")
    clickTextBox()
    print("\n\n3\n\n")
    pyautogui.press("enter")
    time.sleep(5)
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(2)

def sendwhatmsg(
        phone_nos,
        message,
        wait_time=7,
        tab_close=True,
        close_time=3,
        image=None,
) -> None:
    for phone_no in phone_nos:
        global driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(
            "--user-data-dir={}/chrome-data".format(os.path.abspath(os.path.dirname(__file__))))
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        phone_no = "+" + phone_no

        phone_no = phone_no.replace(" ", "")

        if not re.fullmatch(r'^\+?[0-9]{2,4}\s?[0-9]{9,15}', phone_no):
            raise exceptions.InvalidPhoneNumber("Invalid Phone Number.")

        send_message(
            message=message,
            receiver=phone_no,
            wait_time=wait_time,
            image=image
        )
        if tab_close:
            close_tab(wait_time=close_time)
