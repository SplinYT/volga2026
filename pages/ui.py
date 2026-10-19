import calendar
from selenium.common.exceptions import TimeoutException

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Page:
    def __init__(self, driver, settings):
        self.driver = driver
        self.base, timeout = settings
        self.wait = WebDriverWait(driver, timeout)

    @allure.step('Открыть страницу {path}')
    def open(self, path):
        self.driver.get(self.base.rstrip('/') + '/' + path.strip('/') + '/')
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main')))
        return self

    def element(self, css):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))

    @allure.step('Нажать {css}')
    def click(self, css):
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        element.click()

    def hidden(self, css):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, css)))

    def remains(self, css, seconds=1):
        try:
            WebDriverWait(self.driver, seconds, poll_frequency=.1).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, css)))
        except TimeoutException:
            return
        raise AssertionError(f'{css} неожиданно исчез')

    @allure.step('Нажать Escape')
    def escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    @allure.step('Нажать вне контейнера модального окна')
    def outside(self, css):
        overlay = self.element(css)
        ActionChains(self.driver).move_to_element_with_offset(
            overlay, -overlay.size['width'] // 2 + 5,
            -overlay.size['height'] // 2 + 5).click().perform()


class Calendar(Page):
    field = 'main input.jp-contact-form-date'
    picker = '.dp' 

    @allure.step('Ввести дату {value}')
    def enter(self, value):
        field = self.element(self.field)
        field.clear()
        field.send_keys(value)
        field.send_keys(Keys.TAB)

    def value(self):
        return self.element(self.field).get_attribute('value')

    def month(self):
        return self.element('.dp-cal-month').text + ' ' + self.element('.dp-cal-year').text

    @allure.step('Выбрать дату {target} через пагинацию календаря')
    def select(self, target):
        self.click(self.field)
        for _ in range(240):
            current = (int(self.element('.dp-cal-year').text),
                       list(calendar.month_name).index(self.element('.dp-cal-month').text))
            wanted = (target.year, target.month)
            if current == wanted:
                day = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                    f'//button[contains(concat(" ",normalize-space(@class)," ")," dp-day ") '
                    f'and not(contains(@class,"dp-edge-day")) and normalize-space()="{target.day}"]')))
                day.click()
                self.hidden(self.picker)
                return
            old = self.month()
            self.click('.dp-next' if current < wanted else '.dp-prev')
            self.wait.until(lambda _: self.month() != old)
        raise AssertionError('Превышен лимит пагинации')

    def submit(self):
        self.click('main form button[type="submit"]')

    def rejected(self):
        self.wait.until(lambda d: any(
            e.is_displayed() and e.text.strip()
            for e in d.find_elements(By.CSS_SELECTOR, 'main .contact-form__input-error, main .contact-form__error'))
            or self.element(self.field).get_attribute('aria-invalid') == 'true')
        assert self.element(self.field).is_displayed()


class Modals(Page):
    simple = '#pum-1318'
    form = '#pum-674'
    name = '#pum-674 input.name'
    email = '#pum-674 input.email'
    message = '#pum-674 textarea.grunion-field'

    @allure.step('Открыть модальное окно {kind}')
    def show(self, kind):
        self.click('#simpleModal' if kind == 'simple' else '#formModal')
        self.element(self.simple if kind == 'simple' else self.form)

    def close(self, css):
        self.click(css + ' .pum-close')
        self.hidden(css)

    @allure.step('Получить список Automation Tools средствами Selenium')
    def tools(self):
        original = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')
        try:
            self.open('form-fields')
            items = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,
                '//label[normalize-space()="Automation tools"]/following-sibling::ul[1]/li')))
            values = [e.text.strip() for e in items if e.text.strip()]
            assert values, 'Раздел Automation Tools найден, но список пуст'
            return values
        finally:
            self.driver.close()
            self.driver.switch_to.window(original)

    @allure.step('Заполнить форму; Message — список Automation Tools через запятую')
    def fill(self, name='UI Test', email='ui-test@example.com'):
        text = ', '.join(self.tools())
        for css, value in [(self.name, name), (self.email, email), (self.message, text)]:
            element = self.element(css)
            element.clear()
            if value:
                element.send_keys(value)
        return text

    def submit(self):
        self.click(self.form + ' button[type="submit"]')

    def success(self):
        self.wait.until(lambda d: any(e.is_displayed() and 'Thank you' in e.text
            for e in d.find_elements(By.CSS_SELECTOR, '#pum-674 .contact-form-submission, #pum-674 .jetpack-contact-form-success')))

    def rejected(self, css):
        self.wait.until(lambda d: self.element(css).get_attribute('aria-invalid') == 'true'
            or any(e.is_displayed() and e.text.strip() for e in d.find_elements(
                By.CSS_SELECTOR, '#pum-674 .contact-form__input-error, #pum-674 .contact-form__error')))
        assert self.element(css).is_displayed()


class Ads(Page):
    ad = '#pum-1272'

    def appeared(self):
        return self.element(self.ad)

    def close(self):
        self.click(self.ad + ' .pum-close')
        self.hidden(self.ad)
