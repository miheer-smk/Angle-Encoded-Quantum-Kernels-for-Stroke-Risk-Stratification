"""Cross-check every mean+/-SD pair printed in the compiled PDF against results.json."""
import json, re, subprocess, sys

PDF='ijqi_stroke_qksp.pdf'
R=json.load(open('results.json'))
txt=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True).stdout

def ms(v):
    m=sum(v)/len(v); return m,(sum((x-m)**2 for x in v)/len(v))**.5

# Build the set of every legitimate mean+/-SD pair, rounded to 3dp.
legit={}
for tag in ('honest','leaky'):
    for mdl,d in R[tag].items():
        for k,v in d.items():
            if k in ('tn','fp','fn','tp'): continue
            m,s=ms(v)
            legit[(round(m,3),round(s,3))]=legit.get((round(m,3),round(s,3)),[])+[f'{tag}/{mdl}/{k}']

# Extract "0.826 +/- 0.024" style pairs from the PDF text (pdftotext renders \pm as ±).
pairs=re.findall(r'(\d\.\d{3})\s*±\s*(\d\.\d{3})',txt)
print('mean+/-SD pairs found in PDF:',len(pairs))
bad=[]
for a,b in pairs:
    key=(float(a),float(b))
    if key not in legit: bad.append((a,b))
if bad:
    print('!! NOT TRACEABLE to results.json:')
    for a,b in sorted(set(bad)): print('   %s ± %s'%(a,b))
else:
    print('OK: every mean±SD pair in the PDF matches results.json')

# Check the specific headline claims.
def g(tag,mdl,k): return ms(R[tag][mdl][k])
checks=[
 ('QSVM honest AUC',      g('honest','QSVM','auc'),      (0.749,0.033)),
 ('RBF honest AUC',       g('honest','RBF-SVM','auc'),   (0.826,0.024)),
 ('QSVM leaky AUC',       g('leaky','QSVM','auc'),       (0.925,0.010)),
 ('RBF leaky AUC',        g('leaky','RBF-SVM','auc'),    (0.954,0.006)),
 ('RF   leaky AUC',       g('leaky','RF','auc'),         (0.997,0.000)),
 ('QSVM honest recall',   g('honest','QSVM','rec'),      (0.613,0.062)),
 ('RBF honest recall',    g('honest','RBF-SVM','rec'),   (0.754,0.077)),
 ('QSVM honest balacc',   g('honest','QSVM','bal_acc'),  (0.693,0.029)),
 ('QSVM honest spec',     g('honest','QSVM','spec'),     (0.773,0.034)),
 ('RBF honest spec',      g('honest','RBF-SVM','spec'),  (0.751,0.033)),
]
print('\nheadline claims:')
for name,(m,s),(em,es) in checks:
    ok='OK ' if (round(m,3)==em and round(s,3)==es) else 'BAD'
    print('  %s %-22s %.4f±%.4f  (paper says %.3f±%.3f)'%(ok,name,m,s,em,es))

# Derived claims stated in the text.
print('\nderived claims:')
infl=[('RBF-SVM',0.128),('QSVM',0.177),('RF',0.193)]
for mdl,claim in infl:
    d=ms(R['leaky'][mdl]['auc'])[0]-ms(R['honest'][mdl]['auc'])[0]
    print('  %-8s AUC inflation %.4f (paper says %.3f) %s'%(mdl,d,claim,'OK' if abs(d-claim)<5e-4 else 'BAD'))
for mdl in ('RBF-SVM','QSVM'):
    h=ms(R['honest'][mdl]['auprc'])[0]; l=ms(R['leaky'][mdl]['auprc'])[0]
    print('  %-8s AUPRC %.3f -> %.3f  (delta %.3f)'%(mdl,h,l,l-h))
sdh=ms(R['honest']['RBF-SVM']['auc'])[1]; sdl=ms(R['leaky']['RBF-SVM']['auc'])[1]
print('  RBF-SVM AUC SD %.3f -> %.3f  (paper says 0.024 -> 0.006)'%(sdh,sdl))
print('  QSVM vs RBF AUC gap %.3f (paper says 0.078)'%(ms(R['honest']['RBF-SVM']['auc'])[0]-ms(R['honest']['QSVM']['auc'])[0]))

# Clinical arithmetic in the conclusions.
prev=248/4981
n=10000; strokes=prev*n; ctrl=n-strokes
rq,rr=ms(R['honest']['QSVM']['rec'])[0],ms(R['honest']['RBF-SVM']['rec'])[0]
sq,sr=ms(R['honest']['QSVM']['spec'])[0],ms(R['honest']['RBF-SVM']['spec'])[0]
print('\nclinical arithmetic per 10,000 screened:')
print('  prevalence %.4f%% -> %.1f strokes (paper says ~498)'%(prev*100,strokes))
print('  QSVM detects %.0f, RBF detects %.0f, difference %.0f (paper says ~305/~375/~70)'%(
      strokes*rq,strokes*rr,strokes*rr-strokes*rq))
print('  false alerts QSVM %.0f, RBF %.0f, QSVM raises %.0f fewer (paper says ~209)'%(
      ctrl*(1-sq),ctrl*(1-sr),ctrl*(1-sr)-ctrl*(1-sq)))

# Kernel stats
ks=[k for k in R['kernel_stats'] if not k['leaky']]
print('\nkernel stats (honest, %d folds):'%len(ks))
print('  off-diag mean %.4f (paper 0.248), SD %.4f (paper 0.238)'%(
      sum(k['mean'] for k in ks)/len(ks), sum(k['std'] for k in ks)/len(ks)))
print('  rank range %d-%d of 1200 (paper 1,176-1,179)'%(min(k['rank'] for k in ks),max(k['rank'] for k in ks)))
print('  train fold sizes %d-%d (paper 6,098-6,393)'%(min(k['n'] for k in ks),max(k['n'] for k in ks)))

# Test fold composition
m=R['honest']['QSVM']
tot=sorted({m['tn'][i]+m['fp'][i]+m['fn'][i]+m['tp'][i] for i in range(15)})
pos=sorted({m['fn'][i]+m['tp'][i] for i in range(15)})
neg=sorted({m['tn'][i]+m['fp'][i] for i in range(15)})
print('  test folds: n=%s, stroke=%s, control=%s (paper 996-997 / 49-50 / 946-947)'%(tot,pos,neg))
