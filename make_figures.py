"""Regenerate Figs 4-7 from real data / results.json, and run McNemar for seeds 0,1,2."""
import numpy as np, pandas as pd, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from imblearn.combine import SMOTEENN
from scipy.stats import binomtest
import warnings; warnings.filterwarnings('ignore')

SP=''
OUT='figures/'
import os; os.makedirs(OUT,exist_ok=True)
R=json.load(open('results.json'))
A=json.load(open(SP+'analysis.json'))
def ms(v):
    m=float(np.mean(v)); return m,float(np.std(v))

MODELS=['QSVM','RBF-SVM','KNN','RF','DT']
LBL={'QSVM':'QSVM','RBF-SVM':'RBF-SVM','KNN':'KNN (k=5)','RF':'Random Forest','DT':'Decision Tree'}
COL={'QSVM':'#E8833A','RBF-SVM':'#4C9BC0','KNN':'#8367A8','RF':'#B5541F','DT':'#2E6070'}

# ---------------- Fig 4: RF importance, real values ----------------
FEATS=['age','avg_glucose_level','bmi','hypertension','heart_disease']
names={'age':'Age','avg_glucose_level':'Avg Glucose','bmi':'BMI','hypertension':'Hypertension',
       'heart_disease':'Heart Disease','smoking_status':'Smoking Status','work_type':'Work Type',
       'Residence_type':'Residence Type','ever_married':'Ever Married','gender':'Gender'}
imp=A['imp_original']
order=sorted(imp,key=lambda f:imp[f])
fig,ax=plt.subplots(1,2,figsize=(13.5,5.0))
cols=['#5BB98C' if f in FEATS else '#E06B6B' for f in order]
ax[0].barh([names[f] for f in order],[imp[f] for f in order],color=cols,edgecolor='#333',lw=.6)
for i,f in enumerate(order): ax[0].text(imp[f]+.004,i,'%.4f'%imp[f],va='center',fontsize=8.5)
ax[0].set_xlabel('Random Forest importance (original data)'); ax[0].set_xlim(0,0.34)
ax[0].set_title('All 10 features ranked by importance',fontsize=10)
h=[plt.Rectangle((0,0),1,1,color='#5BB98C'),plt.Rectangle((0,0),1,1,color='#E06B6B')]
ax[0].legend(h,['Selected for quantum encoding (clinical)','Not encoded'],fontsize=8,loc='lower right')
desc=sorted(imp,key=lambda f:-imp[f]); vals=[imp[f] for f in desc]; cum=np.cumsum(vals)
ax[1].bar(range(10),vals,color=['#5BB98C' if f in FEATS else '#E06B6B' for f in desc],edgecolor='#333',lw=.6)
ax[1].set_ylim(0,0.40)
ax2=ax[1].twinx(); ax2.plot(range(10),cum,'o-',color='#2b7bba',lw=1.6,ms=4.5,label='Cumulative importance')
selcum=A['selected_cum_original']
ax2.set_ylim(0,1.28); ax2.set_yticks(np.arange(0,1.01,0.2)); ax2.set_ylabel('Cumulative importance',color='#2b7bba')
ax[1].set_xticks(range(10)); ax[1].set_xticklabels([names[f] for f in desc],rotation=45,ha='right',fontsize=8)
ax[1].set_ylabel('Individual importance'); ax[1].set_title('Cumulative importance of RF-ranked features',fontsize=10)
ax2.legend(fontsize=8,loc='center right')
ax[1].text(0.02,0.975,'Green = the 5 clinically selected features,\ntogether %.1f%% of total RF importance'%(selcum*100),
           transform=ax[1].transAxes,va='top',ha='left',fontsize=8.5,
           bbox=dict(fc='#eef7f0',ec='#5BB98C',lw=.8,boxstyle='round,pad=0.35'))
fig.suptitle('Random Forest feature importance on the stroke dataset (N=4,981)',fontsize=12,y=0.99)
fig.tight_layout(); fig.savefig(OUT+'fig4_rf_importance.png',dpi=200); plt.close(fig)

# ---------------- Fig 5: importance before/after SMOTE-ENN (real shifts) ----------------
io,ib=A['imp_original'],A['imp_balanced']
fig,ax=plt.subplots(figsize=(10,4.6))
x=np.arange(len(FEATS)); w=0.38
ax.bar(x-w/2,[io[f] for f in FEATS],w,label='Original (19:1 imbalanced)',color='#E06B6B',edgecolor='#333',lw=.6)
ax.bar(x+w/2,[ib[f] for f in FEATS],w,label='After SMOTE-ENN (training fold)',color='#5BB98C',edgecolor='#333',lw=.6)
for i,f in enumerate(FEATS):
    ax.text(i-w/2,io[f]+.006,'%.3f'%io[f],ha='center',fontsize=8)
    ax.text(i+w/2,ib[f]+.006,'%.3f'%ib[f],ha='center',fontsize=8)
    ax.text(i,-0.035,'%+.1f pp'%((ib[f]-io[f])*100),ha='center',fontsize=8.5,color='#c2410c')
ax.set_xticks(x); ax.set_xticklabels([names[f] for f in FEATS])
ax.set_ylabel('Random Forest importance'); ax.set_ylim(-0.05,0.47); ax.legend(fontsize=9)
ax.set_title('Feature importance is NOT stable across SMOTE-ENN balancing',fontsize=11)
fig.tight_layout(); fig.savefig(OUT+'fig5_importance_shift.png',dpi=200); plt.close(fig)

# ---------------- Fig 6: honest-protocol metric comparison ----------------
mets=[('auc','AUC'),('auprc','AUPRC'),('rec','Recall'),('bal_acc','Balanced Acc.'),
      ('prec','Precision'),('f1','F1'),('acc','Accuracy')]
fig,ax=plt.subplots(figsize=(12.5,4.8))
x=np.arange(len(mets)); w=0.16
for j,m in enumerate(MODELS):
    mu=[ms(R['honest'][m][k])[0] for k,_ in mets]; sd=[ms(R['honest'][m][k])[1] for k,_ in mets]
    ax.bar(x+(j-2)*w,mu,w,yerr=sd,capsize=2.5,label=LBL[m],color=COL[m],edgecolor='#222',lw=.5,
           error_kw=dict(lw=.8))
ax.set_xticks(x); ax.set_xticklabels([n for _,n in mets]); ax.set_ylim(0,1.0)
ax.set_ylabel('Score'); ax.legend(ncol=5,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.09))
ax.set_title('Leakage-free protocol: all metrics, mean $\\pm$ SD over 15 folds (N=4,981, 4.98% prevalence)',fontsize=11)
ax.grid(axis='y',ls=':',alpha=.5); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(OUT+'fig6_metrics_honest.png',dpi=200,bbox_inches='tight'); plt.close(fig)

# ---------------- Fig 7: honest vs leaky AUC ----------------
fig,axs=plt.subplots(1,2,figsize=(12.5,4.6),sharey=True)
for a,tag,t in zip(axs,('honest','leaky'),
        ('Leakage-free protocol\n(split first, SMOTE-ENN inside training fold)',
         'Leaky protocol\n(SMOTE-ENN on full data, then split)')):
    mu=[ms(R[tag][m]['auc'])[0] for m in MODELS]; sd=[ms(R[tag][m]['auc'])[1] for m in MODELS]
    a.bar(range(5),mu,yerr=sd,capsize=3,color=[COL[m] for m in MODELS],edgecolor='#222',lw=.6,error_kw=dict(lw=.9))
    for i,(u,s) in enumerate(zip(mu,sd)): a.text(i,u+s+.015,'%.3f'%u,ha='center',fontsize=9,fontweight='bold')
    a.set_xticks(range(5)); a.set_xticklabels([LBL[m] for m in MODELS],rotation=20,ha='right',fontsize=9)
    a.set_title(t,fontsize=10); a.set_ylim(0,1.24); a.set_yticks(np.arange(0,1.01,0.2))
    a.grid(axis='y',ls=':',alpha=.5); a.set_axisbelow(True)
axs[0].set_ylabel('AUC (mean $\\pm$ SD, 15 folds)')
axs[1].axhline(0.9952,ls='--',color='#b00',lw=1.2)
axs[1].text(-0.35,1.015,'accuracy 99.52% reported in prior work on this dataset',fontsize=8.5,color='#b00',ha='left',va='bottom')
fig.suptitle('Resampling protocol determines apparent performance',fontsize=12)
fig.tight_layout(); fig.savefig(OUT+'fig7_protocol_ablation.png',dpi=200); plt.close(fig)

# ---------------- McNemar for seeds 0,1,2 ----------------
if os.environ.get('SKIP_MCNEMAR'):
    print('figures written to',OUT); raise SystemExit
NQ=5
def RYm(t): return np.array([[np.cos(t/2),-np.sin(t/2)],[np.sin(t/2),np.cos(t/2)]],dtype=complex)
def RZm(t): return np.array([[np.exp(-1j*t/2),0],[0,np.exp(1j*t/2)]],dtype=complex)
def _cnot(c,t,n=NQ):
    D=2**n; M=np.zeros((D,D),dtype=complex)
    for b in range(D):
        bits=[(b>>(n-1-k))&1 for k in range(n)]
        if bits[c]==1: bits[t]^=1
        M[sum(bit<<(n-1-k) for k,bit in enumerate(bits)),b]=1
    return M
RING=np.eye(2**NQ,dtype=complex)
for i in range(NQ): RING=_cnot(i,(i+1)%NQ)@RING
def sv(Xa):
    o=np.empty((len(Xa),2**NQ),dtype=complex)
    for r,x in enumerate(Xa):
        p=np.array([1.0+0j])
        for i in range(NQ): p=np.kron(p,(RZm(np.pi*x[i])@RYm(np.pi*x[i]))[:,0])
        o[r]=RING@p
    return o
df=pd.read_csv('brain_stroke.csv')
d=df.copy()
for c in d.select_dtypes(include=['object','string']).columns:
    d[c]=LabelEncoder().fit_transform(d[c].astype(str))
X=d[FEATS].values.astype(float); y=d['stroke'].values
mc={}
for seed in (0,1,2):
    b=c=0
    for tr,te in StratifiedKFold(5,shuffle=True,random_state=seed).split(X,y):
        Xtr,Xte,ytr,yte=X[tr],X[te],y[tr],y[te]
        Xtr,ytr=SMOTEENN(random_state=seed).fit_resample(Xtr,ytr)
        sc=MinMaxScaler((-1,1)).fit(Xtr); Aa=sc.transform(Xtr); B=np.clip(sc.transform(Xte),-1,1)
        pr=SVC(kernel='rbf',C=1.0,gamma='scale',random_state=seed).fit(Aa,ytr).predict(B)
        PA,PB=sv(Aa),sv(B)
        K=lambda P,Q: np.abs(Q@P.conj().T)**2
        pq=SVC(kernel='precomputed',C=1.0,random_state=seed).fit(K(PA,PA),ytr).predict(K(PA,PB))
        cr,cq=(pr==yte),(pq==yte)
        b+=int(np.sum(cr&~cq)); c+=int(np.sum(cq&~cr))
    p=binomtest(b,b+c,0.5).pvalue
    mc[seed]=dict(b=b,c=c,p=float(p))
    print('seed %d: classic-only=%d quantum-only=%d  p=%.4g'%(seed,b,c,p))
A['mcnemar_by_seed']=mc
json.dump(A,open(SP+'analysis.json','w'),indent=1)
print('figures written to',OUT)
