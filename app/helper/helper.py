from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
import json

def row_to_dict(row):
    """Convert SQLAlchemy row to JSON-serializable dictionary while maintaining types"""
    d = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        
        # Handle None values
        if value is None:
            d[column.name] = None
        # Handle datetime objects
        elif isinstance(value, datetime):
            d[column.name] = value.isoformat()  # ISO format maintains timezone info
        # Handle date objects
        elif isinstance(value, date):
            d[column.name] = value.isoformat()
        # Handle Decimal (common for monetary values)
        elif isinstance(value, Decimal):
            d[column.name] = float(value)
        # Handle UUID
        elif isinstance(value, UUID):
            d[column.name] = str(value)
        # Handle other types that are already JSON serializable
        else:
            d[column.name] = value
    
    return d

def rows_to_dict_list(rows):
    """Convert list of SQLAlchemy rows to list of JSON-serializable dictionaries"""
    return [row_to_dict(row) for row in rows]

