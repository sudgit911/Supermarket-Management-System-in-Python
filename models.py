"""
数据模型定义模块
包含商品、供应商、采购订单、销售记录等数据类
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class Product:
    """商品模型"""
    id: str
    name: str
    category: str
    unit: str
    price: float
    cost_price: float
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        return cls(**data)


@dataclass
class Supplier:
    """供应商模型"""
    id: str
    name: str
    contact: str
    phone: str
    email: str
    address: str
    status: str = "active"  # active/inactive
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Supplier':
        return cls(**data)


@dataclass
class Inventory:
    """库存模型"""
    product_id: str
    quantity: int
    min_stock: int  # 最低库存警戒线
    max_stock: int  # 最高库存限制
    warehouse_location: str
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Inventory':
        return cls(**data)
    
    def is_low_stock(self) -> bool:
        """检查是否库存不足"""
        return self.quantity <= self.min_stock
    
    def is_over_stock(self) -> bool:
        """检查是否库存过剩"""
        return self.quantity >= self.max_stock


@dataclass
class PurchaseOrder:
    """采购订单模型"""
    id: str
    supplier_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_amount: float
    status: str  # pending/completed/cancelled
    order_date: str
    delivery_date: Optional[str] = None
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.total_amount == 0:
            self.total_amount = self.quantity * self.unit_price
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PurchaseOrder':
        return cls(**data)


@dataclass
class SaleRecord:
    """销售记录模型"""
    id: str
    product_id: str
    quantity: int
    unit_price: float
    total_amount: float
    sale_date: str
    customer_name: str = ""
    notes: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.total_amount == 0:
            self.total_amount = self.quantity * self.unit_price
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SaleRecord':
        return cls(**data)
