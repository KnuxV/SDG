import sys

import pyautogui as pgui
import time
import pyperclip
import os
from show_mouse_pos import setup_original_coordinates

pgui.FAILSAFE = True


def workaround_write(text):
    """
    This is a work-around for the bug in pyautogui.write() with non-QWERTY
    keyboards It copies the text to clipboard and pastes it, instead of
    typing it.
    """
    a = pyperclip.copy(text)
    pgui.hotkey('ctrl', 'v')
    a = pyperclip.copy('')


def main(coord: dict, setup_cord=False, start_pubs=1):
    """

    :param coord:
    :param setup_cord:
    :return:

    Args:
        start_pubs:
        start_pubs:
    """
    if not coord or setup_cord:
        coord = setup_original_coordinates()
    # To be changed if we don't start downloading from 1
    record_from = start_pubs
    record_to = record_from + 499
    # text_file_name
    root_file_name = 1
    end_file_name = "txt"
    total_number_pub = int(input("enter total number of publications :\n"))
    root_file_name = int(input("enter first title, 1 or whatever after the "
                               "first bunch of download : \n"))

    while record_from <= total_number_pub:  # To be updated every chunk
        # 1st step : click export + tab delimited file
        time.sleep(1)
        pgui.click(coord['export_position'], interval=0.5)
        # time.sleep(2)
        pgui.click(coord['tab_delimited_file_position'],
                   interval=0.5, button='left')
        # time.sleep(2)
        pgui.click(coord['records_from_button_position'])
        time.sleep(0.1)
        # First box
        pgui.click(coord['records_from_button_position_first_box'])
        time.sleep(0.1)
        # First, we need to empty the box from text
        for i in range(10):
            pgui.press("backspace", interval=0.1)
        # Then, we write the number
        pgui.keyDown('shift')
        pgui.write(str(record_from))
        pgui.keyUp('shift')
        # workaround_write(record_from)

        # Second box
        pgui.click(coord['records_from_button_position_second_box'])
        for i in range(10):
            pgui.press("backspace", interval=0.1)
        pgui.keyDown('shift')
        pgui.write(str(record_to))
        pgui.keyUp('shift')
        # workaround_write(record_to)

        time.sleep(1)
        pgui.click(coord['record_content'])
        time.sleep(1)
        pgui.click(coord['full_record_w_citations'])
        time.sleep(1)
        pgui.click(coord['export'])
        time.sleep(20)

        # need to click above the save button and wait a bit
        pgui.click(coord['above_save_button'])
        # time.sleep(1)
        # pgui.click(ok)

        # click on the text box, erase, and write new file name
        pgui.click(coord['text_box'])
        pgui.hotkey('ctrl', 'a')
        pgui.press('backspace')
        pgui.keyDown('shift')
        pgui.write(str(root_file_name))
        pgui.write('.')
        pgui.keyUp('shift')
        pgui.write(end_file_name)
        pgui.click(coord['save_button'])

        # Update variable
        print(f"Last downloaded: {record_from} to {record_to} in "
              f"{str(root_file_name) + '.' + end_file_name}")
        record_from += 500
        record_to += 500
        # Update this to handle the last thousand elements
        if record_to > total_number_pub:
            record_to = total_number_pub

        root_file_name += 1


if __name__ == "__main__":
    try:
        setup = eval(sys.argv[1])
        start_pubs = int(sys.argv[2])
    except:
        setup = False
        start_pubs = 1
    coordinates = {'export_position': (1235, 596), 'tab_delimited_file_position': (1282, 864), 'records_from_button_position': (1148, 738), 'records_from_button_position_first_box': (1218, 750), 'records_from_button_position_second_box': (1305, 751), 'record_content': (1116, 871), 'full_record': (1102, 940), 'full_record_w_citations': (1103, 977), 'export': (1080, 932), 'above_save_button': (1598, 1148), 'ok': (1447, 253), 'text_box': (1492, 256), 'save_button': (1849, 256)}

    coord_big_pc = {'export_position': (1240, 555),
                    'tab_delimited_file_position': (1337, 794),
                    'records_from_button_position': (1118, 747),
                    'records_from_button_position_first_box': (1242, 748),
                    'records_from_button_position_second_box': (1320, 745),
                    'record_content': (1350, 872),
                    'full_record': (1363, 953),
                    'full_record_w_citations': (1358, 987),
                    'export': (1096, 940), 'above_save_button': (1571, 1149),
                    'ok': (1619, 1134), 'text_box': (1713, 377),
                    'save_button': (1786, 1152)}

    office_half_screen = {'export_position': (720, 552), 'tab_delimited_file_position': (592, 797), 'records_from_button_position': (352, 809), 'records_from_button_position_first_box': (468, 813), 'records_from_button_position_second_box': (552, 806), 'record_content': (354, 947), 'full_record': (378, 1006), 'full_record_w_citations': (328, 1038), 'export': (332, 1002), 'above_save_button': (802, 949), 'ok': (1074, 963), 'text_box': (995, 176), 'save_button': (1080, 959)}

    main(coordinates, setup_cord=setup, start_pubs=start_pubs)
    os.system("shutdown")
