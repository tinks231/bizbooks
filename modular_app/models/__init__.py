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
from .vendor import Vendor
from .invoice import Invoice, InvoiceItem
from .task import Task, TaskUpdate, TaskMaterial, TaskMedia
# Temporarily disabled until quotations module is fully implemented
# from .quotation import Quotation, QuotationItem
from .sales_order import SalesOrder
from .sales_order_item import SalesOrderItem
from .delivery_challan import DeliveryChallan
from .delivery_challan_item import DeliveryChallanItem
from .purchase_bill import PurchaseBill
from .purchase_bill_item import PurchaseBillItem
from .vendor_payment import VendorPayment, PaymentAllocation
from .commission_agent import CommissionAgent, InvoiceCommission
from .subscription import (
    SubscriptionPlan,
    CustomerSubscription,
    SubscriptionPayment,
    SubscriptionDelivery,
    DeliveryDayNote
)
from .customer_order import CustomerOrder, CustomerOrderItem
from .bank_account import BankAccount, AccountTransaction
from .loyalty_program import LoyaltyProgram
from .customer_loyalty_points import CustomerLoyaltyPoints
from .loyalty_transaction import LoyaltyTransaction
from .return_model import Return
from .return_item import ReturnItem
from .item_attribute import ItemAttribute, ItemAttributeValue, TenantAttributeConfig

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
    'Customer', 'Vendor', 'Party',
    'Invoice', 'InvoiceItem',
    'Task', 'TaskUpdate', 'TaskMaterial', 'TaskMedia',
    # 'Quotation', 'QuotationItem',  # Temporarily disabled
    'SalesOrder', 'SalesOrderItem',
    'DeliveryChallan', 'DeliveryChallanItem',
    'PurchaseBill', 'PurchaseBillItem',
    'VendorPayment', 'PaymentAllocation',
    'CommissionAgent', 'InvoiceCommission',
    'SubscriptionPlan', 'CustomerSubscription', 'SubscriptionPayment', 'SubscriptionDelivery', 'DeliveryDayNote',
    'CustomerOrder', 'CustomerOrderItem',
    'BankAccount', 'AccountTransaction',
    'LoyaltyProgram', 'CustomerLoyaltyPoints', 'LoyaltyTransaction',
    'Return', 'ReturnItem',
    'ItemAttribute', 'ItemAttributeValue', 'TenantAttributeConfig'
]

