#%%
import pandas as pd
import numpy as np
from tqdm import tqdm
import statsmodels.api as sm
# %%
df_money=pd.read_csv('./data/money.csv',index_col=0)

'''
AShareMoneyFlow因子
'''
#计算因子值
df_money['buy_large_amt']=df_money[['buy_elg_amt', 'buy_lg_amt', 'buy_med_amt']].sum(axis=1)
df_money['sell_large_amt']=df_money[['sell_elg_amt', 'sell_lg_amt','sell_med_amt']].sum(axis=1)
df_money['b_plus_s']=df_money['buy_large_amt']+df_money['sell_large_amt']
df_money['b_minus_s']=df_money['buy_large_amt']-df_money['sell_large_amt']

df_money['buy_act_amt']=df_money[['buy_act_elg_vol', 'buy_act_lg_vol', 'buy_act_med_vol']].sum(axis=1)
df_money['sell_act_amt']=df_money[['sell_act_elg_vol','sell_act_lg_vol', 'sell_act_med_vol']].sum(axis=1)
df_money['act_b_plus_s']=df_money['buy_act_amt']+df_money['sell_act_amt']
df_money['act_b_minus_s']=df_money['buy_act_amt']-df_money['sell_act_amt']

#透视表获取单个因子数据
df_NI=df_money.pivot_table(index='date',columns='cn_code',values='b_minus_s').fillna(method='pad')
df_NIR=df_money.pivot_table(index='date',columns='cn_code',values='b_plus_s').fillna(method='pad')
df_NI_ACT=df_money.pivot_table(index='date',columns='cn_code',values='act_b_minus_s').fillna(method='pad')
df_NIR_ACT=df_money.pivot_table(index='date',columns='cn_code',values='act_b_plus_s').fillna(method='pad')

#滑动窗口计算
df_NI=df_NI.rolling(20).apply(np.nansum).iloc[20:].dropna(axis=1)
df_NI_ACT=df_NI_ACT.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR=df_NIR.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR_ACT=df_NIR_ACT.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR=df_NI/df_NIR
df_NIR_ACT=df_NI_ACT/df_NIR_ACT

#%%
#保存因子数据
df_NI.to_csv('./data/factor_raw/NI.csv')
df_NI_ACT.to_csv('./data/factor_raw/NI_ACT.csv')
df_NIR.to_csv('./data/factor_raw/NIR.csv')
df_NIR_ACT.to_csv('./data/factor_raw/NIR_ACT.csv')
#%%
'''
IMB指标及MOD修正
'''


df_money['IMB_lg']=np.log(df_money['buy_large_amt']/df_money['sell_large_amt'])
df_return=pd.read_csv('./data/return.csv',index_col=0)

df_MOD=pd.merge(df_money[['date','cn_code','IMB_lg']],df_return,on=['date','cn_code'],how='outer')

#填充空值
df_IMB=df_MOD.pivot_table(index='date',columns='cn_code',values='IMB_lg').fillna(method='pad').dropna(axis=1)
df_ret=df_MOD.pivot_table(index='date',columns='cn_code',values='daily_ret').fillna(method='pad').dropna(axis=1)

df_MOD=pd.merge(df_IMB.stack().reset_index(),df_ret.stack().reset_index(),on=['date','cn_code'])
df_MOD=df_MOD.rename(columns={'0_x':'IMB_lg','0_y':'daily_ret'})

# %%
#OLS回归得到残差
def regress(df_):
    x=sm.add_constant(df_['daily_ret'])
    regression=sm.OLS(df_['IMB_lg'],x)
    model=regression.fit()
    return pd.Series(df_['cn_code'].values,np.array(model.resid))
df_tmp=df_MOD.sort_values(by=['date','cn_code']).groupby('date').apply(regress).reset_index()
df_tmp=df_tmp.rename(columns={'level_1':'resid',0:'cn_code'})

df_new=pd.merge(df_money,df_tmp,on=['date','cn_code'],how='right')

#MOD修正后的数据
df_new['exp']=np.exp(df_new['resid'])
df_new['b_hat']=df_new['exp']/(1+df_new['exp'])*df_new['b_plus_s']
df_new['s_hat']=1/(1+df_new['exp'])*df_new['b_plus_s']

df_new['act_b_hat']=df_new['exp']/(1+df_new['exp'])*df_new['act_b_plus_s']
df_new['act_s_hat']=1/(1+df_new['exp'])*df_new['act_b_plus_s']

df_new['hat_b_minus_s']=df_new['b_hat']-df_new['s_hat']
df_new['hat_b_plus_s']=df_new['b_hat']+df_new['s_hat']

df_new['hat_act_b_minus_s']=df_new['act_b_hat']-df_new['act_s_hat']
df_new['hat_act_b_plus_s']=df_new['act_b_hat']+df_new['act_s_hat']

# %%
#透视表获取单个因子数据
df_NI=df_new.pivot_table(index='date',columns='cn_code',values='hat_b_minus_s').fillna(method='pad')
df_NIR=df_new.pivot_table(index='date',columns='cn_code',values='hat_b_plus_s').fillna(method='pad')
df_NI_ACT=df_new.pivot_table(index='date',columns='cn_code',values='hat_act_b_minus_s').fillna(method='pad')
df_NIR_ACT=df_new.pivot_table(index='date',columns='cn_code',values='hat_act_b_plus_s').fillna(method='pad')

#滑动窗口计算
df_NI=df_NI.rolling(20).apply(np.nansum).iloc[20:].dropna(axis=1)
df_NI_ACT=df_NI_ACT.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR=df_NIR.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR_ACT=df_NIR_ACT.rolling(20).sum().iloc[20:].dropna(axis=1)
df_NIR=df_NI/df_NIR
df_NIR_ACT=df_NI_ACT/df_NIR_ACT
#%%
#保存MOD调整后的因子数据
df_NI.to_csv('./data/factor_MOD/NI.csv')
df_NI_ACT.to_csv('./data/factor_MOD/NI_ACT.csv')
df_NIR.to_csv('./data/factor_MOD/NIR.csv')
df_NIR_ACT.to_csv('./data/factor_MOD/NIR_ACT.csv')
# %%
'''
CNIR因子
'''
df_CNIR=df_new[['date','cn_code','b_hat','s_hat']]

df_CNIR['b_minus_s']=df_CNIR['b_hat']-df_CNIR['s_hat']
df_CNIR['b_plus_s']=df_CNIR['b_hat']+df_CNIR['s_hat']

df_plus=df_CNIR.pivot_table(index='date',columns='cn_code',values='b_plus_s').fillna(method='pad')
df_minus=df_CNIR.pivot_table(index='date',columns='cn_code',values='b_minus_s').fillna(method='pad')

df_CNIR=df_minus.rolling(20).sum().iloc[20:]/df_plus.rolling(20).sum().iloc[20:]
# %%
df_CNIR.to_csv('./data/factor_CNIR/CNIR.csv')
# %%
