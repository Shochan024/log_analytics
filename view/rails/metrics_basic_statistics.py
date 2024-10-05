#!-*-coding:utf-8-*-
from view.base import Base

class MetricsBasicStatistics(Base):
  """
  A class to handle basic statistics for metrics data, inheriting common functionality
  from the Base class, such as data loading and exporting TSV files.

  This class is responsible for calculating summary statistics for selected metrics
  (views, duration, allocation) based on specific PIDs, and exporting the results as a TSV file.

  Methods:
      __init__(): Initializes the class by calling the parent class constructor.
      export_tsv(group_pids, filename): Exports summary statistics for metrics data (for selected PIDs)
                                        to a TSV file.
  """
  def __init__(self, data_folder):
    """
    Initializes the MetricsBasicStatistics class by calling the constructor of the Base class.
    """
    super().__init__(data_folder)


  def export_tsv(self, group_pids, filename):
    """
    Exports basic statistics (mean, std, min, max, etc.) for selected metrics (views, duration, allocation)
    based on the specified group of PIDs. The results are saved as a TSV file.

    Args:
        group_pids (list): A list of PIDs to filter the data and calculate summary statistics.
        filename (str): The name of the file (without extension) to save the summary statistics.

    Returns:
        None
    """
    df = self._load_data('metrics.tsv')

    # Filter the DataFrame to include only rows where 'pid' is in group_pids
    grouped_df = df.query(f'pid in {group_pids}')[['views', 'duration', 'allocation']]

    # Generate summary statistics and round to 2 decimal places
    metrics_summary = grouped_df.describe().round(2).reset_index()

    self._output_tsv(metrics_summary, filename)

__all__ = ['MetricsBasicStatistics']
