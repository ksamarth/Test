#Samarth Kamle
#ITP115, Spring2021
#import statements
from Menu import Menu
from Diner import Diner
class Waiter(object):
    #set diners to empty list, and menu to menu that is being passed through
    def __init__(self, menu):
        self.diners = []
        self.menu = menu
    def addDiner(self, dinerName):
        #append diner name to diner list
        self.diners.append(dinerName)
    def getNumDiners(self):
        #find number of diners
        return len(self.diners)
    def printDinerStatuses(self):
        statusLength = len(Diner.STATUSES)
        #for each status that is there in list, find the customers that are currently in that status
        for status in range(statusLength):
            #print customer that is in the given status
            print("Diners who are",Diner.STATUSES[status]+":")
            for customer in self.diners:
                if customer.getStatus() == status:
                    print(customer)
    def takeOrders(self):
        for customer in self.diners:
            #if the customer status is ordering
            if customer.getStatus() ==1:
                menuLength = range(len(Menu.CATEGORIES))
                #for each item in menu, print out the menu and ask customer to input selection
                for items in menuLength:
                    self.menu.printMenuItems(Menu.CATEGORIES[items])
                    print(customer.getName() + ", please select a",Menu.CATEGORIES[items],"menu item number.")
                    optionInput = int(input("> "))
                    #set a range in which the input must me
                    optionsRange = range(0, self.menu.getNumMenuItems(Menu.CATEGORIES[items]))
                    #set to false
                    optionSelection = False
                    while optionSelection == False:
                        #if the input is in the given range, set to true
                        if optionInput in optionsRange:
                            optionSelection = True
                        #if not, then ask user for input again
                        else:
                            optionSelection = False
                            print("Please enter a valid option:")
                            optionInput = int(input("> "))
                    #add to list of the option that customer ordered
                    customer.addToOrder(self.menu.getMenuItem(Menu.CATEGORIES[items], int(optionInput)))
                print(customer.getName(),"ordered: ")
                #print items that customer ordered
                for orderedItems in menuLength:
                    print("- " + str(customer.getOrder()[orderedItems]))
    def getMealCost(self):
        for customer in self.diners:
            #if customer status is paying, then print their meal cost. round float to two decimals
            if customer.getStatus() == 3:
                print(customer.getName()+", your meal cost is $" + "{:.2f}".format(customer.getMealCost()))
    def removeDiners(self):
        for customer in self.diners:
            #if customer status is leaving, tell goodbye and remove them from customer list
            if customer.getStatus() == 4:
                print(customer.getName() + ", thank you for dining with us! Come again soon!")
                self.diners.remove(customer)
    def advanceDiners(self):
        #for each increment, move the diner status along
        self.printDinerStatuses()
        self.takeOrders()
        self.getMealCost()
        self.removeDiners()
        for diner in self.diners:
            diner.updateStatus()
