import configparser
import jaydebeapi

class PFW:
    def __init__(self):
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read("config.ini")
        self.conn = None
        #self.driver = None  # Store JDBC driver class

    def __connect(self):
        """ Establishes a connection to the database based on config file"""
        try:
            db_config = self.config["AUTH"]
            #self.driver = jaydebeapi.DatabaseDrivers[db_config["driver"]]  # Load driver
            jdbcClassName = db_config['jdbcClassName']
            jdbcUrl = db_config['jdbcUrl']
            dbUser = db_config['dbUser']
            dbPass = db_config['dbPass']
            JarClassPath = db_config['JarClassPath']

            self.conn = jaydebeapi.connect(jdbcClassName,jdbcUrl, [dbUser,dbPass], JarClassPath,)
        except Exception as e:
            print(f"Error connecting to database: {e}")  
                
    def get_parts_purchases(self, days_prior):
            """ Fetches parts purchases data for the specified number of days prior"""
            if not self.conn:
                self.__connect()

            sql = """
                    SELECT 
                    cust.cu_cus "Customer Number"
                    ,cust.cu_br "Branch"
                    ,CASE mh.bh_bc
                        WHEN 'I' THEN 'Equipment Billing'
                        WHEN 'T' THEN 'Rental'      
                        WHEN 'W' THEN 'Work Order'      
                        WHEN 'S' THEN 'Parts Order'      
                        WHEN 'P' THEN 'Parts Invoicing'
                        ELSE mh.bh_bc
                    END AS "Purchase Type"
                    ,mh.bh_ord "Invoice Number"
                    ,SUM( md.bd_prc ) AS "Amount"
                    ,contact.cc_bem "Email"
                    ,cust.cu_nme "Customer Name"
                    ,cust.cu_ad1 "Address"
                    ,CUST.cu_cit "City"
                    ,cust.cu_prv "Province"
                    ,mh.bh_bdt "Purchase Date"
                    FROM 
                    mnbdh mh
                    INNER JOIN cmastr AS cust
                        ON mh.bh_cus = cust.cu_cus
                        AND mh.bh_co = cust.cu_co
                        AND mh.bh_div = cust.cu_div    
                    LEFT JOIN cmascon as contact
                        ON cust.cu_cus = contact.cc_cus
                        AND cust.cu_co = contact.cc_co
                        AND cust.cu_div = contact.cc_div
                        AND contact.cc_num = 0
                    INNER JOIN mnbdd md ON
                        mh.bh_tid = md.bd_tid
                        AND mh.bh_co = md.bd_co
                        AND mh.bh_div = md.bd_div
                        AND mh.bh_br = md.bd_br
                    WHERE
                    mh.bh_bdt >= VARCHAR_FORMAT(current timestamp - 7 DAYS,'YYYYMMDD')
                    AND cust.cu_cus NOT LIKE 'CASH%'
                    AND cust.cu_cus NOT LIKE 'INTER%'
                    AND cust.cu_cus NOT LIKE 'JDWAR%'
                    AND cust.cu_cus NOT LIKE 'TRAN%'
                    --AND md.bd_cash <> ''
                    AND md.bd_tc = 'FC'
                    AND mh.bh_bc IN ('S') -- choose Parts Order invoice types
                    AND contact.cc_bem <> ''
                    AND cust.cu_cus NOT IN ( SELECT 
                                                cust.cu_cus "Customer Number"
                                                FROM 
                                                mnbdh mh
                                                INNER JOIN cmastr AS cust
                                                    ON mh.bh_cus = cust.cu_cus
                                                    AND mh.bh_co = cust.cu_co
                                                    AND mh.bh_div = cust.cu_div    
                                                LEFT JOIN cmascon as contact
                                                    ON cust.cu_cus = contact.cc_cus
                                                    AND cust.cu_co = contact.cc_co
                                                    AND cust.cu_div = contact.cc_div
                                                    AND contact.cc_num = 0
                                                INNER JOIN mnbdd md ON
                                                    mh.bh_tid = md.bd_tid
                                                    AND mh.bh_co = md.bd_co
                                                    AND mh.bh_div = md.bd_div
                                                    AND mh.bh_br = md.bd_br
                                                WHERE
                                                mh.bh_bdt BETWEEN VARCHAR_FORMAT(current timestamp - 31 DAYS,'YYYYMMDD') and VARCHAR_FORMAT(current timestamp - 2 DAYS,'YYYYMMDD')
                                                AND cust.cu_cus NOT LIKE 'CASH%'
                                                AND cust.cu_cus NOT LIKE 'INTER%'
                                                AND cust.cu_cus NOT LIKE 'JDWAR%'
                                                AND cust.cu_cus NOT LIKE 'TRAN%'
                                                --AND md.bd_cash <> ''
                                                AND md.bd_tc = 'FC'
                                                AND mh.bh_bc IN ('S') -- choose Parts Order invoice types
                                                AND contact.cc_bem <> ''
                                                GROUP BY 
                                                cust.cu_cus
                                                ,cust.cu_br
                                                ,mh.bh_bc
                                                ,mh.bh_ord
                                                ,contact.cc_bem
                                                ,cust.cu_nme
                                                ,cust.cu_ad1
                                                ,CUST.cu_cit
                                                ,cust.cu_prv
                                                ,mh.bh_bdt
                                                HAVING
                                                SUM( md.bd_prc * -1 ) >= 500 -- md.bd_prc has to be multiplied by -1 because journal entries show up negative for positive charges
                                        )
                    GROUP BY 
                    cust.cu_cus
                    ,cust.cu_br
                    ,mh.bh_bc
                    ,mh.bh_ord
                    ,contact.cc_bem
                    ,cust.cu_nme
                    ,cust.cu_ad1
                    ,CUST.cu_cit
                    ,cust.cu_prv
                    ,mh.bh_bdt
                    HAVING
                    SUM( md.bd_prc * -1 ) >= 500 -- md.bd_prc has to be multiplied by -1 because journal entries show up negative for positive charges
            """
            try:
                cursor = self.conn.cursor()
                cursor.execute(sql, {"days": days_prior})
                #print(sql)
                cursor.execute(sql)
                data = cursor.fetchall()
                return data
                #return sql
            except Exception as e:
                print(f"Error fetching parts purchases data: {e}")
                return None
            finally:
                if self.conn:
                    self.conn.close()

    def get_equipment_purchases(self, days_prior):
        """ Fetches equipment purchases data for the specified number of days prior"""
        if not self.conn:
            self.__connect()

        sql = """
            SELECT *
            FROM equipment_purchases
            WHERE purchase_date >= CURRENT_DATE - INTERVAL %(days)s DAY;
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, {"days": days_prior})
            data = cursor.fetchall()
            return data
        except Exception as e:
            print(f"Error fetching equipment purchases data: {e}")
            return None
        finally:
            if self.conn:
                self.conn.close()

    def get_service_performed(self, days_prior):
        """ Fetches service performed data for the specified number of days prior"""
        if not self.conn:
            self.__connect()

        sql = """
            SELECT *
            FROM service_performed
            WHERE service_date >= CURRENT_DATE - INTERVAL %(days)s DAY;
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, {"days": days_prior})
            data = cursor.fetchall()
            return data
        except Exception as e:
            print(f"Error fetching service performed data: {e}")
            return None
        finally:
            if self.conn:
                self.conn.close()