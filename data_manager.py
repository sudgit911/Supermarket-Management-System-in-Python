"""
数据管理模块
负责CSV/JSON文件的读写操作
"""
import csv
import json
import os
from typing import List, Dict, Any, Optional, Type, TypeVar
from pathlib import Path

T = TypeVar('T')


class DataManager:
    """数据管理基类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def _get_file_path(self, filename: str) -> Path:
        """获取文件完整路径"""
        return self.data_dir / filename
    
    def save_to_csv(self, filename: str, data: List[Dict[str, Any]], fieldnames: List[str]):
        """保存数据到CSV文件"""
        file_path = self._get_file_path(filename)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def load_from_csv(self, filename: str) -> List[Dict[str, Any]]:
        """从CSV文件加载数据"""
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def save_to_json(self, filename: str, data: List[Dict[str, Any]]):
        """保存数据到JSON文件"""
        file_path = self._get_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_json(self, filename: str) -> List[Dict[str, Any]]:
        """从JSON文件加载数据"""
        file_path = self._get_file_path(filename)
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def file_exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        return self._get_file_path(filename).exists()
    
    def delete_file(self, filename: str):
        """删除文件"""
        file_path = self._get_file_path(filename)
        if file_path.exists():
            file_path.unlink()


class ProductManager(DataManager):
    """商品数据管理"""
    
    FILENAME = "products.json"
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self._products: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """加载商品数据"""
        self._products = self.load_from_json(self.FILENAME)
    
    def _save(self):
        """保存商品数据"""
        self.save_to_json(self.FILENAME, self._products)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有商品"""
        return self._products.copy()
    
    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取商品"""
        for product in self._products:
            if product.get('id') == product_id:
                return product.copy()
        return None
    
    def get_by_name(self, name: str) -> List[Dict[str, Any]]:
        """根据名称搜索商品"""
        return [p.copy() for p in self._products if name.lower() in p.get('name', '').lower()]
    
    def add(self, product: Dict[str, Any]) -> bool:
        """添加商品"""
        # 检查ID是否已存在
        if self.get_by_id(product.get('id')):
            return False
        self._products.append(product)
        self._save()
        return True
    
    def update(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """更新商品"""
        for i, product in enumerate(self._products):
            if product.get('id') == product_id:
                self._products[i].update(updates)
                self._products[i]['updated_at'] = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return True
        return False
    
    def delete(self, product_id: str) -> bool:
        """删除商品"""
        for i, product in enumerate(self._products):
            if product.get('id') == product_id:
                del self._products[i]
                self._save()
                return True
        return False
    
    def search(self, keyword: str, category: str = None) -> List[Dict[str, Any]]:
        """搜索商品"""
        results = []
        keyword = keyword.lower()
        for product in self._products:
            match = False
            if keyword in product.get('name', '').lower():
                match = True
            if keyword in product.get('description', '').lower():
                match = True
            if category and product.get('category') == category:
                match = True
            if match:
                results.append(product.copy())
        return results


class SupplierManager(DataManager):
    """供应商数据管理"""
    
    FILENAME = "suppliers.json"
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self._suppliers: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """加载供应商数据"""
        self._suppliers = self.load_from_json(self.FILENAME)
    
    def _save(self):
        """保存供应商数据"""
        self.save_to_json(self.FILENAME, self._suppliers)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有供应商"""
        return self._suppliers.copy()
    
    def get_active_suppliers(self) -> List[Dict[str, Any]]:
        """获取活跃供应商"""
        return [s.copy() for s in self._suppliers if s.get('status') == 'active']
    
    def get_by_id(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取供应商"""
        for supplier in self._suppliers:
            if supplier.get('id') == supplier_id:
                return supplier.copy()
        return None
    
    def add(self, supplier: Dict[str, Any]) -> bool:
        """添加供应商"""
        if self.get_by_id(supplier.get('id')):
            return False
        self._suppliers.append(supplier)
        self._save()
        return True
    
    def update(self, supplier_id: str, updates: Dict[str, Any]) -> bool:
        """更新供应商"""
        for i, supplier in enumerate(self._suppliers):
            if supplier.get('id') == supplier_id:
                self._suppliers[i].update(updates)
                self._suppliers[i]['updated_at'] = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return True
        return False
    
    def delete(self, supplier_id: str) -> bool:
        """删除供应商"""
        for i, supplier in enumerate(self._suppliers):
            if supplier.get('id') == supplier_id:
                del self._suppliers[i]
                self._save()
                return True
        return False
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索供应商"""
        results = []
        keyword = keyword.lower()
        for supplier in self._suppliers:
            if (keyword in supplier.get('name', '').lower() or
                keyword in supplier.get('contact', '').lower() or
                keyword in supplier.get('phone', '')):
                results.append(supplier.copy())
        return results


class InventoryManager(DataManager):
    """库存数据管理"""
    
    FILENAME = "inventory.json"
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self._inventory: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """加载库存数据"""
        self._inventory = self.load_from_json(self.FILENAME)
    
    def _save(self):
        """保存库存数据"""
        self.save_to_json(self.FILENAME, self._inventory)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有库存"""
        return self._inventory.copy()
    
    def get_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """根据商品ID获取库存"""
        for item in self._inventory:
            if item.get('product_id') == product_id:
                return item.copy()
        return None
    
    def add_or_update(self, inventory: Dict[str, Any]) -> bool:
        """添加或更新库存"""
        product_id = inventory.get('product_id')
        for i, item in enumerate(self._inventory):
            if item.get('product_id') == product_id:
                self._inventory[i] = inventory
                self._save()
                return True
        self._inventory.append(inventory)
        self._save()
        return True
    
    def update_quantity(self, product_id: str, delta: int) -> bool:
        """更新库存数量（增加或减少）"""
        for item in self._inventory:
            if item.get('product_id') == product_id:
                item['quantity'] = item.get('quantity', 0) + delta
                if item['quantity'] < 0:
                    item['quantity'] = 0
                item['last_updated'] = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return True
        return False
    
    def get_low_stock(self) -> List[Dict[str, Any]]:
        """获取低库存商品"""
        results = []
        for item in self._inventory:
            if item.get('quantity', 0) <= item.get('min_stock', 0):
                results.append(item.copy())
        return results
    
    def get_over_stock(self) -> List[Dict[str, Any]]:
        """获取超库存商品"""
        results = []
        for item in self._inventory:
            if item.get('quantity', 0) >= item.get('max_stock', 999999):
                results.append(item.copy())
        return results


class PurchaseManager(DataManager):
    """采购订单数据管理"""
    
    FILENAME = "purchase_orders.json"
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self._orders: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """加载采购订单数据"""
        self._orders = self.load_from_json(self.FILENAME)
    
    def _save(self):
        """保存采购订单数据"""
        self.save_to_json(self.FILENAME, self._orders)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有采购订单"""
        return self._orders.copy()
    
    def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取采购订单"""
        for order in self._orders:
            if order.get('id') == order_id:
                return order.copy()
        return None
    
    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取采购订单"""
        return [o.copy() for o in self._orders if o.get('status') == status]
    
    def get_by_supplier(self, supplier_id: str) -> List[Dict[str, Any]]:
        """根据供应商获取采购订单"""
        return [o.copy() for o in self._orders if o.get('supplier_id') == supplier_id]
    
    def add(self, order: Dict[str, Any]) -> bool:
        """添加采购订单"""
        self._orders.append(order)
        self._save()
        return True
    
    def update_status(self, order_id: str, status: str) -> bool:
        """更新订单状态"""
        for order in self._orders:
            if order.get('id') == order_id:
                order['status'] = status
                order['updated_at'] = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if status == 'completed':
                    order['delivery_date'] = __import__('datetime').datetime.now().strftime("%Y-%m-%d")
                self._save()
                return True
        return False
    
    def delete(self, order_id: str) -> bool:
        """删除采购订单"""
        for i, order in enumerate(self._orders):
            if order.get('id') == order_id:
                del self._orders[i]
                self._save()
                return True
        return False


class SalesManager(DataManager):
    """销售记录数据管理"""
    
    FILENAME = "sales.json"
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        self._sales: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """加载销售记录数据"""
        self._sales = self.load_from_json(self.FILENAME)
    
    def _save(self):
        """保存销售记录数据"""
        self.save_to_json(self.FILENAME, self._sales)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有销售记录"""
        return self._sales.copy()
    
    def get_by_id(self, sale_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取销售记录"""
        for sale in self._sales:
            if sale.get('id') == sale_id:
                return sale.copy()
        return None
    
    def get_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """根据商品获取销售记录"""
        return [s.copy() for s in self._sales if s.get('product_id') == product_id]
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """根据日期范围获取销售记录"""
        results = []
        for sale in self._sales:
            sale_date = sale.get('sale_date', '')
            if start_date <= sale_date <= end_date:
                results.append(sale.copy())
        return results
    
    def add(self, sale: Dict[str, Any]) -> bool:
        """添加销售记录"""
        self._sales.append(sale)
        self._save()
        return True
    
    def delete(self, sale_id: str) -> bool:
        """删除销售记录"""
        for i, sale in enumerate(self._sales):
            if sale.get('id') == sale_id:
                del self._sales[i]
                self._save()
                return True
        return False
