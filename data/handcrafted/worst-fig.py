import matplotlib.pyplot as plt
import numpy as np


# get the time 

def build_fig(m=1, cycle=False):
        legend = ["cb-MUS", "mmc", "mm", "cb"]
        style = [":", "^","-", "-."]
        x=range(50, 401, 10)
        np_x = np.array(x)
        plt.cla()
        for i in range(4): # minimal model checking, minimal model computing, minimal beta-witness, minimal beta-witness with MUS solver
            fs = "worst-wit-50-400-"
            time = []
            fs = fs + str(m) + "-" + str(i)
            if cycle: fs = fs + "-cycle"
            fn = open(fs+".txt", "r")
            line = fn.readline()
            while (line):
                time.append(float(line.split(" ")[1]))
                line = fn.readline()
            fn.close()
            np_y= np.array(time)
            if np.sum(np_y > 0) < len(np_y):
                plt.plot(np_x[np_y > 0], np_y[np_y > 0], style[i], label=legend[i], alpha=.9)
            else:
                plt.plot(np_x[:len(np_y)], np_y[:len(np_y)], style[i], label=legend[i], alpha=.9)
        plt.legend()                   
        plt.ylabel('Time (s)')        
        plt.xlabel('Number of variables (n)')      # 设置y轴的label;
        # fs = "worst-wit-50-400-"+str(m) 
        plt.savefig(fs+".png")

if __name__ == "__main__":
        build_fig(m=1)
        build_fig(m=5)
        build_fig(5,cycle=True)
