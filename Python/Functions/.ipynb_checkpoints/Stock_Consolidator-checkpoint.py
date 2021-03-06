def Stock_Consolidator(df):
    df = df.groupby('date').agg(
        close = pd.NamedAgg(column='close', aggfunc= np.median),
        volume = pd.NamedAgg(column='volume', aggfunc= np.median),
        count = pd.NamedAgg(column='close',aggfunc = len)
    )

    def Col_Diff_Lagger(df,col_name,lag = 1):
        df[col_name+'_prev'] = df[col_name].shift(lag)
        df[col_name+'_diff'] = (df[col_name] - df[col_name+'_prev'])/df[col_name+'_prev']
        df = df.drop(columns = [col_name+'_prev'])
        return df

    df = Col_Diff_Lagger(df,'close',1)
    df = Col_Diff_Lagger(df,'volume',1)
    df['sma'] = df['close'].rolling(Total_Market_Plot_SMA).mean()
    return df