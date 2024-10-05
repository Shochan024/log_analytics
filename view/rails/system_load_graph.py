#!-*-coding:utf-8-*-
import seaborn as sns
import matplotlib.pyplot as plt
from view.base import Base

class SystemLoadGraph(Base):
  """
  SystemLoadGraph class is responsible for visualizing system load data such as model frequency
  and metrics (views, duration, allocation) per PID. The class inherits from the Base class
  which provides common data loading and output functionalities.

  Methods:
      __init__(data_folder): Initializes the class with a given data folder.
      model_freq_graph(col_wrap=4, height=3): Displays histograms of model class frequency per PID.
      metrics_graph(exclude_empty_flg=True): Displays bar charts summarizing views, duration, and allocation metrics per PID.
      metrics_boxplot(): Displays boxplots for views, duration, and allocation metrics.
      __box_plot(axis, data_list, title, labels): Helper method to create boxplots with x-axis labels.
      __plot_bar(axis, df, columns, title, color=None): Helper method to create bar charts for the given data.
  """
  def __init__(self, data_folder):
    """
    Initializes the SystemLoadGraph class with the path to the data folder.

    Args:
        data_folder (str): The path to the folder where data files are stored.
    """
    super().__init__(data_folder)


  def model_freq_graph(self, col_wrap=4, height=3):
    """
    Loads model data from a TSV file and creates a grid of histograms showing the
    frequency of different model class names for each PID.

    Args:
        col_wrap (int): Number of columns in the FacetGrid. Default is 4.
        height (int): Height of each facet in the grid. Default is 3.

    Returns:
        None: If the model data is empty, it logs a warning and skips the visualization.
    """
    df = self._load_data('model.tsv')
    if df.empty:
      self.logger.warning('Model data is empty, skipping display_model_freq')
      return

    grid = sns.FacetGrid(df, col='pid', col_wrap=col_wrap, height=height, sharex=True, sharey=True)
    grid.map_dataframe(sns.histplot, y='class_name')

    self._output_img('model_freq_per_pid')


  def metrics_graph(self, exclude_empty_flg=True):
    """
    Loads metrics data from a TSV file and creates two bar charts. The first chart shows
    the sum of views and duration per PID, and the second chart shows the sum of allocation per PID.

    Returns:
        None: If the metrics data is empty, it logs a warning and skips the visualization.
    """
    df = self._load_data('metrics.tsv')
    if df.empty:
      self.logger.warning('Metrics data is empty, skipping display_metrics')
      return

    # Auto adjust the figure width
    uniq_pid_count = df['pid'].unique().shape[0]
    width_unit = uniq_pid_count // 12

    fig, ax = plt.subplots(2, 1, figsize=(10 * width_unit, 10))

    grouped_df = df.groupby('pid').sum().reset_index()

    # Exclude empty dataframe
    if exclude_empty_flg:
      grouped_df = grouped_df[(grouped_df[['views', 'duration', 'allocation']] != 0).any(axis=1)]

    self.__plot_bar(axis=ax[0], df=grouped_df, columns=['views', 'duration'], title='Sum of Views and Duration per PID')
    self.__plot_bar(axis=ax[1], df=grouped_df, columns=['allocation'], title='Sum of Allocation per PID', color='orange')

    # Adjust the interval between ax[0] and ax[1].
    fig.tight_layout()

    self._output_img('metrics_per_pid')


  def metrics_boxplot(self):
    """
    Loads metrics data from a TSV file and creates boxplots for views, duration, and allocation per PID.

    The first boxplot visualizes views and duration, and the second boxplot shows allocation.
    X-axis labels are added to improve interpretability of the metrics.

    Returns:
        None: If the metrics data is empty, it logs a warning and skips the visualization.
    """
    df = self._load_data('metrics.tsv')

    fig, ax = plt.subplots(2, 1, figsize=(10, 10))
    self.__box_plot(ax[0], [df['views'], df['duration']], 'Views and Duration Boxplot per pid', ['views', 'duration'])
    self.__box_plot(ax[1], [df['allocation']], 'Allocation Boxplot per pid', ['allocation'])

    # Adjust the interval between ax[0] and ax[1].
    fig.tight_layout()

    self._output_img('metric_boxplot')


  def __box_plot(self, axis, data_list, title, labels):
    """
    Helper method to create a boxplot for the given data and add x-axis labels.

    Args:
        axis (matplotlib.axes.Axes): The axis on which to plot the boxplot.
        data_list (list): A list of data to plot in the boxplot.
        title (str): The title of the boxplot.
        labels (list): A list of labels for the x-axis corresponding to the data columns.

    Returns:
        None
    """
    axis.boxplot(data_list)
    axis.set_title(title)
    axis.set_xticklabels(labels)


  def __plot_bar(self, axis, df, columns, title, color=None):
    """
    Helper method to plot a bar chart for the given data columns.

    Args:
        axis (matplotlib.axes.Axes): The axis on which to plot the bar chart.
        df (pandas.DataFrame): The dataframe containing the data to plot.
        columns (list): A list of column names to plot.
        title (str): The title of the bar chart.
        color (str or list, optional): The color(s) to use for the bars. Default is None.

    Returns:
        None
    """
    df.set_index('pid')[columns].plot(kind='bar', ax=axis, color=color)
    axis.set_title(title)
    axis.set_xlabel('PID')
    axis.set_ylabel('Sum')
    axis.set_xticklabels(axis.get_xticklabels(), rotation=45)


__all__ = ['SystemLoadGraph']
