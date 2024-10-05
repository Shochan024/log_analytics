#!-*-coding:utf-8-*-
import os
import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style='whitegrid')

class Base:
  """
  Base class that provides common functionalities such as data loading, output generation,
  and logging for subclasses. This class is designed to be inherited by other classes
  that need to load data, generate visualizations, and log messages.

  Attributes:
      data_folder (str): The path to the folder where data files are stored.
      logger (logging.Logger): Logger for the class, set up to log messages to the console.

  Methods:
      __init__(data_folder): Initializes the class with a given data folder and sets up logging.
      _load_data(file_name): Loads tab-separated data from a file in the specified folder.
      _output_tsv(df, filename): Saves a pandas DataFrame as a TSV file in the specified output folder.
      _output_img(file_name): Saves the current matplotlib plot to a PNG file in the specified folder.
      __get_logger(): Initializes and returns a logger for logging messages.
  """
  def __init__(self, data_folder):
    """
    Initializes the Base class with the path to the data folder and sets up a logger.

    Args:
        data_folder (str): The path to the folder where data files are stored.
    """
    self.data_folder = data_folder
    self.logger = self.__get_logger()


  def _load_data(self, file_name):
    """
    Loads tab-separated data from the specified file within the data folder.

    Args:
        file_name (str): The name of the file to be loaded (assumed to be a TSV file).

    Returns:
        pandas.DataFrame: The loaded data as a DataFrame. If the file is not found,
        an empty DataFrame is returned, and an error is logged.
    """
    file_path = os.path.join('tmp', self.data_folder, file_name)
    try:
      return pd.read_csv(file_path, sep='\t')
    except FileNotFoundError:
      self.logger.error(f'Failed to load {file_path}')
      return pd.DataFrame()


  def _output_tsv(self, df, file_name):
    """
    Saves the given pandas DataFrame as a TSV (tab-separated values) file in the
    'outcomes' folder inside the data folder.

    Args:
        df (pandas.DataFrame): The DataFrame to be saved.
        file_name (str): The base name of the file (without extension) to save the DataFrame as.

    Returns:
        None
    """
    output_dir = os.path.join('tmp', self.data_folder, 'outcomes')
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f'{output_dir}/{file_name}.tsv', index=False)

    self.logger.info(f'{file_name} was exported to {output_dir}.')


  def _output_img(self, file_name):
    """
    Saves the current matplotlib plot as a PNG file in the specified output folder.
    The output folder is created if it doesn't already exist.

    Args:
        file_name (str): The base name of the file (without extension) to save the plot as.

    Returns:
        None
    """
    output_dir = os.path.join('tmp', self.data_folder, 'outcomes')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/{file_name}.png')
    plt.close()

    self.logger.info(f'{file_name}.png was exported to {output_dir}.')


  def __get_logger(self):
    """
    Initializes and returns a logger for the current class. The logger logs messages
    to the console with a specific format and logs at the INFO level by default.

    Returns:
        logging.Logger: The logger for the current class.
    """
    logger = logging.getLogger(self.__class__.__name__)

    if not logger.hasHandlers():
      handler = logging.StreamHandler()
      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
      handler.setFormatter(formatter)
      logger.addHandler(handler)
      logger.setLevel(logging.INFO)

    return logger
