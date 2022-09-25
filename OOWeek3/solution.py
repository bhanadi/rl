class Room():
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def __str__(self):
        return f'{self.name}, {self.size}m'

class NotEnoughSpaceError(Exception):
    def __init__(self,value):
        self.value = value




class House():
    def __init__(self, housesize=100):
        self.rooms = []
        self.housesize = housesize
        self.available_space = (self.housesize - self.size())

    def add_rooms(self, *args):
        for eachroom in args:
            try:
                if eachroom.size > (self.housesize-self.size()):
                    raise NotEnoughSpaceError(
                        f'The room requires {eachroom.size}m while the house has {int(self.housesize) - self.size()}m left')

                self.rooms.append(eachroom)
            except NotEnoughSpaceError as e:
                 print(e)


    def size(self):
        r = sum(one_room.size
                   for one_room in self.rooms)
        return r


    def size(self):
        r = sum(one_room.size
                   for one_room in self.rooms)
        return r

    def __str__(self):
        output = 'House:\n'
        output += '\n'.join(str(one_room)
                            for one_room in self.rooms)
        return output


h = House(0)
r1 = Room('master bedroom', 25)
# r2 = Room('bathroom', 5)
# r3 = Room('living room', 30)
# r4 = Room('kitchen', 20)
# r5 = Room('kitchen', 21)
h.add_rooms(r1)
# h.add_rooms(r1,r2,r3,r4,r5)
print(h)
print(h.size())
print(h.available_space)


    # h = House(100)
    # r1 = Room('master bedroom', 25)
    # r2 = Room('bathroom', 5)
    # r3 = Room('living room', 30)
    # r4 = Room('kitchen', 20)
    # h.add_rooms(r1)
    # print(h)
    # # h.add_rooms(r1, r2, r3, r4)

