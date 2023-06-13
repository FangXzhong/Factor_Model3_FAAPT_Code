import pandas as pd
import numpy as np


def get_annual_factors_return(source_df):
    labels = ['acc', 'agr', 'bm', 'cashpr', 'cfp', 'currat', 'egr', 'ep',
              'invest', 'lgr', 'grcapx', 'operprof', 'pchcapx', 'pchcurrat', 'pchdepr', 'pchsale-pchinvt', 'pchsaleinv',
              'quick', 'roaq', 'roeq', 'roic', 'rsup', 'salecash', 'saleinv', 'salerec', 'sgr', 'sp']
    res = pd.Series([0, ] * 270 + [source_df.realmonth.values[0], ])
    for j in range(27):
        label = labels[j]
        tmp_source_df = source_df[[label, 'MthRet', 'cap']][source_df[label] < source_df[label].quantile(0.98)][
            source_df[label] > source_df[label].quantile(0.02)]
        tmp_source_df.dropna(inplace=True)
        for quant in range(10):
            source_df_q = tmp_source_df[tmp_source_df[label] >= tmp_source_df[label].quantile(0.1 * quant)][
                tmp_source_df[label] <= tmp_source_df[label].quantile(0.1 * (quant + 1))]
            # ret = (source_df_q['MthRet'] * source_df_q['cap']).sum() / source_df_q['cap'].sum()
            if sum(source_df_q['cap'].abs()) == 0:
                ret = 0
            else:
                ret = np.average(source_df_q['MthRet'], weights=source_df_q['cap'].abs())
            res[10 * j + quant] = ret
    return res
