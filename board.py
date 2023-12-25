from PySide2.QtCore import Qt, QSize, Slot
from PySide2.QtWidgets import QPushButton, QLabel, QWidget, QGridLayout
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QApplication, QMessageBox

import random
from typing import Dict, Tuple, List

from ships import Ship, Heading
from ships import AircraftCarrier, Battleship, Cruiser, Submarine, Destroyer

class Tile:
    def __init__(self) -> None:
        self.ship = None
        self.coord = (None, None)
        self.fired_at = False
        self.img = None

        self.button = self.create_button()
    
    def create_button(self) -> QPushButton:
        btn = QPushButton()
        btn.clicked.connect(self.button_callback)
        btn.setFixedSize(32, 32)
        btn.setIconSize(QSize(32, 32))
        return btn
    
    def render(self):
        self.button.setEnabled(not self.fired_at)

        if not self.fired_at:
            self.button.setIcon(QIcon())
        elif self.ship is None:
            self.button.setIcon(MISS_ICON)
        elif not self.ship.sunk:
            self.button.setIcon(HIT_ICON)
        else:
            self.ship.sink_ship()

    @Slot(int, int)
    def ship_sunk(self, x, y):
        self.button.setIcon(self.img)

    def button_callback(self):
        self.fired_at = True
        if self.ship is not None:
            self.ship.hit_ship(self.coord)
        self.render()

class Board:
    def __init__(self, rows: int=10, cols: int=10) -> None:
        self.rows = rows
        self.cols = cols
        self.tiles = [[Tile() for _ in range(cols)] for _ in range(rows)]
        self.ships: Dict[Tuple[int, int], List[str, bool]] = {}
        self.widget = self.create_widget()
        
    def create_widget(self) -> QWidget:
        lo = QGridLayout()
        lo.setSpacing(0)
        lo.setContentsMargins(0, 0, 0, 0)

        for i in range(self.rows):
            lbl = QLabel(text=str(i+1))
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lo.addWidget(lbl, i+1, 0)
        
        for i in range(self.cols):
            lbl = QLabel(text=chr(i+65))
            lbl.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            lo.addWidget(lbl, 0, i+1)

        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                lo.addWidget(tile.button, i+1, j+1)
        w = QWidget()
        w.setLayout(lo)
        return w
    
    def valid_ship_pose(self, ship: Ship) -> bool:
        for coordinate in ship.segments:
            row = self.rows - 1 - coordinate[1]
            col = coordinate[0]
            in_bounds = row >= 0 and row < self.rows and col >= 0 and col < self.cols
            if not in_bounds or self.tiles[row][col].ship is not None:
                return False
        return True
    
    def add_ship(self, ship: Ship):
        if not self.valid_ship_pose(ship):
            return
        self.ships[ship.origin] = [type(ship).__name__, False]
        for coordinate in ship.segments:
            row = self.rows - 1 - coordinate[1]
            col = coordinate[0]
            self.tiles[row][col].ship = ship
            self.tiles[row][col].coord = coordinate
            self.tiles[row][col].img = ship.segments[coordinate].image
            ship.sunk_signal.connect(self.tiles[row][col].ship_sunk)
        ship.sunk_signal.connect(self.sink_handler)

    @Slot(int, int)
    def sink_handler(self, ship_x, ship_y):
        self.ships[(ship_x, ship_y)][1] = True

        all_sunk = True
        for ship in self.ships.values():
            if not ship[1]:
                all_sunk = False

        if all_sunk:
            dialog = QMessageBox(self.widget)
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog.setWindowTitle("Victory!")
            dialog.setText("Congratulations!\nYou sunk the enemy fleet.\nWould you like to play again?")
            ret = dialog.exec_()
            if ret == QMessageBox.Yes:
                self.clear_board()
                self.randomize_board()
            else:
                self.widget.close()

    def clear_board(self):
        for row in self.tiles:
            for tile in row:
                tile.fired_at = False
                tile.ship = None
                tile.img = None
                tile.render()
        self.ships = {}
        
    def randomize_board(self):
        ship_types = [AircraftCarrier, Battleship, Cruiser, Submarine, Destroyer]
        for ship_type in ship_types:
            start = (random.randrange(self.cols), random.randrange(self.rows))
            heading = Heading(random.randrange(4))
            ship = ship_type(start, heading)
            while not self.valid_ship_pose(ship):
                start = (random.randrange(self.cols), random.randrange(self.rows))
                heading = Heading(random.randrange(4))
                ship = ship_type(start, heading)
            self.add_ship(ship)


if __name__ == "__main__":
    app = QApplication()
    MISS_ICON = QIcon(QPixmap("./assets/gray-circle-512.png"))
    HIT_ICON = QIcon(QPixmap("./assets/red-circle-512.png"))
    HIT_ICON.addPixmap(QPixmap("./assets/red-circle-512.png"), QIcon.Disabled)
    board = Board(10, 10)
    board.randomize_board()
    w = board.widget
    w.show()
    app.exec_()
