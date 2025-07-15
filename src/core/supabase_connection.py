from supabase import create_client, Client
from typing import Dict, List, Any, Optional
import logging
import os
from .config import configs
# from dotenv import load_dotenv

# load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseConnection:
    """Manages connection and operations with Supabase database."""
    
    def __init__(self, table_name: Optional[str] = None):
        self.config = {
            "url": configs.supabase_url,
            "key": configs.supabase_key
        }
        self.table_name: str = table_name
    
        """Initialize connection to Supabase."""
        try:
            self.client : Client = create_client(
                self.config["url"],
                self.config["key"]
            )
            logger.info("Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
        
    def connect(self, table_name: Optional[str] = None):
        """Reconnect to Supabase if needed."""
        try:
            self.client = create_client(
                self.config["url"],
                self.config["key"]
            )
            if table_name:
                self.table_name = table_name
            logger.info("Reconnected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to reconnect to Supabase: {e}")
            raise
    
    def get_max_id(self, id_column: str = 'id') -> int:
        logger.info("[SupabaseDB] getting max id")
        """Get the maximum value of the specified ID column."""
        # Order by `id` descending and get the first row
        response = (
            self.client.table(self.table_name)
            .select(id_column)
            .order(id_column, desc=True)
            .limit(1)
            .execute()
        )
        print(response.data)
        if response.data and len(response.data) > 0:
            return int(response.data[0][id_column])
        else:
            raise ValueError("No data found in the table.")
        
    def get_count_rows(self) -> int:
        logger.info("[SupabaseDB] getting count of rows")
        """Get the total number of rows in the table."""
        response = self.client.table(self.table_name).select("count").execute()
        if response.data and len(response.data) > 0:
            return int(response.data[0]['count'])
        else:
            return 0
        
    def insert(self, row: dict):
        logger.info(f"[SupabaseDB] inserting a single row: {row}")
        """Insert a single row."""
        return self.client.table(self.table_name).insert(row).execute()

    def insert_many(self, rows: list[dict]):
        logger.info(f"[SupabaseDB] inserting multiple rows ({len(rows)} data)")
        """Insert multiple rows."""
        return self.client.table(self.table_name).insert(rows).execute()

    def upsert(self, rows: list[dict], conflict_columns: list[str]):
        logger.info(f"[SupabaseDB] upserting multiple rows ({len(rows)} data)")
        """Upsert rows using given conflict columns (must be unique/indexed)."""
        return self.client.table(self.table_name).upsert(rows, on_conflict=conflict_columns).execute()

    def select_all(self, batch_size=1000):
        logger.info(f"[SupabaseDB] select all")
        """Select all rows with optional batching."""
        all_rows = []
        offset = 0

        while True:
            res = self.client.table(self.table_name).select("*").range(offset, offset + batch_size - 1).execute()
            batch = res.data or []
            if not batch:
                break
            all_rows.extend(batch)
            offset += batch_size

        return all_rows

    def select_where(self, conditions: dict, limit: int = None):
        logger.info(f"[SupabaseDB] select where {conditions}")
        """Select rows based on conditions (e.g., {'sku': 'abc'})."""
        query = self.client.table(self.table_name).select("*")
        for col, val in conditions.items():
            query = query.eq(col, val)
        if limit:
            query = query.limit(limit)
        return query.execute().data
    
    def select_like(self, conditions: dict, limit: int = None):
        logger.info(f"[SupabaseDB] select like {conditions}")
        # """Select rows based on conditions with LIKE (e.g., {'sku': 'abc%'}). lowercase."""
        conditions = {k: v.lower() for k, v in conditions.items()}
        query = self.client.table(self.table_name).select("*")
        for col, val in conditions.items():
            query = query.ilike(col, val)
        if limit:
            query = query.limit(limit)
        return query.execute().data
    
    def select_with_limit(self, limit: int = 1000):
        logger.info(f"[SupabaseDB] select with limit {limit}")
        """Select rows with a limit."""
        query = self.client.table(self.table_name).select("*").limit(limit)
        return query.execute().data

    def select_columns_with_conditions_and_batch(self, columns: List[str], batch_size: int = 1000, conditions: Optional[Dict[str, Any]] = None):
        logger.info(f"[SupabaseDB] select all")
        """Select all rows with optional batching."""
        all_rows = []
        offset = 0

        while True:
            res = self.client.table(self.table_name).select(', '.join(columns)).range(offset, offset + batch_size - 1).execute()
            batch = res.data or []
            if not batch:
                break
            all_rows.extend(batch)
            offset += batch_size

        return all_rows
    
    def delete_where(self, conditions: dict):
        logger.info(f"[SupabaseDB] delete where {conditions}")
        """Delete rows based on conditions."""
        query = self.client.table(self.table_name).delete()
        for col, val in conditions.items():
            query = query.eq(col, val)
        return query.execute()

    def update_where(self, conditions: dict, new_values: dict):
        logger.info(f"[SupabaseDB] update where {conditions}")
        """Update specific rows matching conditions with new values."""
        query = self.client.table(self.table_name).update(new_values)
        for col, val in conditions.items():
            query = query.eq(col, val)
        return query.execute()

# Global instance
supabase_db = SupabaseConnection()
supabase_products = SupabaseConnection(table_name="master_products")
supabase_cart = SupabaseConnection(table_name="cart")
supabase_orders = SupabaseConnection(table_name="orders")
supabase_orders_details = SupabaseConnection(table_name="order_details")
supabase_payments = SupabaseConnection(table_name="payments")