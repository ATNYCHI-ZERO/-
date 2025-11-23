#include "sierrachart.h"

#include <algorithm>
#include <cmath>

SCDLLName("Antonio Sierra Recursive Trading Algo")

namespace
{
    enum PersistentStorage
    {
        PERSIST_IN_POSITION = 1,
        PERSIST_ENTRY_PRICE,
        PERSIST_LAST_SIGNAL_INDEX,
        PERSIST_REENTRY_LOCK
    };
}

SCInputRef EnableTrading = sc.Input[0];
SCInputRef RiskPerTrade = sc.Input[1];
SCInputRef ATRMultiplier = sc.Input[2];
SCInputRef ReentryEnabled = sc.Input[3];

SCSFExport scsf_SierraRecursiveAlgo(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Antonio Sierra 900% Recursive Strategy";
        sc.AutoLoop = 1;
        sc.FreeDLL = 0;

        EnableTrading.Name = "Enable Trading";
        EnableTrading.SetYesNo(true);

        RiskPerTrade.Name = "Risk per Trade (%)";
        RiskPerTrade.SetFloat(1.0f);

        ATRMultiplier.Name = "ATR Multiplier for Stop";
        ATRMultiplier.SetFloat(1.6f);

        ReentryEnabled.Name = "Reentry on Trend Confirmation";
        ReentryEnabled.SetYesNo(true);

        return;
    }

    if (sc.Index == 0)
    {
        sc.GetPersistentInt(PERSIST_IN_POSITION) = 0;
        sc.SetPersistentFloat(PERSIST_ENTRY_PRICE, 0.0f);
        sc.GetPersistentInt(PERSIST_LAST_SIGNAL_INDEX) = -1;
        sc.GetPersistentInt(PERSIST_REENTRY_LOCK) = 0;
    }

    if (sc.Index < 1)
        return;

    const float atrMultiplier = std::max(0.1f, ATRMultiplier.GetFloat());
    const float atrValue = sc.ATR(14)[sc.Index];
    if (atrValue <= 0.0f)
        return;

    const float entryPrice = sc.Close[sc.Index];
    const float stopOffset = atrValue * atrMultiplier;
    const float targetOffset = atrValue * (atrMultiplier + 0.5f);

    const bool signalBuy = (sc.Close[sc.Index] > sc.Open[sc.Index]) &&
                           (sc.Volume[sc.Index] > sc.Volume[sc.Index - 1]) &&
                           (sc.Low[sc.Index] > sc.Low[sc.Index - 1]);

    const bool inPosition = sc.GetPersistentInt(PERSIST_IN_POSITION) == 1;
    const bool reentryLocked = sc.GetPersistentInt(PERSIST_REENTRY_LOCK) == 1;

    if (EnableTrading.GetYesNo() && signalBuy && !inPosition)
    {
        if (!reentryLocked || ReentryEnabled.GetYesNo())
        {
            const float perUnitRisk = std::max(stopOffset, 0.01f);
            const float percentRisk = std::max(RiskPerTrade.GetFloat(), 0.0f) / 100.0f;
            float theoreticalRiskCapital = percentRisk * entryPrice;
            if (theoreticalRiskCapital <= 0.0f)
                theoreticalRiskCapital = perUnitRisk;

            int quantity = static_cast<int>(std::floor(theoreticalRiskCapital / perUnitRisk));
            quantity = std::max(quantity, 1);

            s_SCNewOrder order;
            order.OrderQuantity = quantity;
            order.OrderType = SCT_ORDERTYPE_MARKET;
            order.TextTag = "AntonioLongEntry";

            if (sc.BuyEntry(order) > 0)
            {
                sc.GetPersistentInt(PERSIST_IN_POSITION) = 1;
                sc.SetPersistentFloat(PERSIST_ENTRY_PRICE, entryPrice);
                sc.GetPersistentInt(PERSIST_LAST_SIGNAL_INDEX) = sc.Index;
                sc.GetPersistentInt(PERSIST_REENTRY_LOCK) = 1;
            }
        }
    }

    if (inPosition)
    {
        const float entry = sc.GetPersistentFloat(PERSIST_ENTRY_PRICE);
        const float currentClose = sc.Close[sc.Index];

        if (currentClose <= entry - stopOffset)
        {
            s_SCNewOrder exitOrder;
            exitOrder.OrderType = SCT_ORDERTYPE_MARKET;
            exitOrder.TextTag = "AntonioStopExit";

            if (sc.SellExit(exitOrder) > 0)
            {
                sc.GetPersistentInt(PERSIST_IN_POSITION) = 0;
                sc.GetPersistentInt(PERSIST_REENTRY_LOCK) = ReentryEnabled.GetYesNo() ? 0 : 1;
            }
        }
        else if (currentClose >= entry + targetOffset)
        {
            s_SCNewOrder exitOrder;
            exitOrder.OrderType = SCT_ORDERTYPE_MARKET;
            exitOrder.TextTag = "AntonioTargetExit";

            if (sc.SellExit(exitOrder) > 0)
            {
                sc.GetPersistentInt(PERSIST_IN_POSITION) = 0;
                sc.GetPersistentInt(PERSIST_REENTRY_LOCK) = ReentryEnabled.GetYesNo() ? 0 : 1;
            }
        }
    }
}
