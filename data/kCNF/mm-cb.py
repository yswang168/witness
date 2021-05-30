
import numpy as np


# statics the compute time of minimal model of random cnfs 
# by cadical mr_minimal clingo dlv mr_miimal (with minimal reduct when update theories)
def min_model():
   files = [50, 100, 150, 200]
   #data = np.zeros(21,13)
   column = [2,4,6,8,10,12]
   s_time = [0.0]*6 # for sum of the time of cadical, mr_minimal(MMSAT), clingo, dlv, mr_minimal(MRSAT)
   print("cadical  MMSAT   clingo  dlv  MRSAT")
   for i in range(len(files)):
      data = np.loadtxt('mm-'+str(files[i])+'-1.txt')
      print(files[i])
      for j in range(len(column)-1):
          s_time[j] = np.sum(data[:,column[j]])/21.0
          print("%.4f "%s_time[j],end='')
    
      print("%d"%np.sum(data[:,12]))

# statics the overall time and head_2
def CNF_cb_witness():
   cl_len = [3, 4, 5, 6, 10, 20]
   #pids = [22809, 24271, 31153, 27241, 20482, 13590]
   #data = np.zeros(21,13)
   column = [2,5,7,8,6]
   s_time = [0.0]*6 # for sum of the time and head_2
   print("Time, |\Pi_i|\ge 2, |\Pi_2|^c, |\Pi_2|^w, |compactness")
   nt = 1 #16*21*20
   for i in range(len(cl_len)):
    file_name = "wit-" + str(cl_len[i]) + '-' + '50-200-0.txt' # + str(pids[i])
    data = np.loadtxt(file_name)
    print(file_name)
    print("%.4f %d %d %d %d"%( np.sum(data[:,column[0]])/nt, 20*np.sum(data[:,column[1]])/nt, np.sum(data[:,column[2]])/nt,
           np.sum(data[:,column[3]])/nt, np.sum(data[:,column[4]])/nt))
    file_name = "wit-"+str(cl_len[i]) + '-' + '50-200-1.txt' #+ str(pids[i]) + '-MUS'
    print(file_name)
    data = np.loadtxt(file_name)
    #print("%.4f %.4f"%(np.sum(data[:,column[0]])/nt, np.sum(data[:,column[1]])/nt))
    print("%.4f %d %d %d %d"%( 
           np.sum(data[:,column[0]])/nt, 20*np.sum(data[:,column[1]])/nt, np.sum(data[:,column[2]])/nt, 
           np.sum(data[:,column[3]])/nt,  np.sum(data[:,column[4]])/nt))

if __name__ == '__main__':

    CNF_cb_witness()
    #min_model()
