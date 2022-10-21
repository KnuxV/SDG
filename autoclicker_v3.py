"""
V3 of the Web of Science autoclicker based on Selenium
"""

# Imports
import locale
import time
import pathlib
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def wait_for_elem(driver, elem_path, how="id"):
    if how == "id":
        WebDriverWait(driver, timeout=180).until(
            lambda d: d.find_element(By.ID, elem_path))
    elif how == "xpath":
        WebDriverWait(driver, timeout=180).until(
            lambda d: d.find_element(By.XPATH, elem_path))
    elif how == "name":
        WebDriverWait(driver, timeout=180).until(
            lambda d: d.find_element(By.NAME, elem_path))


def get_overlapping_element(driver, element):
    """

    :param driver:
    :param element:
    :return: the overlapping element or None
    """
    rect = element.rect
    result = driver.execute_script(
        "return document.elementFromPoint(arguments[0], arguments[1]);",
        rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2)
    if result == element:
        result = None
    return result


def set_download_folder_firefox(folder_path):
    """

    :param folder_path:
    :return: update the option of the firefox driver so that publications
    are automatically saved to the given folder
    """
    p = pathlib.Path(folder_path)
    p.mkdir(parents=True, exist_ok=True)
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", folder_path)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/x-gzip/txt/csv")
    return options


def set_driver(options):
    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options)
    return driver


def login_wos(driver):
    path = "https://www-webofscience-com.scd-rproxy.u-strasbg.fr/wos/woscc" \
           "/advanced-search "
    driver.get(path)

    # el = WebDriverWait(driver, timeout=180).until(
    #     lambda d: d.find_element(By.NAME, 'username'))
    wait_for_elem(driver, "username", how="name")

    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, "password")

    username.send_keys('michoud')
    password.send_keys("Uy5MMm1<>hzL5k8")

    submit_button = driver.find_element(By.NAME, 'submit')
    submit_button.click()

    # WebDriverWait(driver, timeout=180).until(
    #     lambda d: d.find_element(By.ID, "onetrust-reject-all-handler"))
    wait_for_elem(driver, "onetrust-reject-all-handler", how="id")
    reject_all_button = driver.find_element(By.ID,
                                            "onetrust-reject-all-handler")
    reject_all_button.click()

    # WebDriverWait(driver, timeout=180).until(
    #     lambda d: d.find_element(By.ID, "advancedSearchInputArea"))
    wait_for_elem(driver, "advancedSearchInputArea", how="id")


def enter_query(driver, query):
    advanced_search = driver.find_element(By.ID, "advancedSearchInputArea")
    advanced_search.send_keys(query, Keys.ENTER)


def get_total_pub(driver) -> int:
    total_pub_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[" \
                     "2]/app-input-route/app-base-summary-component/app" \
                     "-search-friendly-display/div[" \
                     "1]/app-general-search-friendly-display/h1/span "
    total_pub = driver.find_element(By.XPATH, total_pub_path)
    total_pub_value = total_pub.text

    return locale.atoi(total_pub_value)


def download_batch(driver, start_pub, end_pub, citations=True):
    """
    Single cycle of download, aka 1000 for non citation batch,
    or 500 if citations
    :param driver:
    :param start_pub:
    :param end_pub: start_pub+499
    :param citations: with or without citations
    :return:
    """
    export_button_path = "/html/body/app-wos/main/div/div/div[" \
                         "2]/div/div/div[" \
                         "2]/app-input-route/app-base-summary" \
                         "-component/div/div[" \
                         "2]/app-page-controls[ " \
                         "1]/div/app-export-option/div/app" \
                         "-export " \
                         "-menu/div/button/span[1]"
    wait_for_elem(driver, export_button_path, how="xpath")
    export_button = driver.find_element(By.XPATH, export_button_path)
    export_button.click()
    # WebDriverWait(driver, timeout=180).until(
    #     lambda d: d.find_element(By.ID, "exportToTabWinButton"))

    wait_for_elem(driver, "exportToTabWinButton", how="id")
    tab_delimited_button = driver.find_element(By.ID, "exportToTabWinButton")
    tab_delimited_button.click()

    # click on record from
    record_from_circle = driver.find_element(By.ID, "radio3-input")
    overlap = get_overlapping_element(driver=driver, element=record_from_circle)
    driver.execute_script("arguments[0].click();", overlap)

    # First box
    first_box = driver.find_element(By.ID, "mat-input-1")
    first_box.clear()
    first_box.send_keys(int(start_pub))
    # Second box
    second_box = driver.find_element(By.ID, "mat-input-2")
    second_box.clear()
    second_box.send_keys(int(end_pub))

    # Clicking on
    record_content_path = "/html/body/app-wos/main/div/div/div[" \
                          "2]/div/div/div[2]/app-input-route[" \
                          "1]/app-export-overlay/div/div[3]/div[" \
                          "2]/app-export-out-details/div/div[2]/form/div/div[" \
                          "1]/wos-select/button "
    record_content = driver.find_element(By.XPATH, record_content_path)
    record_content.click()

    if citations:
        citations_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[" \
                         "2]/app-input-route[1]/app-export-overlay/div/div[" \
                         "3]/div[2]/app-export-out-details/div/div[" \
                         "2]/form/div/div[1]/wos-select/div/div/div[2]/div[4] "
    else:
        citations_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[" \
                         "2]/app-input-route[1]/app-export-overlay/div/div[" \
                         "3]/div[2]/app-export-out-details/div/div[" \
                         "2]/form/div/div[1]/wos-select/div/div/div[2]/div[3] "
    full_content = driver.find_element(By.XPATH, citations_path)
    full_content.click()

    final_export_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[" \
                        "2]/app-input-route[1]/app-export-overlay/div/div[" \
                        "3]/div[2]/app-export-out-details/div/div[" \
                        "2]/form/div/div[2]/button[1] "
    final_export_button = driver.find_element(By.XPATH, final_export_path)
    overlap_export = get_overlapping_element(driver=driver,
                                             element=final_export_button)
    if overlap_export:
        driver.execute_script("arguments[0].click();", overlap_export)
    else:
        final_export_button.click()
    time.sleep(1)


def download_pubs(driver, total_pub, citations=True):
    record_from = 1
    if citations:
        record_to = record_from + 499
    else:
        record_to = record_from + 999

    while record_to <= total_pub:
        download_batch(driver, start_pub=record_from, end_pub=record_to,
                       citations=citations)
        record_from += 500
        record_to += 500

        if record_to > total_pub:
            record_to = total_pub


def run_download():
    pass
