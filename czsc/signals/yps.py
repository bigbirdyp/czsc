import numpy as np
from typing import Union, List
from collections import OrderedDict
from czsc.utils import create_single_signal, get_sub_elements
from czsc import CZSC


def yps_bupiao_V250612(c: CZSC, **kwargs)-> OrderedDict:
    """动量背离买入信号

    参数模板："{freq}_D{di}N{n1}M{n2}_BUPIAOV250612"

    **信号逻辑：**

    1. 计算短期动量指标(n1)和长期动量指标(n2)
    2. 当短期动量指标 <= 20 且长期动量指标 >= 80 时，产生买入信号

    **信号列表：**

    - Signal('日线_D1N3M21_BUPIAOV250612_买入_任意_任意_0')
    - Signal('日线_D1N3M21_BUPIAOV250612_其他_任意_任意_0')

    :param c: CZSC对象
    :param di: 倒数第i根K线
    :param n1: 短期窗口大小
    :param n2: 长期窗口大小
    :return: 信号识别结果
    """

    di = int(kwargs.get("di", 1))
    n1 = int(kwargs.get("n1", 3))
    n2 = int(kwargs.get("n2", 21))
    
    k1, k2, k3 = f"{c.freq.value}_D{di}N{n1}M{n2}_BUPIAOV250612".split("_")
    bars = get_sub_elements(c.bars_raw, di=di, n=max(n1, n2))
    
    v1 = "其他"
    v2 = "任意"
    v3 = "任意"
    
    if len(bars) < max(n1, n2):  # 确保有足够的K线进行计算
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)
        
    # 准备计算动量指标所需的数据
    close = np.array([x.close for x in bars])
    low = np.array([x.low for x in bars])
    
    # 计算当前K线的短期动量指标
    llv_short_current = np.min(low[-n1:])
    hhv_short_current = np.max(close[-n1:])
    short_momentum_current = 100 * (close[-1] - llv_short_current) / (hhv_short_current - llv_short_current) if (hhv_short_current - llv_short_current) > 0 else 0
    
    # # 计算前一根K线的短期动量指标
    # llv_short_prev = np.min(low[-n1-1:-1])
    # hhv_short_prev = np.max(close[-n1-1:-1])
    # short_momentum_prev = 100 * (close[-2] - llv_short_prev) / (hhv_short_prev - llv_short_prev) if (hhv_short_prev - llv_short_prev) > 0 else 0
    
    # 计算长期动量指标
    llv_long = np.min(low[-n2:])
    hhv_long = np.max(close[-n2:])
    long_momentum = 100 * (close[-1] - llv_long) / (hhv_long - llv_long) if (hhv_long - llv_long) > 0 else 0
    
    if short_momentum_current <= 20 and long_momentum >= 80:
        v1 = "买入"
    
    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1, v2=v2, v3=v3) 

def check():
    # from czsc.connectors import research
    from czsc.traders.base import check_signals_acc

    # symbols = research.get_symbols("A股主要指数")
    # bars = research.get_raw_bars(symbols[0], "15分钟", "20181101", "20210101", fq="前复权")
    from czsc.connectors.ts_connector import get_raw_bars

    symbol = '301188.SZ#E'
    bars = get_raw_bars(symbol, freq='日线', sdt='20200101', edt='20250601', fq="前复权")

    signals_config = [{"name": yps_bupiao_V250612, "freq": "日线", "di": 1, "n1": 3, "n2": 21}]
    check_signals_acc(bars, signals_config=signals_config, height="780px", delta_days=1)  # type: ignore


if __name__ == "__main__":
    check()