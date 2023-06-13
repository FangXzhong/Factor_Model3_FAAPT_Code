import pandas as pd
import numpy as np


def get_monthly_factors_return(source_df):
    labels = ['chmom', 'mom6m', 'mom12m', 'dolvol', 'turn']
    res = pd.Series([0, ] * 50 + [source_df.realmonth.values[0], ])
    for j in range(5):
        label = labels[j]
        # tmp_cal_df2 = source_df[[label, 'MthRet', 'cap']][source_df[label] < source_df[label].quantile(0.99)][
        #     source_df[label] > source_df[label].quantile(0.01)]
        tmp_cal_df2 = source_df[[label, 'MthRet', 'cap']]
        tmp_cal_df2.dropna(axis=0, how='any', inplace=True)
        for quant in range(10):
            tmp_cal_df_q = tmp_cal_df2[(tmp_cal_df2[label] >= tmp_cal_df2[label].quantile(0.1 * quant)) &
                                       (tmp_cal_df2[label] <= tmp_cal_df2[label].quantile(0.1 * (quant + 1)))]
            # ret = (tmp_cal_df_q['MthRet'] * tmp_cal_df_q['cap']).sum() / tmp_cal_df_q['cap'].sum()
            if tmp_cal_df_q['cap'].empty:  # 没有满足条件的
                ret = 0
            else:
                ret = np.average(tmp_cal_df_q['MthRet'], weights=tmp_cal_df_q['cap'].abs())
            res[10 * j + quant] = ret
    return res
