DROP TABLE IF EXISTS pending_orders CASCADE;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS users CASCADE ;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS transaction_his CASCADE;
DROP TABLE IF EXISTS user_portfolio CASCADE;
DROP TABLE IF EXISTS market_hour CASCADE;

DROP TRIGGER IF EXISTS user_data on users;

CREATE TABLE stocks (
    id SERIAL,
    symbol VARCHAR NOT NULL UNIQUE ,
    stock_name VARCHAR NOT NULL ,
    day_high FLOAT DEFAULT 0.0,
    day_low FLOAT DEFAULT 0.0,
    prev_curr_price FLOAT DEFAULT -1,
    curr_price FLOAT DEFAULT 0.0,
    open_price FLOAT DEFAULT 0.0,
    close_price FLOAT DEFAULT 0.0,
    volume INTEGER DEFAULT 0,
    mark_cap INTEGER DEFAULT 0,
    PRIMARY KEY(id)
);

CREATE TABLE users (
    id SERIAL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    PRIMARY KEY(id)

);

CREATE TABLE admin_users (
    id SERIAL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    PRIMARY KEY(id)

);

CREATE TABLE transaction_his (
    order_id SERIAL,
    stock_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    trans_type VARCHAR NOT NULL,
    order_type VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL ,
    PRIMARY KEY(order_id),
    CONSTRAINT user_det
      FOREIGN KEY(user_id)
	  REFERENCES users(id)
      ON DELETE CASCADE

);

CREATE TABLE user_portfolio (
    user_id SERIAL NOT NULL,
    funds FLOAT DEFAULT 0.0,
    invested_value FLOAT DEFAULT 0.0,
    CONSTRAINT user_det
      FOREIGN KEY(user_id)
	  REFERENCES users(id)
      ON DELETE CASCADE

);

CREATE TABLE pending_orders (
    order_id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    trans_type VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    order_type VARCHAR NOT NULL ,
    limit_price FLOAT NOT NULL ,
    triggered BOOL DEFAULT FALSE,
    expiry_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT stock_det
      FOREIGN KEY(stock_id)
	  REFERENCES stocks(id),
	CONSTRAINT user_det
      FOREIGN KEY(user_id)
	  REFERENCES users(id)
);

CREATE TABLE market_hour (
  day_name VARCHAR NOT NULL UNIQUE ,  
  from_time TIME NOT NULL,
  to_time TIME NOT NULL 
);

-- Creating Triggers
CREATE OR REPLACE FUNCTION init_user() RETURNS TRIGGER AS
$BODY$
BEGIN
    INSERT INTO
        user_portfolio(user_id)
        VALUES(new.id);

           RETURN new;
END;
$BODY$
language plpgsql;

CREATE TRIGGER user_data AFTER INSERT
    ON users
    FOR EACH ROW
    EXECUTE PROCEDURE init_user();

-- Initialize Market Hours
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Monday','15:00:00', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Tuesday','15:00:00', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Wednesday','15:00:00', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Thursday','15:00:00', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Friday','15:00:00', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Saturday', '9:00:01', '9:00:00');
INSERT INTO market_hour (day_name, to_time, from_time) VALUES ('Sunday', '9:00:01', '9:00:00');
