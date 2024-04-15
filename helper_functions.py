import csv

def write_to_csv(data, filename):
  """
  Writes data to a CSV file

  Args:
      data: List of lists containing the data to write
      filename: The name of the file to write to
  """
  try:
    with open(filename, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerows(data)
  except Exception as e:
    print(f"Error writing data to CSV file: {e}")

