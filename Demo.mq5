//+------------------------------------------------------------------+
//|                                                 ClientSocket.mqh |
//|                                     Copyright 2023, Lethan Corp. |
//|                           https://www.mql5.com/pt/users/14134597 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, Lethan Corp."
#property link      "https://www.mql5.com/pt/users/14134597"
#property version   "1.00"

#include "Libraries\\Monitor.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+

CMonitor *monitor;
int OnInit()
  {
   if(monitor == NULL)
      monitor = new CMonitor(Symbol(), Period());

   static EtypeRun typerun = (MQLInfoInteger(MQL_OPTIMIZATION) || MQLInfoInteger(MQL_TESTER) || MQLInfoInteger(MQL_VISUAL_MODE)) ? TEST : LIVE;

   if(!monitor.OnInit(typerun))
      return (INIT_FAILED);

//---

   return (INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---

   monitor.OnDeinit(reason);

   if(monitor != NULL)
     {
      delete monitor;
      monitor = NULL;
     }
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
     monitor.OnTick();
  }
//+------------------------------------------------------------------+
