//+------------------------------------------------------------------+
//|                                                   WorkSymbol.mqh |
//|                                     Copyright 2021, Lethan Corp. |
//|                           https://www.mql5.com/pt/users/14134597 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, Lethan Corp."
#property link      "https://www.mql5.com/pt/users/14134597"
#property version   "1.00"

#define None ""

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
class CWorkSymbol
  {
private:
   string             m_symbol;        // Symbol
   double             m_tick_size;     // symbol tick size
   int                m_digits;        // symbol digits
public:
                     CWorkSymbol::CWorkSymbol(const string);
   double            CWorkSymbol::NormalizePrice(const double) const;
   bool              CWorkSymbol::Refresh(void);
   string            Name(void);
   double            VolumeMin(string);
   double            Ask(void);
   double            Bid(void);
   double            StepToPrice(double);
  };
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
CWorkSymbol::CWorkSymbol(const string s) : m_symbol(s)
  {
   if(s==None)
      m_symbol=Symbol();
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CWorkSymbol::NormalizePrice(const double price) const
  {
   if(m_tick_size!=0)
      return(NormalizeDouble(MathRound(price/m_tick_size)*m_tick_size,m_digits));
//---
   return(round(NormalizeDouble(price,m_digits)));
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CWorkSymbol::Refresh(void)
  {
   long tmp=0;
//---
   if(!SymbolInfoDouble(m_symbol,SYMBOL_TRADE_TICK_SIZE,m_tick_size))
      return(false);
   if(!SymbolInfoInteger(m_symbol,SYMBOL_DIGITS,tmp))
      return(false);
   m_digits=(int)tmp;
//--- succeed
   return(true);
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
string CWorkSymbol::Name(void)
  {
   return m_symbol;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CWorkSymbol::VolumeMin(string symbol=NULL)
  {
   if(symbol!=None)
      return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   else
      return SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CWorkSymbol::Ask(void)
  {
   return(SymbolInfoDouble(m_symbol, SYMBOL_ASK));
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CWorkSymbol::Bid(void)
  {
   return(SymbolInfoDouble(m_symbol,SYMBOL_BID));
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CWorkSymbol::StepToPrice(double price_step)
  {
   return(SymbolInfoDouble(m_symbol, SYMBOL_POINT)*(double)price_step);
  }
//+------------------------------------------------------------------+
