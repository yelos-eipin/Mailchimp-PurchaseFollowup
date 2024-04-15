from PFWClass import PFW

myPFW = PFW()

myPFW._PFW__connect()

data = myPFW.get_parts_purchases(1)
print(data)