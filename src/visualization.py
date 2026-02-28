import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.animation import FuncAnimation

# ------- Reading in images:
horizontal_road = mpimg.imread("images/road.jpg")
tmp = Image.open("images/road.jpg")
vertical_road = tmp.rotate(90, expand=True)
car = mpimg.imread("images/car.png")

fig, ax = plt.subplots()

# Plot a singular point:
# ax.plot(60, 30, 'ro')

# ---------Show images----------

ax.imshow(horizontal_road, extent=[0, 40, 45, 55])  # left horiz road
ax.imshow(horizontal_road, extent=[60, 100, 45, 55])  # right horiz road
ax.imshow(vertical_road, extent=[45, 55, 0, 40])  # bottom vertical road
ax.imshow(vertical_road, extent=[45, 55, 60, 100])  # top vertical road

# Create multiple cars with different starting positions
car1_img = ax.imshow(car, extent=[45, 55, 5, 15])  # Bottom vertical road
car2_img = ax.imshow(car, extent=[5, 15, 45, 55])  # Left horizontal road
car3_img = ax.imshow(car, extent=[85, 95, 45, 55])  # Right horizontal road


def init():
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    return car1_img, car2_img, car3_img


def update(frame):
    # straight up
    car1_img.set_extent([45, 55, frame - 5, frame + 5])

    # right
    car2_img.set_extent([frame - 5, frame + 5, 45, 55])

    # left
    car3_img.set_extent([100 - frame - 5, 100 - frame + 5, 45, 55])

    return car1_img, car2_img, car3_img


# Run the animation:
ani = FuncAnimation(fig, update, frames=np.linspace(0, 50, 10), init_func=init, blit=False)

plt.show()
