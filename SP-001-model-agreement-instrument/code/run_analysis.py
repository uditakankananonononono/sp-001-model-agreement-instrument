from pathlib import Path
import json, hashlib
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score, accuracy_score

ROOT=Path(__file__).resolve().parents[1]
cols=['id','diagnosis']+[f'{stat}_{feat}' for stat in ['mean','se','worst'] for feat in ['radius','texture','perimeter','area','smoothness','compactness','concavity','concave_points','symmetry','fractal_dimension']]
df=pd.read_csv(ROOT/'data/raw/wdbc.data',header=None,names=cols)
X=df.drop(columns=['id','diagnosis']); y=(df.diagnosis=='M').astype(int).to_numpy()
models={
 'logistic':make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=1)),
 'rbf_svm':make_pipeline(StandardScaler(),SVC(C=2,probability=True,random_state=2)),
 'random_forest':RandomForestClassifier(n_estimators=80,min_samples_leaf=2,max_features='sqrt',random_state=3,n_jobs=-1),
 'knn':make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=11,weights='distance')),
 'gaussian_nb':GaussianNB()
}
rkf=RepeatedStratifiedKFold(n_splits=5,n_repeats=20,random_state=20260921)
rows=[]
for fold,(tr,te) in enumerate(rkf.split(X,y)):
 probs=[]
 for name,m in models.items():
  m.fit(X.iloc[tr],y[tr]); probs.append(m.predict_proba(X.iloc[te])[:,1])
 probs=np.column_stack(probs); ens=probs.mean(1); pred=(ens>=.5).astype(int)
 # disagreement: probability SD plus binary vote entropy, standardized within fold only by rank
 vote=(probs>=.5).mean(1)
 entropy=-(np.clip(vote,1e-8,1-1e-8)*np.log(np.clip(vote,1e-8,1)) + np.clip(1-vote,1e-8,1)*np.log(np.clip(1-vote,1e-8,1)))
 raw=probs.std(1)+entropy/np.log(2)
 rank=pd.Series(raw).rank(pct=True,method='average').to_numpy()
 for j,idx in enumerate(te):
  r={'repeat_fold':fold,'sample_index':int(idx),'id':int(df.id.iloc[idx]),'y':int(y[idx]),'ensemble_prob':float(ens[j]),'prediction':int(pred[j]),'error':int(pred[j]!=y[idx]),'disagreement_raw':float(raw[j]),'disagreement_percentile_within_fold':float(rank[j])}
  r.update({f'prob_{n}':float(probs[j,k]) for k,n in enumerate(models)})
  rows.append(r)
oof=pd.DataFrame(rows)
# pre-locked top quintile
hi=oof.disagreement_percentile_within_fold>.8
err_hi=oof.loc[hi,'error'].mean(); err_lo=oof.loc[~hi,'error'].mean(); err_all=oof.error.mean(); enrichment=err_hi/err_lo
reduction=(err_all-err_lo)/err_all
# cluster bootstrap by sample ID so repeated held-out predictions do not pretend independence
rng=np.random.default_rng(20260921); ids=oof.id.unique(); boots=[]
agg=[]
for i in ids:
 z=oof[oof.id==i]; h=z.disagreement_percentile_within_fold>.8
 agg.append([int((h & (z.error==1)).sum()),int(h.sum()),int((~h & (z.error==1)).sum()),int((~h).sum())])
agg=np.asarray(agg,float)
for _ in range(5000):
 w=rng.multinomial(len(ids),np.full(len(ids),1/len(ids)))
 he,hn,le,ln=w@agg
 if hn>0 and ln>0 and le>0: boots.append((he/hn)/(le/ln))
ci=np.quantile(boots,[.025,.975])
metrics={'n_samples':len(df),'held_out_predictions':len(oof),'malignant_fraction':float(y.mean()),'ensemble_auc':float(roc_auc_score(oof.y,oof.ensemble_prob)),'ensemble_accuracy':float(accuracy_score(oof.y,oof.prediction)),'overall_error':float(err_all),'top_quintile_error':float(err_hi),'remaining_error':float(err_lo),'error_enrichment':float(enrichment),'enrichment_ci95_cluster_bootstrap':[float(ci[0]),float(ci[1])],'selective_error_reduction':float(reduction),'success':bool(enrichment>=2 and reduction>=.25 and ci[0]>1)}
(ROOT/'data/processed').mkdir(exist_ok=True); (ROOT/'results').mkdir(exist_ok=True); (ROOT/'figures').mkdir(exist_ok=True)
oof.to_csv(ROOT/'data/processed/held_out_predictions.csv',index=False)
json.dump(metrics,open(ROOT/'results/metrics.json','w'),indent=2)
# calibration-like risk plot by disagreement decile
q=pd.qcut(oof.disagreement_percentile_within_fold,10,duplicates='drop')
s=oof.groupby(q,observed=True).agg(error_rate=('error','mean'),n=('error','size'),mean_disagreement=('disagreement_percentile_within_fold','mean')).reset_index(drop=True)
s.to_csv(ROOT/'results/disagreement_deciles.csv',index=False)
sns.set_theme(style='whitegrid',context='talk')
fig,ax=plt.subplots(figsize=(9,6)); ax.plot(s.mean_disagreement,s.error_rate,marker='o',lw=2); ax.set(xlabel='Mean within-fold disagreement percentile',ylabel='Held-out error rate',title='Model disagreement concentrates diagnostic errors'); fig.tight_layout(); fig.savefig(ROOT/'figures/error_by_disagreement.png',dpi=220); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,6)); ax.hist(oof.loc[oof.error==0,'disagreement_percentile_within_fold'],bins=20,alpha=.65,label='Correct',density=True); ax.hist(oof.loc[oof.error==1,'disagreement_percentile_within_fold'],bins=20,alpha=.65,label='Error',density=True); ax.set(xlabel='Disagreement percentile',ylabel='Density',title='Errors shift toward high cross-model disagreement'); ax.legend(); fig.tight_layout(); fig.savefig(ROOT/'figures/disagreement_error_hist.png',dpi=220); plt.close(fig)
# coverage-risk curve
cov=[]
for abst in np.linspace(0,.5,51):
 keep=oof.disagreement_percentile_within_fold <= 1-abst
 cov.append({'abstention_fraction':float(abst),'coverage':float(keep.mean()),'error_rate':float(oof.loc[keep,'error'].mean())})
pd.DataFrame(cov).to_csv(ROOT/'results/coverage_risk.csv',index=False)
fig,ax=plt.subplots(figsize=(9,6)); c=pd.DataFrame(cov); ax.plot(c.coverage,c.error_rate,lw=3); ax.invert_xaxis(); ax.set(xlabel='Coverage (fraction receiving prediction)',ylabel='Error rate',title='Selective prediction: risk falls as disagreement triggers abstention'); fig.tight_layout(); fig.savefig(ROOT/'figures/coverage_risk.png',dpi=220); plt.close(fig)
print(json.dumps(metrics,indent=2))
