Rule_Generator = function(History_Table){
  Explore = History_Table %>%
    select_if(is.numeric) %>%
    select(-contains("MAX_"))
  
  STORE = data.frame(Var = character(),
                     VL = numeric(),
                     PL = numeric(),
                     VH = numeric(),
                     PH = numeric())
  Vars = colnames(Explore)
  for(Var in Vars){
    counter = 0
    for(i in seq(min(Explore[,Var],na.rm = T),
                 max(Explore[,Var],na.rm = T),
                 length.out = 25)){
      counter = counter + 1
      Keep_Low = which(Explore[,Var] < i)
      Keep_High = which(Explore[,Var] > i)
      TMP_Low = History_Table[Keep_Low,]
      P_TL = sum(TMP_Low$Profit) + 
        sum(TMP_Low$Buy.Price[is.na(TMP_Low$Sell.Date)] *
              TMP_Low$Pcent.Gain[is.na(TMP_Low$Sell.Date)] *
              TMP_Low$Number[is.na(TMP_Low$Sell.Date)])
      TMP_High = History_Table[Keep_High,]
      P_TH = sum(TMP_High$Profit) + 
        sum(TMP_High$Buy.Price[is.na(TMP_High$Sell.Date)] *
              TMP_High$Pcent.Gain[is.na(TMP_High$Sell.Date)] *
              TMP_High$Number[is.na(TMP_High$Sell.Date)])
      if(counter == 1){
        PL = P_TL
        VL = i
        PH = P_TH
        VH = i
      }else{
        if(P_TL > PL){
          PL = P_TL
          VL = i
        }
        if(P_TH > PH){
          PH = P_TH
          VH = i
        }
      }
    }
    TMP = data.frame(
      Var = Var,
      VL = round(VL, 4),
      PL = PL,
      VH = round(VH, 4),
      PH = PH
    )
    STORE = bind_rows(STORE,TMP)
  }
  
  
  Method_Profit = sum(History_Table$Profit) + 
    sum(History_Table$Buy.Price[is.na(History_Table$Sell.Date)] *
          History_Table$Pcent.Gain[is.na(History_Table$Sell.Date)] *
          History_Table$Number[is.na(History_Table$Sell.Date)])
  
  STORE = STORE %>%
    mutate(MP = Method_Profit) %>%
    rowwise() %>%
    mutate(MAX = max(c(PL,PH))) %>%
    arrange(desc(MAX)) %>%
    filter(MAX > Method_Profit) %>% 
    ungroup()
  
  return(STORE)
}