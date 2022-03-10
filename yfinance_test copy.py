import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np
from pandas_datareader import data as pdr
import statsmodels.api as sm

yf.pdr_override()


class Stock:
    now = dt.datetime.now().date() - dt.timedelta(days=1)
    last_business_day = np.busday_offset(now, 0, roll='backward')
    last_business_day_as_dt = pd.to_datetime(last_business_day).date()
    year = dt.timedelta(days=365)
    one_year_from_last_business_day = last_business_day_as_dt - year
    one_year_ago_business_day = np.busday_offset(
        one_year_from_last_business_day, 0, roll='backward')

    def __init__(self, ticker_id):
        self.ticker = ticker_id
        self.df = pdr.get_data_yahoo(
            self.ticker, self.one_year_ago_business_day, self.last_business_day_as_dt)

    def adj_close(self):
        df = pd.DataFrame()
        df[f'{self.ticker}'] = self.df['Adj Close']
        return df


class Portfolio:

    def __init__(self, ticker_list):
        self.tickers = [Stock(ticker) for ticker in ticker_list]
        self.df = pd.DataFrame()
        self.close_df = pd.DataFrame
        self.return_list = pd.DataFrame
        self.state = 0
        self.betas = []
        self.res_vars = []

    def adj_close_port(self):

        ds = Stock('SPY').adj_close()
        ds1 = Stock('^TYX').adj_close()
        L = [ticker.adj_close() for ticker in self.tickers]
        L.append(ds)
        L.append(ds1)
        df = pd.concat(L, axis=1)
        self.close_df = df
        self.state += 1
        return self.close_df

    def returns(self):

        df = self.adj_close_port()
        print('ADJ CLOSE')
        df_ret = pd.DataFrame()
        for col in df:
            df_ret[f'{col}_ret'] = (df[f'{col}'].pct_change() * 100)
        df_ret = df_ret.dropna()
        self.state += 1
        self.return_list = df_ret
        return df_ret

    def betas_and_res_var(self):

        df = self.returns()
        print('command executed')
        betas = []
        res_vars = []
        df = self.returns()
        df = df.drop(labels=['SPY_ret', '^TYX_ret'], axis=1)

        for col in df:
            y = df[col] - self.return_list['^TYX_ret']
            x = self.return_list['SPY_ret']
            x = sm.add_constant(x)
            model = sm.OLS(y, x).fit()
            betas.append(model.params[1])
            res_vars.append(
                (sum(model.resid ** 2) / (len(model.resid) - 2)) / 100)
            # The above line calculates the residual variance of a stock
        self.betas += betas
        self.res_vars += res_vars
        self.state += 1
        return list(zip(betas, res_vars))

    def alphas(self):
        #Alpha = Ri - (rf + beta(rm-rf))
        L = self.betas_and_res_var()
        df = self.returns()
        df_1 = df.drop(labels=['SPY_ret', '^TYX_ret'], axis=1)
        for col in df_1:

            # portfolio = (input('Enter a list of stocks:'))
            # print(portfolio)
            # portfolio1 = Portfolio(portfolio)
            # print(portfolio1.adj_close_portf())
portfolio = input(
    "Enter a list stock separated by a comma and a space ").split(', ')
portfolio1 = Portfolio(portfolio)
print(portfolio1.alphas())

# df = Stock('SPY').main_df()
L = [1, 2, 3, 4, 5, 6]
print(np.arange())
