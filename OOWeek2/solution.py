class Room:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def __str__(self):
        return f'{self.name}, {self.size}m'


class House:

    def __init__(self):
        self.House = {}
        self.rooms = []

    def add_rooms(self,*houserooms):

        for eachroom in houserooms:
            self.House.setdefault(eachroom.name, eachroom.size)
            self.rooms.append(eachroom.name)


    def size(self):
        return sum([self.House[key] for key in self.House])

    def __str__(self):
       return 'House:' + '\n' + '\n' .join([f'{k}, {v}m' for k, v in self.House.items()])



if __name__ == "__main__":
    house = House()
    # print(house.size())
    # bedroom1 = Room('bedroom1', 10)
    # bedroom2 = Room('bedroom2', 5)
    # kitchen = Room('kitchen', 9)
    # bathroom = Room('bathroom', 3)
    # house.add_rooms(bedroom1,bedroom2, kitchen, bathroom)
    for i in range(10):
        house.add_rooms(Room(f'bedroom {i}', 15))
    for i in range(5):
        house.add_rooms(Room(f'bathroom {i}', 3))
    for i in range(3):
        house.add_rooms(Room(f'kitchen {i}', 3))

    print(house.size())
    print(house.rooms)
    print(len(house.rooms))
    print(house)















