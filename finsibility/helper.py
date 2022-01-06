from flask import request, session, current_app as finsy
from flask_login import current_user

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os
import datetime
import re
import pandas as pd
import json
import decimal
from operator import itemgetter
import time
import requests
import inspect

from finsibility import db
import finsibility.applicationException as appex
from finsibility.models import User
from finsibility.forms import RegistrationForm
import finsibility.constants as constants
import finsibility.endpoints as endpoints
import finsibility.params as stock_params
from finsibility.config import Config, ProductionConfig

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def verify_file(file):
    file_date = None
    filename = None
    file_dates_arr = None

    #finsy.logger.debug("1")

    try:
        filename = file.filename
        finsy.logger.debug(f'filename: {filename}')

        #finsy.logger.debug("3")

        file_split = re.split('[_.]', filename)
        finsy.logger.debug(f'file split: {file_split}')
        file_dates_arr = file_split[-4:-1]
        finsy.logger.debug(f'file dates arr: {file_dates_arr}')
        file_date = datetime.datetime(int(file_dates_arr[0]), int(file_dates_arr[1]), int(file_dates_arr[2]))
        finsy.logger.debug(f'{file_date} - {current_user.id}')

    except Exception as ex:
        finsy.logger.debug(f'ex: {ex}')

        raise appex.FileVerificationFailedExcpetion()

    #finsy.logger.debug("5")

    brokerage_firm = 'TD Ameritrade'
    if check_positions_exist_for_day(file_date, brokerage_firm):
        raise appex.PositionAlreadyUploaded()

    data = None

    try:
        file_path = os.path.join(os.environ['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        data = pd.read_csv(file_path, sep='\t', index_col=False, skiprows=(0, 1, 2, 3, 4, 5, 6), header=(0),
                           thousands=',', na_values=["CB_Data_Unavailable", '--'])
    except Exception:
        raise appex.FileUploadFailed()

    finsy.logger.debug(f'data head before: {data.head()}')
    data.dropna(axis=1, how='all', inplace=True)
    data.dropna(axis=0, inplace=True)
    finsy.logger.debug(f'data head after: {data.head()}')

    if not data.shape[1] == 9:
        raise appex.FileFormatException()

    try:
        mkt_value = round(data['Mkt value'].astype(float).sum(), 2)
    except Exception:
        raise appex.FileFormatException()

    if not data.columns.values[0] == 'Symbol':
        raise appex.FileFormatException()

    data_json = data.to_json(orient='records')  # good
    session_data = {'file_date': file_date, 'positions': data_json}

    return [data.to_html(classes='table', index=False, justify='left')], data.columns.values,mkt_value, session_data


def check_positions_exist_for_day(p_date, brokerage_firm):

    query = '''select exists(select 1 from positions 
                where user_id=:user_id and position_date::date=to_date(:p_date, 'YYYY-MM-DD') and brokerage_firm=:brokerage_firm)'''


    results = False # Extract did not runRan

    finsy.logger.debug(f'{current_user.id} - p_date.strftime("%Y-%m-%d") - {brokerage_firm}')
    try:
        engine = create_engine(os.environ['DATABASE_URL'])
        Session = scoped_session(sessionmaker(bind=engine))

        session = Session()
        results = session.execute(query, {'user_id': current_user.id, 'p_date':p_date.strftime("%Y-%m-%d"), 'brokerage_firm': brokerage_firm}).fetchone()
        finsy.logger.debug(f' results: {results}')

    except Exception as ex:
        finsy.logger.debug(f'Exception in check_positions_exist_for_day: {current_user} - p_date.strftime("%Y-%m-%d") - {brokerage_firm} ex: {ex}')
        raise ex
    finally:
        session.close()
        engine.dispose()

    return results[0]

def register(form: RegistrationForm):
    try:
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
    except Exception as ex:
        finsy.logger.error(f'Exception in register: {form.username.data}, {form.email.data}  ex: {ex}')

        raise appex.UserRegistrationFailedException()


def save_data_to_positions(current_user, file_date, brokerage_firm, positions):
    try:
        engine = create_engine(os.environ['DATABASE_URL'])
        Session = scoped_session(sessionmaker(bind=engine))

        session = Session()

        query = '''insert into positions values (:user_id,:position_date,:brokerage_firm,:positions)'''

        session.execute(query, {'user_id': current_user.id, 'position_date': file_date, 'brokerage_firm': brokerage_firm,'positions': positions})
        session.commit()

    except Exception as ex:
        finsy.logger.error(f'Exception in save_data_to_positions: {current_user} - {file_date} - {brokerage_firm}')
        raise appex.PositionsSaveException()
    finally:
        session.close()
        engine.dispose()



def review_positions(date_value=None):
    quotes = None
    try:
        position_data = get_positions_symbols(date_value)

        symbols = ",".join([x[0] for x in position_data])

        quotes_data = get_fresh_quotes(symbols)
        quotes = quotes_data.json()

        positions_list = []
        for x in position_data:
            positions_dict = {}
            if x[0] in quotes:
                positions_dict['Symbol'] = x[0]
                positions_dict['Quantity'] = x[1]
                positions_dict['Mkt. Value'] = x[2]
                positions_dict['Gain'] = x[3]
                positions_dict['Current Value'] = round(x[1] * decimal.Decimal(quotes[x[0]]['lastPrice']), 2)

                positions_dict['Current Price'] = quotes[x[0]]['lastPrice']
                positions_dict['Bid Price'] = quotes[x[0]]['bidPrice']
                positions_dict['Bid Size'] = quotes[x[0]]['bidSize']
                positions_dict['Low Price'] = quotes[x[0]]['lowPrice']
                positions_dict['High Price'] = quotes[x[0]]['highPrice']
                positions_dict['Net Change'] = quotes[x[0]]['netChange']
                positions_dict['Total Volume'] = quotes[x[0]]['totalVolume']
                positions_dict['Dividend Amount'] = quotes[x[0]]['divAmount']
                if len(quotes[x[0]]['divDate']) > 0:
                    positions_dict['Dividend Date'] = quotes[x[0]]['divDate'][:11]
                else:
                    positions_dict['Dividend Date'] = quotes[x[0]]['divDate']
            else:
                positions_dict = {'Symbol': x[0],
                                  'Quantity': x[1],
                                  'Mkt. Value': x[2],
                                  'Gain': x[3],
                                  'Current Value': 0.0,
                                  'Current Price': 0.0,
                                  'Bid Price': 0.0,
                                  'Bid Size': 0.0,
                                  'Low Price': 0.0,
                                  'High Price': 0.0,
                                  'Net Change': 0.0,
                                  'Total Volume': 0.0,
                                  'Dividend Amount': 0.0,
                                  'Dividend Date': ""
                                  }

            positions_list.append(positions_dict)

        quotes = sorted(positions_list, key=itemgetter('Net Change', 'Gain'), reverse=True)
        df = pd.DataFrame(quotes)
        finsy.logger.debug(f'df: {quotes}')


    except appex.DataFetchException as ex:
        raise ex

    return [df.to_html(classes='table', index=False, justify='left')]


def get_positions_symbols(date_value=None):

    query = """SELECT  pos.symbol, quantity::numeric, value::numeric, gain::numeric
            from
                (
                    select user_id, position_date, obj1->>'Qty' as quantity, obj1->>'Symbol' as symbol, obj1->>'Mkt value' as value, obj1->>'Gain ($)' as gain
                    from positions s, jsonb_array_elements(s.positions) obj1
                ) pos
            left join 
                (
                    SELECT symbol, demographic_data->>'sector' as sector
                    from stock_demographic sd
                ) sd
            on  pos.symbol = sd.symbol
            where pos.user_id=:user_id """

    if date_value:
        query += "and date(pos.position_date) = date(:date_value)"
    else:
        query += "and date(pos.position_date) = (select date(max(position_date)) from positions where user_id=3)"

    results = None

    try:
        engine = create_engine(os.environ['DATABASE_URL'])
        Session = scoped_session(sessionmaker(bind=engine))

        session = Session()
        results = None
        if date_value:
            results = session.execute(query, {'user_id': current_user.id, 'date_value': date_value}).fetchall()
        else:
            results = session.execute(query, {'user_id': current_user.id}).fetchall()

    except Exception as ex:
        func_name = inspect.currentframe().f_code.co_name
        raise appex.DataFetchException(function_name=func_name, reason=ex)
    finally:
        session.close()
        engine.dispose();

    return results


def get_fresh_quotes(symbols):
   quotes_url = endpoints.STOCK_QUOTE_URL
   params = stock_params.STOCK_QUOTE_PRARAM
   params['symbol'] = symbols

   data=None
   start = time.perf_counter()
   try:
        data = requests.get(url=quotes_url, params=params)
   except Exception as ex:
       func_name = inspect.currentframe().f_code.co_name
       raise appex.DataFetchException(function_name=func_name, reason=ex)

   return data
