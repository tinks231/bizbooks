"""
Database models package
"""
from .database import db, init_db
from .tenant import Tenant
from .user import User
from .employee import Employee
from .site import Site
from .attendance import Attendance
from .inventory import Material, Stock, StockMovement, Transfer
from .item import (
    Item, ItemCategory, ItemGroup, ItemImage, ItemStock, 
    ItemStockMovement, InventoryAdjustment, InventoryAdjustmentLine
)
from .expense import Expense, ExpenseCategory
from .purchase_request import PurchaseRequest
from .customer import Customer
from .invoice import Invoice, InvoiceItem
from .task import Task, TaskUpdate, TaskMaterial, TaskMedia
# Temporarily disabled until quotations module is fully implemented
# from .quotation import Quotation, QuotationItem
from .sales_order import SalesOrder
from .sales_order_item import SalesOrderItem
from .delivery_challan import DeliveryChallan
from .delivery_challan_item import DeliveryChallanItem

# Create Party alias for Customer (for unified party management)
Party = Customer

__all__ = [
    'db', 'init_db',
    'Tenant', 'User', 'Employee', 'Site', 'Attendance',
    'Material', 'Stock', 'StockMovement', 'Transfer',
    'Item', 'ItemCategory', 'ItemGroup', 'ItemImage', 'ItemStock',
    'ItemStockMovement', 'InventoryAdjustment', 'InventoryAdjustmentLine',
    'Expense', 'ExpenseCategory',
    'PurchaseRequest',
    'Customer', 'Party',
    'Invoice', 'InvoiceItem',
    'Task', 'TaskUpdate', 'TaskMaterial', 'TaskMedia',
    # 'Quotation', 'QuotationItem',  # Temporarily disabled
    'SalesOrder', 'SalesOrderItem',
    'DeliveryChallan', 'DeliveryChallanItem'
]

