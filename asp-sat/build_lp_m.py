import sys
import os
import subprocess


def build_CO(dirs, AllInstances=False):
# compute an answer set for each intance
# of complext optimization answer sets
# in the ASP compeition 2015
# dirs: the directory where the asp program and its instances are

  asp_solver="clingo"
  asp_grounder="gringo"
  if not dirs.endswith("/"):
    dirs = dirs + "/"
  lp=dirs + "encoding.asp"
  if AllInstances:
    files = list(os.walk(dirs))[0][2]
    files = [f for f in files if f.startswith('0') and f.endswith(".asp")]
    #files = [f for f in files if (f.startswith('0') or f.startswith('1') or f.startswith('2'))  and f.endswith(".asp")]
  else:
    # from instances.competition file
    fp = open(dirs+"instances.competition", "r")
    files = [x.replace("\n","") for x in fp.readlines()]
   
  for f in files:
    f = dirs + f 
    # "/home/wys/asp/ComplexOptimizationOfAnswerSets/"+f
    fm_name = f.replace(".asp",".m")
    if os.path.exists(fm_name): continue
    flp_name = f.replace(".asp",".lp")
    fm = open(f.replace(".asp", ".m"), "w+")
    flp = open(f.replace(".asp", ".lp"), "w")
    subprocess.call([asp_grounder, "-t", f, lp], stdout=flp) 
    subprocess.call([asp_solver, "--time-limit=7200", "--verbose=0", f, lp], stdout=fm)  
    fm.seek(0)
    Line=fm.read(6)
    if Line.find('UNSAT') != -1 or Line.find('UNKNOWN') != -1: continue
    #if Line[0:5] =="UNKNOWN" or Line[0:4] == "UNSAT": continue
    #print("python3.7 cb_witness.py -t 7200 -lp -v4 -TT_PYSAT -q %s %s "%(fm_name,flp_name),file=sys.stdout)
    #subprocess.call(["python3.7", "cb_witness.py", "-t 7200", "-lp", "-mh", "-v4", "-TT_PYSAT", "-q", flp_name, fm_name])
    fm.close()
    flp.close()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    printf("Usage %s <Dir>"%sys.argv[1])
  build_CO(sys.argv[1], True)


