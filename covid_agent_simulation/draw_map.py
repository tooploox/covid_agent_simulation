import cv2
import numpy as np


class Map:
    def __init__(self, grid_width, grid_height):
        self.pixels_per_cell = 20

        self.grid = np.zeros((grid_width, grid_height))
        self.img = np.zeros((grid_width * self.pixels_per_cell,
                             grid_height * self.pixels_per_cell, 3))
        self.drawing = False
        self.clear()
        self.house_id = 1
        self.colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
                       (255, 255, 0), (0, 255, 255)]

    def draw_grid(self):
        for r in range(self.img.shape[0]):
            for c in range(self.img.shape[1]):
                cv2.line(self.img, (r * self.pixels_per_cell, 0),
                         (r * self.pixels_per_cell, self.img.shape[1]),
                         (255, 255, 255))
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
                self.colors[self.house_id]
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False

    def set_id(self, house_id):
        self.house_id = house_id
        print(house_id)

    def clear(self):
        self.grid.fill(0)
        self.img.fill(0)
        self.drawing = False


def draw_map(grid_width, grid_height, num_of_houses, save_path):
    if num_of_houses > 5:
        return

    map = Map(grid_width, grid_height)
    cv2.namedWindow('map')
    cv2.setMouseCallback('map', map.fill_cell)
    while True:
        k = cv2.waitKey(1) & 0xFF

        map.draw_grid()
        if k == ord('q'):
            break
        elif ord('0') <= k <= ord(str(num_of_houses)):
            print('Changing house id to:', chr(k))
            map.set_id(int(chr(k)))
        elif k == ord('c'):
            map.clear()

        cv2.imshow('map', map.get_img())

    cv2.destroyAllWindows()
    np.save(save_path, map.grid)


if __name__ == '__main__':
    print('Use mouse left button to fill cells')
    print('Use numbers 1-5 to change house ids')
    draw_map(10, 10, 3, 'map.npy')
