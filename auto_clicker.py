import pyautogui as pgui
import time
import pyperclip

from show_mouse_pos import setup_original_coordinates


def workaround_write(text):
    """
    This is a work-around for the bug in pyautogui.write() with non-QWERTY keyboards
    It copies the text to clipboard and pastes it, instead of typing it.
    """
    pyperclip.copy(text)
    pgui.hotkey('ctrl', 'v')
    pyperclip.copy('')


# pgui.PAUSE = 2.5
pgui.FAILSAFE = True

# positional variables // TO BE CHANGED IF REUSED, using mouse_pos.py

res_cord = setup_original_coordinates()
export_position = (923, 540)
tab_delimited_file_position = (920, 814)
records_from_button_position = (752, 652)
records_from_button_position_first_box = (916, 651)
records_from_button_position_second_box = (1006, 645)
record_content = (1071, 779)
full_record = (1076, 860)
full_record_w_citations = (1086, 891)
export = (785, 845)
above_save_button = (1259, 934)
ok = (1468, 943)
text_box = (1419, 173)
save_button = (1482, 949)

export_position = res_cord[0]
tab_delimited_file_position = res_cord[1]
records_from_button_position = res_cord[2]
records_from_button_position_first_box = res_cord[3]
records_from_button_position_second_box = res_cord[4]
record_content = res_cord[5]
full_record = res_cord[6]
full_record_w_citations = res_cord[7]
export = res_cord[8]
above_save_button = res_cord[9]
ok = res_cord[10]
text_box = res_cord[11]
save_button = res_cord[12]
# To be changed if we don't start downloading from 1
record_from = 1
record_to = 1000
# text_file_name
root_file_name = 1
end_file_name = ".txt"

if __name__ == "__main__":
    total_number_pub = int(input("enter total number of publications :\n"))
    root_file_name = int(input("enter first title, 1 or whatever after the first bunch of download : \n"))
    while record_from <= total_number_pub:  # To be updated every chunk
        # 1st step : click export + tab delimited file
        time.sleep(1)
        pgui.click(export_position, interval=0.5)
        # time.sleep(2)
        pgui.click(tab_delimited_file_position, interval=0.5, button='left')
        # time.sleep(2)
        pgui.click(records_from_button_position)
        time.sleep(0.1)
        # First box
        pgui.click(records_from_button_position_first_box)
        time.sleep(0.1)
        # First, we need to empty the box from text
        for i in range(10):
            pgui.press("backspace", interval=0.1)
        # Then, we write the number
        # pgui.keyDown('shift')
        # pgui.write(str(record_from))
        # pgui.keyUp('shift')
        workaround_write(record_from)

        # Second box
        pgui.click(records_from_button_position_second_box)
        for i in range(10):
            pgui.press("backspace", interval=0.1)
        # pgui.keyDown('shift')
        # pgui.write(str(record_to))
        # pgui.keyUp('shift')
        workaround_write(record_to)

        time.sleep(1)
        pgui.click(record_content)
        time.sleep(1)
        pgui.click(full_record)
        time.sleep(1)
        pgui.click(export)
        time.sleep(20)

        # need to click above the save button and wait a bit
        pgui.click(above_save_button)
        # time.sleep(1)
        # pgui.click(ok)

        # click on the text box, erase, and write new file name
        pgui.click(text_box)
        pgui.hotkey('ctrl', 'a')
        pgui.press('backspace')
        pgui.keyDown('shift')
        pgui.write(str(root_file_name))
        pgui.write(end_file_name)
        pgui.keyUp('shift')
        pgui.click(save_button)

        # Update variable
        print(f"Last downloaded: {record_from} to {record_to} in {root_file_name}")
        record_from += 1000
        record_to += 1000
        # Update this to handle the last thousand elements
        if record_to > total_number_pub:
            record_to = total_number_pub

        root_file_name += 1
