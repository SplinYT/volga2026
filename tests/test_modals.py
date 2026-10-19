import allure
import pytest
from pages.ui import Modals


@pytest.fixture
def page(driver, settings):
    return Modals(driver, settings).open('modals')


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P01: простое окно содержит ожидаемый текст')
def test_simple_content(page):
    page.show('simple')
    assert 'Hi, I’m a simple modal.' in page.element(page.simple + ' .pum-content').text


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P02: закрытие простого окна крестиком')
def test_simple_close(page):
    page.show('simple')
    page.close(page.simple)
    assert page.element('#formModal').is_enabled()


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P03: повторное открытие простого окна')
def test_simple_reopen(page):
    page.show('simple')
    page.close(page.simple)
    page.show('simple')
    assert page.element(page.simple).is_displayed()


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P04: форма открывается, все поля доступны')
def test_form_fields(page):
    page.show('form')
    for css in [page.name, page.email, page.message]:
        assert page.element(css).is_enabled()


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P05: форма закрывается крестиком')
def test_form_close(page):
    page.show('form')
    page.close(page.form)
    assert page.element('#simpleModal').is_enabled()


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P06: форма закрывается Escape')
def test_form_escape(page):
    page.show('form')
    page.escape()
    page.hidden(page.form)


@allure.feature('Модальные окна')
@pytest.mark.positive
@allure.title('MOD-P07: отправка формы со списком Automation Tools в Message')
def test_submit_form(page):
    page.show('form')
    expected = page.fill()
    assert page.element(page.message).get_attribute('value') == expected
    page.submit()
    page.success()


@allure.feature('Модальные окна')
@pytest.mark.negative
@allure.title('MOD-N01: пустое обязательное имя блокирует отправку')
def test_required_name(page):
    page.show('form')
    page.fill(name='')
    page.submit()
    page.rejected(page.name)


@allure.feature('Модальные окна')
@pytest.mark.negative
@allure.title('MOD-N02: неверный email блокирует отправку')
def test_invalid_email(page):
    page.show('form')
    page.fill(email='invalid-address')
    page.submit()
    page.rejected(page.email)


@allure.feature('Модальные окна')
@pytest.mark.negative
@allure.title('MOD-N03: Escape не закрывает простое окно')
def test_simple_ignores_escape(page):
    page.show('simple')
    page.escape()
    page.remains(page.simple)
