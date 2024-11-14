CREATE DATABASE DBMS_project;
Use DBMS_project;

-- create queries

CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) DEFAULT NULL,
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL
);


CREATE TABLE stock_transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,          
    purchase_type ENUM('BUY', 'SELL') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    stock_symbol VARCHAR(30) NOT NULL,
    transaction_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE portfolio (
    user_id INT NOT NULL,           
    username VARCHAR(30) NOT NULL,
    stock_symbol VARCHAR(30) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id),
	FOREIGN KEY (stock_symbol) REFERENCES portfolio(stock_symbol)
);

CREATE TABLE Anomaly (
    AnomalyID INT AUTO_INCREMENT PRIMARY KEY,
    StockSymbol VARCHAR(10),
    AnomalyType VARCHAR(10),
    AnomalyDate DATE,
    AlertTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (StockSymbol) REFERENCES Stock_transactions(stock_symbol)
);

CREATE TABLE Alerts (
    Alert_ID INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(30),
    Anomaly_ID INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),  
    FOREIGN KEY (Anomaly_ID) REFERENCES Anomaly(Anomaly_ID)  
);

-- alter queries

ALTER TABLE portfolio
ADD COLUMN current_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00;

ALTER TABLE portfolio
ADD COLUMN threshold DECIMAL(10, 5) NOT NULL DEFAULT 0.00000;

-- trigger

DELIMITER //

CREATE TRIGGER add_stock_to_portfolio
AFTER INSERT ON stock_transactions
FOR EACH ROW
BEGIN
    DECLARE existing_count INT;

    SELECT COUNT(*) INTO existing_count 
    FROM portfolio
    WHERE user_id = NEW.user_id AND stock_symbol = NEW.stock_symbol;

    IF existing_count = 0 THEN
        INSERT INTO portfolio (user_id, stock_symbol)
        VALUES (NEW.user_id, NEW.stock_symbol);
    END IF;
END //

DELIMITER ;

-- stored procedures

DELIMITER $$
CREATE PROCEDURE update_current_prices(
    IN p_user_id INT,                    
    IN p_stock_symbol VARCHAR(30),       
    IN p_new_price DECIMAL(10,2)         
)
BEGIN
    UPDATE portfolio
    SET current_price = p_new_price
    WHERE user_id = p_user_id           
    AND stock_symbol = p_stock_symbol;  
END $$
DELIMITER ;


DELIMITER $$

CREATE PROCEDURE insert_anomaly(
    IN p_stock_symbol VARCHAR(10),
    IN p_anomaly_type VARCHAR(10),
    IN p_anomaly_date DATE
)
BEGIN
    INSERT INTO Anomaly (StockSymbol, AnomalyType, AnomalyDate)
    VALUES (p_stock_symbol, p_anomaly_type, p_anomaly_date);
END $$

DELIMITER ;

-- aggregated query

SELECT stock_symbol,
SUM(CASE WHEN purchase_type = 'BUY' THEN quantity ELSE -quantity END) AS total_quantity,
AVG(CASE WHEN purchase_type = 'BUY' THEN price END) AS avg_buy_price,
AVG(CASE WHEN purchase_type = 'SELL' THEN price END) AS avg_sell_price
FROM stock_transactions
WHERE user_id = 2
GROUP BY stock_symbol;

-- nested query

SELECT stock_symbol, trade_count
FROM (
		SELECT stock_symbol, COUNT(*) AS trade_count
		FROM stock_transactions
		WHERE user_id = 2
		GROUP BY stock_symbol
	) 
AS stock_trades
WHERE trade_count >= 1
ORDER BY trade_count DESC
LIMIT 3;

-- join query

SELECT p.stock_symbol, p.threshold, a.anomalytype, a.anomalydate
FROM portfolio p
JOIN Anomaly a ON p.stock_symbol = a.stocksymbol
WHERE p.user_id = 2;

-- insert queries

INSERT INTO stock_transactions 
(user_id, purchase_type, price, quantity, stock_symbol, transaction_date) 
VALUES (2,"BUY", 250.50, 20, "IBM", "2024-10-24");

INSERT INTO portfolio 
(user_id, stock_symbol, threshold) 
VALUES (2, "IBM", 0.5);

-- update queries

UPDATE stock_transactions 
SET purchase_type = "SELL", price = 200.50, quantity = 20, transaction_date = "2024-12-11"
WHERE transaction_id = 120 AND user_id = 2;

UPDATE portfolio 
SET threshold = 1.5 
WHERE user_id = 2 AND stock_symbol = "IBM";

-- delete queries

DELETE FROM portfolio 
WHERE user_id = 2 AND stock_symbol = "IBM";

DELETE FROM stock_transactions 
WHERE user_id = 2 AND stock_symbol = "IBM";

-- select queries

SELECT stock_symbol FROM portfolio WHERE user_id = 2;

SELECT transaction_id, purchase_type, price, quantity, transaction_date 
FROM stock_transactions 
WHERE user_id = 2 AND stock_symbol = "IBM";

SELECT COUNT(*) FROM portfolio 
WHERE user_id = 2 AND stock_symbol = "IBM";

SELECT stock_symbol, threshold, current_price FROM portfolio WHERE user_id = 2;

-- create user and grant

CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';

GRANT SELECT,INSERT, UPDATE, DELETE, TRIGGER, EXECUTE ON dbms_project.* TO 'username'@'localhost';



