from django.http import HttpResponse
from selenium.common import NoSuchWindowException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from whatsappsend.forms import SendMessageForm, MessageForm, UnreadResponseForm
import base64
from whatsappsend.sendmessages import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from django.forms import formset_factory
from django.shortcuts import render
import urllib.request
from .forms import MessageFormText

def index(request):
    return render(request, 'index.html')

def send_attached(request):
    if request.method == 'POST':
        form = SendMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.cleaned_data['message']
            file = form.cleaned_data['file']
            image = form.cleaned_data.get('image')
            if image:
                image_data = base64.b64encode(image.read())
            else:
                image_data = None

            if file:
                # If a file is uploaded, read phone numbers from the file
                phone_nos = []
                for line in file:
                    phone_nos.append(line.decode().strip())
            else:
                # Otherwise, read phone numbers from the message field
                phone_nos = message.strip().split('\n')

            try:
                sendwhatmsg(phone_nos=phone_nos, message=message, image=image_data)
                message = "Message sent successfully"
            except NoSuchWindowException:
                message = "Task Failed: WhatsApp Web Window was closed"
            except:
                message = "Error sending message"

            context = {'form': form, 'message': message}
            return render(request, 'send_attached.html', context=context)

        else:
            # Form is not valid, so
            # we include the errors in the context
            context = {'form': form}
            return render(request, 'send_attached.html', context=context)

    else:
        form = SendMessageForm()
    return render(request, 'send_attached.html', {'form': form})


def read_whatsapp(request):
    msgg = ""
    global unread_chats_data
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--user-data-dir={}/chrome-data".format(os.path.abspath(os.path.dirname(__file__))))
                driver = webdriver.Chrome(options=chrome_options)

                driver.get('https://web.whatsapp.com/')

                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'side')))

                # Find and click the filter button
                filter_button = driver.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/button/div/span')
                filter_button.click()

                time.sleep(5)

                # Find unread chat elements
                unread_chats = driver.find_elements(By.XPATH, '//span[@data-testid="icon-unread-count"]')

                print(f"Number of unread chats: {len(unread_chats)}")

                search_string = form.cleaned_data['string']
                msg = form.cleaned_data['message']
                image = form.cleaned_data.get('image')
                print("\n\n", search_string, "\n\n", msg, "\n\n")

                if image:
                    image = base64.b64encode(image.read())
                else:
                    image = None

                unread_chats_data = []

                for index, chat in enumerate(unread_chats):
                    try:
                        # Find the chat name and number
                        chat_header_element = chat.find_element(By.XPATH,
                                                                './ancestor::div[contains(@class, "_8nE1Y")]/div[contains(@class, "y_sn4")]')
                        chat_name_element = chat_header_element.find_element(By.XPATH, '//span[contains(@class, "ggj6brxn")]')
                        chat_name = chat_name_element.get_attribute('title')

                        unread_messages = chat.text

                        chat_data = {
                            'chat_name': chat_name,
                            'unread_messages': unread_messages,
                            'last_unread_messages': [],
                        }

                        # Click on the chat to open it
                        chat_header_element.click()

                        # Wait for the messages to load
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                          '//div[@class="message-in focusable-list-item _7GVCb _2SnTA _1-FMR"]//div[@class="copyable-text"]')))

                        # Find the messages in the opened chat
                        messages = driver.find_elements(By.XPATH, '//div[@class="hY_ET"]//div[@class="copyable-text"]')

                        # Print the last few messages, based on the number of unread messages
                        for message in messages[-int(unread_messages):]:
                            if message.text.find(search_string) != -1:
                                chat_data['last_unread_messages'].append(f"{message.text}")
                                time.sleep(2)
                                pyautogui.click(WIDTH / 2, HEIGHT / 2 + 15)
                                time.sleep(2)

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

                                    # Paste the image in the WhatsApp chat
                                    messagebox_xpath = "/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]"
                                    messagebox_xpath = "//div[@role='textbox'][@spellcheck='true'][@contenteditable='true']"
                                    message_box = WebDriverWait(driver, 20).until(
                                        EC.visibility_of_element_located((By.XPATH, messagebox_xpath)))
                                    message_box.click()
                                    message_box = driver.find_element(By.XPATH, messagebox_xpath)
                                    message_box.click()
                                    time.sleep(2)
                                    for char in msg:
                                        if char == "\n":
                                            pyautogui.hotkey("shift", "enter")
                                        else:
                                            pyautogui.typewrite(char)
                                    action_chain = ActionChains(driver)
                                    action_chain.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                                    os.remove("temp_image.png")
                                    print("\n\nimage sent\n\n")
                                    time.sleep(2)
                                    # message_box.send_keys(Keys.ENTER)
                                    time.sleep(2)
                                time.sleep(2)
                                send_button_xpath = "//span[@data-testid='send']"
                                send_button = WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.XPATH, send_button_xpath)))

                                try:
                                    WebDriverWait(driver, 10).until(
                                        EC.invisibility_of_element_located((By.XPATH, send_button_xpath)))
                                except TimeoutException:
                                    msgg = "Warning: Send button did not become invisible within the given timeout."


                                clickTextBox()
                                pyautogui.press("enter")
                                time.sleep(2)
                                pyautogui.hotkey('ctrl', 'w')

                        # Navigate back to the chat list
                        driver.back()
                        time.sleep(2)

                        unread_chats_data.append(chat_data)
                        msgg = "Task Completed Successfully"

                    except Exception as e:
                        print(f"Error in processing chat {index + 1}: {str(e)}, It's possible that it's a Group Chat")


                driver.quit()

                # Pass the search_string and unread_chats_data to the template
                context = {
                    'search_string': search_string,
                    'unread_chats_data': unread_chats_data,
                    'number': len(unread_chats)
                }
                return render(request, 'whatsapp_reader.html', context)


            except NoSuchWindowException:

                msgg = "Task Failed: WhatsApp Web Window was closed"

            except:

                msgg = "Error sending message"
        else:
            # Form is not valid, so
            # we include the errors in the context
            print("\n\n\nForm is not valid")
            context = {'form': form}
            return render(request, 'send_by_string.html', context=context)

    else:
        form = MessageForm()

    return render(request, 'send_by_string.html', {'form': form, 'message': msgg})


def bulk_text(request):
    MessageFormSet = formset_factory(MessageFormText, extra=1, can_delete=True, validate_max=True)
    unread_chats_data = []
    messaage_data = []
    string_data = []
    success_message = ""
    msg = ""
    if request.method == 'POST':
        post_data = request.POST.copy()
        form_count = int(post_data.get('messageform_set-TOTAL_FORMS'))
        post_data['messageform_set-TOTAL_FORMS'] = form_count
        formset = MessageFormSet(request.POST, request.FILES, prefix='messageform_set')
        # print(formset)
        if formset.is_valid():
            global messages, unread_messages, chat_data
            # loop through each form in the formset and process the data
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument(
                    "--user-data-dir={}/chrome-data".format(os.path.abspath(os.path.dirname(__file__))))
                driver = webdriver.Chrome(options=chrome_options)

                driver.get('https://web.whatsapp.com/')

                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'side')))

                # Find and click the filter button
                filter_button = driver.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/button/div/span')
                filter_button.click()

                time.sleep(5)

                # Find unread chat elements
                unread_chats = driver.find_elements(By.XPATH, '//span[@data-testid="icon-unread-count"]')

                print(f"Number of unread chats: {len(unread_chats)}")
                for index, chat in enumerate(unread_chats):
                    try:
                        print("Processing chat {}/{}".format(index + 1, len(unread_chats)))
                        # Find the chat name and number
                        chat_header_element = chat.find_element(By.XPATH,
                                                                './ancestor::div[contains(@class, "_8nE1Y")]/div[contains(@class, "y_sn4")]')
                        chat_name_element = chat_header_element.find_element(By.XPATH,
                                                                             '//span[contains(@class, "ggj6brxn")]')
                        chat_name = chat_name_element.get_attribute('title')

                        unread_messages = chat.text

                        chat_data = {
                            'chat_name': chat_name,
                            'unread_messages': unread_messages,
                            'last_unread_messages': [],
                        }

                        # Click on the chat to open it
                        chat_header_element.click()

                        # Wait for the messages to load
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                          '//div[@class="message-in focusable-list-item _7GVCb _2SnTA _1-FMR"]//div[@class="copyable-text"]')))

                        # Find the messages in the opened chat
                        messages = driver.find_elements(By.XPATH, '//div[@class="hY_ET"]//div[@class="copyable-text"]')

                        for form in formset:
                            print("\n\n\outer loop")
                            search_string = form.cleaned_data.get('string')
                            messag = form.cleaned_data.get('message')
                            messaage_data.append(messag)
                            string_data.append(search_string)
                            print("\n\n\n", search_string, messag)
                            for message in messages[-int(unread_messages):]:
                                print("\n\nmessage", message.text.find(search_string))
                                print(f"\n\ninner loop")
                                print("\nmessage:", messag, "\nsearch_string:", search_string)
                                # print("\n\nmessage", message.text)
                                if message.text.find(search_string) != -1:
                                    time.sleep(2)
                                    pyautogui.click(WIDTH / 2, HEIGHT / 2 + 15)
                                    time.sleep(2)
                                    for char in messag:
                                        print("\nchar",char)
                                        if char == "\n":
                                            pyautogui.hotkey("shift", "enter")
                                        else:
                                            pyautogui.typewrite(char)
                                    clickTextBox()
                                    pyautogui.press("enter")
                                    time.sleep(2)
                                    pyautogui.hotkey('ctrl', 'w')
                                    time.sleep(2)
                                    break


                            unread_chats_data.append(chat_data)
                    except Exception as e:
                        print(f"Error in processing chat {index + 1}: {str(e)}, It's possible that it's a Group Chat")

                msg = "Messages sent successfully!"  # set the success message
            except NoSuchWindowException:
                msg = "Task Failed: WhatsApp Web Window was closed"
            except:
                msg = "Error sending message"


            # driver.back()
            time.sleep(2)
            # driver.quit()
            print("\n\nmessage data", messaage_data)
            print("\n\nstring data", string_data)
        else:
            formset = MessageFormSet(request.POST, request.FILES, prefix='messageform_set')
            return render(request, 'bulk_text.html', {'formset': formset})

    else:
        formset = MessageFormSet(prefix='messageform_set')
    context = {'formset': formset, 'success_message': success_message, 'message': msg}
    return render(request, 'bulk_text.html', context)

def response_to_unread(request):
    unread_chats_data = []
    messaage_data = []
    string_data = []
    success_message = ""
    msg = ""
    if request.method == 'POST':
        form = UnreadResponseForm(request.POST, request.FILES)
        if form.is_valid():
            global messages, unread_messages, chat_data
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument(
                    "--user-data-dir={}/chrome-data".format(os.path.abspath(os.path.dirname(__file__))))
                driver = webdriver.Chrome(options=chrome_options)

                driver.get('https://web.whatsapp.com/')

                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'side')))

                # Find and click the filter button
                filter_button = driver.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/button/div/span')
                filter_button.click()

                time.sleep(5)

                # Find unread chat elements
                unread_chats = driver.find_elements(By.XPATH, '//span[@data-testid="icon-unread-count"]')

                print(f"Number of unread chats: {len(unread_chats)}")
                for index, chat in enumerate(unread_chats):
                    try:
                        print("Processing chat {}/{}".format(index + 1, len(unread_chats)))
                        # Find the chat name and number
                        chat_header_element = chat.find_element(By.XPATH,
                                                                './ancestor::div[contains(@class, "_8nE1Y")]/div[contains(@class, "y_sn4")]')
                        chat_name_element = chat_header_element.find_element(By.XPATH,
                                                                             '//span[contains(@class, "ggj6brxn")]')
                        chat_name = chat_name_element.get_attribute('title')

                        unread_messages = chat.text

                        chat_data = {
                            'chat_name': chat_name,
                            'unread_messages': unread_messages,
                            'last_unread_messages': [],
                        }

                        # Click on the chat to open it
                        chat_header_element.click()

                        # Wait for the messages to load
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                          '//div[@class="message-in focusable-list-item _7GVCb _2SnTA _1-FMR"]//div[@class="copyable-text"]')))

                        # Find the messages in the opened chat
                        messages = driver.find_elements(By.XPATH, '//div[@class="hY_ET"]//div[@class="copyable-text"]')

                        print("\n\n\outer loop")
                        messag = form.cleaned_data.get('message')
                        image = form.cleaned_data.get('image')
                        if image:
                            image = base64.b64encode(image.read())
                        else:
                            image = None

                        messaage_data.append(messag)
                        for message in messages[-int(unread_messages):]:
                            time.sleep(2)
                            pyautogui.click(WIDTH / 2, HEIGHT / 2 + 15)
                            time.sleep(2)

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

                                # Paste the image in the WhatsApp chat
                                messagebox_xpath = "/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]"
                                messagebox_xpath = "//div[@role='textbox'][@spellcheck='true'][@contenteditable='true']"
                                message_box = WebDriverWait(driver, 20).until(
                                    EC.visibility_of_element_located((By.XPATH, messagebox_xpath)))
                                message_box.click()
                                message_box = driver.find_element(By.XPATH, messagebox_xpath)
                                message_box.click()
                                time.sleep(2)
                                for char in messag:
                                    if char == "\n":
                                        pyautogui.hotkey("shift", "enter")
                                    else:
                                        pyautogui.typewrite(char)
                                action_chain = ActionChains(driver)
                                action_chain.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                                os.remove("temp_image.png")
                                print("\n\nimage sent\n\n")
                                # message_box.send_keys(Keys.ENTER)
                                time.sleep(2)
                            time.sleep(2)
                            send_button_xpath = "//span[@data-testid='send']"
                            send_button = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located((By.XPATH, send_button_xpath)))

                            try:
                                WebDriverWait(driver, 10).until(
                                    EC.invisibility_of_element_located((By.XPATH, send_button_xpath)))
                            except TimeoutException:
                                msgg = "Warning: Send button did not become invisible within the given timeout."

                            clickTextBox()
                            pyautogui.press("enter")
                            time.sleep(5)
                            pyautogui.hotkey('ctrl', 'w')
                            break


                        unread_chats_data.append(chat_data)
                    except Exception as e:
                        print(f"Error in processing chat {index + 1}: {str(e)}, It's possible that it's a Group Chat")

                msg = "Messages sent successfully!"  # set the success message
            except NoSuchWindowException:
                msg = "Task Failed: WhatsApp Web Window was closed"
            except:
                msg = "Error sending message"
        else:
            form = UnreadResponseForm(request.POST, request.FILES)
            return render(request, 'unread_response.html', {'form': form})

    else:
        form = UnreadResponseForm()
    context = {'form': form, 'success_message': success_message, 'message': msg}
    return render(request, 'unread_response.html', context)
