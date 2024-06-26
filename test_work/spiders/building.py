import scrapy
from scrapy.selector import Selector 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

class BuildingSpider(scrapy.Spider):
    name = "building"
    allowed_domains = ["xn--80az8a.xn--d1aqf.xn--p1ai"]
    start_urls = ["https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?place=0-44&objStatus=0"]

    def __init__(self):
        chrome_service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service)

    def parse(self, response):
        self.driver.get(response.url)
        
        # Ожидаем появления кнопки "Показать еще"
        try:
            show_more_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.styles__ButtonWrapper-sc-40tof2-0.kYqzc.Newbuildings__ButtonLoadMore-sc-1bou0u4-15.bpTAvq"))
            )
        except:
            print("Кнопка 'Показать еще' не найдена на странице")
            return
        
        # Счетчик для отслеживания количества загруженных карточек
        loaded_cards = 0
        
        while show_more_button.is_displayed():
            # Нажимаем на кнопку "Показать еще"
            self.driver.execute_script("arguments[0].click();", show_more_button)
            print("Нажалась кнопка")
            
            # Ждем загрузки новых результатов
            sleep(3)
            
            # Обновляем ссылку на кнопку "Показать еще"
            try:
                show_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.styles__ButtonWrapper-sc-40tof2-0.kYqzc.Newbuildings__ButtonLoadMore-sc-1bou0u4-15.bpTAvq")
            except:
                print("Кнопка 'Показать еще' больше не отображается на странице")
                break
            
            # Обновляем счетчик загруженных карточек
            new_cards = len(self.driver.find_elements(By.CSS_SELECTOR, "div.Newbuildings__NewBuildingList-sc-1bou0u4-14.huMfny > div"))
            if new_cards == loaded_cards:
                print("Все карточки загружены")
                break
            loaded_cards = new_cards
        
        # Получаем HTML-код страницы после загрузки всех результатов
        html = self.driver.page_source
        sel = Selector(text=html)
        
        buildings = sel.css("div.Newbuildings__NewBuildingList-sc-1bou0u4-14.huMfny > div")
        
        if not buildings:
            print("Ничего не найдено")
        else:
            for building in buildings:
                print("Объект недвижимости найден")
                
                # Находим ссылку на страницу объекта
                detail_page_link = building.css('a.NewBuildingItem__ImageWrapper-sc-o36w9y-2.iLOAue::attr(href)').get()
                if detail_page_link:
                    detail_page_link = response.urljoin(detail_page_link)
                    yield scrapy.Request(detail_page_link, callback=self.parse_detail)
        
    def parse_detail(self, response):
        self.driver.get(response.url)
        
        # Ожидаем появления элементов на странице
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.Header__Name-sc-eng632-3.fSjDTR'))
        )
        
        # Получаем HTML-код страницы
        html = self.driver.page_source
        sel = Selector(text=html)
        
        # Парсинг информации на странице объекта
        title = sel.css('h1.Header__Name-sc-eng632-3.fSjDTR::text').get()
        address = sel.xpath('//p[contains(@class, "Header__Address-sc-eng632-8")]/text()').get()
        if address:
            address = address.strip()
        else:
            address = "Нет данных"


        building_id = response.css('p.ButtonsRow__ObjectId-sc-1a7tla9-7.dXNRhw::text').get()
        if building_id:
            building_id = building_id.split('&nbsp;')[-1]
        else:
            building_id = "Нет данных"
            
        commissioning = response.css('div.Row-sc-13pfgqd-0.dJkQFS div.Row__Value-sc-13pfgqd-2.dySlPJ::text').get()
        if commissioning:
            commissioning = commissioning.strip()
        else:
            commissioning = "Нет данных"
            
        developer = sel.css('a.Link__LinkContainer-sc-1u7ca6h-0.hYekpU::text').get()
        
        group = response.css('div.Row-sc-13pfgqd-0.dJkQFS div.Row__Value-sc-13pfgqd-2.dySlPJ a.Link__LinkContainer-sc-1u7ca6h-0.hYekpU::text').get()
        if not group:
            group = "Нет данных"


        date = response.css('div.Row__Value-sc-13pfgqd-2.dySlPJ').get()
        if date:
            date = date.strip()
        else:
            date = "Нет данных"
            
        key = response.css('div.Row__Value-sc-13pfgqd-2.dySlPJ').get()
        
        price = response.css('div.Row__Value-sc-13pfgqd-2.dySlPJ').get()
        
        buy = response.css('div.Row__Value-sc-13pfgqd-2.dySlPJ').get()
        
        class_estate = response.css('span.CharacteristicsBlock__RowSpan-sc-1fyyfia-4.eCBXEE').get()
        apartment = sel.xpath('//span[contains(@class, "CharacteristicsBlock__RowSpan-sc-1fyyfia-4") and text()="Количество квартир"]/following-sibling::span/text()').get()

        yield {
            'Заголовок': title,
            'Адрес': address,
            'ID': building_id,
            'Ввод в эксплуатацию': commissioning,
            'Застройщик': developer,
            'Группа компаний': group,
            'Дата публикации': date,
            'Выдача ключей': key,
            'Средняя цена за 1 м²': price,
            'Распроданность квартир': buy,
            'Класс недвижимости': class_estate,
            'Количество квартир': apartment
        }

    def closed(self, reason):
        self.driver.quit()