import pandas as pd
import time
import os
import urllib.parse
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FILE = "example.csv"
TIME_BETWEEN_MESSAGES = 10


def format_phone_number(value):
    try:
        num_str = str(value).replace(".0", "").strip()
        num = "".join([c for c in num_str if c.isdigit()])

        if len(num) == 13:
            return num
        elif len(num) == 12 and num.startswith("55"):
            return f"{num[:4]}9{num[4:]}"
        elif len(num) == 11:
            return f"55{num}"
        elif len(num) == 10:
            return f"55{num[:2]}9{num[2:]}"
        else:
            return None
    except:
        return None


def send_messages():
    if not os.path.exists(FILE):
        print(f"Error: The file {FILE} doesn't exist.")
        return

    data = pd.read_csv(FILE)
    data.columns = [c.upper().strip for c in data.columns]

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get("https://web.whatsapp.com/")

    print("Please scan the QR code to log in to WhatsApp Web.")
    print("When you have logged in, press Enter to continue...")

    input()

    for index, row in data.iterrows():
        name = row.get("NOME", "there")

        if pd.isna(name) or str(name).strip() == "":
            name = "there"

        raw_phone = row.get("TELEFONE")
        total = row.get("TOTAL", 0)

        if pd.isna(raw_phone):
            continue

        phone_number = format_phone_number(raw_phone)

        if not phone_number:
            print(f"Skipping invalid phone number: {raw_phone}")
            continue

        try:
            val_float = float(total)
            formatted_value = (
                f"R$ {val_float:,.2f}".replace(".", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

        except:
            formatted_value = f"R$ 0,00"

        message = f"""
        Hi {name}, I hope you're doing well! I wanted to let you know that your total amount is {formatted_value}. If you have any questions, feel free to reach out. Have a great day!
        """

        encoded_message = urllib.parse.quote(message)
        url = (
            f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
        )

        print(f"[{index+1}/{len(data)}] Sending message to {name} ({phone_number})...")

        try:
            driver.get(url=url)

            text_box = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true']")
                )
            )

            time.sleep(2)

            try:
                text_box.click()
                time.sleep(1)
                text_box.send_keys(Keys.ENTER)
            except Exception as e:
                print(
                    f"Error clicking or sending keys to text box for {phone_number}: {e}"
                )

        except TimeoutError:
            print(f"Failed to load WhatsApp Web for {phone_number}. Skipping.")
            continue
        except Exception as e:
            print(f"An error occurred while sending message to {phone_number}: {e}")
            continue

    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    send_messages()
