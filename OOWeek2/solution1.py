class Room:
    def __init__(self,name,size):
        self.name = name
        self.size = size

    def __str__(self):
        return f'{self.name}, {self.size}m'


class House:
    rooms = []
    def __init__(self):
        self.House = {}



    def add_rooms(self,*houserooms):
        rooms = []
        for eachroom in houserooms:
            self.House.setdefault(eachroom.name,eachroom.size)
            rooms.append(eachroom.name)
        return self.House


    def size(self):
        return sum([self.House[key] for key in self.House])

    def rooms(self):
        return list(self.House)

    def __str__(self):
        # return f'{vars(self)}'
        return  '\n'.join([f'{k}' for k in vars(self)]) +':'+'\n'+ '\n'.join([f'{k}, {v}m' for k, v in self.House.items()])
        # return '\n'.join([f'{k},{v}' for k, v in self.House.items()])


if __name__ == "__main__":
    house = House()
    print(house.size())
    bedroom = Room('bedroom', 10)
    kitchen = Room('kitchen', 9)
    bathroom = Room('bathroom', 3)
    print(house.add_rooms(bedroom,kitchen,bathroom))
    print(house.size())
    print(house)















