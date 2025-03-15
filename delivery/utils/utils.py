from models.model import *

def get_x_from_location(location: Location):
    print(location.x)
    return location.x

def euclidean_distance(location1: Location, location2: Location):
    return ((location1.x - location2.x)**2 + (location1.y - location2.y)**2)**0.5
