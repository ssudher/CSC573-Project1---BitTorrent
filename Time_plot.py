import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import collections


def plot_perf(csv_name):
    data = pd.read_csv(csv_name)
    rfc_dict = {}
    rfc_final = {}
    performance = []
    objects = []

    #store the values in a dict
    for i,j in data.iterrows():
        rfc_dict[int(j[0])] = j[1]

    #reorder the dict based on the RFC_ID
    for key in sorted(rfc_dict):
        rfc_final[key] = rfc_dict[key]

    #store the x and y axis values from the sorted dict
    for key in rfc_final.keys():
        performance.append(rfc_final[key])
        objects.append(str(key))

    x = np.arange(len(objects))

    plt.bar(x, performance, align='center', alpha=0.8)
    plt.xticks(x, objects)
    plt.ylabel('Time')
    plt.xlabel('RFC ID')
    result = "RFC vs Time - Total time: " + str(sum(performance)) + ' seconds'
    plt.title(result)

    plt.show()