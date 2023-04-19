""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
import datetime
import re
import hashlib
from datetime import date
import os
import image_lib
import inspect
import sys
import sqlite3
import apod_api

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['image_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    #Complete function body
    apod_date = date.fromisoformat('2022-12-25')
    if len(sys.argv) == 1:
        apod_date = date.today()
    if len(sys.argv) == 2:
        apod_date = date.today().strftime('%Y-%m-%d')
        try:
            apod_date = date.fromisoformat(sys.argv[1])
        except:
            sys.exit(1)
        if apod_date > date.today():
            print("Error cannot do a date in the fucher")
        elif apod_date < date(1995,6,16):
            print("Error cannot do a date pass 1995-6-16")
    if len(sys.argv) >= 3:
        print('Error too many arguments')
        sys.exit(1)
    print('Date suscclefully collected')
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    # Determine the path of the image cache directory
    image_cache_dir = os.path.join(parent_dir,'image_cache')
    # Create the image cache directory if it does not already exist
    if os.path.exists(image_cache_dir):
        print('image_cache_dir is there')
    elif os.mkdir(image_cache_dir):
        print('image_cache_dir was made')


        
    # Determine the path of image cache DB
    image_cache_db = os.path.join(image_cache_dir, 'apod.db')
    # Create the DB if it does not already exist
    if os.path.exists(image_cache_db):
        print(f'image_cache_db is a there')
    else:
        con = sqlite3.connect(image_cache_db)
        cur = con.cursor()
        # SQL query that creates a table named 'apod'.
        create_apod_tbl_query = """
            CREATE TABLE IF NOT EXISTS apod
            (
                id INTEGER PRIMARY KEY,
                apod_title TEXT NOT NULL,
                apod_explanation TEXT NOT NULL,
                image_path TEXT NOT NULL,
                hash_value TEXT NOT NULL
            );
        """
        # Execute the SQL query to create the 'apod' table.
        cur.execute(create_apod_tbl_query)
        con.commit()
        con.close()

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """

    # Download the APOD information from the NASA API
    apod_info = apod_api.get_apod_info(apod_date)

    # Download the APOD image
    apod_url = apod_api.get_apod_image_url(apod_info)
    image_data = image_lib.download_image(apod_url)
    
    # Check whether the APOD already exists in the image cache
    hash_value = hashlib.sha256(image_data).hexdigest()
    hash_checker = get_apod_id_from_db(hash_value)
    # Save the APOD file to the image cache directory
    apod_title = apod_info['title']
    apod_explanation =  apod_info['explanation']
    
    if hash_checker != 0:
        return hash_checker
    elif hash_checker == 0:
        apod_path = determine_apod_file_path(apod_title, apod_url)
        image_lib.save_image_file(image_data, apod_path)
        add_apod_path = add_apod_to_db(apod_title, apod_explanation, apod_path, hash_value)
        return add_apod_path
    else:
        return 0



def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # Complete function body
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    add_apod_query = """
        INSERT INTO apod
        (
            apod_title,
            apod_explanation,
            image_path,
            hash_value
        )
        VALUES (?, ?, ?, ?);
    """
    new_image = (title, explanation, file_path, sha256)   
    new_image_cash = cur.execute(add_apod_query, new_image)
    con.commit()
    con.close()
    new_image_cash_last = new_image_cash.lastrowid
    if new_image_cash_last:
        return new_image_cash_last
    else:
        return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # Complete function body
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    apod_qurey = f"""
            SELECT id FROM apod WHERE hash_value ='{image_sha256}'
        """
    cur.execute(apod_qurey)
    apod_qurey_reults = cur.fetchone()
    con.close()
    if apod_qurey_reults is not None:
        return apod_qurey_reults[0]
    else:
        return 0

def determine_apod_file_path(apod_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body
    apod_image= '.' + image_url.split('.')[-1]
    apod_title = apod_title.strip()
    apod_title = re.sub(r'\s+', '', apod_title)
    apod_title = re.sub(r'[^\w\d]', '', apod_title)
    apod_path = os.path.join(image_cache_dir, apod_title + apod_image)


    return apod_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # Query DB for image info
    con = sqlite3.connect(image_cache_db)
    cur = con.cursor()
    apod_query = f""" SELECT apod_title, apod_explanation, image_path
                      FROM apod
                      Where id='{image_id}'
    """

    cur.execute(apod_query)
    apod_query_results = cur.fetchone()
    con.close()

    # Put information into a dictionary
    apod_info = {
        'apod_title': apod_query_results[0], 
        'apod_explanation': apod_query_results[1],
        'image_path': apod_query_results[2],
    }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    return

if __name__ == '__main__':
    main()