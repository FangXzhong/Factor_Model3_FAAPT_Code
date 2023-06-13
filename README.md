本项目是Factor-Model3_FAAPT的代码复现，仅供学习用

**注意**：运行之前请在raw_data文件夹中添加源数据文件，因为源数据文件太大不方便放在GitHub仓库

这些源数据文件包括crsp_monthly.csv、compustat_annual.csv、risk_free(annualized).csv

同时，为了便于后续处理，这里在temp文件夹里放了中间变量crsp_processed.csv，在output文件夹里面记录了res.csv和factors.csv

目前的结果和论文里面的相差比较大，我认为主要原因是，由于构建因子时需要有十个资产组合，而早年部分因子数据缺失（如1973年没有acc的任何数据），
因此我采取了直接令该资产组合的加权平均收益率为0的做法——肯定是不合适的。从res可以看到，早年间有很多很多0，这可能对最终结果有较大影响。

