import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- PostgreSQL connection settings from environment variables ---
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")
EXCEL_FILE_PATH = "/opt/airflow/data/raw/online_retail.xlsx"

# --- Validate required environment variables ---
required_vars = {
    "PG_HOST": PG_HOST,
    "PG_PORT": PG_PORT,
    "PG_USER": PG_USER,
    "PG_PASSWORD": PG_PASSWORD,
    "PG_DATABASE": PG_DATABASE
}
missing = [k for k, v in required_vars.items() if not v]
if missing:
    raise EnvironmentError(f"❌ Missing required environment variables: {', '.join(missing)}")

def load_excel_to_postgres():
    # Load Excel file
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
    except Exception as e:
        raise FileNotFoundError(f"❌ Failed to load Excel file at {EXCEL_FILE_PATH}: {e}")

    # Drop rows with missing values in essential columns
    df = df.dropna(subset=["InvoiceNo", "StockCode", "Quantity", "InvoiceDate", "UnitPrice"])

    # Standardize column names: lowercase + underscores
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Rename columns to simulate a card transaction dataset
    df = df.rename(columns={
        "invoice_no": "transaction_id",
        "customer_id": "cardholder_id",
        "unit_price": "amount",
        "invoice_date": "transaction_date"
    })

    # Connect to PostgreSQL and upload data
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE
        )
        cursor = conn.cursor()

        # Create table if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_transactions (
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

        # Truncate if existing data
        cursor.execute("TRUNCATE TABLE card_transactions;")

        # Insert all rows from the DataFrame into the database
        tuples = [tuple(x) for x in df.to_numpy()]
        insert_query = """
            INSERT INTO card_transactions (
                transaction_id, stock_code, description, quantity,
                transaction_date, amount, cardholder_id, country
            ) VALUES %s;
        """
        execute_values(cursor, insert_query, tuples)

        conn.commit()
        print("✅ Data loaded to PostgreSQL!")

    except Exception as e:
        raise RuntimeError(f"❌ Failed to load data to PostgreSQL: {e}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Entry point
if __name__ == "__main__":
    load_excel_to_postgres()
