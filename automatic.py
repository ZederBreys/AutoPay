import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

def get_payment_link(login: str, password: str, amount: int = 300) -> str:
    """Авторизация и получения ссылки на оплату"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Работа без GUI
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU

    driver = uc.Chrome(options=chrome_options)  # Новый экземпляр драйвера
    try:
        # Этап 1: Авторизация
        URL = "https://ztv.su/login"
        driver.get(URL)
        
        email_input = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "inputEmail"))
        )
        email_input.send_keys(login)
        
        password_input = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "inputPassword"))
        )
        password_input.send_keys(password)
        
        login_button = WebDriverWait(driver, 45).until(
            EC.element_to_be_clickable((By.ID, "login"))
        )
        login_button.click()
        
        # Этап 2: Получение ссылки на оплату
        URL = "https://ztv.su/clientarea.php?action=addfunds"
        driver.get(URL)
        
        amount_input = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "amount"))
        )
        amount_input.clear()
        amount_input.send_keys(str(amount))
        
        top_up_button = WebDriverWait(driver, 45).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Пополнить']"))
        )
        top_up_button.click()
        
        WebDriverWait(driver, 120).until(
            lambda d: "yoomoney.ru/checkout/payments" in d.current_url
        )
        payment_url = driver.current_url
    except Exception as e:
        print("Ошибка:", e)
        payment_url = ""
    finally:
        driver.quit()  # корректное завершение сессии
    return payment_url
