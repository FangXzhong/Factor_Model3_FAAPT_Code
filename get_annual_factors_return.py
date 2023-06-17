import pandas as pd
import numpy as np


def get_annual_factors_return(source_df):
    labels = ['acc', 'agr', 'bm', 'cashpr', 'cfp', 'currat', 'egr', 'ep',
              'invest', 'lgr', 'grcapx', 'operprof', 'pchcapx', 'pchcurrat', 'pchdepr', 'pchsale-pchinvt', 'pchsaleinv',
              'quick', 'roaq', 'roeq', 'roic', 'rsup', 'salecash', 'saleinv', 'salerec', 'sgr', 'sp']
    res = pd.Series([0, ] * 270 + [source_df.realmonth.values[0], ])
    print(source_df.realmonth.values[0])
    set0 = set(range(10))  # 配合第23行那一段用
    for j in range(27):
        label = labels[j]
        tmp_source_df = source_df[[label, 'MthRet', 'cap']][source_df[label] < source_df[label].quantile(0.98)][
            source_df[label] > source_df[label].quantile(0.02)]
        tmp_source_df.dropna(inplace=True)
        if tmp_source_df.empty:
            res[j * 10:j * 10 + 10] = [0, ] * 10
        else:
            tmp_source_df['percent_position'] = tmp_source_df.iloc[:, 0].rank(pct=True)
            tmp_source_df['percent_flag'] = tmp_source_df.percent_position // .1


            # 这一步是因为，在实际跑的时候，realmonth=6且j=23时候，出现了没有分位数为6的情况
            flag_list = tmp_source_df.percent_flag.unique()
            if len(flag_list) != 10:
                to_be_added = set0 - set(flag_list)
                for item in to_be_added:
                    tmp_source_df.loc[len(tmp_source_df)] = [0, ] * 4 + [item, ]

            res[j * 10:j * 10 + 10] = tmp_source_df.groupby('percent_flag').apply(
                lambda x: sum(x.iloc[:, 1] * x.iloc[:, 2]) / sum(x.iloc[:, 2]) if sum(tmp_source_df['cap']) == 0 else 0)
        # print(j)
    return res
