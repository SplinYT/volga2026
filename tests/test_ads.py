import allure
import pytest
from selenium.common.exceptions import ElementClickInterceptedException
from pages.ui import Ads


@pytest.fixture
def page(driver, settings):
    return Ads(driver, settings).open('ads')


@allure.feature('Реклама')
@pytest.mark.positive
@allure.title('ADS-P01: реклама появляется автоматически')
def test_auto_open(page):
    assert page.appeared().is_displayed()


@allure.feature('Реклама')
@pytest.mark.positive
@allure.title('ADS-P02: окно содержит рекламный текст')
def test_content(page):
    page.appeared()
    assert 'I am an ad.' in page.element(page.ad + ' .pum-content').text


@allure.feature('Реклама')
@pytest.mark.positive
@allure.title('ADS-P03: крестик закрывает рекламное окно')
def test_close(page):
    page.appeared()
    page.close()
    assert page.element('main h1').text == 'Ads'


@allure.feature('Реклама')
@pytest.mark.positive
@allure.title('ADS-P04: реклама появляется после обновления страницы')
def test_refresh(page):
    page.appeared()
    page.close()
    page.driver.refresh()
    assert page.appeared().is_displayed()


@allure.feature('Реклама')
@pytest.mark.positive
@pytest.mark.parametrize('width,height', [(390, 844), (768, 1024), (1440, 1000)],
                         ids=['ADS-P05', 'ADS-P06', 'ADS-P07'])
@allure.title('Кнопка закрытия доступна в окне {width}×{height}')
def test_responsive_close(page, width, height):
    page.driver.set_window_size(width, height)
    page.appeared()
    button = page.element(page.ad + ' .pum-close')
    rect = button.rect
    viewport = page.driver.execute_script('return [innerWidth, innerHeight]')
    assert 0 <= rect['x'] and rect['x'] + rect['width'] <= viewport[0]
    top = page.driver.execute_script('return arguments[0].getBoundingClientRect().top', button)
    assert 0 <= top and top + rect['height'] <= viewport[1]
    page.close()


@allure.feature('Реклама')
@pytest.mark.negative
@allure.title('ADS-N01: Escape не закрывает рекламу')
def test_escape_ignored(page):
    page.appeared()
    page.escape()
    page.remains(page.ad)


@allure.feature('Реклама')
@pytest.mark.negative
@allure.title('ADS-N02: нажатие на подложку не закрывает рекламу')
def test_overlay_ignored(page):
    page.appeared()
    page.outside(page.ad)
    page.remains(page.ad)


@allure.feature('Реклама')
@pytest.mark.negative
@allure.title('ADS-N03: реклама блокирует нажатие на фоновую ссылку')
def test_background_blocked(page):
    page.appeared()
    link = page.element('main a')
    url = page.driver.current_url
    with pytest.raises(ElementClickInterceptedException):
        link.click()
    assert page.driver.current_url == url
    page.remains(page.ad)
