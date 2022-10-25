"""
V3 of the Web of Science autoclicker based on Selenium
"""

# Imports
import locale
import sys
import time
import pathlib
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, \
    StaleElementReferenceException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def click_button(driver, elem_path, how):
    path = elem_path
    if how == "xpath":
        elem = driver.find_element(By.XPATH, path)
    elif how == "id":
        elem = driver.find_element(By.ID, path)
    elif how == "name":
        elem = driver.find_element(By.NAME, path)
    else:
        raise Exception("this find_element method was not implemented")

    overlap = get_overlapping_element(driver=driver,
                                      element=elem)
    try:
        elem.click()
    except:
        if overlap:
            driver.execute_script("arguments[0].click();", overlap)


def wait_for_elem(driver, elem_path, how="id"):
    i_e = (NoSuchElementException, StaleElementReferenceException)
    if how == "id":
        WebDriverWait(driver, timeout=180, ignored_exceptions=i_e) \
            .until(lambda d: d.find_element(By.ID, elem_path))
    elif how == "xpath":
        WebDriverWait(driver, timeout=180, ignored_exceptions=i_e) \
            .until(lambda d: d.find_element(By.XPATH, elem_path))
    elif how == "name":
        WebDriverWait(driver, timeout=180, ignored_exceptions=i_e) \
            .until(lambda d: d.find_element(By.NAME, elem_path))


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


def login_wos(driver,
              ini_path="https://www-webofscience-com.scd-rproxy.u-strasbg.fr/"
                       "wos/woscc/advanced-search"):
    driver.get(ini_path)

    # el = WebDriverWait(driver, timeout=180).until(
    #     lambda d: d.find_element(By.NAME, 'username'))
    wait_for_elem(driver, "username", how="name")

    username = driver.find_element(By.NAME, 'username')
    password = driver.find_element(By.NAME, "password")

    username.send_keys('michoud')
    password.send_keys("Uy5MMm1<>hzL5k8")

    submit_button = driver.find_element(By.NAME, 'submit')
    submit_button.click()

    wait_for_elem(driver, "onetrust-reject-all-handler", how="id")
    reject_all_button = driver.find_element(By.ID,
                                            "onetrust-reject-all-handler")
    reject_all_button.click()

    wait_for_elem(driver, "advancedSearchInputArea", how="id")


def enter_query(driver, query):
    advanced_search = driver.find_element(By.ID, "advancedSearchInputArea")
    advanced_search.clear()
    advanced_search.send_keys(query, Keys.ENTER)


def get_total_pub(driver) -> int:
    """
    OBSOLETE, BUT SHOULD WORK
    :param driver:
    :return:
    """
    other_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/" \
                 "app-input-route/app-base-summary-component/div/div[2]/" \
                 "app-page-controls[1]/div/app-export-option/div/" \
                 "mat-checkbox/label/span[2]"
    wait_for_elem(driver, elem_path=other_path, how="xpath")
    total_pub = driver.find_element(By.XPATH, other_path)

    total_pub_value = total_pub.text
    total_pub_value = total_pub_value.split("/")[-1]
    print(total_pub_value)
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
    time.sleep(2)
    export_button_path = "/html/body/app-wos/main/div/div/div[2]/div/div/" \
                         "div[2]/app-input-route/app-base-summary-component/" \
                         "div/div[2]/app-page-controls[1]/div/" \
                         "app-export-option/div/app-export-menu/div/button"
    wait_for_elem(driver, export_button_path, how="xpath")
    click_button(driver, export_button_path, "xpath")
    """export_button = driver.find_element(By.XPATH, export_button_path)
    try:
        export_button.click()
    except:
        # clicking on overlapping element
        driver.execute_script("arguments[0].click();",
                              get_overlapping_element(driver, export_button))"""

    wait_for_elem(driver, "exportToTabWinButton", how="id")
    click_button(driver, elem_path="exportToTabWinButton", how="id")

    """tab_delimited_button = driver.find_element(By.ID, "exportToTabWinButton")
    tab_delimited_button.click()"""


    # click on record from

    path = '//*[@id="radio3-input"]'
    wait_for_elem(driver, path, how="xpath")
    click_button(driver, path, "xpath")
    """record_from_circle_all = driver.find_element(By.XPATH, path)
    overlap = get_overlapping_element(driver=driver,
                                      element=record_from_circle_all)
    driver.execute_script("arguments[0].click();", overlap)"""

    # click on record from
    path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/" \
           "app-input-route[1]/app-export-overlay/div/div[3]/div[2]/" \
           "app-export-out-details/div/div[2]/form/div/fieldset/" \
           "mat-radio-group/div[3]/mat-radio-button/label/span[1]/span[3]"
    """record_from_circle = driver.find_element(By.XPATH, path)
    overlap = get_overlapping_element(driver=driver, element=record_from_circle)
    driver.execute_script("arguments[0].click();", overlap)"""
    click_button(driver, path, how="xpath")

    # mat input increased by one after each iteration, for 2nd batch
    # mat-input-3 and mat-input-4 for 2nd box
    # So we define mat-input as a modulo 500 from end_pub which starts at 500
    # We also take the round up number so that the last download is correct
    def return_input(num):
        nb = int(2 * np.ceil(num / 500))
        return nb - 1, nb

    # First box
    first_box = driver.find_element(By.ID,
                                    f"mat-input-{return_input(end_pub)[0]}")
    first_box.clear()
    first_box.send_keys(int(start_pub))

    # Second box
    second_box = driver.find_element(By.ID,
                                     f"mat-input-{return_input(end_pub)[1]}")
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

    # Clicking on export
    test_path = '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/' \
                'app-input-route[1]/app-export-overlay/div/div[3]/div[2]/' \
                'app-export-out-details/div/div[2]/form/div/div[2]/' \
                'button[1]/span[1]'
    """    final_export_button = driver.find_element(By.XPATH, test_path)

    overlap_export = get_overlapping_element(driver=driver,
                                             element=final_export_button)
    if overlap_export:
        driver.execute_script("arguments[0].click();", overlap_export)
    else:
        final_export_button.click()"""
    click_button(driver=driver, elem_path=test_path, how="xpath")
    # waiting till pop-up windows is gone before starting a new cycle
    window_path = "/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/" \
                  "app-input-route[1]/app-export-overlay/div/div[3]"
    WebDriverWait(driver, timeout=180).until_not(
        lambda d: d.find_element(By.XPATH, window_path))
    print("Closing window...")


def download_pubs(driver, total_pub, citations=True):
    record_from = 1
    if citations:
        revolution = 500
        record_to = revolution
    else:
        revolution = 500
        record_to = revolution

    while record_to <= total_pub:
        print(f"Downloading publications from {record_from} to {record_to}.")
        download_batch(driver, start_pub=record_from, end_pub=record_to,
                       citations=citations)
        record_from += revolution
        record_to += revolution

        if record_to > total_pub:
            print("last download of the batch")
            print(record_from, int(total_pub))
            download_batch(driver, start_pub=record_from, end_pub=total_pub,
                           citations=citations)


def run_download_sdg(sdg: int, target_lst=()):
    """
    :param sdg:
    :param target_lst: if == empty tuple, we download all targets from SDG
    :return: nothing, but will download all publications in said target/sdg
    """
    sdg_name = "SDG" + str(sdg)
    # getting query excel sheet
    df_query = pd.read_excel("query/aurora_wos_v2_extra.xlsx",
                             sheet_name=sdg_name, index_col=0).iloc[1:, :]
    print(df_query.Target.to_list())
    for ind, row in df_query.iterrows():
        # unpacking from excel
        target, description, query, query_wos, total_pub, *links = row.to_list()

        if target in target_lst or target_lst == '0':
            print(
                f"Downloading SDG{sdg}\ntarget = {target}\ntotal_pubs = "
                f"{int(total_pub)}")
            if total_pub < 100000:

                run_download_target(
                    address="https://www-webofscience-com.scd-rproxy.u"
                            "-strasbg.fr"
                            "/wos/woscc/advanced-search",
                    sdg_name=sdg_name, target=target, query=query_wos,
                    total_pub=total_pub)
            else:
                # If more than 100k pubs, we have special queries from the Excel
                # that split the download with custom dates.
                print("Above 100k pubs, special queries activated")
                links = [link for link in links if str(link) != 'nan']
                for ind_link, link in enumerate(links):
                    print(f"Batch number {ind_link + 1} out of {len(links)}")

                    run_download_target(address=link, sdg_name=sdg_name,
                                        target=target, query=None,
                                        total_pub=total_pub)


def run_download_target(address, sdg_name, target, query, total_pub):
    path = f"/home/kevin-work/PycharmProjects/SDG_DST/data/raw/raw_sdg/" \
           f"{sdg_name}/{target.replace(' ', '')}"
    options = set_download_folder_firefox(path)
    driver = set_driver(options=options)
    login_wos(driver=driver, ini_path=address)
    if query:
        # when more than 100k pubs, there's no query but custom ini_path
        enter_query(driver=driver, query=query)

    download_pubs(driver, total_pub=total_pub, citations=True)
    driver.close()


if __name__ == '__main__':
    try:
        sdg_number = int(sys.argv[1])
        target_lst = sys.argv[2:]
        if target_lst[0] == '0':
            target_lst = '0'
        else:
            target_lst = tuple(target_lst)
        print(target_lst)
    except:
        print("Need arguments 1= SDG number 2+ = target names")

    run_download_sdg(sdg_number, target_lst=target_lst)