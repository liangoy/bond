from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def count_feb_29(start_date, end_date):
    count = 0
    for year in range(start_date.year, end_date.year + 1):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            feb_29 = date(year, 2, 29)
            if start_date <= feb_29 < end_date:
                count += 1
    return count


def calculate_interest_payments_times(end_date_str, payment_months=6):
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    today = date.today()

    if today > end_date:
        raise Exception('today > end_date')

    if end_date.day == 31 or (end_date.month == 2 and end_date.day >= 28):
        raise Exception('Irregular Value Date')

    payments_times = 0
    while end_date - relativedelta(months=payment_months * payments_times) > today:
        payments_times += 1
    last_payment_date = end_date - relativedelta(months=payment_months * payments_times)
    next_payment_date = end_date - relativedelta(months=payment_months * (payments_times - 1))
    next_payment_date = min(next_payment_date, end_date)
    days_since_last_payment = (today - last_payment_date).days - count_feb_29(last_payment_date, today)
    days_to_next_payment = (next_payment_date - today).days - count_feb_29(today, next_payment_date)

    return payments_times, days_since_last_payment, days_to_next_payment


def ytm2netprice(ytm, rate, end_date):
    pay_tims, days_since_last_payment, days_to_next_payment = calculate_interest_payments_times(end_date)

    unpayed_interest = days_since_last_payment / 365 * rate

    first_time = days_to_next_payment / (365 / 2)
    s = 0
    for i in range(pay_tims):
        s += (rate / 2) / (1 + ytm / 2 / 100) ** (i + first_time)
    s += 100 / (1 + ytm / 2 / 100) ** (i + first_time)

    return s - unpayed_interest


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
