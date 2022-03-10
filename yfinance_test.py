import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np
from pandas_datareader import data as pdr
import statsmodels.api as sm
import sqlite3

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
        self.betas = []
        self.res_vars = []
        self.alphas = []
        self.info = {}

    def adj_close_port(self):
        ds = Stock('SPY').adj_close()
        ds1 = Stock('^TYX').adj_close()
        L = [ticker.adj_close() for ticker in self.tickers]
        L.append(ds)
        L.append(ds1)
        df = pd.concat(L, axis=1)
        self.close_df = df
        return self.close_df

    def returns(self):
        self.adj_close_port()
        df = self.adj_close_port()
        print('command executed')
        df_ret = pd.DataFrame()
        for col in df:
            df_ret[f'{col}_ret'] = (df[f'{col}'].pct_change() * 100)
        df_ret = df_ret.dropna()
        self.return_list = df_ret
        return self.return_list

    def betas_and_res_var(self):
        self.returns()
        print('command executed')
        betas = []
        res_vars = []
        df = self.return_list
        df = df.drop(labels=['SPY_ret', '^TYX_ret'], axis=1).copy()

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
        return list(zip(betas, res_vars))

    def alpha_list(self):
        self.betas_and_res_var()
        df = self.return_list
        alphas = []
        for i in range(len(self.tickers)):
            alphas.append(df[f'{self.tickers[i].ticker}_ret'][-1] - df['^TYX_ret'][-2] - self.betas[i] *
                          (df['SPY_ret'][-2] - df['^TYX_ret'][-2]))
            # real return - expected return
        self.alphas += [x/100 for x in alphas]
        return alphas

    def info_df(self):
        self.alpha_list()
        self.info = {self.tickers[i].ticker: [self.alphas[i], self.betas[i], self.res_vars[i]] for i in
                     range(len(self.tickers))}
        return pd.DataFrame.from_dict(self.info, orient='index', columns=['alpha', 'beta', 'res_var'])

    def save_to_db(self):
        df = self.info_df()
        con = sqlite3.connect('Portfolios.db')
        cur = con.cursor()
        df.to_sql('Portfolio1', con, if_exists= 'append', index=False)
        print('Saved to db')

# portfolio = (input('Enter a list of stocks:'))
# print(portfolio)
# portfolio1 = Portfolio(portfolio)
# print(portfolio1.adj_close_portf())
portfolio = input(
    "Enter a list stock separated by a comma and a space ").split(', ')
portfolio1 = Portfolio(portfolio)
print(portfolio1.info_df())

# df = Stock('SPY').main_df()
