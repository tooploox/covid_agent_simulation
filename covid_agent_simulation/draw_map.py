import cv2
import numpy as np
import argparse
import random

USAGE = "Use mouse left button to fill cells. To change id, " \
        "press n for next and p for previous. " \
        "Use c to clear. Use q to quit and save map. Common space has id 0"


class Map:
    def __init__(self, grid_width, grid_height):
        self.pixels_per_cell = 20

        self.grid = np.ones((grid_width, grid_height)) * -1
        self.img = np.zeros((grid_width * self.pixels_per_cell,
                             grid_height * self.pixels_per_cell, 3),
                            dtype=np.uint8)
        self.drawing = False
        self.house_id = 1
        self.houses_colors = {0: (255, 255, 255), 1: (255, 0, 0)}

    def draw_grid(self):
        for r in range(self.img.shape[0]):
            cv2.line(self.img, (r * self.pixels_per_cell, 0),
                     (r * self.pixels_per_cell, self.img.shape[1]),
                     (255, 255, 255))
        for c in range(self.img.shape[1]):
            cv2.line(self.img, (0, c * self.pixels_per_cell),
                     (self.img.shape[1], c * self.pixels_per_cell),
                     (255, 255, 255))

    def get_img(self):
        return self.img

    def fill_cell(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.fill_cell(cv2.EVENT_MOUSEMOVE, x, y, flags, params)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            xp = x // self.pixels_per_cell
            yp = y // self.pixels_per_cell

            if xp < 0 or xp >= self.grid.shape[1] or yp < 0 or yp >= self.grid.shape[0]:
                return

            self.grid[yp, xp] = self.house_id
            self.img[yp * self.pixels_per_cell:(yp + 1) * self.pixels_per_cell,
            xp * self.pixels_per_cell:(xp + 1) * self.pixels_per_cell] = \
                self.houses_colors[self.house_id]
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

    def set_id(self, house_id):
        if house_id not in self.houses_colors:
            self.houses_colors[house_id] = (random.randint(0, 255),
                                            random.randint(0, 255),
                                            random.randint(0, 255))

        print(self.houses_colors)
        self.house_id = house_id

    def clear(self):
        self.grid.fill(0)
        self.img.fill(0)
        self.drawing = False


def draw_map(grid_width, grid_height, save_path):
    map = Map(grid_width, grid_height)
    cv2.namedWindow('map')
    cv2.setMouseCallback('map', map.fill_cell)
    house_id = 1
    INTERIOR_ID = 0
    while True:
        k = cv2.waitKey(1) & 0xFF

        map.draw_grid()
        if k == ord('q'):
            break
        elif k == ord('n'):
            house_id += 1
            print('Incrementing id:', house_id)
            map.set_id(house_id)
        elif k == ord('p'):
            if house_id > 0:
                house_id -= 1
                print('Decrementing id:', house_id)
                map.set_id(house_id)
        elif k == ord('c'):
            map.clear()

        elif k == ord('i'):
            map.set_id(INTERIOR_ID)

        cv2.imshow('map', map.get_img())

    cv2.destroyAllWindows()
    np.save(save_path, map.grid)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid_width", default=50, type=int)
    parser.add_argument("--grid_height", default=50, type=int)
    parser.add_argument("--save_path", default="map.npy")
    return parser.parse_args()


if __name__ == '__main__':
    print(USAGE)
    args = parse_arguments()
    draw_map(args.grid_width, args.grid_height, args.save_path)
