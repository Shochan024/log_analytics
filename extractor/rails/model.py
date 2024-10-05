#!-*-coding:utf-8-*-
import re
import os
import inflect
import mysql.connector
from dotenv import load_dotenv
from extractor.log_file_base import LogFileBase
from dataclasses import dataclass

@dataclass
class DataStruct:
  """
  Data structure to hold the parsed log information, including the process ID (PID)
  and the class name of the ActiveRecord model involved.

  Attributes:
      pid (str): The process ID extracted from the log entry.
      class_name (str): The name of the ActiveRecord model involved in the log entry.
  """
  pid: str = None
  class_name: str = None


class Model(LogFileBase):
  """
  Model class to extract specific ActiveRecord model names and process IDs from log entries.

  This class uses a predefined regular expression pattern to identify the presence of
  ActiveRecord models, as well as the process ID (PID) from each log entry.

  Inherits from the ExtractBase class to utilize its log file handling capabilities.
  """
  PATTERN = None
  EXCLUDE_CLASS_NAMES = ['ArInternalMetadata', 'SchemaMigration']

  def __init__(self):
    """
    Initializes the Model class, setting the data structure for parsed log entries.

    The `DataStruct` is used to store the parsed PID and ActiveRecord model class names.
    """
    self.data_class = DataStruct
    self.inflect_engine = inflect.engine()
    self.PATTERN = self.__modelname_into_regexp()
    super().__init__()


  def extract_additional_data(self, log_line):
    """
    Extracts the model name from the log line.

    Args:
        log_line (str): A single line of log data.

    Returns:
        DataStruct: A dataclass containing the model name and PID.
        None: If the model name is not found.
    """
    if 'DEBUG' not in log_line:
      return None

    match = self.PATTERN.search(log_line)
    if not match:
      return None

    return DataStruct(class_name = match.group(0))


  def __modelname_into_regexp(self):
    """
    Retrieves table names from the database and constructs a regex pattern for model names.

    Returns:
        re.Pattern: A compiled regular expression for model names.
    """
    tables_taple = self.__get_model_name_from_db()
    table_names = [self.__to_camel_case_with_purlize(el[0]) for el in tables_taple]
    escaped_table_names = [re.escape(el) for el in table_names]
    filtered_list = list(filter(lambda el: el not in self.EXCLUDE_CLASS_NAMES, escaped_table_names))

    return re.compile('|'.join(filtered_list))


  def __to_camel_case_with_purlize(self, text):
    """
    Converts a given text to CamelCase and singularizes the words.

    Args:
        text (str): The input text (likely a table name) to be converted.

    Returns:
        str: The CamelCase and singularized version of the input text.
    """
    if text is None:
      return None

    words = text.replace('-', ' ').replace('_', ' ').split()
    singular_words = [self.inflect_engine.singular_noun(word) or word for word in words]

    return ''.join(word.capitalize() for word in singular_words)


  def __get_model_name_from_db(self):
    """
    Retrieves the model names (table names) from the MySQL database.

    Returns:
        list: A list of tuples containing table names.
    """

    connection = None
    db_operator = None

    try:
      connection = self.__connect()
      db_operator = connection.cursor()
      db_operator.execute('SHOW TABLES;')

      return db_operator.fetchall()
    except mysql.connector.ProgrammingError as e:
      self.logger.error(f'A ProgrammingError occurred: {e}')

    except mysql.connector.Error as e:
      self.logger.error(f'A MySQL error occurred: {e}')

    finally:
      if db_operator:
        db_operator.close()
      if connection and connection.is_connected():
        connection.close()


  def __connect(self):
    """
    Establishes a connection to the MySQL database using credentials from a .env file.

    Returns:
        mysql.connector.connection.MySQLConnection: The MySQL connection object.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')

    if load_dotenv(dotenv_path) is False:
      raise FileNotFoundError(f'Failed to load the .env file from {dotenv_path}')

    host = os.environ.get('HOST')
    user_name = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    db_name = os.environ.get('DB_NAME')

    if not all([host, user_name, password, db_name]):
      raise mysql.connector.EnvironmentError('Define the connection information in the .env file')

    try:
      conn = mysql.connector.connect(
        host = host,
        user = user_name,
        password = password,
        database = db_name
      )

      return conn
    except mysql.connector.Error as e:
      self.logger.error(f'Error connecting to MySQL: {e}')
      raise

__all__ = ['Model']
