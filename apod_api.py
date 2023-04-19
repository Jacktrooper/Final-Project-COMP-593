'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
from datetime import date
import datetime

NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"

def main():
    # TODO: Add code to test the functions in this module
    apod_date = datetime.date(2022, 2, 21)
    apod_info = get_apod_info(apod_date)
    if apod_info:
        print(apod_info["title"])
        apod_image_url = get_apod_image_url(apod_info)
        print(apod_image_url)

    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    if isinstance(apod_date, str):
        apod_date = date.today().strftime('%Y-%m-%d')
    params = {'date': apod_date, 'api_key': '6kNeT0r4ipbCnx8rfwsbdbuVZHhISOc12kABGNS5'}
    response = requests.get(NASA_APOD_URL, params=params)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        print(f"Failed to get APOD info for {apod_date}")
        return None  

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict['hdurl']
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict['thumbnail_url']
    else:
        print("Unknown media type for APOD")
        return None


if __name__ == '__main__':
    main()