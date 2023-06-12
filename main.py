import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

import warnings

warnings.filterwarnings('ignore')

import tool_func

# %% 切换工作目录，这是为了防止数据文件和代码文件不在同一个目录下
os.chdir(r"E:\Onedrive\OneDrive-personal\OneDrive\大学\大四下\投资中的数据分析方法\小组pre\show")

# %% 开始处理月度数据crsp_monthly
df = pd.read_csv(r".\raw_data\crsp_monthly.csv")

df['year'] = df.MthCalDt.apply(lambda x: x.split(sep='-')[0])
df['month'] = df.MthCalDt.apply(lambda x: x.split(sep='-')[1])
df['year'] = df['year'].astype(np.int32)
df['month'] = df['month'].astype(np.int8)

df['ind'] = df.SICCD // 100  # 这一步主要是为了方便后面行业相关因子的处理，因为SICCD前两位是行业代码

df.dropna(subset=['Ticker'], inplace=True)
df.drop(labels=['MthCalDt'], axis=1, inplace=True)

tickers = df.Ticker.unique()

#%% 在这里有一个需要讨论的地方，宇川在这里先把那些在指定时间段内没上市或者退市的股票全删了，就是说如果这个股票在xx年x月-yy年y月的数据存在nan值，
# 就把这个股票直接咔嚓掉了。我感觉原文的操作应该不是这样，毕竟从1976.1-2016.12一直存活的股票并不多，而且我们似乎并不要求每个时间点的股票池都一样？

# %% 搞几个因子出来
df['mom6m'] = df.MthPrc.shift(1) / df.MthPrc.shift(6) - 1
df['mom12m'] = df.MthPrc.shift(1) / df.MthPrc.shift(12) - 1
df['mom6-12m'] = df.MthPrc.shift(7) / df.MthPrc.shift(12) - 1
df['chmom'] = df['mom6m'] - df['mom6-12m']
df.drop(['mom6-12m'], axis=1, inplace=True)

df['dolvol'] = np.log(df.MthVol.shift(1))*df.MthPrc.shift(1) + np.log(df.MthVol.shift(2))*df.MthPrc.shift(2)
df['turn'] = (df.MthVol.shift(1) + df.MthVol.shift(2) + df.MthVol.shift(3)) * df.ShrOut / 3

# 这里保存中间变量的原因详见temp/readme.md
# df.to_csv(r'./temp/crsp_processed.csv')  # 其实涉及到I/O的都会很慢，我自己跑的时候就把这里注释掉了

#%% 开始搞年度数据 compustat_annual, 先清洗一下
df_comp = pd.read_csv(r'./raw_data/compustat_auunal.csv')

# replaced by fxz
used_tic = df.Ticker.unique()
num_tics = used_tic.shape[0]
df_comp2 = df_comp[df_comp.indfmt=='INDL']
df2 = df_comp2[df_comp2.tic.isin(used_tic)]

df2.drop(['gvkey', 'indfmt', 'consol', 'popsrc', 'datafmt', 'curcd'], axis=1, inplace=True)

df2['year'] = df2.datadate.apply(lambda x: x.split(sep='-')[0])
df2['month'] = df2.datadate.apply(lambda x: x.split(sep='-')[1])
df2['year'] = df2['year'].astype(np.int32)
df2['month'] = df2['month'].astype(np.int8)
df2['realmonth'] = 12*(df2.year-1999) + df2.month

df2['mkvalt2'] = df2.csho * df2.prcc_f

#%% 还是年度数据 compustat_annual，开始往里面加因子
# 比较耗时间，4min20s（i5 11300H + 32GB DRAM）
df2 = df2.groupby('tic', as_index=False).apply(tool_func.get_factors_from_annual_data)

#%% 上面的df2就是宇川写的那个compustat_0606.csv
