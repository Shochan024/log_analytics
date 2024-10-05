#!-*-coding:utf-8-*-
import re
import os
import logging
import pandas as pd
from abc import ABC, abstractmethod

class LogFileBase(ABC):
  """
  Base class for extracting data from log files. Provides common functionality for
  reading log files, processing log lines, and exporting the results to a TSV file.

  Attributes:
      PID_PATTERN (re.Pattern): Regular expression pattern for matching process IDs (PID) in log lines.
      data_list (list): A list to store extracted data from the logs.
  """
  PID_PATTERN = re.compile(r'\[.*?\s(#\d{1,})\]')

  def __init__(self):
    """
    Initializes the ExtractBase class and sets up an empty data list to store
    extracted log data.
    """
    self.data_list = []
    self.logger = self.__get_logger()


  @abstractmethod
  def extract_additional_data(self, log_line):
    """
    Abstract method to be implemented by subclasses to extract custom data from the log line.
    This method is intended to be overridden in the subclass with the specific pattern matching logic.
    """
    pass


  def export_tsv(self, log_name_pattern, output_folder):
    """
    Exports the parsed log data to a TSV file in the specified output folder.

    This method scans through the 'logs' directory for files that match the provided
    log_name_pattern. For each matching log file, it extracts the relevant data and
    stores it in a DataFrame, which is then exported to a TSV file.

    Args:
        log_name_pattern (re.Pattern): A regular expression pattern to match log file names.
        output_folder (str): The folder where the output TSV file should be saved.

    Raises:
        OSError: If there is an issue with creating or accessing files/directories.

    Example:
        export_tsv(re.compile(r'production.log.\\d{6}'), 'output')
    """

    logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
    if not os.path.exists(logs_dir):
      self.logger.error(f'Log directory not found: {logs_dir}')
      return

    log_files = os.listdir(logs_dir)
    for log in log_files:
      match_flg = log_name_pattern.match(log)
      if match_flg:
        self.__convert_log_into_array(f'{logs_dir}/{log}')

    output_dir = os.path.join(os.path.dirname(__file__), '../tmp', output_folder)
    os.makedirs(output_dir, exist_ok=True)

    if self.data_list:
      df = pd.DataFrame(self.data_list)
      output_file_path = f'{output_dir}/{self.__class__.__name__.lower()}.tsv'
      with open(output_file_path, 'w', newline='') as f:
        df.to_csv(f, sep='\t', index=False)
      self.logger.info(f'Data exported to {output_file_path}')
    else:
      self.logger.warning('No data found to export')


  def _init_entity(self, log_line):
    """
    Extracts the PID and additional data from a log line. The additional data
    is provided by the subclass's extract_additional_data implementation.

    Args:
        log_line (str): A single line of log data.

    Returns:
        dataclass: A dataclass containing the extracted PID and additional data.
        None: If the log line does not match the expected patterns.
    """
    pid_match = self.PID_PATTERN.search(log_line)
    if not pid_match:
      return False

    additional_data = self.extract_additional_data(log_line)
    if additional_data is None:
      return False

    # Extract additional data from the subclass implementation
    additional_data.pid = pid_match.group(1)

    return additional_data

  def __get_logger(self):
    """
    Initializes and returns a logger instance that can be used in child classes.
    """
    logger = logging.getLogger(self.__class__.__name__)

    if not logger.hasHandlers():
      handler = logging.StreamHandler()
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)
      logger.addHandler(handler)
      logger.setLevel(logging.INFO)

    return logger


  def __convert_log_into_array(self, filename):
    """
    Reads a log file and processes each line to extract relevant data.

    This method opens the specified log file and iterates over each line. It
    calls the `_init_entity` method to parse the data from the line. If data is
    successfully extracted, it is added to the `data_list`.

    Args:
        filename (str): The path to the log file to be processed.

    Raises:
        OSError: If there is an error while opening the log file.
    """
    try:
      self.logger.info(f'Starting to process log file: {filename}')
      with open(filename, mode='r') as log_file:
        for line in log_file:
          entity = self._init_entity(line)
          if entity:
            self.data_list.append(entity)

        if not self.data_list:
          self.logger.warning(f'No data extracted from log file: {filename}')
    except OSError as e:
      self.logger.exception(f'Error opening file {filename}: {e}')
      raise
