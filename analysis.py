"""
Supplementary analysis for the revised manuscript.
(1) Random Forest feature importances on the original vs SMOTE-ENN balanced data
    -> Sec 2.3 numbers and Fig. 5 (importance stability).
(2) Pooled McNemar test, QSVM vs RBF-SVM, honest protocol.
Uses exactly the pipeline of reproduce_qksp.py.
"""
import numpy as np, pandas as pd, json
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from imblearn.combine import SMOTEENN
from scipy.stats import binomtest

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
for i in range(NQ): RING=_cnot(i,(i+1)%NQ)@RING

def statevectors(Xa):
    out=np.empty((len(Xa),2**NQ),dtype=complex)
    for r,x in enumerate(Xa):
        psi=np.array([1.0+0j])
        for i in range(NQ):
            q=(RZ(np.pi*x[i])@RY(np.pi*x[i]))[:,0]
            psi=np.kron(psi,q)
        out[r]=RING@psi
    return out

def fidelity_kernel(PA,PB): return np.abs(PB@PA.conj().T)**2

df=pd.read_csv('brain_stroke.csv')
d=df.copy()
for c in d.select_dtypes(include=['object','string']).columns:
    d[c]=LabelEncoder().fit_transform(d[c].astype(str))
ALL=[c for c in d.columns if c!='stroke']
FEATS=['age','avg_glucose_level','bmi','hypertension','heart_disease']
Xall=d[ALL].values.astype(float); y=d['stroke'].values
X=d[FEATS].values.astype(float)
out={}

# ---------- (1) RF importances, averaged over seeds 0,1,2 ----------
def rf_imp(Xa,ya,seeds=(0,1,2)):
    acc=np.zeros(Xa.shape[1])
    for s in seeds:
        acc+=RandomForestClassifier(n_estimators=100,random_state=s,n_jobs=-1).fit(Xa,ya).feature_importances_
    return acc/len(seeds)

imp_orig=rf_imp(Xall,y)
bal=[SMOTEENN(random_state=s).fit_resample(Xall,y) for s in (0,1,2)]
imp_bal=np.mean([RandomForestClassifier(n_estimators=100,random_state=s,n_jobs=-1)
                 .fit(Xb,yb).feature_importances_ for s,(Xb,yb) in zip((0,1,2),bal)],axis=0)

out['features']=ALL
out['imp_original']={f:float(v) for f,v in zip(ALL,imp_orig)}
out['imp_balanced']={f:float(v) for f,v in zip(ALL,imp_bal)}
idx=[ALL.index(f) for f in FEATS]
out['selected_cum_original']=float(imp_orig[idx].sum())
out['selected_cum_balanced']=float(imp_bal[idx].sum())
out['max_abs_shift_pp']=float(np.max(np.abs(imp_bal-imp_orig))*100)
out['balanced_sizes']=[[int((yb==0).sum()),int((yb==1).sum())] for _,yb in bal]

print("== RF importance (mean of seeds 0-2) ==")
print("%-20s %10s %10s %8s"%("feature","original","balanced","shift pp"))
for f in sorted(ALL,key=lambda f:-imp_bal[ALL.index(f)]):
    i=ALL.index(f)
    print("%-20s %10.4f %10.4f %8.2f"%(f,imp_orig[i],imp_bal[i],(imp_bal[i]-imp_orig[i])*100))
print("selected-5 cumulative: original %.4f  balanced %.4f"%(out['selected_cum_original'],out['selected_cum_balanced']))
print("max abs shift: %.2f pp"%out['max_abs_shift_pp'])
print("SMOTE-ENN balanced sizes (neg,pos):",out['balanced_sizes'])

# ---------- (2) Pooled McNemar, honest protocol ----------
b=c=0; nt=0
for seed in (0,):
    skf=StratifiedKFold(5,shuffle=True,random_state=seed)
    for tr,te in skf.split(X,y):
        Xtr,Xte,ytr,yte=X[tr],X[te],y[tr],y[te]
        Xtr,ytr=SMOTEENN(random_state=seed).fit_resample(Xtr,ytr)
        sc=MinMaxScaler((-1,1)).fit(Xtr)
        A=sc.transform(Xtr); B=np.clip(sc.transform(Xte),-1,1)
        rbf=SVC(kernel='rbf',C=1.0,gamma='scale',probability=True,random_state=seed).fit(A,ytr)
        pr=rbf.predict(B)
        PA=statevectors(A); PB=statevectors(B)
        q=SVC(kernel='precomputed',C=1.0,probability=True,random_state=seed).fit(fidelity_kernel(PA,PA),ytr)
        pq=q.predict(fidelity_kernel(PA,PB))
        cr=(pr==yte); cq=(pq==yte)
        b+=int(np.sum(cr&~cq)); c+=int(np.sum(cq&~cr)); nt+=len(yte)
        print("  fold n=%d  classic-only-correct=%d  quantum-only-correct=%d"%(len(yte),np.sum(cr&~cq),np.sum(cq&~cr)))

p=binomtest(b,b+c,0.5).pvalue
out['mcnemar']=dict(classic_correct_quantum_wrong=b,quantum_correct_classic_wrong=c,
                    n_total=nt,p_two_sided=float(p))
print("\n== Pooled McNemar (honest, seed 0, 5 held-out splits, n=%d) =="%nt)
print("classical-correct/quantum-wrong b=%d ; quantum-correct/classical-wrong c=%d"%(b,c))
print("exact two-sided p = %.3e"%p)

json.dump(out,open('analysis.json','w'),indent=1)
