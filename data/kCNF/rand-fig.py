import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def draw(fn='50-200-MUS'):
    figure = plt.figure()
    ax = plt.axes(projection='3d')

    X = np.arange(50,201,10)
    Y = np.arange(3.0,5.1,0.1)

    x,y = np.meshgrid(X,Y)
    z = np.loadtxt(fn )[:,2].reshape((21,16))

    #X,Y = np.meshgrid(X,Y)
    #ax.plot_wireframe(X,Y,Z1D)

    ax.plot_surface(x,y,z,rstride=1,cstride=1,cmap='rainbow')
    # get the time 
    #plt.legend()                   


    ax.set_title('Time(s)')
    ax.set_ylabel('ratio')
    ax.set_xlabel('Number of variables')
    '''
    plt.zlabel('Tims(s)')
    plt.ylabel('Ration')        
    plt.xlabel('Number of variables (n)')
    '''
    plt.savefig("rand-" + fn + ".png")

    '''    
    z = np.loadtxt("50-4-200-MUS.txt")[:,2].reshape((21,16))
    ax.plot_surface(x,y,z,rstride=1,cstride=1,cmap='rainbow')
    plt.savefig("rand-50-4-200-MUS.png")
    '''

if __name__ == "__main__":

    pids = [20482, 22809, 24271, 31153, 27241, 13590, 28652]
    ks = [10, 3, 4, 5, 6, 20, 30]
    for i in [5,6]:
        draw(str(ks[i])+"-50-200-" + str(pids[i]) + "-MUS")
        draw(str(ks[i])+"-50-200-" + str(pids[i]))
