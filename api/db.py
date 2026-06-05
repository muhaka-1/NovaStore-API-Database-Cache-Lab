import os
from decimal import Decimal
import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "novastore"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )


def _convert_product(row):
    if row is None:
        return None
    product = dict(row)
    if isinstance(product.get("price"), Decimal):
        product["price"] = float(product["price"])
    if product.get("created_at") is not None:
        product["created_at"] = product["created_at"].isoformat()
    return product


def get_all_products_from_db():
    query = """
        SELECT id, name, price, category, stock, created_at
        FROM products
        ORDER BY id;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return [_convert_product(row) for row in rows]


def get_product_by_id_from_db(product_id):
    # ✅ TODO Uppgift 5 - Query by id, return dict or None
    query = """
        SELECT id, name, price, category, stock, created_at
        FROM products
        WHERE id = %s;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (product_id,))
            row = cur.fetchone()
    return _convert_product(row)


def insert_product_into_db(product):
    # ✅ TODO Uppgift 8 - INSERT and return the created row
    query = """
        INSERT INTO products (name, price, category, stock)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, price, category, stock, created_at;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (
                product["name"],
                product["price"],
                product.get("category"),
                product.get("stock", 0),
            ))
            row = cur.fetchone()
        conn.commit()
    return _convert_product(row)