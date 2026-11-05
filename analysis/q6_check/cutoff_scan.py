"""How connected is the crystalline set? Components of PTM fcc/hcp particles vs connection distance."""
import sys, itertools, numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
sys.path.insert(0,'.')
from q6_fast import read_lammpstrj
from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier, CommonNeighborAnalysisModifier
R="../../simulations/4_Clean_NoSwap_Replication/dr_0.04/"
FR=[(9,100,"2.10M"),(9,250,"2.25M"),(12,250,"3.00M")]
for seg,loc,lab in FR:
    path=f"{R}production_3M_seg{seg:03d}/traj.lammpstrj"
    ts,ty,pos,box=next(itertools.islice(read_lammpstrj(path),loc,loc+1))
    for name,mod in (("PTM",PolyhedralTemplateMatchingModifier(rmsd_cutoff=0.10)),("CNA",CommonNeighborAnalysisModifier(mode=CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff))):
        pl=import_file(path,multiple_frames=True); pl.modifiers.append(mod)
        st=np.asarray(pl.compute(loc).particles["Structure Type"])
        cr=np.where(np.isin(st,[1,2]))[0]            # fcc + hcp
        p=pos[cr]%box; tree=cKDTree(p,boxsize=box)
        out=[]
        for c in (1.15,1.25,1.35,1.45):
            pr=tree.query_pairs(c,output_type="ndarray"); n=len(cr)
            g=coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(n,n))
            k,labl=connected_components(g,directed=False); sz=np.sort(np.bincount(labl))[::-1]
            out.append("cut %.2f: largest %3d, #comps>=10: %2d, next %s"%(c,sz[0],(sz>=10).sum(),list(sz[1:4])))
        print(lab,name,"fcc+hcp total =",len(cr)); [print("    ",o) for o in out]
