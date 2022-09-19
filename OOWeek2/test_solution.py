from solution import Room, House


def test_empty_house():
    h = House()
    assert h.size() == 0


def test_small_house():
    h = House()
    bedroom = Room('bedroom', 10)
    kitchen = Room('kitchen', 9)
    bathroom = Room('bathroom', 3)
    h.add_rooms(bedroom, kitchen, bathroom)

    assert h.size() == 22
    assert len(h.rooms) == 3
    assert str(h) == '''House:
bedroom, 10m
kitchen, 9m
bathroom, 3m'''


def test_palace():
    h = House()

    for i in range(10):
        h.add_rooms(Room(f'bedroom {i}', 15))

    for i in range(5):
        h.add_rooms(Room(f'bathroom {i}', 3))

    for i in range(3):
        h.add_rooms(Room(f'kitchen {i}', 3))

    assert h.size() == 174
    assert len(h.rooms) == 18