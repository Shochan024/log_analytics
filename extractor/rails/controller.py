#!-*-coding:utf-8-*-
import re
from extractor.log_file_base import LogFileBase
from dataclasses import dataclass

@dataclass
class DataStruct:
  """
  Data structure to hold parsed log information, specifically for controller-related entries.

  Attributes:
      pid (str): The process ID extracted from the log entry.
      controller_name (str): The name of the controller and action extracted from the log entry.
  """
  pid: str = None
  controller_name: str = None


class Controller(LogFileBase):
  """
  Controller class to extract controller action log data, specifically process ID (PID)
  and controller action names, from log entries.

  This class utilizes a regular expression to identify controller action patterns in log entries
  and inherits from the `ExtractBase` class to reuse its log processing functionality.
  """
  PATTERN = re.compile(r'[A-Za-z]*Controller\#[^\s]+')

  def __init__(self):
    """
    Initializes the Controller class and sets the data structure for parsed log entries.

    The `DataStruct` is used to store the PID and controller name from each log entry.
    """
    self.data_class = DataStruct
    super().__init__()


  def extract_additional_data(self, log_line):
    """
    Extracts controller name from the log line.

    Args:
        log_line (str): A single line of log data.

    Returns:
        DataStruct: A `DataStruct` object containing the extracted controller name and PID.
        None: If the controller name is not found.
    """
    match = self.PATTERN.search(log_line)
    if not match:
      return None

    return DataStruct(controller_name = match.group(0))

__all__ = ['Controller']
