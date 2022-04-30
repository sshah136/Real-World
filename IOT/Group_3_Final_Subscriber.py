import random
import threading
import time
import tkinter
from json import JSONDecodeError

import paho.mqtt.client as mqtt
import json
import Final_util as util

import numpy as np
from tkinter import Tk, Canvas, Frame, BOTH, Label, messagebox
from collections import deque

# hyperparameters to control # of data samples to display in the chart
num_of_sample = 80
# distance between each point on line
x_distance = 5
# random value upper bound
end = 200
data = deque()
# used for quitting sub thread
program_terminated = False


def switch_start_and_stop():
    data_processing_thread.start()


class DisplayChart(Frame):

    def __init__(self, end):
        super().__init__()
        self.end = end
        self.line = []
        self.rectangle = []
        self.canvas = None
        self.initUI()

    def initUI(self):
        self.master.title('Historical Data')
        self.pack(fill=BOTH, expand=1)
        if self.canvas is None:
            self.canvas = Canvas(self, bg='#F1F3F6')
        canvas = self.canvas

        def display_chart(parent: DisplayChart):
            global data
            reset_canvas(parent)
            # parent.res.clear()
            # for j in range(20):
            #     parent.res.append(random.randint(0, parent.end))
            x = 10
            y_static = 200 if len(data) > 0 else 100

            start_button = tkinter.Button(canvas, text='Start',
                                          command=switch_start_and_stop)
            canvas.create_window(200, 20, window=start_button)

            # label2 = Label(canvas, text="Data Range: " + str(num) + " - " + str((num + 5)), width=15, height=2,
            #                bg='#F1F3F6', font='Times 10'),
            # canvas.create_window(60, 60, window=label2)

            if len(data) < 2:
                return
            # for i in range(num_of_sample):
            #     y = data[i]
            #     parent.rectangle.append(canvas.create_rectangle(x, y_static - y, x + 30, y_static, fill='lightgreen'))
            #     line_array.extend([x + 15, y_static - y])
            #     x = x + 40

            for i in range(0, len(data) - 1):
                y = data[i]
                parent.line.append(
                    canvas.create_line(x, y_static - y * 5,
                                       x + x_distance, y_static - data[i + 1] * 5,
                                       fill='blue', width=2.2))
                x = x + x_distance

        def reset_canvas(parent: DisplayChart):
            for rec in parent.rectangle:
                parent.canvas.delete(rec)

            for e in parent.line:
                parent.canvas.delete(e)
            parent.rectangle.clear()
            parent.line.clear()

        # Label
        label1 = Label(canvas, text="Temperature", width=15, height=2, bg='#F1F3F6', font='Times 10'),
        canvas.create_window(40, 20, window=label1)
        canvas.create_line(40, 20, 150, 20, fill="blue")

        # button and input textfield is no longer needed
        canvas.pack(fill=BOTH, expand=1)
        display_chart(self)


# lock for updating mutable variable
lock = threading.Lock()
root = Tk()
client = mqtt.Client()
ex = DisplayChart(end=end)


def on_message(client, userdata, message):
    global data
    incoming = message.payload.decode('utf-8')
    try:
        obj = json.loads(incoming)
        util.print_data(obj)
        current_temp = obj['temperature']
        # handle outliers
        if current_temp < -40 or current_temp > 40:
            current_temp = np.median(data)
        if len(data) < num_of_sample:
            data.append(current_temp)
        else:
            data.popleft()
            data.append(current_temp)
        ex.initUI()
    except JSONDecodeError as e:
        print('corrupted data')
        print(incoming)


def update_data():
    global data
    client.connect('localhost', 1883)
    client.subscribe(util.topic)
    client.on_message = on_message
    client.on_disconnect = lambda c, u, r: print('disconnected')
    client.on_unsubscribe = lambda c, u, r: print('unsubscribe')
    client.subscribe(util.topic)
    while True:
        lock.acquire()
        if program_terminated:
            print('program terminated')
            client.loop_stop()
            client.unsubscribe(util.topic)
            client.disconnect()
            lock.release()
            return
        lock.release()
        client.loop()


def on_closing():
    global program_terminated
    print('program terminated')
    lock.acquire()
    program_terminated = True
    lock.release()
    root.destroy()


if __name__ == '__main__':
    data_processing_thread = threading.Thread(target=update_data, args=())
    data_processing_thread.setDaemon(True)
    root.eval('tk::PlaceWindow . center')
    root.protocol("WM_DELETE_WINDOW", on_closing)
    # data_processing_thread.start()
    # root.after(500, update_data)
    root.mainloop()
