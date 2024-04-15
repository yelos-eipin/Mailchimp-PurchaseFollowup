
import jaydebeapi

def connect():
   #variables
   jdbcClassName = "com.ibm.as400.access.AS400JDBCDriver"
   jdbcUrl = "jdbc:as400://PFWF2009.ADP-ID.NET;libraries=PFWF2009;translate binary=true"
   dbUser = "user"
   dbPass = "pass"
   JarClassPath = "/home/papatux/jtopen_11.2/lib/jt400.jar"

   print('Connecting to DB...')
   conn = jaydebeapi.connect(jdbcClassName,jdbcUrl, [dbUser, dbPass], JarClassPath,)

   return conn