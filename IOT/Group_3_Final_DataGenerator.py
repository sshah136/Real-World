import numpy as np
import random
import math
import matplotlib.pyplot as plt

class DataGenerator:
    @property
    def __get_random(self):
        return random.random()

    def __get_noise(self, mu: float, sigma: float) -> float:
        """
        sensor noise
        :return:
        """
        return random.gauss(mu, sigma)

    def __init__(self, title: str = 'temperature', sensor_noise=(0.6, 0.5, 1., 1.2)):
        """

        :param title: 0 o'clock
        :param sensor_noise: sensor noise parameter of each season (winter, spring, summer, autumn)
        """
        self.title = title
        self.sensor_noise = sensor_noise
        self.sensor_parameter = sensor_noise
        self.counter = 0
        self.range = 0.
    
    # Generate random data values
    def sense(self) -> float:
        """
        measure every one second of a day
        :return:
        """
        day_of_year = self.counter % 365
        noise = self.__get_random
        # sin circle
        circle = 22.8 * math.pi
        # peak and valley of function
        if self.counter % int(circle * math.pi) == 0:
            self.range = self.__get_random * 15 + 5
        # offset, shift lowest temperature
        offset = 10
        # moderate sensor error in sprint
        if 90 > day_of_year >= 0:
            noise = self.__get_random * self.sensor_noise[0]
        # big sensor error in summer
        elif 120 > day_of_year >= 90:
            noise = self.__get_random * self.sensor_noise[1]
        elif 240 > day_of_year >= 120:
            noise = self.__get_random * self.sensor_noise[2]
        # big sensor error in winter
        elif 365 > day_of_year >= 240:
            noise = self.__get_random * self.sensor_noise[3]
        v = np.sin(self.counter / circle) * self.range + offset + noise
        self.counter += 1
        return v

# Plot to show pattern
if __name__ == '__main__':
    dg = DataGenerator()
    x = [_ for _ in range(365 * 3)]
    y = [dg.sense() for _ in x]
    plt.xlabel('days')
    plt.ylabel('temp')
    plt.plot(x, y)
    plt.show()
