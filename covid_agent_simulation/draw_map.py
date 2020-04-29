import cv2
import numpy as np
import argparse
import random

USAGE = "Use mouse left button to fill cells. To change id, " \
        "press n for next and p for previous. " \
        "Use c to clear. Use q to quit and save map. " \
        "Non movable space has id 0. Common space has id 1."


class Map:
    def __init__(self, grid_width, grid_height, load_path):
        self.pixels_per_cell = 20
        self.house_id = 1
        self.drawing = False
        self.houses_colors = {0: (0, 0, 0), 1: (255, 255, 255), 2: (255, 0, 0)}

        if load_path is None:
            self.grid = np.zeros((grid_height, grid_width))
            self.img = np.zeros((grid_height * self.pixels_per_cell,
                                 grid_width * self.pixels_per_cell, 3),
                                dtype=np.uint8)
        else:
            self.__load_grid(load_path)
            self.img = np.zeros((self.grid.shape[0] * self.pixels_per_cell, self.grid.shape[1] * self.pixels_per_cell,
                                 3), dtype=np.uint8)
            self.__draw_initial_houses()

    def draw_grid(self):
        for r in range(self.img.shape[0]):
            cv2.line(self.img, (0, r * self.pixels_per_cell),
                     (self.img.shape[1], r * self.pixels_per_cell),
                     (255, 255, 255))
        for c in range(self.img.shape[1]):
            cv2.line(self.img, (c * self.pixels_per_cell, 0),
                     (c * self.pixels_per_cell, self.img.shape[1]),
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
        self.house_id = house_id

    def get_id(self):
        return self.house_id

    def clear(self):
        self.grid.fill(0)
        self.img.fill(0)
        self.drawing = False

    def __load_grid(self, load_path):
        self.grid = np.load(load_path)

    def __draw_initial_houses(self):
        house_number = int(self.grid.max()) + 1
        for i in range(2, house_number + 1):
            self.set_id(i)

        for r in range(self.grid.shape[0]):
            for c in range(self.grid.shape[1]):
                self.img[r * self.pixels_per_cell:(r + 1) * self.pixels_per_cell,
                         c * self.pixels_per_cell:(c + 1) * self.pixels_per_cell] = \
                    self.houses_colors[int(self.grid[r, c])]


def draw_map(grid_width, grid_height, save_path, load_path):
    map = Map(grid_width, grid_height, load_path)
    cv2.namedWindow('map')
    cv2.setMouseCallback('map', map.fill_cell)
    while True:
        k = cv2.waitKey(1) & 0xFF

        map.draw_grid()
        if k == ord('q'):
            break
        elif k == ord('n'):
            map.set_id(map.get_id() + 1)
            print('Incrementing id:', map.get_id())
        elif k == ord('p'):
            if map.get_id() > 0:
                map.set_id(map.get_id() - 1)
                print('Decrementing id:', map.get_id())
        elif k == ord('c'):
            map.clear()

        cv2.imshow('map', map.get_img())

    cv2.destroyAllWindows()
    np.save(save_path, map.grid)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid_width", default=40, type=int)
    parser.add_argument("--grid_height", default=25, type=int)
    parser.add_argument("--save_path", default="map.npy")
    parser.add_argument("--load_path", default=None)
    return parser.parse_args()


if __name__ == '__main__':
    print(USAGE)
    args = parse_arguments()
    draw_map(args.grid_width, args.grid_height, args.save_path, args.load_path)
