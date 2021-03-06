def Group_Consolidator(Combined_Data,
                       groups,
                       column,
                       min_last_ret = -0.10,
                       max_rsi = 100,
                       min_macd = -10,
                       min_risk_ratio = 0,
                       min_alpha = -2,
                       max_alpha_p = 1,
                       max_beta_p = 1,
                       min_beta = -2,
                       max_beta = 2
                      ):
    Group_Data = defaultdict(pd.DataFrame)
    for i in groups:
        TMP = Stock_Consolidator(Combined_Data[Combined_Data[column] == i])
        mask = [i in TMP.index.values for i in Total_Market.index.values]
        TM_TMP = Total_Market.iloc[mask,:]

        Stock_Count = int(TMP['count'].tail(1))
        TMP['Market_Return'] = TM_TMP['close_diff']

        ## Rolling OLS Regression
        rols = RollingOLS(TMP['close_diff'],sm.add_constant(TMP['Market_Return']),window = OLS_Window).fit()

        ## Pulling Relevent Information
        alpha_pvalue = list(pd.Series(np.around(rols.pvalues[:,0],2)))
        beta_pvalue = list(pd.Series(np.around(rols.pvalues[:,1],2)))
        alpha = list(rols.params['const'])
        beta = list(rols.params['Market_Return'])
        
        last_price = TMP['close']
        ret = TMP['close_return']
        rsi = TMP['RSI']
        macd = TMP['MACD']
        
        ## Calculating Various Risk Metrics
        sd_ret = np.round(np.std(TMP['close_diff'][TMP['close_diff'] > 0].tail(14)),6)
        sd_loss = np.round(np.std(TMP['close_diff'][TMP['close_diff'] <= 0].tail(14)),6)
        risk_ratio = sd_ret/sd_loss
        mu_ret = np.mean(TMP['close_diff'].tail(14))
        
        ## Daily Movement For Loss Orders
        TMP['close_yesterday'] = TMP['close'].shift(1)
        sd_day_up = np.std( \
                           (TMP['high'].tail(14) - TMP['close_yesterday'].tail(14))/TMP['close_yesterday'].tail(14) \
                          )
        mu_day_up = np.mean((TMP['high'].tail(14) - TMP['close_yesterday'].tail(14))/TMP['close_yesterday'].tail(14))
        sd_day_down = np.std( \
                           (TMP['low'].tail(14) - TMP['close_yesterday'].tail(14))/TMP['close_yesterday'].tail(14) \
                          )
        mu_day_down = np.mean((TMP['low'].tail(14) - TMP['close_yesterday'].tail(14))/TMP['close_yesterday'].tail(14))

        Group_Data[i] = pd.DataFrame(data = {'last_period_return':ret,
                                             'last_price':last_price,
                                             'mu_day_up':mu_day_up,
                                             'sd_day_up':sd_day_up,
                                             'mu_day_down':mu_day_down,
                                             'sd_day_down':sd_day_down,
                                             'risk_ratio': risk_ratio,
                                             'mu_ret':mu_ret,
                                             'rsi':rsi,
                                             'macd':macd,
                                             'alpha':alpha,
                                             'alpha_p':alpha_pvalue,
                                             'beta':beta,
                                             'beta_p':beta_pvalue}).tail(5)
    for s in Group_Data:
        Group_Data[s].insert(0, column, [s]*len(Group_Data[s]))

    Combined_Group = pd.concat(Group_Data.values())  
    Group_Summary = Combined_Group. \
        groupby(column). \
        mean(). \
        sort_values(by = ['alpha','beta'],ascending = [0,1])
    
    Group_Summary = Group_Summary[Group_Summary.risk_ratio > min_risk_ratio]
    Group_Summary = Group_Summary[Group_Summary.last_period_return > min_last_ret]
    Group_Summary = Group_Summary[Group_Summary.rsi < max_rsi]
    Group_Summary = Group_Summary[Group_Summary.macd > min_macd]
    
    Group_Summary = Group_Summary[Group_Summary.alpha > min_alpha]
    Group_Summary = Group_Summary[Group_Summary.alpha_p < max_alpha_p]
    
    Group_Summary = Group_Summary[Group_Summary.beta > min_beta]
    Group_Summary = Group_Summary[Group_Summary.beta < max_beta]
    Group_Summary = Group_Summary[Group_Summary.beta_p < max_beta_p]
    
    return Group_Summary