import os
import platform
from pathlib import Path

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService


def pytest_addoption(parser):
    parser.addoption('--browser', choices=['chrome', 'firefox'], default='chrome')
    parser.addoption('--headed', action='store_true')
    parser.addoption('--container', action='store_true', help='Chrome в изолированном контейнере')
    parser.addoption('--base-url', default='https://practice-automation.com')
    parser.addoption('--timeout', type=float, default=20)


@pytest.fixture
def driver(request):
    browser = request.config.getoption('--browser')
    options = webdriver.ChromeOptions() if browser == 'chrome' else webdriver.FirefoxOptions()
    if not request.config.getoption('--headed'):
        options.add_argument('--headless=new' if browser == 'chrome' else '-headless')
    if browser == 'chrome' and request.config.getoption('--container'):
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    if os.getenv('BROWSER_BINARY'):
        options.binary_location = os.environ['BROWSER_BINARY']
    service_cls = ChromeService if browser == 'chrome' else FirefoxService
    service = service_cls(executable_path=os.environ['DRIVER_PATH']) if os.getenv('DRIVER_PATH') else service_cls()
    factory = webdriver.Chrome if browser == 'chrome' else webdriver.Firefox
    instance = factory(options=options, service=service)
    request.node.ui_driver = instance
    instance.set_window_size(1440, 1000)
    instance.set_page_load_timeout(45)
    yield instance
    instance.quit()


@pytest.fixture
def settings(request):
    return request.config.getoption('--base-url'), request.config.getoption('--timeout')


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    instance = getattr(item, 'ui_driver', None)
    if report.failed and instance is not None:
        try:
            allure.attach(instance.get_screenshot_as_png(), 'Состояние при ошибке', allure.attachment_type.PNG)
            allure.attach(instance.current_url, 'URL', allure.attachment_type.TEXT)
            allure.attach(instance.page_source, 'HTML', allure.attachment_type.HTML)
        except Exception as error:
            allure.attach(str(error), 'Ошибка получения диагностики', allure.attachment_type.TEXT)


def pytest_sessionfinish(session, exitstatus):
    directory = Path(session.config.option.allure_report_dir or 'allure-results')
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'environment.properties').write_text(
        f'Browser={session.config.getoption("--browser")}\n'
        f'Base.URL={session.config.getoption("--base-url")}\n'
        f'Python={platform.python_version()}\n', encoding='utf-8')
