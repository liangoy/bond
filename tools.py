from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def calculate_interest_payments_times(end_date_str, payment_months=6):
    # 将字符串转换为日期对象
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    today = date.today()

    # 如果今天已经过了结束日期，返回0, None, 和0
    if today > end_date:
        return 0, None, 0

    # 找到第一个付息日
    first_payment_date = date(end_date.year, end_date.month, end_date.day)
    while first_payment_date > today:
        first_payment_date -= relativedelta(months=payment_months)

    # 从第一个付息日开始，计算所有的付息日
    payment_dates = []
    current_date = first_payment_date
    last_payment_date = None
    while current_date <= end_date:
        if current_date > today:
            payment_dates.append(current_date)
        elif current_date <= today:
            last_payment_date = current_date
        current_date += relativedelta(months=payment_months)

    # 计算距离最近付息日的天数
    if payment_dates:
        next_payment_date = payment_dates[0]
        days_to_next_payment = (next_payment_date - today).days
    else:
        days_to_next_payment = None

    # 计算从上一个付息日到今天的天数
    if last_payment_date:
        days_since_last_payment = (today - last_payment_date).days
    else:
        days_since_last_payment = 0

    return len(payment_dates), days_since_last_payment, days_to_next_payment


def ytm2netprice(ytm, rate, end_date):
    pay_tims, days_since_last_payment, days_to_next_payment = calculate_interest_payments_times(end_date)

    unpad_interest = days_since_last_payment / 365.25 * rate

    first_time = days_to_next_payment / (365.25 / 2)
    s = 0
    for i in range(pay_tims):
        s += (rate / 2) / (1 + ytm / 2 / 100) ** (i + first_time)
    s += 100 / (1 + ytm / 2 / 100) ** (i + first_time)

    return s - unpad_interest


def netprice2ytm(price, rate, end_date, tolerance=1e-4, max_iterations=1000):
    ytm_low, ytm_high = 0, 100  # 假设YTM在0%到100%之间
    for _ in range(max_iterations):
        ytm_mid = (ytm_low + ytm_high) / 2
        price_mid = ytm2netprice(ytm_mid, rate, end_date)

        if abs(price_mid - price) < tolerance:
            return ytm_mid

        if price_mid > price:
            ytm_low = ytm_mid
        else:
            ytm_high = ytm_mid

    raise ValueError("未能在指定迭代次数内找到解")


if __name__ == '__main__':
    print(ytm2netprice(1.89, 2.47, '2054-07-25'))
    print(netprice2ytm(113.177, 2.47, '2054-07-25'))
    print(netprice2ytm(115.6, 2.57, '2054-05-20'))
