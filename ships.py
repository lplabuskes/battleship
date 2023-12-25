from dataclasses import dataclass
from typing import Dict, Tuple, List
from enum import Enum
from PySide2.QtGui import QPixmap, QIcon, QMatrix
from PySide2.QtCore import QObject, Signal


class Heading(Enum):
    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3


@dataclass
class ShipSegment:
    image: QIcon = None
    hit: bool = False


class Ship(QObject):
    offsets: List[Tuple[int, int]] = []
    paths: List[str] = []
    sunk_signal = Signal(int, int)

    def __init__(self, origin: Tuple[int, int], heading: Heading=Heading.EAST) -> None:
        super().__init__()
        self.sunk = False
        self.origin = origin
        self.segments = self.__class__.generate_segments(origin, heading)

    @classmethod
    def generate_segments(cls, origin: Tuple[int, int], heading: Heading) -> Dict[Tuple[int, int], ShipSegment]:
        rotation = QMatrix()
        if heading == Heading.EAST:
            rotation.rotate(0.0)
            instance_offsets = [(x, y) for x, y in cls.offsets]
        elif heading == Heading.NORTH:
            rotation.rotate(-90.0)
            instance_offsets = [(-y, x) for x, y in cls.offsets]
        elif heading == Heading.WEST:
            rotation.rotate(-180.0)
            instance_offsets = [(-x, -y) for x, y in cls.offsets]
        else:  # i.e South
            rotation.rotate(-270.0)
            instance_offsets = [(y, -x) for x, y in cls.offsets]

        segments = {}
        for offset, path in zip(instance_offsets, cls.paths):
            position = (offset[0] + origin[0], offset[1] + origin[1])
            img = QPixmap(path)
            img = img.transformed(rotation)
            icon = QIcon(img)
            icon.addPixmap(img, QIcon.Disabled)
            segments[position] = ShipSegment(image=icon)

        return segments
        
    def hit_ship(self, coordinates: Tuple[int, int]):
        seg = self.segments.get(coordinates)
        if seg is None:
            return
        seg.hit = True

        sunk = True
        for seg in self.segments.values():
            if not seg.hit:
                sunk = False
                break
        self.sunk = sunk

    def sink_ship(self):
        self.sunk_signal.emit(*self.origin)


class Destroyer(Ship):
    offsets = [(0, 0), (1, 0)]
    paths = [f"./assets/ships/des{i}.png" for i in range(2)]


class Cruiser(Ship):
    offsets = [(0, 0), (1, 0), (2, 0)]
    paths = [f"./assets/ships/cru{i}.png" for i in range(3)]


class Submarine(Ship):
    offsets = [(0, 0), (1, 0), (2, 0)]
    paths = [f"./assets/ships/sub{i}.png" for i in range(3)]


class Battleship(Ship):
    offsets = [(0, 0), (1, 0), (2, 0), (3, 0)]
    paths = [f"./assets/ships/bat{i}.png" for i in range(4)]


class AircraftCarrier(Ship):
    offsets = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    paths = [f"./assets/ships/air{i}.png" for i in range(5)]
