import argparse
import numpy as np
import glob
import os
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def solved(lines, instance): 
   # return 1: if the instance is solved according to wit_lines, which is a list of lines from the witness
   # 	    2: if the instance is unsatisfiable
   # 	    3: if the instance is out of time, the next line is not invalid model
   for i in range(len(lines)):
      if lines[i].find(instance) >= 0 and i < len(lines)-1:
          if lines[i+1].find('YES') >=0 : return 1
          if lines[i+1].find('invalid') or lines[i+1].find('Unknown') >=0: return 2
   return 3


def get_metrics_from_file(fl):
   ### to improve it 
   '''
   YES
   0 0 0 atoms, head>2 clauses, clauses
   Time: 0.089 (s)
   Memory: 39.613 (M)
   The witness is compact: True

   n_solved = int( os.popen('grep Time '+ fl +' | wc -l').read().split()[0])
   n_compact = int (os.popen('grep True ' + fl + ' | wc -l').read().split()[0])
   _time, _mem, _clauses = .0, .0, [.0]*3
   if n_solved > 0:
       _time = float(os.popen('grep Time ' +fl).read().split()[1] )
       _mem = float(os.popen('grep Memory ' + fl).read().split()[1])
       _clauses = [int (x) for x in os.popen('grep head\>2 ' + fl).read().split()[:3]]
   '''
   lines = os.popen('tail -5 ' + fl).readlines()
   n_solved, n_compact, _time, _mem, _clauses = 0,0,.0, .0, [.0]*3
   if len(lines) == 5:
      n_solved = 1
      _clauses = [int(x) for x in lines[1].split()[:3]]
      _time = float(lines[2].split()[1])
      _mem = float(lines[3].split()[1])
      if lines[4].find('True') >= 0: n_compact = 1
   return n_solved, n_compact,_time, _mem, _clauses

def draw_k_cnf(data,save ): # draw the figure of k-cnf and save it

    figure = plt.figure()
    ax = plt.axes(projection='3d')

    X = np.arange(50,201,10)
    Y = np.arange(3.0,5.1,0.1)

    x,y = np.meshgrid(X,Y)
    z = data #loadtxt(fn )[:,2].reshape((21,16))

    ax.plot_surface(x,y,z,rstride=1,cstride=1,cmap='rainbow')

    ax.set_title('Time(s)')
    ax.set_ylabel('ratio')
    plt.savefig(save)


def statistics_k_CNF(cdir="data/3CNF",  _mh=True, _mus=True, draw=False, k=3, save=True):
   _pos_wit =".wit"
   if _mh:  _pos_wit += "-mh"
   if _mus: _pos_wit += "-mus"
   data = np.zeros((5,21,16)) #|\Pi_i|^a, |\Pi_i|^2, |\Pi_i|^t, compact, time
   nr = [_i for _i in range(30,51)]
   nc = [_i for _i in range(50,201,10)]
   clauses = [0,0,0, 0] #number of compact, |\Pi_i|^a, |\Pi_i|^2, |\Pi_i|^t, 
   for i in range(len(nr)):
       for j in range(len(nc)):
           for k in range(20):
              wit = cdir + "/" + str(nc[j])+"/"+ "{:.1f}".format(nr[i]/10) + "-" + str(k) + _pos_wit
              _, _compact, _time, _, _clauses = get_metrics_from_file(wit)
              for _i in range(3): data[_i, i,j] += _clauses[_i]
              data[3, i,j] += _compact,
              data[4, i,j] += _time

   _save = cdir 
   if _mh: _save += "-mh"
   if _mus: _save += "-mus"
   if draw: draw_k_cnf(data[4,:,:], _save+".png")
   if save: np.save(_save,data)   

def one_dir_statics(lp_cnf=0, type=0):
# compute the 1-8) for the _directory _dir
   # lp_cnf 0: for logic program, 1 for cnf theory
   # type =0: without MUS solver, the file is instance.wit-mh
   # type = 1: with MUS solver, the file is instance.wit-mh-mus

   theory_model = [['lp', 'm'], ['cnf', 'm-m']]
   _instances = glob.glob( '*.' + theory_model[lp_cnf][0] )
   _models = [s.replace('.' + theory_model[lp_cnf][0], '.' + theory_model[lp_cnf][1]) for s in _instances]
   if type == 0:
       _wits = [s.replace('.' + theory_model[lp_cnf][0], '.wit-mh') for s in _instances]
   else:
       _wits = [s.replace('.' + theory_model[lp_cnf][0], '.wit-mh-mus') for s in _instances]
   #_models= glob.glob( '*.' + theory_model[lp_cnf][1] )

   metrics = [.0, .0]
   n_solved, n_compact, time, mem, clauses = 0, 0, .0, .0, [0,0,0]
   __unknown = 0
   for i in range(len(_instances)): #_theory in _instances:
      if os.path.getsize(_model[i]) == 0: __unknown += 1
      if not os.path.exists(_wits[i]): continue
      _solved, _compact, _time, _mem, _clauses = get_metrics_from_file(_wits[i])
      if _solved == 1:
          metrics[0] +=  os.path.getsize(_instances[i])
          metrics[1] +=  os.path.getsize(_models[i])
       
      n_solved += _solved
      n_compact += _compact
      time += _time
      mem += _mem
      for i in range(3):  clauses[i] += _clauses[i]

   n_select = len(_instances)
   n_unsat = int (os.popen('grep ^UNSAT *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_unknown = int( os.popen('grep ^UNKNOWN  *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_sat   = n_select - n_unsat - n_unknown - __unknown

   if n_solved > 0:
       metrics[0] = metrics[0]  / n_solved / 1024 / 1024 # in MB
       metrics[1] = metrics[1]  / n_solved / 1024  # in KB
       time /= n_solved
       mem  /= n_solved
   return n_select, n_sat, n_unsat, n_solved, metrics[0], metrics[1], time, mem, clauses[0], clauses[1], clauses[2], n_compact



def one_dir(lp_cnf=0, type=0, up_time=0):
# compute the 1-8) for the _directory _dir
   # lp_cnf 0: for logic program, 1 for cnf theory
   # type =0: without MUS solver
   # type = 1: with MUS solver

   theory_model = [['lp', 'm'], ['cnf', 'm-m']]
   _instances = glob.glob( '*.' + theory_model[lp_cnf][0] ) 
   _models = [s.replace('.' + theory_model[lp_cnf][0], '.' + theory_model[lp_cnf][1]) for s in _instances]
   #_models= glob.glob( '*.' + theory_model[lp_cnf][1] )

   f_wit = open('wit-'+str(type) + '.txt', 'r')
   wit_lines = f_wit.readlines()
   f_wit.close()


   metrics = [.0, .0]
   __unknown = 0
   for i in range(len(_instances)): #_theory in _instances:
      if os.path.getsize(_models[i]) == 0: __unknown += 1
      if solved(wit_lines, _instances[i]) == 1:      
          metrics[0] +=  os.path.getsize(_instances[i])
          metrics[1] +=  os.path.getsize(_models[i]) 

   n_select = len(_instances)
   n_unsat = int (os.popen('grep ^UNSAT *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_unknown = int( os.popen('grep ^UNKNOWN  *.' + theory_model[lp_cnf][1] + '|wc -l').read().split()[0] )
   n_sat   = n_select - n_unsat - n_unknown - __unknown

   n_solved = 0  # int( os.popen('grep Time wit-' + str(type) + '.txt | wc -l').read().split()[0])
   n_compact = int (os.popen('grep True  wit-' + str(type) + '.txt | wc -l').read().split()[0])
   #n_tm_out = # the same as memory out
   
   time, mem, clauses = .0, .0, [0,0,0]
   _time = os.popen('grep Time wit-' + str(type) + '.txt').read().split('\n')
   _mem = os.popen('grep Memory wit-' + str(type) + '.txt').read().split('\n')
   _clauses = os.popen('grep head\>2 wit-' + str(type) + '.txt').read().split('\n')

   for i in range(len(_time)-1):
        cb_time = float(_time[i].split()[1])
        if up_time > 0 and cb_time > up_time: continue
        n_solved += 1
        time += float(_time[i].split()[1])
        mem += float(_mem[i].split()[1])
        clauses[0] += int(_clauses[i].split()[0])
        clauses[1] += int(_clauses[i].split()[1])
        clauses[2] += int(_clauses[i].split()[2])
   if n_solved > 0:
       metrics[0] = metrics[0]  / n_solved / 1024 / 1024 # in MB
       metrics[1] = metrics[1]  / n_solved / 1024  # in KB 
       time /= n_solved
       mem  /= n_solved
#       for i in range(3):
#           clauses[i] /= n_solved
   return n_select, n_sat, n_unsat, n_solved, metrics[0], metrics[1], time, mem, clauses[0], clauses[1], clauses[2], n_compact

def statics_asp_sat(dir="asp-sat/data/", wit=True, up_time=0):
   _dtype = ('asp', 'sat')
   up_time = (3600, 45)
   print("|select| |sat| |unsat| |solved| |Sigma|(M) |Model|(K) CPU(s) MEM (M)  |atom-2|  |clauses-2| |clauses| |compact|")
   for _d in range(len(_dtype)):
       
       dirs = os.popen('ls '+dir+"/"+_dtype[_d]).read().split()
       for dclass in dirs:
          cur_dir = os.getcwd()
          os.chdir(dir+"/"+_dtype[_d]+"/"+dclass)
          print(dclass)
          if wit: __res = one_dir_statics(lp_cnf=_d, type=0)#, time=time)
          else: __res = one_dir(lp_cnf=_d, type=0, up_time=up_time[_d])
          for i in __res: ## in one_dir_statics(lp_cnf=_d, type=0): #one_dir(lp_cnf=_d, type=0):
              if type(i) == int:
                  print("{:<6} ".format(i), end='')
              else: # float
                  print("%.4f "%i, end='')
          print("\n")
          if wit: __res = one_dir_statics(lp_cnf=_d, type=1)#, time=time)
          else: __res = one_dir(lp_cnf=_d, type=1, up_time=up_time[_d])
          for i in __res: ## in one_dir_statics(lp_cnf=_d, type=0): #one_dir(lp_cnf=_d, type=0):
          #for i in one_dir_statics(lp_cnf=_d, type=1): #one_dir(lp_cnf=_d, type=1):
              if type(i) == int:
                  print("{:<6} ".format(i), end='')
              else: # float
                  print("%.4f "%i, end='')
          print("\n")
          #print("{0} \n {1}\n".format(dclass, one_dir(lp_cnf=_d, type=0)))
          #print("    {0}\n".format(dclass, one_dir(lp_cnf=_d, type=1)))
          os.chdir(cur_dir)
       print("\n")

def kCNFs(dir="data"): # statistics all the average time, overall compact, |\Pi|_i^a, |\Pi|_i^2, |\Pi|_i^t
              # from the corresponding np file: 3CNF-mh-mus.npy, 3CNF-mh.npy
              #|\Pi_i|^a, |\Pi_i|^2, |\Pi_i|^t, compact, time
   kcnfs = [3,4,5,6,10,20,30]
   print("|\Pi_i|^a, |\Pi_i|^2, |\Pi_i|^t, compact, time")
   for i in range(len(kcnfs)):
       print("No mus: %d "%kcnfs[i])
       data = np.load(dir+"/"+ str(kcnfs[i]) +"CNF-mh.npy")     
       for j in range(4):
           print("%d "%np.sum(data[j,:,:]), end="")
       print("%.2f "%(np.sum(data[4,:,:])))#/(21*16*20)))
       data = np.load(dir+"/"+ str(kcnfs[i]) +"CNF-mh-mus.npy")     
       print("with mus: %d "% kcnfs[i])
       for j in range(4):
           print("%d "%np.sum(data[j,:,:]), end="")
       print("%.2f "%(np.sum(data[4,:,:])))#/(21*16*20)))
   

if __name__ == "__main__":
   
    '''# to compute 
    1) |selected| the number instances selected from all the instances (SAT: == |total|, ASP: <=|total|)
    2) |sat| the number of satisfiable benchmarks instance (in 2 hours)
    2.5) |unsat| the number of unsatisfiable benchmarks instance (in 2 hours)

       1) and 2) are computed by find .lp and .m (.cnf and .m-m respectively)
    3) |solved| minimal witness is computed in 2 hours
       These three can put together as /total/sat(2)/solved(2)

       The followin are all in average of solved intances
    4) |\Sigma| the size of solved instances (logic program or cnf theory)
    5) |M|      the size of the minimal model 
    6) Time:    cpu time 
    7) Mem:     mem 
    8) |\Pi|a:  the number of atoms with more than one clauses in its witness
       |\Pi|2:  the number clauses with more than one positive atoms in its witness
       |\Pi|t:  the size of the witness for this kind of atom

       3-8) are computed from witness-0.txt (without mus solver) and witness-1.txt (with mus solver)

    '''
    parser = argparse.ArgumentParser(description='statistics the metrics of minimal beta witnesses in a given directory')
    parser.add_argument("-dir", type=str, default="asp-sat/data/", help = "The path to compute minimal beta witness")
    parser.add_argument("-k", type=int, default=3, help = "K-CNF, 0 for handcrafted case")
    parser.add_argument("-mh", action='store_true', help = "multiple heads in witness")
    parser.add_argument("-mus", action='store_true', help = "with MUS solver")
    parser.add_argument("-wit", action='store_true', help = "from the wit-0/1.txt")
    parser.add_argument("-fig", action='store_true', help = "draw fig")
    parser.add_argument("-save", action='store_true', help = "save data")
    parser.add_argument("-type", type=int, default=0, help = "0: asp-sat, 1:")
    parser.add_argument("-time", type=int, default=0, help = "the upper bound time limit (s)")

    args = parser.parse_args()

    if args.type == 0: 
        statics_asp_sat(dir=args.dir, wit=args.wit, up_time = args.time)
        ## in the other implimentation
    elif args.type == -1:
        kCNFs(dir=args.dir)

    else:  ## k-cnf
        statistics_k_CNF(cdir=args.dir, _mh=args.mh, _mus=args.mus, draw=args.fig, k=args.k, save=args.save)

