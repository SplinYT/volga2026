import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.ui import Modals


@allure.feature('Дополнительное требование: Message')
@pytest.mark.positive
@allure.title('FORM-P01: заполнить Message списком из раздела Automation tools')
def test_message_from_tools(driver, settings):
    page = Modals(driver, settings).open('form-fields')
    items = page.wait.until(EC.visibility_of_all_elements_located((By.XPATH,
        '//label[normalize-space()="Automation tools"]/following-sibling::ul[1]/li')))
    values = [item.text.strip() for item in items]
    assert values and all(values)
    with allure.step('Соединить названия через запятую и заполнить Message'):
        expected = ', '.join(values)
        page.element('#message').clear()
        page.element('#message').send_keys(expected)
    assert page.element('#message').get_attribute('value') == expected
