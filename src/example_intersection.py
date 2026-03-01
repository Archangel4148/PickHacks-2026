from intersection import Approach, Intersection, Road, Turn


def build_four_way_intersection():
    approach_north = Approach(name="north", has_crosswalk=True)
    approach_south = Approach(name="south", has_crosswalk=True)
    road_ns = Road(approaches=[approach_north, approach_south])

    approach_east = Approach(name="east", has_crosswalk=True)
    approach_west = Approach(name="west", has_crosswalk=True)
    road_ew = Road(approaches=[approach_east, approach_west])

    topology = {
        "north": {"west": Turn.RIGHT_TURN, "south": Turn.THROUGH, "east": Turn.LEFT_TURN},
        "east": {"north": Turn.RIGHT_TURN, "west": Turn.THROUGH, "south": Turn.LEFT_TURN},
        "south": {"east": Turn.RIGHT_TURN, "north": Turn.THROUGH, "west": Turn.LEFT_TURN},
        "west": {"south": Turn.RIGHT_TURN, "east": Turn.THROUGH, "north": Turn.LEFT_TURN},
    }
    approaches = (approach_north, approach_east, approach_south, approach_west)
    return approaches, Intersection(roads=[road_ns, road_ew], topology=topology)

def build_t_junction():
    approach_north = Approach(name="north", has_crosswalk=True)
    approach_south = Approach(name="south", has_crosswalk=True)
    road_ns = Road(approaches=[approach_north, approach_south])

    approach_east = Approach(name="east", has_crosswalk=True)
    road_e = Road(approaches=[approach_east])

    topology = {
        "north": {"south": Turn.THROUGH, "east": Turn.LEFT_TURN},
        "east": {"north": Turn.RIGHT_TURN, "south": Turn.LEFT_TURN},
        "south": {"east": Turn.RIGHT_TURN, "north": Turn.THROUGH},
    }
    approaches = (approach_north, approach_east, approach_south)
    return approaches, Intersection(roads=[road_ns, road_e], topology=topology)