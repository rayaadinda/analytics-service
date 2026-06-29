import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://kji_user:kji_password@localhost:5433/kji_db?schema=public"

# SQLAlchemy doesn't support the schema query parameter in the connection string like Prisma does
CLEAN_DATABASE_URL = DATABASE_URL.split("?")[0]

engine = create_engine(CLEAN_DATABASE_URL)

def fetch_aggregated_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    # Postgres timestamp without time zone doesn't like tz-aware datetimes
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)
    
    query = text("""
        SELECT 
            i.id as inventory_id,
            i."partNumber" as part_number,
            i."partName" as part_name,
            COUNT(ci.id) as jumlah_transaksi,
            SUM(ci.quantity) as total_qty,
            COUNT(DISTINCT c."workOrder") as jumlah_wo,
            COUNT(DISTINCT c."checkoutDate") as frekuensi_hari
        FROM "Inventory" i
        JOIN "CheckoutItem" ci ON ci."inventoryId" = i.id
        JOIN "Checkout" c ON c.id = ci."checkoutId"
        WHERE c."checkoutDate" >= :start_date AND c."checkoutDate" <= :end_date
        GROUP BY i.id, i."partNumber", i."partName"
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"start_date": start_date, "end_date": end_date})
    
    if len(df) > 0:
        df['rata_rata_qty'] = df['total_qty'] / df['jumlah_transaksi']
    else:
        df['rata_rata_qty'] = []
        
    return df
