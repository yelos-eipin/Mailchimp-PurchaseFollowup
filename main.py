from PFWClass import PFW
from helper_functions import write_to_csv
import configparser

def main():
  """
  Main function to fetch data and write to CSV
  """
  config = configparser.ConfigParser()
  config.read("config.ini")

  days_prior = 32  # Adjust as needed
  output_dir = config["OUTPUT"]["CSVOutputPath"]  # Get output path from config
  column_names = ["Branch", "Customer Name", "Email", "Purchase Date"]

  pfw = PFW()

  # Fetch and write parts data
  parts_data = pfw.get_parts_purchases(days_prior)
  if parts_data:
    write_to_csv(parts_data, f"{output_dir}/PartsPurchasesLast24Hours_FileOutput.csv", column_names)
  
  # Fetch and write equipment data
  equipment_data = pfw.get_equipment_purchases(days_prior)
  if equipment_data:
    write_to_csv(equipment_data, f"{output_dir}/EquipmentPurchasesLast24Hours_FileOutput.csv", column_names)

  # Fetch and write service data
  service_data = pfw.get_service_performed(days_prior)
  if service_data:
    write_to_csv(service_data, f"{output_dir}/ServicePerformedLast24Hours_FileOutput.csv", column_names)

if __name__ == "__main__":
  main()    