import yfinance as yf
import numpy as np
import pandas as pd
import time
import os
from datetime import datetime

# -------------------------------
# Technical Indicator Calculations
# -------------------------------

def calc_smma(series, length):
    smma = series.copy()
    smma.iloc[:length] = series.iloc[:length].mean()
    for i in range(length, len(series)):
        smma.iloc[i] = (smma.iloc[i - 1] * (length - 1) + series.iloc[i]) / length
    return smma

def calc_zlema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    return ema1 + (ema1 - ema2)

def calculate_impulse_macd(df, lengthMA=34, lengthSignal=9):
    src = (df['High'] + df['Low'] + df['Close']) / 3
    hi = calc_smma(df['High'], lengthMA)
    lo = calc_smma(df['Low'], lengthMA)
    mi = calc_zlema(src, lengthMA)

    md = np.where(mi > hi, mi - hi,
                  np.where(mi < lo, mi - lo, 0))

    md_series = pd.Series(md.ravel(), index=df.index)
    sb = md_series.rolling(window=lengthSignal).mean()
    sh = md_series - sb
    return md_series, sb, sh

def linreg(series, length):
    idx = np.arange(length)
    def calc(i):
        y = series[i - length + 1: i + 1]
        if len(y) < length:
            return np.nan
        slope, intercept = np.polyfit(idx, y, 1)
        return intercept + slope * (length - 1)
    return [np.nan if i < length - 1 else calc(i) for i in range(len(series))]

# -------------------------------
# Market Monitoring Function
# -------------------------------

def monitor_market():
    df = yf.download('^NSEI', period='7d', interval='5m', progress=False)
    df.dropna(inplace=True)

    md, sb, sh = calculate_impulse_macd(df)
    latest_sh = sh.iloc[-1]
    histo_state = "Positive" if latest_sh > 0 else "Negative" if latest_sh < 0 else "Zero"
    macd_sideways = -10 <= latest_sh <= 10

    df['EMA7'] = df['Close'].ewm(span=7, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    linreg_len = 11
    df['lin_open'] = linreg(df['Open'], linreg_len)
    df['lin_close'] = linreg(df['Close'], linreg_len)

    latest = df.iloc[[-1]]
    close = float(latest['Close'].iloc[0])
    ema7 = float(latest['EMA7'].iloc[0])
    ema50 = float(latest['EMA50'].iloc[0])
    ema200 = float(latest['EMA200'].iloc[0])
    lin_open = float(latest['lin_open'].iloc[0])
    lin_close = float(latest['lin_close'].iloc[0])

    candle_vs_white_line = (
        "Candle is above the 7 EMA (Bullish / Uptrend)" if lin_close > ema7 else
        "Candle is below the 7 EMA (Bearish / Downtrend)" if lin_close < ema7 else
        "Candle is at the 7 EMA"
    )

    ema_touching_candle = (
        "Yes, 7 EMA is touching the candle (between linear open and close)"
        if min(lin_open, lin_close) <= ema7 <= max(lin_open, lin_close)
        else "No, 7 EMA is not touching the candle"
    )

    signal = "Golden Cross (Bullish)" if ema50 > ema200 else \
             "Death Cross (Bearish)" if ema50 < ema200 else "Neutral"

    candle_color = "Green (Bullish)" if lin_close > lin_open else \
                   "Red (Bearish)" if lin_close < lin_open else "Doji (Neutral)"

    candle_strength_pct = abs(lin_close - lin_open) / close * 100
    strength_threshold_strong = 0.5
    strength_threshold_weak = 0.1

    if candle_strength_pct >= strength_threshold_strong:
        candle_strength = f"Very Strong Candle ({candle_strength_pct:.2f}%)"
    elif candle_strength_pct <= strength_threshold_weak:
        candle_strength = f"Weak Candle ({candle_strength_pct:.2f}%)"
    else:
        candle_strength = f"Moderate Strength Candle ({candle_strength_pct:.2f}%)"

    ema50_slope = np.polyfit(range(10), df['EMA50'].iloc[-10:], 1)[0]
    ema200_slope = np.polyfit(range(10), df['EMA200'].iloc[-10:], 1)[0]
    ema_distance_pct = abs(ema50 - ema200) / ema200 * 100

    if abs(ema50_slope) < 0.02 and abs(ema200_slope) < 0.02 and ema_distance_pct < 1:
        ema_status = "Sideways and close to each other"
    elif ema_distance_pct < 1:
        ema_status = "Close to each other but with movement"
    else:
        ema_status = "EMAs showing divergence or trend"

    ema7_slope = np.polyfit(range(10), df['EMA7'].iloc[-10:], 1)[0]
    ema7_sideways = abs(ema7_slope) < 0.02

    # Beautified Output
    print("=" * 80)
    print(f"📊  Market Analysis — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n📈 Price & EMA Overview")
    print("-" * 80)
    print(f"🔹 Latest Close Price : ₹{close:.2f}")
    print(f"🔸 EMA7 : {ema7:.2f}   |   EMA50 : {ema50:.2f}   |   EMA200 : {ema200:.2f}")
    print(f"📍 EMA Signal : {signal}")
    print(f"🔄 EMA 50/200 Trend : {ema_status}")

    print("\n🕯️ Candle Analysis")
    print("-" * 80)
    print(f"🟢 Type     : {candle_color}")
    print(f"💪 Strength : {candle_strength}")

    print("\n📐 Position Relative to EMA7")
    print("-" * 80)
    print(f"➡️ {candle_vs_white_line}")
    print(f"🤝 EMA Touching Candle? : {ema_touching_candle}")
    print(f"📊 EMA7 Slope : {'📏 Sideways' if ema7_sideways else '📈 Trending'}")

    print("\n💹 Impulse MACD Histogram")
    print("-" * 80)
    print(f"🧭 State : {histo_state} ({latest_sh:.6f})")
    print(f"📉 Market Condition : {'🔁 Sideways (−10 to +10)' if macd_sideways else '📊 Trending'}")

    print("\n📢 Trade Recommendations")
    print("-" * 80)
    buy_conditions = [
        candle_color == "Green (Bullish)",
        candle_strength_pct >= strength_threshold_strong,
        lin_close > ema7,
        signal == "Golden Cross (Bullish)",
        latest_sh > 0,
        not ema7_sideways,
        not macd_sideways
    ]

    sell_conditions = [
        candle_color == "Red (Bearish)",
        candle_strength_pct >= strength_threshold_strong,
        lin_close < ema7,
        signal == "Death Cross (Bearish)",
        latest_sh < 0,
        not ema7_sideways,
        not macd_sideways
    ]

    if all(buy_conditions):
        print("✅ BUY Signal : Strong bullish candle above EMA7 with Golden Cross and trending MACD")
    elif all(sell_conditions):
        print("🔻 SELL Signal : Strong bearish candle below EMA7 with Death Cross and trending MACD")
    elif candle_color == "Doji (Neutral)" or ema7_sideways or macd_sideways:
        print("⏸️ HOLD / AVOID : Sideways market or unclear signal")
    else:
        print("⚠️ No clear entry signal. Wait for stronger confirmation.")

    # Save to CSV (Structured Log)
    log_file = "market_analysis_log.csv"
    df_log_entry = {
        "Datetime": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "Nifty50": [f"{close:.2f}"],  # Store as a formatted string instead of raw float

        "EMA Signal": [signal],
        "Candle Color": [candle_color],
        "Candle vs EMA7": [
            "Above EMA7" if lin_close > ema7 else
            "Below EMA7" if lin_close < ema7 else
            "At EMA7"
        ],
        "MACD State": [histo_state],
        "Market Condition": [
            "Sideways (−10 to +10)" if macd_sideways else "Trending"
        ],
        "Buy": [""],
        "Sell": [""],
        "Profit/Loss": [""]
    }

    df_log = pd.DataFrame(df_log_entry)

    if not os.path.exists(log_file):
        df_log.to_csv(log_file, index=False)
    else:
        df_log.to_csv(log_file, mode='a', index=False, header=False)

    print("=" * 80)

# -------------------------------
# Main Loop
# -------------------------------

if __name__ == "__main__":
    while True:
        try:
            monitor_market()
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(3)