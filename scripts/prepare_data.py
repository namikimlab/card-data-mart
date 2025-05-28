import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "dbt_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "***REMOVED***")
PG_DATABASE = os.getenv("PG_DATABASE", "retail")

def load_excel_to_postgres():
    df = pd.read_excel("data/raw/online_retail.xlsx")

    df = df.dropna(subset=["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "UnitPrice"])

    # 열 이름 소문자 + 언더스코어 처리
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # 컬럼명 재정의: 카드 거래 형태
    df = df.rename(columns={
        "invoice_no": "transaction_id",
        "customer_id": "cardholder_id",
        "unit_price": "amount",
        "invoice_date": "transaction_date"
    })

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS card_transactions;")
    cursor.execute("""
        CREATE TABLE card_transactions (
            transaction_id TEXT,
            stock_code TEXT,
            description TEXT,
            quantity INTEGER,
            transaction_date TIMESTAMP,
            amount FLOAT,
            cardholder_id TEXT,
            country TEXT
        );
    """)

    tuples = [tuple(x) for x in df.to_numpy()]
    insert_query = """
        INSERT INTO card_transactions (
            transaction_id, stock_code, description, quantity,
            transaction_date, amount, cardholder_id, country
        ) VALUES %s;
    """
    execute_values(cursor, insert_query, tuples)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data loaded to PostgreSQL!")

if __name__ == "__main__":
    load_excel_to_postgres()
