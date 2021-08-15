#Samarth Kamle
#ITP115, Spring2021
#import menuitem
from MenuItem import MenuItem
class Diner (object):
    #set statuses in a list
    STATUSES =  ["seated","ordering","eating","paying","leaving"]
    def __init__(self,dinerName):
       #set name to dinername, order to empty list, and status to zero
       self.name = dinerName
       self.order = []
       self.status = 0
    #get methods to return appropriate variables
    def getName(self):
           return self.name
    def getOrder(self):
           return self.order
    def getStatus(self):
           return self.status
    #update the status for each increment
    def updateStatus(self):
           self.status = self.status + 1
    #add the item to the list
    def addToOrder(self,menuItem):
           self.order.append(menuItem)
    #print the items that the customer bought
    def printOrder():
           print(self.name,"ordered:")
           for items in self.order:
               print(items)
    #update cost based on items that customer bought
    def getMealCost(self):
           totalCost = 0.0
           for item in self.order:
               totalCost += item.getPrice()
           return totalCost
    #str method to print customer status
    def __str__(self):
           dinerStatus = "Diner "+self.name+" is currently "+Diner.STATUSES[self.status]+"."
           return dinerStatus