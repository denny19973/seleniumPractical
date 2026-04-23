import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def browser():
    # 建立 Chrome 設定（用來關閉干擾測試的功能）
    options = Options()

    # 使用乾淨環境
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")

    # 關閉瀏覽器儲存密碼與提示視窗（避免遮擋元素導致測試失敗）
    prefs = {
        # 關閉「是否要儲存密碼」的提示
        "credentials_enable_service": False,
        # 關閉 Chrome 內建密碼管理器
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    # 建立獨立 profile
    options.add_argument("--user-data-dir=/tmp/selenium_profile")

    # 關閉自動化提示
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 使用 webdriver-manager 自動下載並管理 ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://www.saucedemo.com/")
    yield driver
    driver.quit()


# 失敗自動截圖
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("browser")
        if driver:
            screenshot = driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"{item.name}_fail",
                attachment_type=allure.attachment_type.PNG
            )
