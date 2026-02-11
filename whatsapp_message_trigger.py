import time
import os
import pyautogui
import pandas as pd
import pywhatkit as kt

FILE = "example.csv"
TIME_BETWEEN_MESSAGES = 10
WAITING_TIME = 15


def data_treatment():
    if not os.path.exists(FILE):
        print(f"Error: The file {FILE} doesn't exist.")

        return None

    data = pd.read_csv(FILE)

    def treat_phone_number(phone_number):
        try:
            cleaned_number = str(int(float(phone_number)))

            if len(cleaned_number) in [10, 11]:
                return f"+55{cleaned_number}"
            elif len(cleaned_number) > 11:
                return (
                    f"+{cleaned_number}"
                    if not cleaned_number.startswith("+")
                    else cleaned_number
                )
            return None

        except ValueError:
            print(f"Error: Invalid phone number '{phone_number}'")
            return None

    data["formated_phone_number"] = data["TELEFONE"].apply(treat_phone_number)

    data_validated = data.dropna(subset=["formated_phone_number"])

    return data_validated


def send_messages(data):
    data = data_treatment()

    if data is None or data.empty:
        print("No valid phone numbers found")
        return

    print(f"Total valid phone numbers: {len(data)}")
    print("Don't touch the computer while the messages are being sent!")

    counter = 0

    for index, row in data.iterrows():
        counter += 1
        name = row["NOME"]
        phone_number = row["formated_phone_number"]
        total = row["TOTAL"]

        formatted_value = f"""
        Olá {name}, tudo bem? Aqui é da empresa XYZ, e estamos entrando em contato para informar que o valor total da sua compra é de R$ {total:.2f}. Agradecemos pela preferência e estamos à disposição para qualquer dúvida ou assistência que você possa precisar. Tenha um ótimo dia!
        """

        print(
            f"Sending message to {name} at {phone_number} (Message {counter}/{len(data)})"
        )

        try:
            kt.sendwhatmsg_instantly(
                phone_number,
                formatted_value,
                wait_time=WAITING_TIME,
                tab_close=True,
                close_time=3,
            )

            pyautogui.press("enter")

            time.sleep(TIME_BETWEEN_MESSAGES)

        except Exception as e:
            print(f"Failed to send message to {phone_number}: {e}")

    print("All messages have been sent!")


if __name__ == "__main__":
    send_messages()
