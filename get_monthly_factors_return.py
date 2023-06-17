import pandas as pd
import numpy as np


def get_monthly_factors_return(source_df):
    labels = ['chmom', 'mom6m', 'mom12m', 'dolvol', 'turn']
    res = pd.Series([0, ] * 50 + [source_df.realmonth.values[0], ])
    for j in range(5):
        label = labels[j]
        tmp_cal_df2 = source_df[[label, 'MthRet', 'cap']][(source_df[label] < source_df[label].quantile(0.99))&
                                                          (source_df[label] > source_df[label].quantile(0.01))]
        tmp_cal_df2.dropna(axis=0, how='any', inplace=True)
        if tmp_cal_df2.empty:
            res[j * 10:j * 10 + 10] = [0, ] * 10
        else:
            tmp_cal_df2['percent_position'] = tmp_cal_df2.iloc[:, 0].rank(pct=True)
            tmp_cal_df2['percent_flag'] = tmp_cal_df2.percent_position // .1
            res[j * 10:j * 10 + 10] = tmp_cal_df2.groupby('percent_flag').apply(
                lambda x: sum(x.iloc[:, 1] * x.iloc[:, 2]) / sum(x.iloc[:, 2]) if not tmp_cal_df2['cap'].empty else 0)
    return res
