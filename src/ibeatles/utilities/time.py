import datetime

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_current_time_in_special_file_name_format():
    """format the current date and time into something like  04m_07d_2022y_08h_06mn"""
    current_time = datetime.datetime.now().strftime("%mm_%dd_%Yy_%Hh_%Mmn")
    return current_time
