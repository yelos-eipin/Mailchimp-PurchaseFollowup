import csv

def write_to_csv(data, filename, column_names=None):
  """
  Writes data to a CSV file

  Args:
      data: List of lists containing the data to write
      filename: The name of the file to write to
  """
  try:
    with open(filename, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile)
      if column_names:
          writer.writerow(column_names)  # Write header row with column names
      writer.writerows(data)
  except Exception as e:
    print(f"Error writing data to CSV file: {e}")

