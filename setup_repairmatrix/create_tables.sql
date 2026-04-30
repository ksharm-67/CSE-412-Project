CREATE TABLE CUSTOMER  ( C_CUSTKEY  INTEGER NOT NULL,
                            C_NAME       VARCHAR(25) NOT NULL,
                            C_PHONE  CHAR(15) NOT NULL,
                            C_EMAIL    VARCHAR(152));

CREATE TABLE ORDERPARTS  ( O_REPAIRKEY  INTEGER NOT NULL,
                            O_PARTKEY       INTEGER NOT NULL,
                            O_QTYUSED    INTEGER NOT NULL);

CREATE TABLE PART  ( P_PARTKEY     INTEGER NOT NULL,
                          P_NAME        VARCHAR(55) NOT NULL,
                          P_SERIALNUM        VARCHAR(150) NOT NULL,
                          P_STOCKQTY       INTEGER NOT NULL,
                          P_UNITPRICE       DECIMAL(6, 2) NOT NULL);

CREATE TABLE DEVICE ( D_DEVICEKEY     INTEGER NOT NULL,
                             D_DEVICETYPE        VARCHAR(50) NOT NULL,
                             D_SERIALNUM     VARCHAR(150) NOT NULL,
                             D_CUSTKEY  INTEGER NOT NULL,
                             D_MODEL       VARCHAR(100) NOT NULL,
                             D_BRAND     VARCHAR(50) NOT NULL);

CREATE TABLE REPAIRORDER ( RO_REPAIRKEY     INTEGER NOT NULL,
                             RO_ORDERKEY    INTEGER NOT NULL,
                             RO_CUSTKEY    INTEGER NOT NULL,
                             RO_DEVICEKEY    INTEGER NOT NULL,
                             RO_TECHKEY     INTEGER NOT NULL,
                             RO_TOTALCOST  DECIMAL(15,2)  NOT NULL,
                             RO_ISSUEDECRIPTION     VARCHAR(500) NOT NULL,
                             RO_STATUS      VARCHAR(10) NOT NULL,
                             RO_DATESTARTED DATE NOT NULL,
                             RO_DATEFINISHED DATE);

CREATE TABLE TECHNICIAN ( T_TECHKEY     INTEGER NOT NULL,
                             T_NAME        VARCHAR(25) NOT NULL,
                             T_SPECIALTY    VARCHAR(40) NOT NULL,
                             T_HOURLYRATE   DECIMAL(5,2) NOT NULL);

