import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn import metrics

train = pd.read_csv('../feature/trainb_featureV2.csv')
test = pd.read_csv('../feature/testb_featureV2.csv')

dtrain = xgb.DMatrix(train.drop(['uid','label'],axis=1),label=train.label)
dtest = xgb.DMatrix(test.drop(['uid'],axis=1))

def evalMetric(preds,dtrain):
    label = dtrain.get_label()
    pre = pd.DataFrame({'preds':preds,'label':label})
    pre= pre.sort_values(by='preds',ascending=False)
    
    auc = metrics.roc_auc_score(pre.label,pre.preds)

    pre.preds=pre.preds.map(lambda x: 1 if x>=0.5 else 0)

    f1 = metrics.f1_score(pre.label,pre.preds)
    res = 0.6*auc +0.4*f1
    return 'res',res
	
params = {
    'objective':'rank:pairwise',
    'learning rate':0.1,
    'alpha':10.006,
    # 'scale_pos_weight':2,
    'gamma': 0.01,
    'subsample': 0.8,
    'min_child_weight':1,
    'max_depth':5,
    'colsample_bytree':0.85,
}

xgb.cv(params, dtrain, feval=evalMetric, nfold=4, num_boost_round=200)

model = xgb.train(params, dtrain,feval=evalMetric, num_boost_round=200)
pred=model.predict(dtest)
res =pd.DataFrame({'uid':test.uid,'label':pred})
res=res.sort_values(by='label',ascending=False)
res.label=res.label.map(lambda x: 1 if x>=0.6 else 0)
res.label = res.label.map(lambda x: int(x))
res.label.sum()
res.to_csv('testb.csv',index=False,header=False,sep=',',columns=['uid','label'])
