import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

df = pd.read_csv("E0.csv")


df_numeric = df.select_dtypes(include=["float64", "int64"]).drop(columns=["FTR","B365H","B365D","B365A","BWH","BWD","BWA","BFH","BFD","BFA","PSH","PSD","PSA","WHH","WHD","WHA","1XBH","1XBD","1XBA","MaxH","MaxD","MaxA","AvgH","AvgD","AvgA","BFEH","BFED","BFEA","B365>2.5","B365<2.5","P>2.5","P<2.5","Max>2.5","Max<2.5","Avg>2.5","Avg<2.5","BFE>2.5","BFE<2.5","AHh","B365AHH","B365AHA","PAHH","PAHA","MaxAHH","MaxAHA","AvgAHH","AvgAHA","BFEAHH","BFEAHA","B365CH","B365CD","B365CA","BWCH","BWCD","BWCA","BFCH","BFCD","BFCA","PSCH","PSCD","PSCA","WHCH","WHCD","WHCA","1XBCH","1XBCD","1XBCA","MaxCH","MaxCD","MaxCA","AvgCH","AvgCD","AvgCA","BFECH","BFECD","BFECA","B365C>2.5","B365C<2.5","PC>2.5","PC<2.5","MaxC>2.5","MaxC<2.5","AvgC>2.5","AvgC<2.5","BFEC>2.5","BFEC<2.5","AHCh","B365CAHH","B365CAHA","PCAHH","PCAHA","MaxCAHH","MaxCAHA","AvgCAHH","AvgCAHA","BFECAHH","BFECAHA"], errors="ignore")

# Matriz de correlação
plt.figure(figsize=(12, 10))
sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Matriz de Correlação")
plt.show()


X = add_constant(df_numeric)
vif_data = pd.DataFrame()
vif_data["feature"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

print(vif_data)
