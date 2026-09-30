"""Exact, conservative discount arithmetic; no network or MCP dependency."""
from decimal import Decimal, InvalidOperation
from fractions import Fraction


def number(value):
    if isinstance(value, bool):
        raise ValueError('數值不可為布林值')
    try:
        d = Decimal(str(value))
        if not d.is_finite() or abs(d) > Decimal('1e15') or d.as_tuple().exponent < -6:
            raise ValueError('數值須有限、絕對值不超過 10^15，且最多六位小數')
        return Fraction(d)
    except (InvalidOperation, TypeError):
        raise ValueError('請使用不含千分位與貨幣符號的數值') from None


def rounded(value, digits=2, up=False):
    scale = 10 ** digits
    n, d = (value * scale).as_integer_ratio()
    units = -(-n // d) if up else n // d
    s = f'{units // scale}.{units % scale:0{digits}d}' if digits else str(units)
    return s.rstrip('0').rstrip('.') if '.' in s else s


def metrics(ratio):
    return {
        'pay_ratio_exact': f'{ratio.numerator}/{ratio.denominator}',
        'zhe_conservative': rounded(ratio * 10, 2, True),
        'percent_off_conservative': rounded((1-ratio)*100, 2),
    }


def calculate_discount_range(products, currency='TWD', conditions=''):
    """All products must share a currency and eligibility conditions."""
    if not products or len(products) > 1000:
        raise ValueError('請提供 1–1000 件商品')
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError('幣別不可空白')
    if not isinstance(conditions, str):
        raise ValueError('conditions 須為文字')
    rows, ratios, ids = [], [], set()
    for p in products:
        if not isinstance(p, dict) or set(p) - {'id', 'name', 'original_price', 'sale_price'}:
            raise ValueError('商品欄位僅接受 id/name/original_price/sale_price')
        if not {'id', 'name', 'original_price', 'sale_price'} <= set(p):
            raise ValueError('缺少必要商品欄位')
        if not isinstance(p['id'], str) or not p['id'].strip() or p['id'] in ids:
            raise ValueError('商品 id 必須為非空且不可重複的字串')
        if not isinstance(p['name'], str) or not p['name'].strip():
            raise ValueError('商品名稱不可空白')
        ids.add(p['id'])
        original, sale = number(p['original_price']), number(p['sale_price'])
        if original <= 0 or sale < 0 or sale > original:
            raise ValueError('原價須大於 0，優惠價須介於 0 與原價之間')
        ratio = sale / original
        ratios.append(ratio)
        rows.append({**p, **metrics(ratio), 'saved_amount': rounded(original-sale, 6)})
    low, high = min(ratios), max(ratios)
    prefix = f'指定商品（{conditions.strip()}）' if conditions.strip() else '指定商品'
    zhe = rounded(low*10, 2, True)
    off = rounded((1-low)*100, 2)
    if low == 1:
        copies = [f'{prefix}目前無折扣']
    elif low == 0:
        copies = [f'{prefix}部分商品優惠價 0 元', f'{prefix}最高省 100%']
    elif zhe == '10' or off == '0':
        copies = [f'{prefix}享優惠價，請參閱各商品售價']
    else:
        copies = [f'{prefix}低至 {zhe} 折', f'{prefix}最高省 {off}%', f'{prefix}最高 {off}% OFF']
    return {
        'currency': currency, 'conditions': conditions.strip(), 'product_count': len(rows),
        'summary': {
            'lowest_zhe': rounded(low*10, 2, True), 'highest_zhe': rounded(high*10, 2, True),
            'minimum_percent_off': rounded((1-high)*100, 2),
            'maximum_percent_off': rounded((1-low)*100, 2),
            'best_discount_product_ids': [p['id'] for p,r in zip(products,ratios) if r == low],
            'least_discount_product_ids': [p['id'] for p,r in zip(products,ratios) if r == high],
        }, 'products': rows, 'suggested_copy': copies,
        'rounding_policy': '折數無條件進位至小數 2 位；省%無條件捨去至小數 2 位，不放大優惠。精確比例另列。',
        'scope_note': '僅代表輸入商品，不推論全館；價格須為已確認實付價。不同會員、門檻、幣別請分次計算。未計運費、點數或未來回饋。',
    }


def convert_discount(value, input_type):
    v = number(value)
    if input_type == 'zhe' and 0 <= v <= 10:
        ratio = v/10
    elif input_type == 'percent_off' and 0 <= v <= 100:
        ratio = 1-v/100
    else:
        raise ValueError('input_type 須為 zhe（0–10 折）或 percent_off（0–100%）')
    return metrics(ratio)
