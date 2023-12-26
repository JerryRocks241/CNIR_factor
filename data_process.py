#%%
import pandas as pd
import os
from tqdm import tqdm

# %%
ls_money=os.listdir('./data/money_flow')
ls_return=os.listdir('./data/return')
# %%
df_money=pd.DataFrame()
for money in tqdm(ls_money):
    df_tmp=pd.read_pickle('./data/money_flow/'+money,compression='gzip')
    df_money=pd.concat([df_money,df_tmp])
#%%
df_money.to_csv('./data/money.csv')
#%%
df_return=pd.DataFrame()
for ret in tqdm(ls_return):
    df_tmp=pd.read_csv('./data/return/'+ret,sep='\t')
    df_return=pd.concat([df_return,df_tmp])
# %%
df_return.to_csv('./data/return.csv')
