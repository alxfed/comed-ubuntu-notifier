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


TIMEZONE = 'America/Chicago'
# see ZoneInfo documentation for details if necessary.
# https://docs.python.org/3/library/zoneinfo.html


def send_notification(urgency, title, message, icon='dialog-information'):
    """ Sends a Ubuntu® desktop notification using the notify-send command-line tool.
    """
    try:
        subprocess.run([
            'notify-send',
            '--icon=' + icon,
            '--urgency=' + urgency,
            title,
            message
        ], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: 'notify-send' command not found or failed.")
        print("Please install it with 'sudo apt install libnotify-bin'")


def read_prices():
    """ Download five-minute prices from ComEd® website, using
        the 'comed-prices' Python library.
        https://pypi.org/project/comed-prices/
    """
    now = datetime.now()
    time_20_min_ago = now - timedelta(minutes=20)
    time_format = "%Y%m%d%H%M"
    current_time_str = now.strftime(time_format)
    past_time_str = time_20_min_ago.strftime(time_format)

    # Read the prices in a time interval that would
    # return at least 3 prices.
    prices = five_minute_prices(
        start=past_time_str,
        end=current_time_str,
        tz=TIMEZONE)

    # report the time at which the prices were checked
    # and the program was working properly.
    print("Checked the prices at ", now.strftime("%H:%M"), "  local time")
    if len(prices) >= 3:
        # The API has returned 3 or more prices in the 20min interval.
        # Process the prices and a timestamp of the latest one.
        newest_price_record = prices[0]
        price = newest_price_record['price']
        time_stamp = newest_price_record['local_time']

        # Other prices for calculating the trend.
        previous_price = prices[1]['price']
        before_previous_price = prices[2]['price']

        return time_stamp,price, previous_price, before_previous_price

    elif len(prices) < 3:
        # Sometimes there are 'holes' in the data.
        # Process the price and a timestamp of the latest one.
        newest_price_record = prices[0]
        price = newest_price_record['price']
        time_stamp = newest_price_record['local_time']

        return time_stamp, price, price, price

    else:
        # The API has not returned any prices at all
        # (is not working properly).
        print("Error: API is not working properly, it has not returned any prices.")
        return now, 0, 0, 0


if __name__ == "__main__":
    """ Start from the command line in this directory 
        by running 'python3 main.py'.
    """
    print(f"Starting the ComEd® Ubuntu® desktop notifier in {TIMEZONE} at ", datetime.now().strftime("%H:%M"))
    while True:
        # Read the prices and a timestamp of the latest one
        time_stamp,price, before, before_before = read_prices()

        # Calculate the trend
        if price > before:
            trend = "up"
        else:
            trend = "down"

        # Send a particular notification if necessary.
        # Icons - at the end of https://wiki.ubuntu.com/UbuntuStudio/Artwork/UbuntuStudioIconSet
        if price >= 10.0:
            ''' Higher than 10 ¢/kWh
            '''
            send_notification(
                'normal', #'critical',
                f'({time_stamp.strftime("%H:%M")}) ComEd® price :  {price} ¢/kWh',
                f"Before: {before};  Before before: {before_before}.  Trend: {trend}",
                "weather-storm"
            )
            print(f"Sent a critical notification about price {price} ¢/kWh at ", time_stamp.strftime("%H:%M"))
        elif price >= 6.0:
            ''' Higher than 6 ¢/kWh but lower than 10 ¢/kWh
            '''
            send_notification(
                'normal',
                f'({time_stamp.strftime("%H:%M")}) ComEd® price :  {price} ¢/kWh',
                f"Before: {before};  Before before: {before_before}.  Trend: {trend}",
                "weather-severe-alert"
            )
            print(f"Sent a normal notification about price {price} ¢/kWh at ", time_stamp.strftime("%H:%M"))
        elif price >= 4.0:
            ''' Higher than 4 ¢/kWh but lower than 6 ¢/kWh
            '''
            send_notification(
                'normal',
                f'({time_stamp.strftime("%H:%M")}) ComEd® price :  {price} ¢/kWh',
                f"Before: {before};  Before before: {before_before}.  Trend: {trend}",
                "weather-few-clouds"
            )
            print(f"Sent a normal notification about price {price} ¢/kWh at ", time_stamp.strftime("%H:%M"))
        elif price >= 2.0:
            ''' Higher than 2 ¢/kWh
            '''
            send_notification(
                'low',
                f'({time_stamp.strftime("%H:%M")}) ComEd® price :  {price} ¢/kWh',
                f"Before: {before};  Before before: {before_before}.  Trend: {trend}",
                "weather-clear"
            )
            print(f"Sent a low urgency notification about price {price} ¢/kWh at ", time_stamp.strftime("%H:%M"))
        else:
            ''' Lower than 2 ¢/kWh
            '''
            send_notification(
                'low',
                f'({time_stamp.strftime("%H:%M")}) ComEd® price :  {price} ¢/kWh',
                f"Before: {before};  Before before: {before_before}.  Trend: {trend}",
                "weather-clear"
            )
            print(f"Sent a low urgency notification about the price {price} ¢/kWh at ", time_stamp.strftime("%H:%M"))

        time.sleep(253) # Wait for 5 minutes
