import pyautogui as pgui
import time


def print_position():
    """
    print mouse position,
    :return: nothing
    """
    try:
        while True:
            x, y = pgui.position()
            print(x, y)
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n')


def setup_original_coordinates():
    dic_pos = {
        'export_position': (923, 510),
        'tab_delimited_file_position': (970, 730),
        'records_from_button_position': (775, 621),
        'records_from_button_position_first_box': (929, 613),
        'records_from_button_position_second_box': (1002, 608),
        'record_content': (1051, 735),
        'full_record': (1071, 800),
        'full_record_w_citations': (876, 873),
        'export': (770, 788),
        'above_save_button': (1298, 934),
        'ok': (1222, 833),
        'text_box': (1459, 175),
        'save_button': (1485, 947),
    }

    for pos_name, pos in dic_pos.items():
        print(f"Position mouse on '{pos_name}'")
        if pos_name == "above_save_button":
            time.sleep(7)
        else:
            time.sleep(3)
        x, y = pgui.position()
        dic_pos[pos_name] = (x, y)

    print(dic_pos)
    for pos_name, pos in dic_pos.items():
        print(f'{pos_name} = {pos}')
    return dic_pos


if __name__ == "__main__":
    # setup_original_coordinates()
    print_position()