"""
Honest re-run of the EXISTING methodology. Nothing new is introduced:
same dataset, same SMOTE-ENN, same 5 features, same baselines, same
angle-encoded 5-qubit feature map. Only the PROTOCOL is corrected.
"""
import numpy as np, pandas as pd, json, time
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, recall_score, precision_score,
                             f1_score, roc_auc_score, average_precision_score,
                             balanced_accuracy_score, confusion_matrix)
from imblearn.combine import SMOTEENN

NQ = 5
def RY(t): return np.array([[np.cos(t/2),-np.sin(t/2)],[np.sin(t/2),np.cos(t/2)]],dtype=complex)
def RZ(t): return np.array([[np.exp(-1j*t/2),0],[0,np.exp(1j*t/2)]],dtype=complex)
def _cnot(c,t,n=NQ):
    D=2**n; M=np.zeros((D,D),dtype=complex)
    for b in range(D):
        bits=[(b>>(n-1-k))&1 for k in range(n)]
        if bits[c]==1: bits[t]^=1
        M[sum(bit<<(n-1-k) for k,bit in enumerate(bits)),b]=1
    return M
RING=np.eye(2**NQ,dtype=complex)
for i in range(NQ): RING=_cnot(i,(i+1)%NQ)@RING   # CNOT ring as described in the paper

def statevectors(Xa):
    """RY(pi*x) then RZ(pi*x) per qubit, then CNOT ring. Exact statevector."""
    out=np.empty((len(Xa),2**NQ),dtype=complex)
    for r,x in enumerate(Xa):
        psi=np.array([1.0+0j])
        for i in range(NQ):
            q=(RZ(np.pi*x[i])@RY(np.pi*x[i]))[:,0]
            psi=np.kron(psi,q)
        out[r]=RING@psi
    return out

def fidelity_kernel(PA,PB):
    return np.abs(PB@PA.conj().T)**2

def metrics(yt,yp,ys):
    tn,fp,fn,tp=confusion_matrix(yt,yp,labels=[0,1]).ravel()
    return dict(acc=accuracy_score(yt,yp), bal_acc=balanced_accuracy_score(yt,yp),
                rec=recall_score(yt,yp,zero_division=0),
                prec=precision_score(yt,yp,zero_division=0),
                f1=f1_score(yt,yp,zero_division=0),
                spec=tn/(tn+fp) if tn+fp else 0.0,
                auc=roc_auc_score(yt,ys), auprc=average_precision_score(yt,ys),
                tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))

df=pd.read_csv('brain_stroke.csv')
d=df.copy()
for c in d.select_dtypes(include=['object','string']).columns:
    d[c]=LabelEncoder().fit_transform(d[c].astype(str))
FEATS=['age','avg_glucose_level','bmi','hypertension','heart_disease']  # the paper's 5
X=d[FEATS].values.astype(float); y=d['stroke'].values

SEEDS=[0,1,2,3,4]
res={"honest":{}, "leaky":{}, "kernel_stats":[], "preds":{}}

def run_protocol(leaky, seed):
    """leaky=True reproduces the paper's protocol (balance whole set, then split)."""
    out={}
    if leaky:
        Xb,yb=SMOTEENN(random_state=seed).fit_resample(X,y)
    else:
        Xb,yb=X,y
    skf=StratifiedKFold(5,shuffle=True,random_state=seed)
    fold_rows=[]
    for tr,te in skf.split(Xb,yb):
        Xtr,Xte,ytr,yte=Xb[tr],Xb[te],yb[tr],yb[te]
        if not leaky:
            Xtr,ytr=SMOTEENN(random_state=seed).fit_resample(Xtr,ytr)
        sc=MinMaxScaler((-1,1)).fit(Xtr)
        A=sc.transform(Xtr); B=np.clip(sc.transform(Xte),-1,1)
        row={}
        for name,m in [("RBF-SVM",SVC(kernel='rbf',C=1.0,gamma='scale',probability=True,random_state=seed)),
                       ("KNN",KNeighborsClassifier(5)),
                       ("DT",DecisionTreeClassifier(max_depth=10,random_state=seed)),
                       ("RF",RandomForestClassifier(n_estimators=100,random_state=seed,n_jobs=-1))]:
            m.fit(A,ytr); row[name]=metrics(yte,m.predict(B),m.predict_proba(B)[:,1])
        PA=statevectors(A); PB=statevectors(B)
        Ktr=fidelity_kernel(PA,PA); Kte=fidelity_kernel(PA,PB)
        off=Ktr[~np.eye(len(Ktr),dtype=bool)]
        res["kernel_stats"].append(dict(leaky=leaky,seed=int(seed),n=int(len(Ktr)),
            mean=float(off.mean()),std=float(off.std()),
            rank=int(np.linalg.matrix_rank(Ktr[:1200,:1200],tol=1e-8))))
        q=SVC(kernel='precomputed',C=1.0,probability=True,random_state=seed).fit(Ktr,ytr)
        row["QSVM"]=metrics(yte,q.predict(Kte),q.predict_proba(Kte)[:,1])
        fold_rows.append(row)
    for mdl in fold_rows[0]:
        out[mdl]={k:[f[mdl][k] for f in fold_rows] for k in fold_rows[0][mdl]}
    return out

t0=time.time()
for seed in SEEDS:
    for leaky in (False,True):
        tag="leaky" if leaky else "honest"
        r=run_protocol(leaky,seed)
        for mdl,vals in r.items():
            res[tag].setdefault(mdl,{})
            for k,v in vals.items():
                res[tag][mdl].setdefault(k,[]).extend(v)
    print(f"  seed {seed} done  t={time.time()-t0:.0f}s",flush=True)

json.dump(res,open('results.json','w'),indent=1)

print("\n%-9s %-8s %-14s %-14s %-14s %-14s"%("PROTOCOL","MODEL","AUC","Recall","Precision","Bal.Acc"))
print("-"*82)
for tag in ("honest","leaky"):
    for mdl in ["RBF-SVM","KNN","DT","RF","QSVM"]:
        m=res[tag][mdl]
        f=lambda k:"%.3f±%.3f"%(np.mean(m[k]),np.std(m[k]))
        print("%-9s %-8s %-14s %-14s %-14s %-14s"%(tag,mdl,f('auc'),f('rec'),f('prec'),f('bal_acc')))
    print("-"*82)
