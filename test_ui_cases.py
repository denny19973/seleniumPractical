import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import login


@allure.title("TC_001 驗證使用正確帳密可成功登入")
def test_valid_login(browser):
    login(browser)
    assert "inventory.html" in browser.current_url


@allure.title("TC_002 驗證錯誤帳號密碼時顯示錯誤提示")
def test_invalid_login(browser):
    browser.find_element(By.ID, "user-name").send_keys("wrong_user")
    browser.find_element(By.ID, "password").send_keys("wrong_pass")
    browser.find_element(By.ID, "login-button").click()
    login_error_msg = browser.find_element(
        By.CLASS_NAME, "error-message-container").text
    assert "Username and password do not match" in login_error_msg or "Epic sadface" in login_error_msg


@allure.title("TC_003 驗證點擊 'Add to cart' 後商品會進入購物車")
def test_add_to_cart(browser):
    login(browser)
    browser.find_elements(By.CLASS_NAME, "btn_inventory")[0].click()
    cart_count = browser.find_element(
        By.CLASS_NAME, "shopping_cart_badge").text
    assert cart_count == "1"


@allure.title("TC_04 驗證在結帳頁面未填寫資料時，系統會攔截並顯示錯誤訊息")
def test_login_fail_screenshot(browser):
    login(browser)
    browser.find_elements(By.CLASS_NAME, "btn_inventory")[0].click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    browser.find_element(By.ID, "checkout").click()
    browser.find_element(By.ID, "continue").click()
    checkout_error_msg = browser.find_element(
        By.CLASS_NAME, "error-message-container").text
    assert "Error: First Name is required" in checkout_error_msg
    assert "checkout-step-one.html" in browser.current_url


@allure.title("TC_05 驗證結帳頁面商品價格相加跟下方總價一樣")
def test_cart_price_total(browser):
    login(browser)

    browser.find_elements(By.CLASS_NAME, "btn_inventory")[0].click()
    browser.find_elements(By.CLASS_NAME, "btn_inventory")[1].click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    browser.find_element(By.ID, "checkout").click()
    browser.find_element(By.ID, "first-name").send_keys("Test")
    browser.find_element(By.ID, "last-name").send_keys("User")
    browser.find_element(By.ID, "postal-code").send_keys("12345")
    browser.find_element(By.ID, "continue").click()

    # 取得所有商品價格加總
    prices = browser.find_elements(By.CLASS_NAME, "inventory_item_price")
    total_calculated = sum(float(p.text.replace("$", "")) for p in prices)

    # 頁面顯示的總金額
    total_displayed_text = browser.find_element(
        By.CLASS_NAME, "summary_subtotal_label").text
    total_displayed = float(total_displayed_text.replace("Item total: $", ""))

    # 驗證兩者是否一致
    assert abs(total_calculated - total_displayed) < 0.01, \
        f"金額不符：計算總和 {total_calculated}，顯示為 {total_displayed}"


@allure.title("TC_06 驗證從購物車移除商品後商品不再顯示")
def test_remove_item_from_cart(browser):
    login(browser)
    browser.find_elements(By.CLASS_NAME, "btn_inventory")[0].click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    browser.find_element(By.CLASS_NAME, "cart_button").click()
    cart_items = browser.find_elements(By.CLASS_NAME, "cart_item")
    assert len(cart_items) == 0, "商品尚未成功從購物車移除"


@allure.title("TC_07 驗證價格排序（高到低）是否正確")
def test_price_sort_high_to_low(browser):
    login(browser)
    # 導入selenium提供控制下拉選單Select
    from selenium.webdriver.support.ui import Select
    Select(browser.find_element(By.CLASS_NAME,
           "product_sort_container")).select_by_value("hilo")
    prices = [float(p.text.replace("$", "")) for p in browser.find_elements(
        By.CLASS_NAME, "inventory_item_price")]
    assert prices == sorted(prices, reverse=True)


@allure.title("TTC_08 驗證商品名稱可進入詳細頁並能返回清單頁")
def test_product_detail_and_back(browser):
    login(browser)
    first_item = browser.find_elements(By.CLASS_NAME, "inventory_item_name")[0]
    name = first_item.text
    first_item.click()
    assert browser.find_element(
        By.CLASS_NAME, "inventory_details_name").text == name
    browser.find_element(By.ID, "back-to-products").click()
    assert "inventory" in browser.current_url


@allure.title("TC_09 驗證頁面上關鍵元件存在、可見、可互動")
def test_ui_elements_interactable(browser):
    login(browser)
    cart_icon = browser.find_element(By.ID, "shopping_cart_container")
    sort_dropdown = browser.find_element(
        By.CLASS_NAME, "product_sort_container")
    add_button = browser.find_elements(By.CLASS_NAME, "btn_inventory")[0]
    # 使用Selenium中is_enabled()，is_displayed()來判斷
    assert cart_icon.is_displayed() and cart_icon.is_enabled()
    assert sort_dropdown.is_displayed() and sort_dropdown.is_enabled()
    assert add_button.is_displayed() and add_button.is_enabled()


@allure.title("TC_010 驗證結帳流程在 5 秒內完成")
def test_checkout_performance(browser):
    login(browser)
    browser.find_elements(By.CLASS_NAME, "btn_inventory")[0].click()
    browser.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    browser.find_element(By.ID, "checkout").click()
    browser.find_element(By.ID, "first-name").send_keys("Speed")
    browser.find_element(By.ID, "last-name").send_keys("Tester")
    browser.find_element(By.ID, "postal-code").send_keys("12345")
    # 使用time.time()取得當下的時間，這是計時的起點，代表「點擊結帳」之前的時間。
    start_time = time.time()
    browser.find_element(By.ID, "continue").click()
    # Selenium 的顯性等待（Explicit Wait）
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.ID, "finish")))
    browser.find_element(By.ID, "finish").click()
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "complete-header")))
    # 紀錄結帳流程完成時的時間點
    end_time = time.time()
    assert end_time - start_time <= 5
