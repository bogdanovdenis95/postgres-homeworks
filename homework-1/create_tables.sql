-- SQL-команды для создания таблиц
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_name TEXT NOT NULL
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    title TEXT,
    birth_date DATE,
    notes TEXT
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    employee_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    ship_city TEXT NOT NULL,
    CONSTRAINT orders_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);