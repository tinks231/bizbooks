"""
Stock Batch Service
Business logic for GST-aware batch tracking and allocation
"""
from models import db, StockBatch, Item, InvoiceItem
from sqlalchemy import and_
from datetime import datetime
import pytz
from decimal import Decimal


class StockBatchService:
    """Service for managing stock batches with GST tracking"""
    
    @staticmethod
    def create_batch_from_purchase(purchase_bill_item, purchase_bill):
        """
        Create a stock batch when a purchase bill item is added
        
        Args:
            purchase_bill_item: PurchaseBillItem model instance
            purchase_bill: PurchaseBill model instance
        
        Returns:
            StockBatch instance
        """
        # Calculate GST and ITC if applicable
        gst_per_unit = Decimal('0')
        itc_per_unit = Decimal('0')
        
        if purchase_bill.gst_applicable and purchase_bill_item.gst_rate > 0:
            # Calculate GST per unit
            gst_per_unit = (purchase_bill_item.taxable_value / purchase_bill_item.quantity) * \
                          (purchase_bill_item.gst_rate / 100)
            # ITC is the same as GST paid
            itc_per_unit = gst_per_unit
        
        # Calculate base cost (without GST)
        base_cost = purchase_bill_item.taxable_value / purchase_bill_item.quantity
        total_cost = base_cost + gst_per_unit
        
        # Calculate total ITC for the batch
        itc_total = itc_per_unit * purchase_bill_item.quantity
        
        # Create batch
        batch = StockBatch(
            tenant_id=purchase_bill.tenant_id,
            item_id=purchase_bill_item.item_id,
            purchase_bill_id=purchase_bill.id,
            purchase_bill_item_id=purchase_bill_item.id,
            purchase_bill_number=purchase_bill.bill_number,
            purchase_date=purchase_bill.bill_date,
            vendor_id=purchase_bill.vendor_id,
            vendor_name=purchase_bill.vendor_name,
            site_id=purchase_bill_item.site_id,
            
            # Quantity
            quantity_purchased=purchase_bill_item.quantity,
            quantity_remaining=purchase_bill_item.quantity,
            quantity_sold=Decimal('0'),
            quantity_adjusted=Decimal('0'),
            
            # KEY: GST status
            purchased_with_gst=purchase_bill.gst_applicable,
            
            # Costs
            base_cost_per_unit=base_cost,
            gst_rate=purchase_bill_item.gst_rate if purchase_bill.gst_applicable else Decimal('0'),
            gst_per_unit=gst_per_unit,
            total_cost_per_unit=total_cost,
            
            # ITC
            itc_per_unit=itc_per_unit,
            itc_total_available=itc_total,
            itc_claimed=Decimal('0'),
            itc_remaining=itc_total,
            
            # Batch details
            batch_number=purchase_bill_item.batch_number,
            expiry_date=purchase_bill_item.expiry_date,
            batch_status='active',
            
            # Audit
            notes=f'Created from purchase bill {purchase_bill.bill_number}',
            created_by=purchase_bill.vendor_name
        )
        
        db.session.add(batch)
        return batch
    
    @staticmethod
    def get_available_stock(item_id, tenant_id, require_gst_stock=False):
        """
        Get available stock for an item
        
        Args:
            item_id: Item ID
            tenant_id: Tenant ID
            require_gst_stock: If True, only return GST-purchased stock
        
        Returns:
            dict with stock breakdown
        """
        query = StockBatch.query.filter(
            and_(
                StockBatch.item_id == item_id,
                StockBatch.tenant_id == tenant_id,
                StockBatch.batch_status == 'active',
                StockBatch.quantity_remaining > 0
            )
        )
        
        if require_gst_stock:
            query = query.filter(StockBatch.purchased_with_gst == True)
        
        batches = query.order_by(StockBatch.purchase_date.asc()).all()
        
        total_qty = sum([float(b.quantity_remaining) for b in batches])
        gst_qty = sum([float(b.quantity_remaining) for b in batches if b.purchased_with_gst])
        non_gst_qty = sum([float(b.quantity_remaining) for b in batches if not b.purchased_with_gst])
        
        # 🆕 FALLBACK: If no batches exist, use opening_stock from item master
        # This handles existing inventory added before batch tracking was implemented
        if not batches:
            item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
            if item and item.opening_stock > 0:
                total_qty = float(item.opening_stock)
                
                # User's logic: Use gst_rate to classify existing inventory
                if item.gst_rate > 0:
                    # Taxable item - assume purchased WITH GST (benefit of doubt)
                    gst_qty = total_qty
                    non_gst_qty = 0
                else:
                    # Exempt item (books, vegetables) - no GST applicable
                    gst_qty = 0
                    non_gst_qty = total_qty
        
        return {
            'total_stock': total_qty,
            'gst_stock': gst_qty,
            'non_gst_stock': non_gst_qty,
            'batches': batches,
            'uses_fallback': len(batches) == 0  # Flag to indicate using opening_stock
        }
    
    @staticmethod
    def validate_invoice_item(item_id, quantity, invoice_type, customer, tenant_id):
        """
        Validate if an item can be added to an invoice
        
        Args:
            item_id: Item ID
            quantity: Requested quantity
            invoice_type: 'taxable', 'non_taxable', or 'credit_adjustment'
            customer: Customer model instance
            tenant_id: Tenant ID
        
        Returns:
            dict with status and message
        """
        # Get item to check GST rate
        item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return {
                'status': 'error',
                'message': 'Item not found'
            }
        
        # 🆕 USER'S LOGIC: Block GST invoices for exempt items (gst_rate = 0)
        # Examples: Books, Vegetables, Education Services
        if invoice_type in ['taxable', 'credit_adjustment']:
            if item.gst_rate == 0:
                return {
                    'status': 'error',
                    'error_type': 'exempt_item',
                    'message': f'''Cannot create GST invoice for exempt item.
                    
                    Item: {item.name}
                    GST Rate: 0% (Exempt by law)
                    
                    This item is GST-exempt. Only non-taxable invoices are allowed.''',
                    'suggestions': ['non_taxable_invoice_only']
                }
        
        # Get stock information
        stock_info = StockBatchService.get_available_stock(item_id, tenant_id)
        
        # For non-taxable invoices, any stock is fine
        if invoice_type == 'non_taxable':
            if quantity > stock_info['total_stock']:
                return {
                    'status': 'error',
                    'message': f"Insufficient stock. Available: {stock_info['total_stock']} units"
                }
            return {'status': 'ok'}
        
        # 🆕 USER'S LOGIC: For taxable invoices, MUST have GST stock
        # "No GST purchase = No GST sale" - PERIOD!
        if invoice_type in ['taxable', 'credit_adjustment']:
            if quantity > stock_info['gst_stock']:
                # Check customer type for better messaging
                customer_type = getattr(customer, 'gst_registration_type', 'unregistered')
                
                return {
                    'status': 'error',
                    'error_type': 'insufficient_gst_stock',
                    'message': f'''Cannot create GST invoice - insufficient GST stock.
                    
                    Requested: {quantity} units
                    GST Stock Available: {stock_info['gst_stock']} units
                    Non-GST Stock: {stock_info['non_gst_stock']} units
                    
                    ⚠️ Items purchased WITHOUT GST cannot be sold WITH GST invoice.
                    
                    Options:
                    1. Reduce quantity to {stock_info['gst_stock']} units (GST stock available)
                    2. Create non-GST invoice (kaccha bill) for this sale
                    3. Later create Credit Adjustment invoice for compliance (if needed)''',
                    'available_gst_stock': stock_info['gst_stock'],
                    'available_non_gst_stock': stock_info['non_gst_stock'],
                    'suggestions': ['reduce_quantity', 'non_taxable_invoice', 'credit_adjustment_route']
                }
            
            return {'status': 'ok'}
        
        return {'status': 'ok'}
    
    @staticmethod
    def allocate_stock_for_invoice_item(item_id, quantity, invoice_type, tenant_id):
        """
        Allocate stock batches for an invoice item (FIFO)
        
        Args:
            item_id: Item ID
            quantity: Quantity to allocate
            invoice_type: Invoice type
            tenant_id: Tenant ID
        
        Returns:
            dict with allocation details or error
        """
        # Get available batches
        query = StockBatch.query.filter(
            and_(
                StockBatch.item_id == item_id,
                StockBatch.tenant_id == tenant_id,
                StockBatch.batch_status == 'active',
                StockBatch.quantity_remaining > 0
            )
        ).order_by(StockBatch.purchase_date.asc())
        
        # Filter by GST status if needed
        if invoice_type in ['taxable', 'credit_adjustment']:
            # For taxable/credit adjustment: only use GST stock
            available_batches = query.filter(StockBatch.purchased_with_gst == True).all()
        elif invoice_type == 'non_taxable':
            # Prefer non-GST batches first (save GST stock for taxable sales)
            # First get non-GST batches, then GST batches
            non_gst_batches = StockBatch.query.filter(
                and_(
                    StockBatch.item_id == item_id,
                    StockBatch.tenant_id == tenant_id,
                    StockBatch.batch_status == 'active',
                    StockBatch.quantity_remaining > 0,
                    StockBatch.purchased_with_gst == False
                )
            ).order_by(StockBatch.purchase_date.asc()).all()
            
            gst_batches = StockBatch.query.filter(
                and_(
                    StockBatch.item_id == item_id,
                    StockBatch.tenant_id == tenant_id,
                    StockBatch.batch_status == 'active',
                    StockBatch.quantity_remaining > 0,
                    StockBatch.purchased_with_gst == True
                )
            ).order_by(StockBatch.purchase_date.asc()).all()
            
            available_batches = non_gst_batches + gst_batches
        else:
            # Default: get all batches
            available_batches = query.all()
        
        # Allocate from batches (FIFO)
        allocated = []
        remaining_qty = Decimal(str(quantity))
        
        for batch in available_batches:
            if remaining_qty <= 0:
                break
            
            allocated_from_batch = min(batch.quantity_remaining, remaining_qty)
            
            allocated.append({
                'batch_id': batch.id,
                'batch': batch,
                'quantity': float(allocated_from_batch),
                'cost_per_unit': float(batch.base_cost_per_unit),
                'itc_per_unit': float(batch.itc_per_unit) if batch.purchased_with_gst else 0,
                'has_gst_backing': batch.purchased_with_gst
            })
            
            remaining_qty -= allocated_from_batch
        
        # 🆕 FALLBACK: If no batches allocated, use opening_stock
        if not allocated:
            # Get item to check opening_stock
            item = Item.query.filter_by(id=item_id, tenant_id=tenant_id).first()
            if item and item.opening_stock >= quantity:
                # Use opening_stock as fallback (for legacy inventory)
                # Determine if this stock has GST backing based on item.gst_rate
                has_gst_backing = item.gst_rate > 0
                
                allocated.append({
                    'batch_id': None,  # No batch (using opening_stock)
                    'batch': None,
                    'quantity': float(quantity),
                    'cost_per_unit': float(item.cost_price) if item.cost_price else 0,
                    'itc_per_unit': 0,  # No ITC for opening stock
                    'has_gst_backing': has_gst_backing,
                    'uses_opening_stock': True  # Flag for special handling
                })
                remaining_qty = Decimal('0')
        
        if remaining_qty > 0:
            return {
                'status': 'error',
                'message': f'Insufficient stock. Still need {float(remaining_qty)} units.'
            }
        
        return {
            'status': 'success',
            'allocated': allocated,
            'uses_fallback': any(a.get('uses_opening_stock') for a in allocated)
        }
    
    @staticmethod
    def process_invoice_item_allocation(invoice_item, allocated_batches, reduce_stock=True):
        """
        Process the allocation of batches to an invoice item
        
        Args:
            invoice_item: InvoiceItem instance
            allocated_batches: List of allocation dicts from allocate_stock_for_invoice_item
            reduce_stock: If False, don't reduce stock (for credit_adjustment)
        
        Returns:
            dict with allocation summary
        """
        total_cost = Decimal('0')
        total_itc = Decimal('0')
        uses_fallback = False
        
        for alloc in allocated_batches:
            batch = alloc['batch']
            qty = Decimal(str(alloc['quantity']))
            
            # 🆕 FALLBACK HANDLING: Check if using opening_stock instead of batch
            if alloc.get('uses_opening_stock'):
                uses_fallback = True
                # Get item and reduce opening_stock
                item = Item.query.get(invoice_item.item_id)
                if item and reduce_stock:
                    # Convert Decimal to float for compatibility with database column type
                    item.opening_stock = float(item.opening_stock) - float(qty)
                    print(f"✅ Reduced opening_stock for item {item.id} by {float(qty)}. New: {item.opening_stock}")
                
                # Calculate costs from alloc (no batch object)
                cost_for_qty = Decimal(str(alloc['cost_per_unit'])) * qty
                itc_for_qty = Decimal('0')  # No ITC for opening stock
                
                total_cost += cost_for_qty
                total_itc += itc_for_qty
                continue
            
            # Normal batch processing
            if batch:
                # Calculate costs
                cost_for_qty = batch.base_cost_per_unit * qty
                itc_for_qty = batch.itc_per_unit * qty if batch.purchased_with_gst else Decimal('0')
                
                total_cost += cost_for_qty
                total_itc += itc_for_qty
                
                if reduce_stock:
                    # Reduce batch quantity and claim ITC
                    batch.allocate_quantity(qty)
        
        # Update invoice item with cost tracking
        if invoice_item.quantity > 0:
            invoice_item.cost_base = total_cost / Decimal(str(invoice_item.quantity))
            invoice_item.cost_gst_paid = total_itc / Decimal(str(invoice_item.quantity))
        
        # Link to primary batch (first one) - only if not using fallback
        if allocated_batches and not uses_fallback:
            invoice_item.stock_batch_id = allocated_batches[0]['batch_id']
            invoice_item.uses_gst_stock = allocated_batches[0]['has_gst_backing']
        elif uses_fallback:
            # Flag that this used opening_stock, not batches
            invoice_item.stock_batch_id = None
            invoice_item.uses_gst_stock = allocated_batches[0]['has_gst_backing'] if allocated_batches else False
        
        return {
            'total_cost': float(total_cost),
            'total_itc_available': float(total_itc),
            'batches_used': len(allocated_batches),
            'uses_fallback': uses_fallback
        }
    
    @staticmethod
    def return_stock_from_invoice_item(invoice_item):
        """
        Return stock back to batches (for returns/cancellations)
        
        Args:
            invoice_item: InvoiceItem instance
        """
        # Find the batch(es) that were used
        # For simplicity, return to the primary batch
        if invoice_item.stock_batch_id:
            batch = StockBatch.query.get(invoice_item.stock_batch_id)
            if batch:
                batch.return_quantity(Decimal(str(invoice_item.quantity)))
    
    @staticmethod
    def get_stock_summary_for_product(item_id, tenant_id):
        """
        Get a detailed stock summary for a product
        
        Args:
            item_id: Item ID
            tenant_id: Tenant ID
        
        Returns:
            dict with comprehensive stock info
        """
        stock_info = StockBatchService.get_available_stock(item_id, tenant_id)
        
        # Get batch history
        all_batches = StockBatch.query.filter(
            and_(
                StockBatch.item_id == item_id,
                StockBatch.tenant_id == tenant_id
            )
        ).order_by(StockBatch.purchase_date.desc()).all()
        
        # Calculate values
        total_value_gst = sum([
            float(b.quantity_remaining * b.base_cost_per_unit)
            for b in all_batches
            if b.purchased_with_gst and b.batch_status == 'active'
        ])
        
        total_value_non_gst = sum([
            float(b.quantity_remaining * b.base_cost_per_unit)
            for b in all_batches
            if not b.purchased_with_gst and b.batch_status == 'active'
        ])
        
        total_itc_available = sum([
            float(b.itc_remaining)
            for b in all_batches
            if b.purchased_with_gst and b.batch_status == 'active'
        ])
        
        return {
            'total_stock': stock_info['total_stock'],
            'gst_stock': stock_info['gst_stock'],
            'non_gst_stock': stock_info['non_gst_stock'],
            'total_value_gst_stock': total_value_gst,
            'total_value_non_gst_stock': total_value_non_gst,
            'total_value': total_value_gst + total_value_non_gst,
            'total_itc_available': total_itc_available,
            'active_batches': len([b for b in all_batches if b.batch_status == 'active']),
            'total_batches': len(all_batches),
            'batches': all_batches
        }

