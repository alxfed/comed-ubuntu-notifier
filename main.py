# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""

import subprocess
import time
from datetime import datetime, timedelta
from comed_prices import five_minute_prices


def send_notification(title, message, icon='dialog-information'):
    """
    Sends a desktop notification using the notify-send command-line tool.
    """
    try:
        subprocess.run([
            'notify-send',
            '--icon=' + icon,
            title,
            message
        ], check=True)
        # print("Notification sent successfully via notify-send.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'notify-send' command not found or failed.")
        print("Please install it with 'sudo apt install libnotify-bin'")


def read_prices():
    now = datetime.now()
    time_20_min_ago = now - timedelta(minutes=20)
    time_format = "%Y%m%d%H%M"
    current_time_str = now.strftime(time_format)
    past_time_str = time_20_min_ago.strftime(time_format)
    prices = five_minute_prices(
        start=past_time_str,
        end=current_time_str,
        tz='America/Chicago')
    print("Checked at ", now.strftime("%H:%M"))
    price = prices[0]['price']
    previous_price = prices[1]['price']
    before_previous_price = prices[2]['price']
    return price, previous_price, before_previous_price


if __name__ == "__main__":
    print("Starting background notification loop (using notify-send)...")
    count = 1
    while True:
        price, before, before_before = read_prices()
        if price > before:
            trend = "up"
        else:
            trend = "down"
        if price >= 2.0:
            send_notification(
                f"ComEd price: {price} cents/kWh",
                f"Before: {before}.  Trend: {trend}",
                # "utilities-system-monitor" # A different standard icon
            )
            print("Notified at ", datetime.now().strftime("%H:%M"))
        time.sleep(3000) # Wait for 30 seconds
