#!-*-coding:utf-8-*-
import re
from extractor.log_file_base import LogFileBase
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class DataStruct:
  """
  Data structure to hold parsed log metrics.

  Attributes:
      pid (str): Process ID extracted from the log.
      views (Decimal): Time spent rendering views, in milliseconds.
      duration (Decimal): Time spent in ActiveRecord operations, in milliseconds.
      allocation (int): Number of allocations.
  """
  pid: str = None
  views: Decimal = None
  duration: Decimal = None
  allocation: int = None


class Metrics(LogFileBase):
  """
  Metrics class to extract and parse log data related to views, ActiveRecord operations,
  and allocations from log files.

  This class inherits from `ExtractBase` and provides custom logic to extract
  specific metrics such as views, ActiveRecord duration, and allocations from log entries.
  """
  VIEWS_PATTERN = re.compile(r'Views: (\d+)(?:\.(\d+))?ms')
  DURATION_PATTERN = re.compile(r'ActiveRecord: (\d+)(?:\.(\d+))?ms')
  ALLOCATION_PATTERN = re.compile(r'Allocations: (\d+)')

  def __init__(self):
    """
    Initializes the Metrics class and sets the data structure for parsed log entries.

    The `DataStruct` is used to store the metrics extracted from each log line.
    """
    self.data_class = DataStruct
    super().__init__()


  def extract_additional_data(self, log_line):
      """
      Extracts views, ActiveRecord duration, and allocations from the log line.

      Args:
          log_line (str): A single line of log data.

      Returns:
          DataStruct: A `DataStruct` object containing the extracted metrics.
          None: If the metrics are not found.
      """
      if 'INFO' not in log_line:
        return None

      # Extract metrics using regular expressions
      views_match = self.VIEWS_PATTERN.search(log_line)
      duration_match = self.DURATION_PATTERN.search(log_line)
      allocation_match = self.ALLOCATION_PATTERN.search(log_line)

      # If the required metrics are missing, return None
      if not all([views_match]):
        return None

      views = self.__extract_decimal(views_match) if views_match else None
      duration = self.__extract_decimal(duration_match) if duration_match else None
      allocation = int(allocation_match.group(1)) if allocation_match else None

      return DataStruct(views = views, duration = duration, allocation = allocation)


  def __extract_decimal(self, match):
    """
    Converts the matched groups for views or ActiveRecord duration to a Decimal value.

    Args:
        match (re.Match): A match object containing the extracted numerical groups from the log.

    Returns:
        Decimal: A decimal representation of the extracted time in milliseconds.
    """
    decimal_part = match.group(2) if match.group(2) else '0'
    return Decimal(f'{match.group(1)}.{decimal_part}')

__all__ = ['Metrics']
