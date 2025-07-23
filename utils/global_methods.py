"""
Centralized global methods for generative agents.
Contains utility functions used throughout the project.
"""
import random
import string
import csv
import time
import datetime as dt
import pathlib
import os
import sys
import numpy
import math
import shutil, errno
from typing import List, Dict, Any, Union, Optional
from pathlib import Path

from os import listdir

def create_folder_if_not_there(curr_path: str) -> bool: 
    """
    Checks if a folder in the curr_path exists. If it does not exist, creates
    the folder. 
    Note that if the curr_path designates a file location, it will operate on 
    the folder that contains the file. But the function also works even if the 
    path designates to just a folder. 
    
    Args:
        curr_path: Path to check/create
        
    Returns: 
        True: if a new folder is created
        False: if a new folder is not created
    """
    outfolder_name = curr_path.split("/")
    if len(outfolder_name) != 1: 
        # This checks if the curr path is a file or a folder. 
        if "." in outfolder_name[-1]: 
            outfolder_name = outfolder_name[:-1]

        outfolder_name = "/".join(outfolder_name)
        if not os.path.exists(outfolder_name):
            os.makedirs(outfolder_name)
            return True

    return False 

def write_list_of_list_to_csv(curr_list_of_list: List[List[str]], out_fname: str) -> None:
    """
    Takes a list of list and saves it to a csv file.
    
    Args:
        curr_list_of_list: list to write. The list comes in the following form:
                          [['key1', 'val1-1', 'val1-2'...],
                           ['key2', 'val2-1', 'val2-2'...],]
        out_fname: name of the csv file to write    
    """
    create_folder_if_not_there(out_fname)
    with open(out_fname, "w") as f:
        writer = csv.writer(f)
        for row in curr_list_of_list: 
            writer.writerow(row)

def read_file_to_list(curr_file: str, header: bool = False, strip_trail: bool = True) -> List[List[str]]:
    """
    Reads in a csv file to a list of list. If header is True, it returns a 
    tuple where the first element is the header list, and the second element is
    the content in list of list. 
    
    Args:
        curr_file: name of the csv file to read
        header: if True, treat the first line as a header
        strip_trail: if True, strip trailing newlines and spaces
        
    Returns:
        Content of the csv file in list of list form. 
    """
    analysis_list = []
    if header: 
        header_list = []

    if os.path.exists(curr_file): 
        with open(curr_file, "r", encoding='utf-8') as f_analysis_file:
            data_reader = csv.reader(f_analysis_file, delimiter=",")
            if header: 
                header_list = next(data_reader)
            for row in data_reader:
                if strip_trail: 
                    row = [i.strip() for i in row]
                analysis_list += [row]

    if header: 
        return (header_list, analysis_list)
    else: 
        return analysis_list

def read_file_to_set(curr_file: str, col: int = 0) -> set:
    """
    Reads in a file and extracts a particular column into a set.
    
    Args:
        curr_file: name of the file to read
        col: column index to extract (default: 0)
        
    Returns:
        Set containing values from the specified column
    """
    curr_set = set()
    if os.path.exists(curr_file): 
        with open(curr_file, "r") as f_analysis_file:
            data_reader = csv.reader(f_analysis_file, delimiter=",")
            for row in data_reader:
                if len(row) > col:
                    curr_set.add(row[col].strip())
    return curr_set

def check_if_file_exists(curr_file: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(curr_file)

def find_filenames(path_to_dir: str, suffix: str = "") -> List[str]:
    """
    Given a directory, returns all filenames (with extensions) in the directory
    with the specified suffix.
    
    Args:
        path_to_dir: Path to the directory
        suffix: File suffix to filter by (e.g., ".txt")
        
    Returns:
        List of filenames
    """
    filenames = listdir(path_to_dir)
    if suffix:
        return [filename for filename in filenames if filename.endswith(suffix)]
    return filenames

def copyanything(src: str, dst: str) -> None:
    """
    Copy a file or directory tree from src to dst.
    
    Args:
        src: Source path
        dst: Destination path
    """
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy2(src, dst)
        else: 
            raise

def get_random_alphanumeric(i: int = 6, j: int = 6) -> str:
    """
    Returns a random alphanumeric string with length between i and j.
    
    Args:
        i: minimum length
        j: maximum length
        
    Returns:
        Random alphanumeric string
    """
    k = random.randint(i, j)
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
    return x

def make_new_datetime_str() -> str:
    """
    Creates a new datetime string for use in file names.
    
    Returns:
        Datetime string in format: YYYYMMDD_HHMMSS
    """
    curr_datetime = dt.datetime.now()
    datetime_str = f"{curr_datetime.year:04d}{curr_datetime.month:02d}{curr_datetime.day:02d}_"
    datetime_str += f"{curr_datetime.hour:02d}{curr_datetime.minute:02d}{curr_datetime.second:02d}"
    return datetime_str

def convert_datetime_str_to_datetime(datetime_str: str) -> dt.datetime:
    """
    Convert datetime string back to datetime object.
    
    Args:
        datetime_str: Datetime string in format YYYYMMDD_HHMMSS
        
    Returns:
        datetime object
    """
    year = int(datetime_str[:4])
    month = int(datetime_str[4:6])
    day = int(datetime_str[6:8])
    hour = int(datetime_str[9:11])
    minute = int(datetime_str[11:13])
    second = int(datetime_str[13:15])
    
    return dt.datetime(year, month, day, hour, minute, second)

def calculate_time_diff(start_datetime: Union[str, dt.datetime], 
                       end_datetime: Union[str, dt.datetime]) -> float:
    """
    Calculate time difference in seconds between two datetime objects or strings.
    
    Args:
        start_datetime: Start time
        end_datetime: End time
        
    Returns:
        Time difference in seconds
    """
    if isinstance(start_datetime, str):
        start_datetime = convert_datetime_str_to_datetime(start_datetime)
    if isinstance(end_datetime, str):
        end_datetime = convert_datetime_str_to_datetime(end_datetime)
    
    return (end_datetime - start_datetime).total_seconds()

def convert_string_to_datetime(datetime_str: str) -> Optional[dt.datetime]:
    """
    Convert various datetime string formats to datetime object.
    
    Args:
        datetime_str: Datetime string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d_%H%M%S",
        "%Y%m%d",
        "%H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return dt.datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    return None

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with fallback.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with fallback.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def normalize_path(path: str) -> str:
    """
    Normalize a file path for cross-platform compatibility.
    
    Args:
        path: File path to normalize
        
    Returns:
        Normalized path
    """
    return str(Path(path).resolve())

def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (including the dot)
    """
    return Path(filename).suffix

def get_file_stem(filename: str) -> str:
    """
    Get file name without extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        File name without extension
    """
    return Path(filename).stem