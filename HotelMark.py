# HotelMark. Marks from hotel name.

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


def get_tripadvisor_reviews(hotel_name, max_reviews=20):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    # Инициализация драйвера
    service = Service(executable_path='/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)


    try:
        # 1. Поиск отеля
        driver.get("https://www.tripadvisor.com")
        time.sleep(2)

        # Принимаем куки
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
            time.sleep(1)
        except:
            pass

        # Ищем поле поиска
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"][name="q"]')))
        search_box.clear()
        search_box.send_keys(hotel_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # 2. Переход на страницу отеля
        hotel_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test-target="hotels-list"] a:first-child')))
        hotel_link.click()
        time.sleep(3)

        # 3. Переход к отзывам
        reviews_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "#REVIEWS")]')))
        reviews_tab.click()
        time.sleep(2)

        # 4. Прокрутка и сбор отзывов
        reviews = []
        collected = 0

        while collected < max_reviews:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_blocks = soup.find_all('div', class_='review-container')

            for review in review_blocks:
                if collected >= max_reviews:
                    break

                try:
                    author = review.find('div', class_='info_text').div.get_text(strip=True)
                    date = review.find('span', class_='ratingDate')['title']
                    rating_class = review.find('span', class_='ui_bubble_rating')['class'][1]
                    rating = int(rating_class.split('_')[-1]) / 10
                    text = review.find('p', class_='partial_entry').get_text(strip=True)

                    reviews.append({
                        'author': author,
                        'date': date,
                        'rating': rating,
                        'text': text
                    })
                    collected += 1
                except Exception as e:
                    continue

            # Попытка перейти на следующую страницу
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'a.next')
                next_btn.click()
                time.sleep(3)
            except:
                break

        return pd.DataFrame(reviews)

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return pd.DataFrame()

    finally:
        driver.quit()

if __name__ == "__main__":
    hotel_name = "Radisson Blu Hotel, Moscow"
    reviews_df = get_tripadvisor_reviews(hotel_name, max_reviews=10)

    if not reviews_df.empty:
        reviews_df.to_csv(f'{hotel_name}_reviews.csv', index=False, encoding='utf-8-sig')
        print(f"Собрано {len(reviews_df)} отзывов. Данные сохранены в CSV.")
    else:
        print("Не удалось собрать отзывы")