import psycopg2

from private import settings


class MyDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = psycopg2.connect(host="localhost", user=settings.db_username, password=settings.db_password, database="optiondata") 
        self._db_cur = self._db_connection.cursor()

    def query(self, query):
        return self._db_cur.execute(query)

    def __del__(self):
        self._db_connection.close()

    def check_holiday(self, underlying_symbol, quote_date):
        query = "SELECT NOT EXISTS(SELECT * FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "')"
        self.query(query)
        row = self._db_cur.fetchone()
        return row[0]

    def select_strike_by_delta(self, quote_date, underlying_symbol, expiration, option_type, indelta, divisor=1): 
        query = "SELECT strike, delta FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike % " + str(divisor) + " = 0 ORDER BY ABS(delta - " + str(indelta) + ") LIMIT 1;"
        self.query(query)
        row = self._db_cur.fetchone()
        if row == None:
            return None
        strike = row[0]
        return strike 

    def select_strike_by_midprice(self, quote_date, underlying_symbol, expiration, option_type, inmidprice, divisor=1): 
        query = "SELECT strike FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike % " + str(divisor) + " = 0 AND mid_1545 !=0 AND mid_1545 <=" + str(inmidprice) + " ORDER BY strike DESC LIMIT 1;"
        self.query(query)
        row = self._db_cur.fetchone()
        if row == None:
            return None
        strike = row[0]
        return strike 
    
    def select_expiration(self, quote_date, underlying_symbol, option_type, days): 
        query = "SELECT DISTINCT expiration, ABS(DATE_PART('day', expiration - " + str(quote_date) + ") - 90) AS difference FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND option_type = '" + option_type + "' AND expiration >= '" + str(quote_date) + "'::date AND expiration <= ('" + str(quote_date) + "'::date + interval '" + str(days + 50) + " days')" + " AND expiration >= ('" + str(quote_date) + "'::date + interval '" + str(days - 50) + " days') ORDER BY difference ASC LIMIT 1;"
        self.query(query)
        row = self._db_cur.fetchone()
        if row == None:
            return None
        expiration = row[0]
        return expiration

    def select_iv(self, quote_date, underlying_symbol, expiration, option_type, strike):
        query = "SELECT iv FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike = '" + str(strike) + "'"
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: return None 
        iv = row[0]
        return float(iv) 
       
    def select_delta(self, quote_date, underlying_symbol, expiration, option_type, strike):
        query = "SELECT delta FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike = '" + str(strike) + "'"
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: return None 
        delta = row[0]
        return delta 

    def select_vega(self, quote_date, underlying_symbol, expiration, option_type, strike):
        query = "SELECT vega FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike = '" + str(strike) + "'"
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: return None 
        vega = row[0]
        return vega 

    def select_theta(self, quote_date, option):   
        query = "SELECT theta FROM optiondata WHERE underlying_symbol = '" + option.underlying + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(option.expiration) + "' AND option_type = '" + option.type + "' AND strike = '" + str(option.strike) + "'"
        self.query(query)
        row = self._db_cur.fetchone()
        theta = row[0]
        return theta 

    def select_strikes(self, underlying_symbol, quote_date, expiration):   
        query = "SELECT DISTINCT strike FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "'"
        self.query(query)
        strikes = self._db_cur.fetchall()
        return strikes 

    def select_strikes_midprice(self, underlying_symbol, quote_date, expiration, option_type, divisor):   
        query = "SELECT strike, mid_1545 FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND option_type = '" + option_type + "' AND strike % " + str(divisor) + " = 0 AND mid_1545 != 0 ORDER BY strike asc" 
        self.query(query)
        results = self._db_cur.fetchall()
        return results
    
    def check_option(self, underlying_symbol, strike, quote_date, expiration): 
        query = "SELECT EXISTS (SELECT * FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND strike = '" + str(strike) + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "')"
        self.query(query)
        row = self._db_cur.fetchone()
        if row == None:
            return None 
        result = row[0] 
        return result
        
    def query_midprice_underlying(self, underlying_symbol, quote_date): 
        if quote_date == None: quote_date = self.query_maxdate()
        query = "SELECT underlying_mid_1545 FROM optiondata WHERE underlying_symbol = '" + str(underlying_symbol) + "' AND quote_date = '" + str(quote_date) + "'"
        self.query(query)
        row = self._db_cur.fetchone()
        if row == None:
            return None
        return float(row[0])
    
    def query_midprice(self, quote_date, option, printalot=False): 
        if quote_date == None: quote_date = self.query_maxdate()
        query = "SELECT mid_1545 FROM optiondata WHERE mid_1545 != 0 AND underlying_symbol = '" + option.underlying + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(option.expiration) + "' AND strike = '" + str(option.strike) + "' AND option_type = '" + option.type + "'"    
#         print(query) 
        self.query(query)
        if printalot: print(query) 
        row = self._db_cur.fetchone()
        if row == None: 
            return None
        return float(row[0]) 

    def query_maxdate(self):
        self.query("SELECT MAX(quote_date) FROM optiondata")
        row = self._db_cur.fetchone()
        maxdate = row[0]
        return maxdate 

    def check_exists(self, underlying, expiration):
        query = "SELECT EXISTS(SELECT 1 FROM optiondata WHERE underlying_symbol = '" + underlying + "' AND expiration = '" + str(expiration) + "')"
        self.query(query)
        row = self._db_cur.fetchone()
        return row[0]

    def query_expiration_before(self, underlying_symbol, strike, option_type, quote_date, later_expiration, budget):
        query = "SELECT expiration FROM optiondata WHERE quote_date = '" + str(quote_date) + "' AND underlying_symbol = '" + underlying_symbol + "' AND expiration > '" + str(quote_date) + "' AND expiration < '" + str(later_expiration) + "' AND option_type = '" + str(option_type) + "' AND strike = '" + str(strike) + "' AND mid_1545 <= " + str(budget) + " AND mid_1545 != 0 ORDER BY expiration DESC LIMIT 1"
#         print(query) 
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: 
            return None
        return row[0]

    def query_teenie_strike(self, underlying_symbol, quote_date, expiration, option_type):
        query = "SELECT strike FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration ='" + str(expiration) + "' AND ask_1545 = '0.05' AND option_type = '" + option_type + "' ORDER BY strike DESC LIMIT 1"
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: 
            print("return None")
            return None 
        return row[0]
    
    def query_credit(self, quote_date, underlying_symbol, expiration, strike, option_type, width): 
        query = "SELECT -(mid_1545) + (SELECT DISTINCT mid_1545 FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND strike = '" + str(strike - width) + "' AND option_type = '" + option_type + "' AND mid_1545 != 0 LIMIT 1) FROM optiondata WHERE underlying_symbol = '" + underlying_symbol + "' AND quote_date = '" + str(quote_date) + "' AND expiration = '" + str(expiration) + "' AND strike = '" + str(strike) + "' AND option_type = '" + option_type + "'"    
        self.query(query)
        row = self._db_cur.fetchone()
        if row is None: return None
        if row[0] is None: return None
        return float(row[0]) 
    
