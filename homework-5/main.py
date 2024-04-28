import json
import psycopg2

from config import config

def main():
    script_file = 'fill_db.sql'
    json_file = 'suppliers.json'
    db_name = 'my_new_db'

    params = config()
    conn = None

    create_database(params, db_name)
    print(f"БД {db_name} успешно создана")

    # Обновить параметры подключения с новым именем базы данных
    params.update({'dbname': db_name})

    try:
        # Подключиться к новой базе данных
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                execute_sql_script(cur, script_file)
                print(f"БД {db_name} успешно заполнена")

                create_suppliers_table(cur)
                print("Таблица suppliers успешно создана")

                create_supplier_products_table(cur)
                print("Таблица supplier_products успешно создана")

                suppliers = get_suppliers_data(json_file)
                insert_suppliers_data(cur, suppliers)
                print("Данные в suppliers и supplier_products успешно добавлены")

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def create_database(params, db_name) -> None:
    """Создает новую базу данных."""
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute("COMMIT;")
            cur.execute(f"CREATE DATABASE {db_name};")

def execute_sql_script(cur, script_file) -> None:
    """Выполняет скрипт из файла для заполнения БД данными."""
    with open(script_file, 'r') as file:
        sql_script = file.read()
        cur.execute(sql_script)

def create_suppliers_table(cur) -> None:
    """Создает таблицу suppliers."""
    cur.execute("""
        CREATE TABLE suppliers (
            supplier_id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            contact VARCHAR(255),
            address VARCHAR(255),
            phone VARCHAR(20),
            fax VARCHAR(20),
            homepage VARCHAR(255)
        );
    """)

def create_supplier_products_table(cur) -> None:
    """Создает промежуточную таблицу supplier_products."""
    cur.execute("""
        CREATE TABLE supplier_products (
            supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
            product_id_ref INTEGER NOT NULL REFERENCES products(product_id),
            PRIMARY KEY (supplier_id, product_id_ref)
        );
    """)

def get_suppliers_data(json_file: str) -> list[dict]:
    """Извлекает данные о поставщиках из JSON-файла и возвращает список словарей с соответствующей информацией."""
    with open(json_file, 'r') as file:
        return json.load(file)

def insert_suppliers_data(cur, suppliers: list[dict]) -> None:
    """Добавляет данные из suppliers в таблицу suppliers и промежуточную таблицу supplier_products."""
    for supplier in suppliers:
        # Добавить поставщика в таблицу suppliers
        cur.execute("""
            INSERT INTO suppliers (company_name, contact, address, phone, fax, homepage)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING supplier_id;
        """, (supplier['company_name'], supplier['contact'], supplier['address'], supplier['phone'], supplier['fax'], supplier['homepage']))
        supplier_id = cur.fetchone()[0]

        # Добавить все продукты поставщика в промежуточную таблицу supplier_products
        for product in supplier['products']:
            cur.execute("""
                SELECT product_id FROM products WHERE product_name = %s;
            """, (product,))
            result = cur.fetchone()
            if result is not None:
                product_id_ref = result[0]
                cur.execute("""
                    INSERT INTO supplier_products (supplier_id, product_id_ref) VALUES (%s, %s);
                """, (supplier_id, product_id_ref))
            else:
                print(f"Продукт {product} не найден в таблице products")

if __name__ == '__main__':
    main()
