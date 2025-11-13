#include "sierrachart.h"

SCDLLName("Antonio Sierra Recursive Trading Algo")

namespace
{
constexpr int kPositionStateKey = 1;
constexpr int kLastExitReasonKey = 2;
constexpr int kStoredQuantityKey = 3;

constexpr int kStoredEntryPriceKey = 1;
constexpr int kLastExitPriceKey = 2;
constexpr int kStoredEntryAtrKey = 3;

enum ExitReason
{
    EXIT_NONE = 0,
    EXIT_TARGET = 1,
    EXIT_STOP = 2
};
}

SCSFExport scsf_SierraRecursiveAlgo(SCStudyInterfaceRef sc)
{
    constexpr int kAtrLength = 14;

    SCInputRef EnableTrading = sc.Input[0];
    SCInputRef RiskPerTrade = sc.Input[1];
    SCInputRef ATRMultiplier = sc.Input[2];
    SCInputRef ReentryEnabled = sc.Input[3];

    if (sc.SetDefaults)
    {
        sc.GraphName = "Antonio Sierra 900% Recursive Strategy";
        sc.AutoLoop = 1;
        sc.GraphRegion = 0;
        sc.StudyDescription = "Recursive trend-following strategy with ATR-based risk management.";
        sc.DrawZeros = 0;
        sc.UsesMarketDepthData = 0;
        sc.UpdateAlways = 0;
        sc.FreeDLL = 0;
        sc.DataStartIndex = kAtrLength;

        EnableTrading.Name = "Enable Trading";
        EnableTrading.SetYesNo(true);

        RiskPerTrade.Name = "Maximum Stop Distance (% of price)";
        RiskPerTrade.SetFloat(1.0f);

        ATRMultiplier.Name = "ATR Multiplier for Stop";
        ATRMultiplier.SetFloat(1.6f);

        ReentryEnabled.Name = "Allow Reentry After Stop";
        ReentryEnabled.SetYesNo(true);

        return;
    }

    if (sc.Index < kAtrLength || sc.Index < 1)
        return;

    const bool inPosition = sc.GetPersistentInt(kPositionStateKey) != 0;
    const ExitReason lastExit = static_cast<ExitReason>(sc.GetPersistentInt(kLastExitReasonKey));
    const float lastExitPrice = sc.GetPersistentFloat(kLastExitPriceKey);

    SCFloatArrayRef atrArray = sc.ATR(kAtrLength);
    const float atr = atrArray[sc.Index];
    if (atr <= 0.0f)
        return;

    const float currentClose = sc.Close[sc.Index];
    const float currentOpen = sc.Open[sc.Index];
    const float priorVolume = sc.Volume[sc.Index - 1];
    const float priorLow = sc.Low[sc.Index - 1];
    const float currentVolume = sc.Volume[sc.Index];
    const float currentLow = sc.Low[sc.Index];

    const float stopDistance = atr * ATRMultiplier.GetFloat();
    const float percentRisk = (stopDistance / currentClose) * 100.0f;
    const bool riskAcceptable = percentRisk <= RiskPerTrade.GetFloat();

    const bool signalBuy = currentClose > currentOpen &&
                           currentVolume > priorVolume &&
                           currentLow > priorLow;

    bool allowEntry = EnableTrading.GetYesNo() && !inPosition && signalBuy && riskAcceptable;
    if (!ReentryEnabled.GetYesNo() && lastExit == EXIT_STOP)
    {
        allowEntry = allowEntry && currentClose > lastExitPrice;
    }

    if (allowEntry)
    {
        s_SCNewOrder entryOrder;
        entryOrder.OrderType = SCT_ORDERTYPE_MARKET;
        entryOrder.Quantity = 1;
        entryOrder.TextTag = "AntonioLongEntry";

        const int result = sc.BuyEntry(entryOrder);
        if (result > 0)
        {
            sc.SetPersistentInt(kPositionStateKey, 1);
            sc.SetPersistentFloat(kStoredEntryPriceKey, currentClose);
            sc.SetPersistentFloat(kStoredEntryAtrKey, atr);
            sc.SetPersistentInt(kStoredQuantityKey, entryOrder.Quantity);
            sc.SetPersistentInt(kLastExitReasonKey, EXIT_NONE);
        }
    }

    if (inPosition)
    {
        const float entryPrice = sc.GetPersistentFloat(kStoredEntryPriceKey);
        float entryAtr = sc.GetPersistentFloat(kStoredEntryAtrKey);
        if (entryAtr <= 0.0f)
            entryAtr = atr;

        const float stopLevel = entryPrice - entryAtr * ATRMultiplier.GetFloat();
        const float targetLevel = entryPrice + entryAtr * (ATRMultiplier.GetFloat() + 0.5f);
        const bool stopTriggered = currentClose <= stopLevel;
        const bool targetTriggered = currentClose >= targetLevel;

        if (stopTriggered || targetTriggered)
        {
            s_SCNewOrder exitOrder;
            exitOrder.OrderType = SCT_ORDERTYPE_MARKET;
            int storedQuantity = sc.GetPersistentInt(kStoredQuantityKey);
            if (storedQuantity <= 0)
                storedQuantity = 1;
            exitOrder.Quantity = storedQuantity;
            exitOrder.TextTag = stopTriggered ? "AntonioStopExit" : "AntonioTargetExit";

            const int exitResult = sc.SellExit(exitOrder);
            if (exitResult > 0)
            {
                sc.SetPersistentInt(kPositionStateKey, 0);
                sc.SetPersistentInt(kStoredQuantityKey, 0);
                sc.SetPersistentInt(kLastExitReasonKey, stopTriggered ? EXIT_STOP : EXIT_TARGET);
                sc.SetPersistentFloat(kLastExitPriceKey, currentClose);
            }
        }
    }
}
