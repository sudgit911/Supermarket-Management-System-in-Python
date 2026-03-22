"""
业务逻辑服务模块
实现核心业务逻辑，包括采购入库、库存更新、销售处理等
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import uuid

from models import Product, Supplier, Inventory, PurchaseOrder, SaleRecord
from data_manager import ProductManager, SupplierManager, InventoryManager, PurchaseManager, SalesManager


class ProductService:
    """商品服务"""
    
    def __init__(self, data_dir: str = "data"):
        self.manager = ProductManager(data_dir)
    
    def create_product(self, name: str, category: str, unit: str, 
                       price: float, cost_price: float, description: str = "") -> Product:
        """创建商品"""
        product = Product(
            id=str(uuid.uuid4())[:8],
            name=name,
            category=category,
            unit=unit,
            price=price,
            cost_price=cost_price,
            description=description
        )
        if self.manager.add(product.to_dict()):
            return product
        raise ValueError("商品创建失败")
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """获取所有商品"""
        return self.manager.get_all()
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取商品详情"""
        return self.manager.get_by_id(product_id)
    
    def update_product(self, product_id: str, **kwargs) -> bool:
        """更新商品信息"""
        return self.manager.update(product_id, kwargs)
    
    def delete_product(self, product_id: str) -> bool:
        """删除商品"""
        return self.manager.delete(product_id)
    
    def search_products(self, keyword: str, category: str = None) -> List[Dict[str, Any]]:
        """搜索商品"""
        return self.manager.search(keyword, category)
    
    def get_categories(self) -> List[str]:
        """获取所有商品分类"""
        products = self.manager.get_all()
        categories = set()
        for p in products:
            categories.add(p.get('category', '未分类'))
        return sorted(list(categories))


class SupplierService:
    """供应商服务"""
    
    def __init__(self, data_dir: str = "data"):
        self.manager = SupplierManager(data_dir)
    
    def create_supplier(self, name: str, contact: str, phone: str, 
                        email: str, address: str) -> Supplier:
        """创建供应商"""
        supplier = Supplier(
            id=str(uuid.uuid4())[:8],
            name=name,
            contact=contact,
            phone=phone,
            email=email,
            address=address
        )
        if self.manager.add(supplier.to_dict()):
            return supplier
        raise ValueError("供应商创建失败")
    
    def get_all_suppliers(self) -> List[Dict[str, Any]]:
        """获取所有供应商"""
        return self.manager.get_all()
    
    def get_active_suppliers(self) -> List[Dict[str, Any]]:
        """获取活跃供应商"""
        return self.manager.get_active_suppliers()
    
    def get_supplier(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """获取供应商详情"""
        return self.manager.get_by_id(supplier_id)
    
    def update_supplier(self, supplier_id: str, **kwargs) -> bool:
        """更新供应商信息"""
        return self.manager.update(supplier_id, kwargs)
    
    def delete_supplier(self, supplier_id: str) -> bool:
        """删除供应商"""
        return self.manager.delete(supplier_id)
    
    def search_suppliers(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索供应商"""
        return self.manager.search(keyword)
    
    def set_supplier_status(self, supplier_id: str, status: str) -> bool:
        """设置供应商状态"""
        return self.manager.update(supplier_id, {'status': status})


class InventoryService:
    """库存服务"""
    
    def __init__(self, data_dir: str = "data", product_manager: ProductManager = None):
        self.manager = InventoryManager(data_dir)
        # 如果提供了外部的 product_manager，则使用它，否则创建新的
        self.product_manager = product_manager if product_manager else ProductManager(data_dir)
    
    def initialize_inventory(self, product_id: str, quantity: int = 0, 
                            min_stock: int = 10, max_stock: int = 1000,
                            warehouse_location: str = "默认仓库") -> bool:
        """初始化商品库存"""
        # 检查商品是否存在
        product = self.product_manager.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品不存在: {product_id}")
        
        inventory = Inventory(
            product_id=product_id,
            quantity=quantity,
            min_stock=min_stock,
            max_stock=max_stock,
            warehouse_location=warehouse_location
        )
        return self.manager.add_or_update(inventory.to_dict())
    
    def get_all_inventory(self) -> List[Dict[str, Any]]:
        """获取所有库存"""
        inventory_list = self.manager.get_all()
        # 补充商品信息
        result = []
        for inv in inventory_list:
            product = self.product_manager.get_by_id(inv.get('product_id'))
            if product:
                inv['product_name'] = product.get('name')
                inv['product_category'] = product.get('category')
                inv['unit'] = product.get('unit')
            result.append(inv)
        return result
    
    def get_inventory(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取商品库存"""
        inv = self.manager.get_by_product_id(product_id)
        if inv:
            product = self.product_manager.get_by_id(product_id)
            if product:
                inv['product_name'] = product.get('name')
                inv['product_category'] = product.get('category')
                inv['unit'] = product.get('unit')
        return inv
    
    def add_stock(self, product_id: str, quantity: int) -> bool:
        """增加库存（入库）"""
        if quantity <= 0:
            raise ValueError("入库数量必须大于0")
        return self.manager.update_quantity(product_id, quantity)
    
    def reduce_stock(self, product_id: str, quantity: int) -> bool:
        """减少库存（出库）"""
        if quantity <= 0:
            raise ValueError("出库数量必须大于0")
        
        # 检查库存是否充足
        inv = self.manager.get_by_product_id(product_id)
        if not inv:
            raise ValueError(f"商品库存不存在: {product_id}")
        
        current_qty = inv.get('quantity', 0)
        if current_qty < quantity:
            raise ValueError(f"库存不足，当前库存: {current_qty}")
        
        return self.manager.update_quantity(product_id, -quantity)
    
    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """获取低库存商品"""
        items = self.manager.get_low_stock()
        result = []
        for item in items:
            product = self.product_manager.get_by_id(item.get('product_id'))
            if product:
                item['product_name'] = product.get('name')
                item['unit'] = product.get('unit')
            result.append(item)
        return result
    
    def get_over_stock_items(self) -> List[Dict[str, Any]]:
        """获取超库存商品"""
        items = self.manager.get_over_stock()
        result = []
        for item in items:
            product = self.product_manager.get_by_id(item.get('product_id'))
            if product:
                item['product_name'] = product.get('name')
                item['unit'] = product.get('unit')
            result.append(item)
        return result
    
    def update_stock_settings(self, product_id: str, min_stock: int = None, 
                             max_stock: int = None, warehouse_location: str = None) -> bool:
        """更新库存设置"""
        inv = self.manager.get_by_product_id(product_id)
        if not inv:
            raise ValueError(f"商品库存不存在: {product_id}")
        
        updates = {}
        if min_stock is not None:
            updates['min_stock'] = min_stock
        if max_stock is not None:
            updates['max_stock'] = max_stock
        if warehouse_location is not None:
            updates['warehouse_location'] = warehouse_location
        
        for key, value in updates.items():
            inv[key] = value
        inv['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return self.manager.add_or_update(inv)


class PurchaseService:
    """采购服务"""
    
    def __init__(self, data_dir: str = "data", supplier_manager: SupplierManager = None, 
                 product_manager: ProductManager = None, inventory_service: InventoryService = None):
        self.manager = PurchaseManager(data_dir)
        self.supplier_manager = supplier_manager if supplier_manager else SupplierManager(data_dir)
        self.product_manager = product_manager if product_manager else ProductManager(data_dir)
        # 如果提供了外部的 inventory_service，则使用它，否则创建新的
        if inventory_service:
            self.inventory_service = inventory_service
        else:
            self.inventory_service = InventoryService(data_dir, self.product_manager)
    
    def create_purchase_order(self, supplier_id: str, product_id: str, 
                              quantity: int, unit_price: float, 
                              notes: str = "") -> PurchaseOrder:
        """创建采购订单"""
        # 验证供应商
        supplier = self.supplier_manager.get_by_id(supplier_id)
        if not supplier:
            raise ValueError(f"供应商不存在: {supplier_id}")
        
        # 验证商品
        product = self.product_manager.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品不存在: {product_id}")
        
        if quantity <= 0:
            raise ValueError("采购数量必须大于0")
        
        if unit_price <= 0:
            raise ValueError("采购单价必须大于0")
        
        order = PurchaseOrder(
            id=str(uuid.uuid4())[:8],
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=quantity * unit_price,
            status="pending",
            order_date=datetime.now().strftime("%Y-%m-%d"),
            notes=notes
        )
        
        if self.manager.add(order.to_dict()):
            return order
        raise ValueError("采购订单创建失败")
    
    def complete_purchase_order(self, order_id: str) -> bool:
        """完成采购订单（入库）"""
        order = self.manager.get_by_id(order_id)
        if not order:
            raise ValueError(f"采购订单不存在: {order_id}")
        
        if order.get('status') != 'pending':
            raise ValueError(f"订单状态不正确，当前状态: {order.get('status')}")
        
        product_id = order.get('product_id')
        quantity = order.get('quantity', 0)
        
        # 检查库存记录是否存在
        inv = self.inventory_service.get_inventory(product_id)
        if not inv:
            # 初始化库存
            self.inventory_service.initialize_inventory(product_id, quantity)
        else:
            # 增加库存
            self.inventory_service.add_stock(product_id, quantity)
        
        # 更新订单状态
        return self.manager.update_status(order_id, "completed")
    
    def cancel_purchase_order(self, order_id: str) -> bool:
        """取消采购订单"""
        order = self.manager.get_by_id(order_id)
        if not order:
            raise ValueError(f"采购订单不存在: {order_id}")
        
        if order.get('status') != 'pending':
            raise ValueError("只能取消待处理的订单")
        
        return self.manager.update_status(order_id, "cancelled")
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """获取所有采购订单"""
        orders = self.manager.get_all()
        return self._enrich_orders(orders)
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """获取待处理订单"""
        orders = self.manager.get_by_status("pending")
        return self._enrich_orders(orders)
    
    def get_completed_orders(self) -> List[Dict[str, Any]]:
        """获取已完成订单"""
        orders = self.manager.get_by_status("completed")
        return self._enrich_orders(orders)
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单详情"""
        order = self.manager.get_by_id(order_id)
        if order:
            return self._enrich_order(order)
        return None
    
    def _enrich_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为订单补充供应商和商品信息"""
        return [self._enrich_order(order) for order in orders]
    
    def _enrich_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """为单个订单补充信息"""
        supplier = self.supplier_manager.get_by_id(order.get('supplier_id'))
        product = self.product_manager.get_by_id(order.get('product_id'))
        
        order_copy = order.copy()
        if supplier:
            order_copy['supplier_name'] = supplier.get('name')
        if product:
            order_copy['product_name'] = product.get('name')
            order_copy['unit'] = product.get('unit')
        return order_copy
    
    def get_purchase_stats_by_supplier(self, supplier_id: str) -> Dict[str, Any]:
        """获取供应商采购统计"""
        orders = self.manager.get_by_supplier(supplier_id)
        total_orders = len(orders)
        total_amount = sum(o.get('total_amount', 0) for o in orders if o.get('status') == 'completed')
        completed_orders = len([o for o in orders if o.get('status') == 'completed'])
        
        return {
            'supplier_id': supplier_id,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'total_amount': total_amount
        }


class SalesService:
    """销售服务"""
    
    def __init__(self, data_dir: str = "data", product_manager: ProductManager = None, 
                 inventory_service: InventoryService = None):
        self.manager = SalesManager(data_dir)
        self.product_manager = product_manager if product_manager else ProductManager(data_dir)
        # 如果提供了外部的 inventory_service，则使用它，否则创建新的
        if inventory_service:
            self.inventory_service = inventory_service
        else:
            self.inventory_service = InventoryService(data_dir, self.product_manager)
    
    def create_sale(self, product_id: str, quantity: int, 
                    unit_price: float = None, customer_name: str = "", 
                    notes: str = "") -> SaleRecord:
        """创建销售记录"""
        # 验证商品
        product = self.product_manager.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品不存在: {product_id}")
        
        # 检查库存
        inv = self.inventory_service.get_inventory(product_id)
        if not inv or inv.get('quantity', 0) < quantity:
            raise ValueError(f"库存不足，当前库存: {inv.get('quantity', 0) if inv else 0}")
        
        if quantity <= 0:
            raise ValueError("销售数量必须大于0")
        
        # 使用商品售价作为默认单价
        if unit_price is None:
            unit_price = product.get('price', 0)
        
        sale = SaleRecord(
            id=str(uuid.uuid4())[:8],
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=quantity * unit_price,
            sale_date=datetime.now().strftime("%Y-%m-%d"),
            customer_name=customer_name,
            notes=notes
        )
        
        # 保存销售记录
        if self.manager.add(sale.to_dict()):
            # 减少库存
            self.inventory_service.reduce_stock(product_id, quantity)
            return sale
        
        raise ValueError("销售记录创建失败")
    
    def get_all_sales(self) -> List[Dict[str, Any]]:
        """获取所有销售记录"""
        sales = self.manager.get_all()
        return self._enrich_sales(sales)
    
    def get_sale(self, sale_id: str) -> Optional[Dict[str, Any]]:
        """获取销售记录详情"""
        sale = self.manager.get_by_id(sale_id)
        if sale:
            return self._enrich_sale(sale)
        return None
    
    def get_sales_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """获取商品销售记录"""
        sales = self.manager.get_by_product(product_id)
        return self._enrich_sales(sales)
    
    def get_sales_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取日期范围内的销售记录"""
        sales = self.manager.get_by_date_range(start_date, end_date)
        return self._enrich_sales(sales)
    
    def _enrich_sales(self, sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为销售记录补充商品信息"""
        return [self._enrich_sale(sale) for sale in sales]
    
    def _enrich_sale(self, sale: Dict[str, Any]) -> Dict[str, Any]:
        """为单个销售记录补充信息"""
        product = self.product_manager.get_by_id(sale.get('product_id'))
        
        sale_copy = sale.copy()
        if product:
            sale_copy['product_name'] = product.get('name')
            sale_copy['unit'] = product.get('unit')
            sale_copy['category'] = product.get('category')
        return sale_copy


class StatisticsService:
    """统计报表服务"""
    
    def __init__(self, data_dir: str = "data"):
        self.product_manager = ProductManager(data_dir)
        self.supplier_manager = SupplierManager(data_dir)
        self.inventory_manager = InventoryManager(data_dir)
        self.purchase_manager = PurchaseManager(data_dir)
        self.sales_manager = SalesManager(data_dir)
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """获取库存汇总统计"""
        inventory = self.inventory_manager.get_all()
        products = self.product_manager.get_all()
        
        total_products = len(products)
        total_inventory_value = 0
        total_items = 0
        low_stock_count = 0
        
        for inv in inventory:
            qty = inv.get('quantity', 0)
            total_items += qty
            
            product = self.product_manager.get_by_id(inv.get('product_id'))
            if product:
                total_inventory_value += qty * product.get('cost_price', 0)
            
            if qty <= inv.get('min_stock', 0):
                low_stock_count += 1
        
        return {
            'total_products': total_products,
            'total_items': total_items,
            'total_inventory_value': round(total_inventory_value, 2),
            'low_stock_count': low_stock_count
        }
    
    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取销售汇总统计"""
        if start_date and end_date:
            sales = self.sales_manager.get_by_date_range(start_date, end_date)
        else:
            sales = self.sales_manager.get_all()
        
        total_sales = len(sales)
        total_revenue = sum(s.get('total_amount', 0) for s in sales)
        total_quantity = sum(s.get('quantity', 0) for s in sales)
        
        # 按商品统计
        product_sales = {}
        for sale in sales:
            pid = sale.get('product_id')
            if pid not in product_sales:
                product = self.product_manager.get_by_id(pid)
                product_sales[pid] = {
                    'product_name': product.get('name') if product else '未知',
                    'quantity': 0,
                    'revenue': 0
                }
            product_sales[pid]['quantity'] += sale.get('quantity', 0)
            product_sales[pid]['revenue'] += sale.get('total_amount', 0)
        
        return {
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'total_quantity': total_quantity,
            'product_sales': product_sales
        }
    
    def get_purchase_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取采购汇总统计"""
        orders = self.purchase_manager.get_all()
        
        if start_date and end_date:
            orders = [o for o in orders if start_date <= o.get('order_date', '') <= end_date]
        
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.get('status') == 'completed'])
        pending_orders = len([o for o in orders if o.get('status') == 'pending'])
        total_amount = sum(o.get('total_amount', 0) for o in orders if o.get('status') == 'completed')
        
        # 按供应商统计
        supplier_stats = {}
        for order in orders:
            if order.get('status') != 'completed':
                continue
            sid = order.get('supplier_id')
            if sid not in supplier_stats:
                supplier = self.supplier_manager.get_by_id(sid)
                supplier_stats[sid] = {
                    'supplier_name': supplier.get('name') if supplier else '未知',
                    'order_count': 0,
                    'total_amount': 0
                }
            supplier_stats[sid]['order_count'] += 1
            supplier_stats[sid]['total_amount'] += order.get('total_amount', 0)
        
        return {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_amount': round(total_amount, 2),
            'supplier_stats': supplier_stats
        }
    
    def get_profit_analysis(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取利润分析"""
        sales_summary = self.get_sales_summary(start_date, end_date)
        purchase_summary = self.get_purchase_summary(start_date, end_date)
        
        revenue = sales_summary['total_revenue']
        cost = purchase_summary['total_amount']
        profit = revenue - cost
        
        return {
            'revenue': revenue,
            'cost': cost,
            'profit': round(profit, 2),
            'profit_margin': round(profit / revenue * 100, 2) if revenue > 0 else 0
        }
    
    def generate_inventory_report(self) -> str:
        """生成库存报表文本"""
        lines = []
        lines.append("=" * 80)
        lines.append("库存报表".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        summary = self.get_inventory_summary()
        lines.append(f"商品总数: {summary['total_products']}")
        lines.append(f"库存总件数: {summary['total_items']}")
        lines.append(f"库存总价值: ¥{summary['total_inventory_value']:.2f}")
        lines.append(f"低库存商品数: {summary['low_stock_count']}")
        lines.append("")
        
        # 详细库存列表
        lines.append("-" * 80)
        lines.append(f"{'商品名称':<20} {'分类':<12} {'库存量':<10} {'单位':<8} {'仓库位置':<15}")
        lines.append("-" * 80)
        
        inventory = self.inventory_manager.get_all()
        for inv in inventory:
            product = self.product_manager.get_by_id(inv.get('product_id'))
            if product:
                name = product.get('name', '')[:18]
                category = product.get('category', '')[:10]
                qty = inv.get('quantity', 0)
                unit = product.get('unit', '')
                location = inv.get('warehouse_location', '')[:13]
                lines.append(f"{name:<20} {category:<12} {qty:<10} {unit:<8} {location:<15}")
        
        lines.append("-" * 80)
        lines.append("")
        
        # 低库存预警
        low_stock = self.inventory_manager.get_low_stock()
        if low_stock:
            lines.append("⚠️ 低库存预警:")
            for item in low_stock:
                product = self.product_manager.get_by_id(item.get('product_id'))
                if product:
                    lines.append(f"  - {product.get('name')}: 当前 {item.get('quantity')}，最低 {item.get('min_stock')}")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_sales_report(self, start_date: str = None, end_date: str = None) -> str:
        """生成销售报表文本"""
        lines = []
        lines.append("=" * 80)
        lines.append("销售报表".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        if start_date and end_date:
            lines.append(f"统计期间: {start_date} 至 {end_date}")
            lines.append("")
        
        summary = self.get_sales_summary(start_date, end_date)
        lines.append(f"销售笔数: {summary['total_sales']}")
        lines.append(f"销售总量: {summary['total_quantity']}")
        lines.append(f"销售总额: ¥{summary['total_revenue']:.2f}")
        lines.append("")
        
        # 按商品统计
        if summary['product_sales']:
            lines.append("-" * 80)
            lines.append("按商品统计:")
            lines.append(f"{'商品名称':<20} {'销售数量':<12} {'销售额':<15}")
            lines.append("-" * 80)
            
            for pid, stats in summary['product_sales'].items():
                name = stats['product_name'][:18]
                qty = stats['quantity']
                revenue = stats['revenue']
                lines.append(f"{name:<20} {qty:<12} ¥{revenue:,.2f}")
            
            lines.append("-" * 80)
        
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
