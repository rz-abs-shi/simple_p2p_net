from datetime import datetime


def print_time():
    print("Time: " + datetime.now().strftime('%H:%M:%S'))
