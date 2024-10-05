#!-*-coding:utf-8-*-
import re
from extractor.rails import Controller, Metrics, Model
from view.rails import SystemLoadGraph, MetricsBasicStatistics
from invoke import task

@task
def export_rails_log_data(c, data_folder, rails_env='production'):
  """
  Task to export Rails log data for controller, metrics, and model logs, filtered by the environment (e.g., production).

  This task processes logs by extracting data for the Controller, Metrics, and Model. The log file pattern is based
  on the specified Rails environment, and the extracted data is saved in TSV format within the specified data folder.

  Args:
      c (invoke.Context): Invoke context object, automatically passed when the task is called.
      data_folder (str): The folder where the extracted log data will be saved.
      rails_env (str, optional): The Rails environment to filter log files (default is 'production').

  Returns:
      None
  """
  log_name_pattern = re.compile(rf'{rails_env}.log.\d{{6}}')

  # Loop through each class (Controller, Metrics, Model) to export data
  for cls in [Controller, Metrics, Model]:
    try:
      instance = cls()
      instance.export_tsv(log_name_pattern, data_folder)
    except Exception as e:
      print(f'Error exporting data for {cls.__name__}: {e}')


@task
def export_rails_system_load_graph(c, data_folder, exclude_empty_flg=True):
  """
  Task to generate and export system load graphs based on model and metrics data.

  This task generates three types of graphs:
  1. Model frequency graph: Displays histograms that show the frequency of different model class names per PID.
  2. Metrics boxplot: Displays boxplots to visualize the distribution of views, duration, and allocation per PID.
  3. Metrics bar charts: Displays bar charts summarizing the total views, duration, and allocation per PID.

  The graphs are generated using data from TSV files located in the specified data folder. The results are then saved
  as image files within the same folder. The task also includes an option to exclude empty rows when generating
  the metrics bar charts.

  Args:
      c (invoke.Context): Invoke context object, automatically passed when the task is called.
      data_folder (str): The folder where the system load graphs will be saved.
      exclude_empty_flg (bool, optional): Flag to exclude rows where all metrics are 0 when generating the metrics bar charts.
                                          Default is True.

  Returns:
      None
  """

  # Create an instance of SystemLoadGraph to generate the required graphs
  view_obj = SystemLoadGraph(data_folder)
  view_obj.model_freq_graph()
  view_obj.metrics_boxplot()
  view_obj.metrics_graph(exclude_empty_flg=exclude_empty_flg)


@task
def export_rails_metrics_statistics(c, data_folder, group_pids, file_name):
  """
  Task to export basic statistics for Rails metrics data, filtered by a group of PIDs.

  This task generates summary statistics (mean, standard deviation, min, max, etc.) for the metrics data (views, duration,
  and allocation) based on a specified group of PIDs. The results are saved in TSV format.

  Args:
      c (invoke.Context): Invoke context object, automatically passed when the task is called.
      data_folder (str): The folder where the statistics data will be saved.
      group_pids (list): A list of PIDs to filter the metrics data for statistical calculations.
      file_name (str): The name of the file (without extension) to save the statistics data as.

  Returns:
      None
  """

  # Create an instance of MetricsBasicStatistics to export summary statistics
  view_obj = MetricsBasicStatistics(data_folder)
  view_obj.export_tsv(group_pids, file_name)
