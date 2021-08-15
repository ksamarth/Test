#Samarth Kamle
#ITP115, Spring2021
#this is the class for menuitem
class MenuItem(object):
    #init assigns all the values
    def __init__(self,name,category,price,desc):
        self.name = name
        self.category = category
        self.price = float(price)
        self.desc = desc
    #get methods to return appropriate variable
    def getName (self):
        return self.name
    def getCategory (self):
        return self.category
    def getPrice (self):
        return self.price
    def getDesc (self):
        return self.desc
    #in this str method we concatenate everything about the menu items
    def __str__(self):
        message = self.name+" ("+self.category+"): $"+str(self.price)+"\n"+self.desc
        return message