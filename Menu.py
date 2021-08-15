#Samarth Kamle
#ITP115, Spring2021
#importing menuitem
from MenuItem import MenuItem
class Menu(object):
    #assign categories
    CATEGORIES = ["Drink","Appetizer","Entree","Dessert"]
    def __init__(self, file):
        #EXTRA CREDIT: dictionary to store empty lists
        self.items = {"Drink": [], "Appetizer": [], "Entree": [], "Dessert": []}
        #open file
        fileItems = open(file, "r")
        #for each item in the file, strip the line. then split it upon the comma to get the individual items then store in list
        for item in fileItems:
            stripLine = item.strip()
            eachItem = stripLine.split(",")
            menuItems =  MenuItem(eachItem[0], eachItem[1],eachItem[2],eachItem[3])
            self.items[menuItems.getCategory()].append(menuItems)
        #close file
        fileItems.close()
    def getMenuItem(self,itemCategory,categoryIndex):
        #error checking
        if itemCategory in Menu.CATEGORIES:
            #only return if position is within the 0-3 range and if the position is less than the length of the index
            if  categoryIndex >= 0 and categoryIndex <= 3 and categoryIndex < len(self.items[itemCategory]):
                return self.items[itemCategory][categoryIndex]
    def getNumMenuItems(self,itemCategory):
        #if the category is in the categories, return its length
        if itemCategory in Menu.CATEGORIES:
            return len(self.items[itemCategory])
        #if its not then return 0
        elif itemCategory not in Menu.CATEGORIES:
            return 0
    def printMenuItems(self, itemCategory):
        #error checking to see if category is in the earlier set CATEGORIES
        if itemCategory in Menu.CATEGORIES:
            print("-----"+itemCategory+"-----")
        numberofItems = self.getNumMenuItems(itemCategory)
        #print out the option choices
        for number in range(numberofItems):
            print(str(number)+")",str(self.items[itemCategory][number]))

