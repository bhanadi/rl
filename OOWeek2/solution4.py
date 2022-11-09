class Room:
    def __init__(self,name,size):
        self.name = name
        self.size = size

    def __str__(self):
        return f'{self.name}, {self.size}m'


class House:

    def __init__(self):
        self.rooms = []

    def add_rooms(self, *houserooms):
        for eachroom in houserooms:
            self.rooms.append(eachroom)


    def __str__(self):
        return f'{self.room}'



if __name__ == "__main__":
    house = House()
    bedroom = Room('bedroom', 10)
    kitchen = Room('kitchen', 9)
    bathroom = Room('bathroom', 3)
    print(bedroom)
    house.add_rooms(bedroom,kitchen,bathroom)
    print(str(house))
    # print(len(house.rooms))














