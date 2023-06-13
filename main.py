import os
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from statsmodels.tsa.stattools import acf, pacf
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import warnings

import tool_func
import get_monthly_factors_return
import get_annual_factors_return

warnings.filterwarnings('ignore')
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

# %% 在这里有一个需要讨论的地方，宇川在这里先把那些在指定时间段内没上市或者退市的股票全删了，就是说如果这个股票在xx年x月-yy年y月缺少数据，
# 就把这个股票直接咔嚓掉了。我感觉原文的操作应该不是这样，毕竟从1973.1-2016.12一直存活的股票并不多，而且我们似乎并不要求每个时间点的股票池都一样？

# %% 搞几个因子出来
df.dropna(subset=['MthPrc', 'MthVol'],inplace=True)
df['mom6m'] = df.MthPrc.shift(1) / df.MthPrc.shift(6) - 1
df['mom12m'] = df.MthPrc.shift(1) / df.MthPrc.shift(12) - 1
df['mom6-12m'] = df.MthPrc.shift(7) / df.MthPrc.shift(12) - 1
df['chmom'] = df['mom6m'] - df['mom6-12m']
df.drop(['mom6-12m'], axis=1, inplace=True)

df['dolvol'] = np.log(df.MthVol.shift(1)) * df.MthPrc.shift(1) + np.log(df.MthVol.shift(2)) * df.MthPrc.shift(2)
df['turn'] = (df.MthVol.shift(1) + df.MthVol.shift(2) + df.MthVol.shift(3)) * df.ShrOut / 3

# 这里保存中间变量的原因详见temp/readme.md
# df.to_csv(r'./temp/crsp_processed.csv')  # 其实涉及到I/O的都会很慢，我自己跑的时候就把这里注释掉了

# %% 开始搞年度数据 compustat_annual, 先清洗一下
df_comp = pd.read_csv(r'./raw_data/compustat_auunal.csv')

# replaced by fxz
used_tic = df.Ticker.unique()
num_tics = used_tic.shape[0]
df_comp2 = df_comp[df_comp.indfmt == 'INDL']
df2 = df_comp2[df_comp2.tic.isin(used_tic)]

df2.drop(['gvkey', 'indfmt', 'consol', 'popsrc', 'datafmt', 'curcd'], axis=1, inplace=True)

df2['year'] = df2.datadate.apply(lambda x: x.split(sep='-')[0])
df2['month'] = df2.datadate.apply(lambda x: x.split(sep='-')[1])
df2['year'] = df2['year'].astype(np.int32)
df2['month'] = df2['month'].astype(np.int8)
df2['realmonth'] = 12 * (df2.year - 1999) + df2.month

df2['mkvalt2'] = df2.csho * df2.prcc_f

# %% 还是年度数据 compustat_annual，开始往里面加因子
# 比较耗时间，4min20s（i5 11300H + 32GB DRAM）
df2 = df2.groupby('tic', as_index=False).apply(tool_func.get_factors_from_annual_data)

# %% 上面的df2就是宇川写的那个compustat_0606.csv，接下来要搞出来月度的monthly_df
# 这里宇川给了解释，这个地方是因为 那个market anomalies和portfolio是月度更新的
# 所以每个月需要重新计算各个market anomalies的值，按照这个值的顺序构建投资组合
# 而我们能够有的用于计算的数据只有年度的，所以对于每个月份而言，
# 我们要选择距离ta最近的一个年报的数据作为这个公司在这个月的数据，
# 同时在年报数据当中有ta发布所在的月份，在遍历每个月的时候，
# 用于构建这个月的portfolio的数据就是这个时间前后六个月内发布的年报的所有数据

# 这里realmonth是以2000年1月为1，往前的就是负的，往后就是正的
# 这一步速度还能接受，1min左右(i5-11300H + 32GB DRAM)
monthly_df = df2[(df2.realmonth >= -311) & (df2.realmonth <= -300)]

for i in range(-310, 211):
    monthly_df = pd.concat([monthly_df, df2[(df2.realmonth >= i - 6) & (df2.realmonth < i + 6)]], ignore_index=True)

# %% 处理月度收益相关因子
labels = ['chmom', 'mom6m', 'mom12m', 'dolvol', 'turn', 'acc', 'agr', 'bm', 'cashpr', 'cfp', 'currat', 'egr', 'ep',
          'invest', 'lgr', 'grcapx', 'operprof', 'pchcapx', 'pchcurrat', 'pchdepr', 'pchsale-pchinvt', 'pchsaleinv',
          'quick', 'roaq', 'roeq', 'roic', 'rsup', 'salecash', 'saleinv', 'salerec', 'sgr', 'sp']

tic_lst = df.Ticker.unique()
df['ret_ahead'] = df.MthRet.shift(-1)
df['realmonth'] = 12 * (df.year - 1973) + df.month
df['cap'] = df.MthPrc * df.ShrOut

# 用于计算月度收益相关因子的数据
cal_df1 = df.sort_values('realmonth', ascending=True)

# %% 添加无风险利率
rf_df = pd.read_csv(r'raw_data/risk_free(annualized).csv')
rf_df.dropna(subset=['TMYTM'], inplace=True)
rf_df['rf'] = (rf_df.TMYTM / 100 + 1) ** (1 / 12) - 1  # 得到月的无风险利率
rf_df['year'] = rf_df.MCALDT.apply(lambda x: int(x.split(sep='-')[0]))
rf_df['month'] = rf_df.MCALDT.apply(lambda x: int(x.split(sep='-')[1]))
rf_df['realmonth'] = 12 * (rf_df['year'] - 1973) + rf_df['month']

rf_df = rf_df.iloc[:528, :]  # 不知道为啥，下载的数据重复了一遍

# %% 搞定月度return
# 这一步速度还能接受，整个cell 1min10s左右(i5-11300H + 32GB DRAM)
temp = cal_df1.groupby('realmonth').apply(get_monthly_factors_return.get_monthly_factors_return)
temp2 = temp.apply(pd.Series)
temp2.rename(columns=lambda x: x + 1, inplace=True)
temp2.rename(columns={51: 'realmonth'}, inplace=True)
temp2.realmonth.astype(np.int32)

res = pd.DataFrame(np.zeros((44 * 12, 1)))  # 44年，一共44*12行
res['year'] = (res.index // 12 + 1973).astype(np.int32)
res['month'] = (res.index % 12 + 1).astype(np.int8)
res['realmonth'] = (res.year - 1973) * 12 + res.month
res.drop(0, axis=1, inplace=True)

res = res.set_index('realmonth').join(temp2.set_index('realmonth'), on='realmonth')
del temp, temp2

# %% 年度财报
df['tic'] = df.Ticker
cal_df2 = monthly_df.merge(df[['cap', 'MthRet', 'ret_ahead', 'realmonth', 'tic']], how='left')

# cal_df2.dropna(subset=['cap', 'MthRet'], inplace=True)  # 这个有问题，这一步之前两百多万条数据，之后只有25万条，且都是99年之后的
cal_df2.cap.replace(np.nan, 0, inplace=True)
cal_df2.MthRet.replace(np.nan, 0, inplace=True)

cal_df2.sgr.replace([-np.inf, np.inf], 0.026, inplace=True)
cal_df2.saleinv.replace([-np.inf, np.inf], 6.94, inplace=True)
cal_df2.salecash.replace([-np.inf, np.inf], 1.35, inplace=True)
cal_df2.sgr.replace([-np.inf, np.inf], 1.34, inplace=True)
cal_df2.roic.replace([-np.inf, np.inf], 0.0456, inplace=True)
cal_df2.roeq.replace([-np.inf, np.inf], 0.0815, inplace=True)
cal_df2.roaq.replace([-np.inf, np.inf], 0.021, inplace=True)
cal_df2.quick.replace([-np.inf, np.inf], 1.61, inplace=True)
cal_df2.pchsaleinv.replace([-np.inf, np.inf], 0, inplace=True)
cal_df2['pchsale-pchinvt'].replace([-np.inf, np.inf], 0, inplace=True)
cal_df2.pchdepr.replace([-np.inf, np.inf], 0, inplace=True)
cal_df2.pchcurrat.replace([-np.inf, np.inf], 0, inplace=True)
cal_df2.pchcapx.replace([-np.inf, np.inf], 0, inplace=True)
cal_df2.operprof.replace([-np.inf, np.inf], 0.234, inplace=True)
cal_df2.grcapx.replace([-np.inf, np.inf], 0, inplace=True)
cal_df2.lgr.replace([-np.inf, np.inf], 0.0504, inplace=True)
cal_df2.egr.replace([-np.inf, np.inf], 0.0638, inplace=True)
cal_df2.currat.replace([-np.inf, np.inf], 1.9, inplace=True)
cal_df2.cashpr.replace([-np.inf, np.inf], 0.834, inplace=True)
cal_df2.acc.replace([-np.inf, np.inf], -0.0378, inplace=True)
cal_df2.agr.replace([-np.inf, np.inf], 0.0247, inplace=True)

# 这一步贼费时间，得26min(i5-11300H 32GB DRAM)
temp3 = cal_df2.groupby('realmonth').apply(get_annual_factors_return.get_annual_factors_return)

temp4 = temp3.apply(pd.Series)
temp4.rename(columns=lambda x: x + 1, inplace=True)
temp4.rename(columns={271: 'realmonth'}, inplace=True)
temp4.realmonth.astype(np.int32)

res['realmonth'] = range(1, 529)
realmonth_list = temp4['realmonth']
temp4.drop('realmonth',axis=1, inplace=True)
temp4.rename(columns=lambda x: x+50, inplace=True)
temp4['realmonth'] = realmonth_list
res = res.set_index('realmonth').join(temp4.set_index('realmonth'), on='realmonth')
del temp3, temp4

# %% 渐进PCA
N = 320  # 32个因子*每个因子十个
T = 276  #

R = np.array(res.iloc[:, 2:])
rf_matrix = np.tile(rf_df.rf, (320, 1)).T
R = R - rf_matrix
ori_mat = np.dot(R, R.T) / (N * T)

pca = PCA(n_components=9)
pca.fit(ori_mat)
eigenvalues, eigenvectors = np.linalg.eig(ori_mat)
factors = eigenvectors[:, :9]
factor_df = pd.DataFrame(factors, index=[i for i in range(13, 289)], columns=[i for i in range(1, 10)])
factor_df.to_csv(r'output/factors.csv')

# %% 描述性统计
# 均值
# factor_df.mean()

# ACF
# factor_df.apply(acf).loc[1,:]

pca.explained_variance_ratio_.cumsum()

# %% beta
betas = pd.DataFrame(np.zeros((32, 9)), index=labels, columns=[i for i in range(1, 10)])
