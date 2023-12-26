#%%
import pandas as pd
from tqdm import tqdm
import numpy as np
from scipy.stats import rankdata
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
#%%
class factor_test():

    def __init__(self):
        self.factor=pd.DataFrame()
        self.ret=pd.DataFrame()
        self.fac_rank=pd.DataFrame()
        self.ret_rank=pd.DataFrame()
        self.ranks=[]

    def rankIC(self):
        df_ret=self.ret.pivot_table(index='date',columns='cn_code',values='daily_ret').fillna(method='pad').dropna(axis=1)

        #将前一日因子与后一日收益率对齐
        df_tmp=self.factor.shift(1).stack().reset_index().rename(columns={'level_1':'cn_code',0:'factor'}).dropna(axis=1)
        df_tmp['cn_code']=df_tmp['cn_code'].astype('Int64')
        df_tmp=pd.merge(df_tmp,df_ret.stack().reset_index().rename(columns={0:'daily_ret'}),on=['date','cn_code'],how='inner')


        #分别计算rank值
        df_fac=df_tmp.pivot_table(index='date',columns='cn_code',values='factor')
        df_ret=df_tmp.pivot_table(index='date',columns='cn_code',values='daily_ret').fillna(method='pad')

        self.fac_rank=df_fac.apply(lambda row:row.rank(),axis=1).astype(int)
        self.ret_rank=df_ret.apply(lambda row:row.rank(),axis=1).astype(int)

        self.ranks=[spearmanr(self.fac_rank.iloc[i].values,self.ret_rank.iloc[i].values)[0] for i in range(self.fac_rank.shape[0])]

        return self.ranks[0]
    
    def RankICIR(self):
        return np.mean(self.ranks)/np.std(self.ranks)
    
    def Hedge(self):
        #多空分类
        df_tmp=self.fac_rank.stack().reset_index().rename(columns={0:'rank'})
        df_tmp=pd.merge(df_tmp,self.ret,on=['date','cn_code'],how='left')

        df_ret=df_tmp.pivot_table(index='date',columns='cn_code',values='daily_ret')+1
        N=df_ret.shape[1]
        n_group=N//10

        long=df_ret[self.fac_rank<n_group]
        long=long.apply(lambda row:np.nanmean(row),axis=1).cumprod()

        short=df_ret[self.fac_rank>=(N-n_group)]
        short=short.apply(lambda row:np.nanmean(row),axis=1).cumprod()

        df_hedge=pd.merge(pd.DataFrame(long),pd.DataFrame(short),on='date',how='inner')
        df_hedge.index=pd.to_datetime(df_hedge.index.astype(str))

        plt.plot(df_hedge)
#%%
'''
AShareMoneyFlow因子检验
'''
NI_test=factor_test()
NI_test.factor=pd.read_csv('./data/factor_raw/NI.csv',index_col=0)
NI_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NI_ACT_test=factor_test()
NI_ACT_test.factor=pd.read_csv('./data/factor_raw/NI_ACT.csv',index_col=0)
NI_ACT_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NIR_test=factor_test()
NIR_test.factor=pd.read_csv('./data/factor_raw/NIR.csv',index_col=0).dropna(axis=1)
NIR_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NIR_ACT_test=factor_test()
NIR_ACT_test.factor=pd.read_csv('./data/factor_raw/NIR_ACT.csv',index_col=0).dropna(axis=1)
NIR_ACT_test.ret=pd.read_csv('./data/return.csv',index_col=0)
#%%
[NI_test.rankIC(),NI_ACT_test.rankIC(),NIR_test.rankIC(),NIR_ACT_test.rankIC()]
#%%
[NI_test.RankICIR(),NI_ACT_test.RankICIR(),NIR_test.RankICIR(),NIR_ACT_test.RankICIR()]
# %%
'''
MOD修正因子
'''
NI_MOD_test=factor_test()
NI_MOD_test.factor=pd.read_csv('./data/factor_MOD/NI.csv',index_col=0)
NI_MOD_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NI_ACT_MOD_test=factor_test()
NI_ACT_MOD_test.factor=pd.read_csv('./data/factor_MOD/NI_ACT.csv',index_col=0)
NI_ACT_MOD_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NIR_MOD_test=factor_test()
NIR_MOD_test.factor=pd.read_csv('./data/factor_MOD/NIR.csv',index_col=0).dropna(axis=1)
NIR_MOD_test.ret=pd.read_csv('./data/return.csv',index_col=0)

NIR_ACT_MOD_test=factor_test()
NIR_ACT_MOD_test.factor=pd.read_csv('./data/factor_MOD/NIR_ACT.csv',index_col=0).dropna(axis=1)
NIR_ACT_MOD_test.ret=pd.read_csv('./data/return.csv',index_col=0)

#%%
[NI_MOD_test.rankIC(),NI_ACT_MOD_test.rankIC(),NIR_MOD_test.rankIC(),NIR_ACT_MOD_test.rankIC()]
#%%
[NI_MOD_test.RankICIR(),NI_ACT_MOD_test.RankICIR(),NIR_MOD_test.RankICIR(),NIR_ACT_MOD_test.RankICIR()]

# %%
'''
CNIR因子
'''
CNIR_test=factor_test()
CNIR_test.factor=pd.read_csv('./data/factor_CNIR/CNIR.csv',index_col=0)
CNIR_test.ret=pd.read_csv('./data/return.csv',index_col=0)
#%%
CNIR_test.rankIC()
#%%
CNIR_test.RankICIR()
# %%
NI_test.Hedge()
# %%
NI_MOD_test.Hedge()
# %%
CNIR_test.Hedge()

# %%
