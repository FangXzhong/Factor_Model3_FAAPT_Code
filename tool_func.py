"""
这是一些工具函数
"""


def get_factors_from_annual_data(source_df):
    """
    从年度数据中得到因子
    :param source_df: 一个pandas.DataFrame
    :return: 加上了一堆因子的pandas.DataFrame
    """
    # acc
    source_df['acc'] = (source_df.ib - source_df.oancf) / source_df['at']
    source_df['acc'].fillna(
        source_df.act.diff(1).fillna(0) - source_df.che.diff(1).fillna(0) - source_df.lct.diff(1).fillna(
            0) - source_df.dlc.diff(1).fillna(0) + source_df.txt.diff(1).fillna(0))
    # agr
    source_df['agr'] = source_df['at'].pct_change()
    # bm
    source_df['bm'] = source_df['ceq'] / source_df['mkvalt2']
    source_df['bm'].fillna(source_df['ceq'] / source_df['mkvalt'], inplace=True)
    # cashpr
    source_df.dltt.fillna(source_df.dltt.interpolate(), inplace=True)
    source_df['cashpr'] = (source_df.mkvalt2 + source_df.dltt - source_df['at']) / source_df.che
    # cfp
    source_df['cfp'] = source_df.oancf / source_df.mkvalt2
    source_df['cfp'].fillna(source_df.oancf / source_df.mkvalt, inplace=True)
    # currat
    source_df['currat'] = source_df.act / source_df.lct
    source_df.currat.fillna(source_df.currat.mean(), inplace=True)
    # egr
    source_df['egr'] = source_df.ceq.pct_change()
    source_df['egr'].fillna(0, inplace=True)
    # ep
    source_df['ep'] = source_df.ib / source_df.mkvalt2
    source_df['ep'].fillna(source_df.ib / source_df.mkvalt, inplace=True)
    # grcapx
    source_df['grcapx'] = source_df.capx.pct_change(periods=2)
    source_df['grcapx'].fillna(0, inplace=True)
    # invest
    source_df['invest'] = source_df['at'].shift(1) * (
                source_df.ppent.shift(1).fillna(0) + source_df.invt.shift(1).fillna(0))
    # lgr
    source_df['lgr'] = source_df['lt'].pct_change()
    source_df['lgr'].fillna(0)
    # operprof
    source_df.xsga.fillna(0, inplace=True)
    source_df.xint.fillna(0, inplace=True)
    source_df['operprof'] = (source_df.revt - source_df.cogs - source_df.xsga - source_df.xint) / source_df.seq.shift(1)
    # pchcapx
    source_df['pchcapx'] = source_df.capx.pct_change()
    source_df['pchcapx'].fillna(0, inplace=True)
    # pchcurrat
    source_df['pchcurrat'] = source_df.currat.pct_change()
    source_df.pchcurrat.fillna(0, inplace=True)
    # pchdepr
    source_df.dp.fillna(source_df.dp.interpolate(), inplace=True)
    source_df.ppent.fillna(source_df.ppent.interpolate(), inplace=True)
    source_df['pchdepr'] = (source_df.dp / source_df.ppent).pct_change()
    source_df.pchdepr.fillna(0, inplace=True)
    # pchsale - pchinvt
    source_df['pchsale'] = source_df.sale.pct_change()
    source_df['pchinvt'] = source_df.invt.pct_change()
    source_df['pchsale-pchinvt'] = source_df.pchsale - source_df.pchinvt
    source_df['pchsale-pchinvt'].fillna(0, inplace=True)
    # saleinv & pchsaleinv
    source_df['saleinv'] = source_df.sale / source_df.invt
    source_df['pchsaleinv'] = source_df.saleinv.pct_change()
    source_df['pchsaleinv'].fillna(0, inplace=True)
    # quick
    source_df['quick'] = (source_df['at'] - source_df.invt.fillna(0)) / source_df['lt']
    # roaq
    source_df['roaq'] = source_df.ib / source_df['at'].shift(1)
    source_df['roaq'].fillna(0, inplace=True)
    # roeq
    source_df['roeq'] = source_df.ib / source_df.seq.shift(1)
    source_df['roeq'].fillna(0, inplace=True)
    # roic
    source_df['roic'] = (source_df.ebit - source_df.nopi.fillna(0)) / (source_df.ceq + source_df['lt'] - source_df.che)
    source_df['roic'].fillna(0, inplace=True)
    # rsup
    source_df['rsup'] = source_df.sale.diff(1) / source_df.mkvalt2
    source_df['rsup'].fillna(source_df.sale.diff(1) / source_df.mkvalt, inplace=True)
    # salecash
    source_df['salecash'] = source_df.sale / source_df.ceq
    # salerec
    source_df['salerec'] = source_df.sale / source_df.rect
    # sgr
    source_df['sgr'] = source_df.sale.pct_change()
    source_df['sgr'].fillna(0, inplace=True)
    # sp
    source_df['sp'] = source_df.sale / source_df.mkvalt2
    source_df['sp'].fillna(source_df.sale / source_df.mkvalt, inplace=True)
    return source_df

