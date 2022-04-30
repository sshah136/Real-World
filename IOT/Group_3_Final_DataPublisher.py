import paho.mqtt.client as mqtt
import time
import json
import random
from Final_DataGenerator import *
import Final_util as util
from colorama import Fore
import string


class IOTPublisher:

    def __init__(self, topic: string, successful_rate: float = 0.99, corrupt_chance: float = 0.005,
                 interval: float = 0.3,
                 outlier_chance: float = 0.01):
        """
        an IOT Publisher
        :param topic topic that is going to use for the publisher
        :param successful_rate: by default, 99% of the data will be successfully sent to the broker
        :param corrupt_chance: by default, 0.05% of the data sent will be corrupted
        :param interval data sending interval
        :param outlier_chance chances of generating the data that is off the chart
        """
        assert 0 <= successful_rate <= 1
        assert 1 >= corrupt_chance >= 0
        assert topic is not None
        self.topic = topic
        self.client = mqtt.Client()
        self.data_generator = DataGenerator()
        self.successful_rate = successful_rate
        self.corrupt_chance = corrupt_chance
        self.interval = interval
        self.outliter_chance = outlier_chance

    def run(self):
        client = self.client
        client.connect('localhost', 1883)
        
        #generate data to send to the broker at regular intervals
        client.loop_start()
        time.sleep(1)
        while True:
            successful = random.random() < self.successful_rate
            corrupted = random.random() > (1 - self.corrupt_chance)
            if not successful:
                print(f'{Fore.RED}message sent failed')
                time.sleep(self.interval)
                continue
            if corrupted:
                # generate corrupted data
                letters = string.ascii_lowercase
                corrupted_data = ''.join(random.choice(letters) for _ in range(50))
                client.publish(util.topic, corrupted_data)
                print(f'{Fore.YELLOW}Data Corrupted: {corrupted_data}')
            else:
                # sent meaningful data
                sensor_read = self.data_generator.sense()
                if random.random() > (1 - self.outliter_chance):
                    # generate data off the chart
                    print(f'{Fore.BLUE} extreme outliers')
                    sensor_read = sensor_read * 20 * random.randint(-10, 10)
                new_data = util.generate_data(sensor_read)
                json_data = json.dumps(new_data)
                client.publish(self.topic, json_data)
                print(f'{Fore.GREEN}Message sent: {json_data}')
            time.sleep(self.interval)

        client.loop_stop()


# test publisher
if __name__ == '__main__':
    # Set occurance for corrupted data or failing message by changing the chance values respectively
    publisher = IOTPublisher(topic=util.topic,
                             successful_rate=0.99,
                             interval=0.1,
                             corrupt_chance=0.005,
                             outlier_chance=0.03)
    publisher.run()
