from datetime import date

import allure
import pytest
from pages.ui import Calendar


@pytest.fixture
def page(driver, settings):
    return Calendar(driver, settings).open('calendars')


@allure.feature('Календарь')
@pytest.mark.positive
@allure.title('CAL-P01: календарь открывается при нажатии на поле')
def test_open(page):
    page.click(page.field)
    assert page.element(page.picker).is_displayed()


@allure.feature('Календарь')
@pytest.mark.positive
@pytest.mark.parametrize('direction,reverse', [('next', 'prev'), ('prev', 'next')], ids=['CAL-P02', 'CAL-P03'])
@allure.title('Пагинация календаря: {direction} и возврат')
def test_month_navigation(page, direction, reverse):
    page.click(page.field)
    before = page.month()
    page.click('.dp-' + direction)
    page.wait.until(lambda _: page.month() != before)
    page.click('.dp-' + reverse)
    page.wait.until(lambda _: page.month() == before)


@allure.feature('Календарь')
@pytest.mark.positive
@pytest.mark.parametrize('month,day', [(1, 1), (12, 31), (4, 30), (2, 29)],
                         ids=['CAL-P04', 'CAL-P05', 'CAL-P06', 'CAL-P07'])
@allure.title('Выбор граничной даты: месяц {month}, день {day}')
def test_select_boundary_date(page, month, day):
    year = date.today().year
    if month == 2:
        while year % 4 or (year % 100 == 0 and year % 400 != 0):
            year += 1
    target = date(year, month, day)
    page.select(target)
    assert page.value() == target.isoformat()


@allure.feature('Календарь')
@pytest.mark.negative
@pytest.mark.parametrize('value', ['not-a-date', '2025-02-29', '2026-13-01'],
                         ids=['CAL-N01', 'CAL-N02', 'CAL-N03'])
@allure.title('Некорректная дата {value} отклоняется')
def test_invalid_date(page, value):
    page.enter(value)
    page.submit()
    page.rejected()
