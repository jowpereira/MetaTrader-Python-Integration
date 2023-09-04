//+------------------------------------------------------------------+
//|                                                      Moniotr.mqh |
//|                                     Copyright 2021, Lethan Corp. |
//|                           https://www.mql5.com/pt/users/14134597 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, Lethan Corp."
#property link      "https://www.mql5.com/pt/users/14134597"
#property version   "1.00"

#include "FileCSV.mqh"
#include "WorkSymbol.mqh"
#include <Trade\Trade.mqh>

#define isna(data) (data==NULL)?true:(data=="")?true:false

sinput group   "Expert Configuration"
sinput int                InpStep                = 100;
sinput uint               InpMagicEA             = 999;
sinput ulong              InpDeviation           = 35;
input double              InpLot                 = 0.01;    //Lot size
input int                 InpTakeProfit          = 0;       //Take Profit (0-off)
input int                 InpStopLoss            = 0;       //Stop Loss   (0-off)

#define HEADER_FILE_INIT {"typerun"}
#define LINES_FILE_INT(TYPE) {{string(TYPE)}}
#define IDX(n) n

#define FuncSymbol(NAME, TYPE)                                       \
class NAME##Function {                                               \
public:                                                              \
    TYPE operator[](int idx) {                                       \
        return i##NAME(CMonitor::m_symbol, CMonitor::m_period, idx); \
    }                                                                \
};                                                                   \
NAME##Function NAME;
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
enum EtypeRun
  {
   TEST,
   LIVE
  };
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
class CMonitor
  {
private:
                     FuncSymbol(Open, double);
                     FuncSymbol(High, double);
                     FuncSymbol(Low, double);
                     FuncSymbol(Close, double);
   CFileCSV*         File;
   CTrade*           Trade;
   CWorkSymbol*      WS;
   static datetime   m_last_time;
   bool              NewBar(void);
   EtypeRun          m_type_run;
   static string     m_symbol;
   static ENUM_TIMEFRAMES m_period;
   MqlParam          m_params[];
   string            m_comment;

public:
                     CMonitor(string, ENUM_TIMEFRAMES);
                    ~CMonitor();
   bool              OnInit(EtypeRun);
   void              OnTick(void);
   void              OnDeinit(const int reason);
   void              ConfigParam(int, int, ENUM_MA_METHOD, ENUM_APPLIED_PRICE);
  };

static string CMonitor::m_symbol;
static ENUM_TIMEFRAMES CMonitor::m_period;
static datetime CMonitor::m_last_time;

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
CMonitor::CMonitor(string symbol, ENUM_TIMEFRAMES timeframe) : m_comment("")
  {
   m_symbol = symbol;
   m_period = timeframe;

   if(File == NULL)
      File = new CFileCSV();

   if(Trade == NULL)
      Trade = new CTrade();

   if(WS == NULL)
      WS = new CWorkSymbol(symbol);
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
CMonitor::~CMonitor()
  {
   if(File != NULL)
     {
      File.SetCommon(true);
      File.FolderDelete("TransferML");

      delete File;
      File = NULL;
     }

   if(Trade != NULL)
     {
      delete Trade;
      Trade = NULL;
     }

   if(WS != NULL)
     {
      delete WS;
      WS = NULL;
     }
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void CMonitor::OnDeinit(const int reason)
  {
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CMonitor::OnInit(EtypeRun type_run)
  {
   bool res = true;

   File.SetCommon(true);
   File.Open("TransferML/init.csv", FILE_WRITE | FILE_SHARE_READ | FILE_ANSI);
   string header[1] = HEADER_FILE_INIT;
   string lines[1][1] = LINES_FILE_INT(type_run);

   if((File.WriteHeader(header) < 1 & File.WriteLine(lines) < 1) != 0)
      res = false;

   File.Close();

   while(!File.IsExist("TransferML/init_checked.csv", FILE_COMMON))
     {
      //waiting for startup
      Comment("waiting for startup");
     }

   m_type_run = type_run;
   Trade.SetExpertMagicNumber(InpMagicEA);
   Trade.SetDeviationInPoints(InpDeviation);
   Trade.SetAsyncMode(true);

   if(!WS.Refresh())
      res = false;

   Comment("");

   return res;
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void CMonitor::OnTick(void)
  {
   string temp = "";
   m_comment = "";

   StringAdd(m_comment, "last_tick: " + string(TimeTradeServer()) + "\n");
   temp = "nome_ativo: " + WS.Name();
   StringAdd(m_comment, temp + "\n");
   temp = "last_price: " + string(Close[0]);
   StringAdd(m_comment, temp + "\n");

   if(CMonitor::NewBar())
     {

      if(m_type_run == TEST)
        {
         string header[3] = { "command", "open", "close" };
         string payload[][3];

         ArrayResize(payload, IDX(InpStep));

         payload[0][0] = "start";

         for(int i = IDX(InpStep); i >= 1; i--)
           {
            payload[fabs(i - (IDX(InpStep) - 1))][1] = string(Open[i]);
            payload[fabs(i - (IDX(InpStep) - 1))][2] = string(Close[i]);
           }

         File.SetCommon(true);
         File.Open("TransferML/mode_test.csv", FILE_WRITE | FILE_ANSI);
         File.WriteHeader(header);

         File.WriteLine(payload);
         File.Close();

         while(!File.IsExist("TransferML/predict_test.csv", FILE_COMMON))
           {
            //waiting for prediction
            StringAdd(m_comment, "waiting for prediction...");
           }

         File.Open("TransferML/predict_test.csv", FILE_COMMON | FILE_READ | FILE_CSV, ';');
         double received = StringToDouble(File.Read());
         File.Delete();

         Print("Value of Prediction: ", received);
         
        }
     }

   Comment(m_comment);
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CMonitor::NewBar(void)
  {
   datetime time[];
   if(CopyTime(CMonitor::m_symbol, CMonitor::m_period, 0, 1, time) < 1)
      return false;
   if(time[0] == CMonitor::m_last_time)
      return false;
   return bool(m_last_time = time[0]);
  }
//+------------------------------------------------------------------+
