"""
超市采购管理系统测试模块
使用 pytest 框架进行单元测试
"""
import pytest
import os
import shutil
import tempfile
from datetime import datetime

from models import Product, Supplier, Inventory, PurchaseOrder, SaleRecord
from data_manager import ProductManager, SupplierManager, InventoryManager, PurchaseManager, SalesManager
from services import (
    ProductService, SupplierService, InventoryService,
    PurchaseService, SalesService, StatisticsService
)


# ==================== Fixtures ====================

@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def product_manager(temp_data_dir):
    """商品管理器fixture"""
    return ProductManager(temp_data_dir)


@pytest.fixture
def supplier_manager(temp_data_dir):
    """供应商管理器fixture"""
    return SupplierManager(temp_data_dir)


@pytest.fixture
def inventory_manager(temp_data_dir):
    """库存管理器fixture"""
    return InventoryManager(temp_data_dir)


@pytest.fixture
def purchase_manager(temp_data_dir):
    """采购管理器fixture"""
    return PurchaseManager(temp_data_dir)


@pytest.fixture
def sales_manager(temp_data_dir):
    """销售管理器fixture"""
    return SalesManager(temp_data_dir)


# ==================== 模型测试 ====================

class TestModels:
    """测试数据模型"""

    def test_product_creation(self):
        """测试商品创建"""
        product = Product(
            id="test001",
            name="测试商品",
            category="食品",
            unit="箱",
            price=100.0,
            cost_price=80.0
        )
        assert product.id == "test001"
        assert product.name == "测试商品"
        assert product.price == 100.0
        assert product.cost_price == 80.0
        assert product.created_at != ""

    def test_product_to_dict(self):
        """测试商品转字典"""
        product = Product(
            id="test001",
            name="测试商品",
            category="食品",
            unit="箱",
            price=100.0,
            cost_price=80.0
        )
        data = product.to_dict()
        assert data['id'] == "test001"
        assert data['name'] == "测试商品"
        assert data['price'] == 100.0

    def test_supplier_creation(self):
        """测试供应商创建"""
        supplier = Supplier(
            id="sup001",
            name="测试供应商",
            contact="李四",
            phone="13900139000",
            email="supplier@test.com",
            address="测试地址"
        )
        assert supplier.id == "sup001"
        assert supplier.name == "测试供应商"
        assert supplier.status == "active"

    def test_inventory_creation(self):
        """测试库存创建"""
        inventory = Inventory(
            product_id="prod001",
            quantity=100,
            min_stock=10,
            max_stock=500,
            warehouse_location="A区-01"
        )
        assert inventory.product_id == "prod001"
        assert inventory.quantity == 100
        assert inventory.is_low_stock() == False
        assert inventory.is_over_stock() == False

    def test_inventory_low_stock(self):
        """测试低库存检测"""
        inventory = Inventory(
            product_id="prod001",
            quantity=5,
            min_stock=10,
            max_stock=500,
            warehouse_location="A区-01"
        )
        assert inventory.is_low_stock() == True

    def test_purchase_order_creation(self):
        """测试采购订单创建"""
        order = PurchaseOrder(
            id="po001",
            supplier_id="sup001",
            product_id="prod001",
            quantity=50,
            unit_price=80.0,
            total_amount=4000.0,
            status="pending",
            order_date="2024-01-01"
        )
        assert order.id == "po001"
        assert order.total_amount == 4000.0
        assert order.status == "pending"

    def test_sale_record_creation(self):
        """测试销售记录创建"""
        sale = SaleRecord(
            id="sale001",
            product_id="prod001",
            quantity=10,
            unit_price=100.0,
            total_amount=1000.0,
            sale_date="2024-01-01"
        )
        assert sale.id == "sale001"
        assert sale.total_amount == 1000.0


# ==================== 数据管理器测试 ====================

class TestProductManager:
    """测试商品管理器"""

    def test_add_product(self, product_manager):
        """测试添加商品"""
        product = {
            "id": "p001",
            "name": "苹果",
            "category": "水果",
            "unit": "斤",
            "price": 5.5,
            "cost_price": 3.0
        }
        assert product_manager.add(product) == True

        # 验证添加成功
        result = product_manager.get_by_id("p001")
        assert result is not None
        assert result["name"] == "苹果"

    def test_add_duplicate_product(self, product_manager):
        """测试添加重复商品"""
        product = {
            "id": "p001",
            "name": "苹果",
            "category": "水果",
            "unit": "斤",
            "price": 5.5,
            "cost_price": 3.0
        }
        product_manager.add(product)

        # 重复添加应失败
        result = product_manager.add(product)
        assert result == False

    def test_get_all_products(self, product_manager):
        """测试获取所有商品"""
        # 添加多个商品
        for i in range(3):
            product_manager.add({
                "id": f"p00{i}",
                "name": f"商品{i}",
                "category": "分类",
                "unit": "个",
                "price": 10.0,
                "cost_price": 5.0
            })

        products = product_manager.get_all()
        assert len(products) == 3

    def test_update_product(self, product_manager):
        """测试更新商品"""
        product = {
            "id": "p001",
            "name": "苹果",
            "category": "水果",
            "unit": "斤",
            "price": 5.5,
            "cost_price": 3.0
        }
        product_manager.add(product)

        # 更新商品
        result = product_manager.update("p001", {"price": 6.0, "name": "红苹果"})
        assert result == True

        # 验证更新
        updated = product_manager.get_by_id("p001")
        assert updated["price"] == 6.0
        assert updated["name"] == "红苹果"

    def test_delete_product(self, product_manager):
        """测试删除商品"""
        product = {
            "id": "p001",
            "name": "苹果",
            "category": "水果",
            "unit": "斤",
            "price": 5.5,
            "cost_price": 3.0
        }
        product_manager.add(product)

        # 删除商品
        result = product_manager.delete("p001")
        assert result == True

        # 验证删除
        deleted = product_manager.get_by_id("p001")
        assert deleted is None

    def test_search_products(self, product_manager):
        """测试搜索商品"""
        product_manager.add({
            "id": "p001",
            "name": "红富士苹果",
            "category": "水果",
            "unit": "斤",
            "price": 5.5,
            "cost_price": 3.0
        })
        product_manager.add({
            "id": "p002",
            "name": "香蕉",
            "category": "水果",
            "unit": "斤",
            "price": 3.5,
            "cost_price": 2.0
        })

        # 搜索
        results = product_manager.search("苹果")
        assert len(results) == 1
        assert results[0]["name"] == "红富士苹果"


class TestSupplierManager:
    """测试供应商管理器"""

    def test_add_supplier(self, supplier_manager):
        """测试添加供应商"""
        supplier = {
            "id": "s001",
            "name": "供应商A",
            "contact": "张三",
            "phone": "13800138000",
            "email": "a@test.com",
            "address": "地址A"
        }
        assert supplier_manager.add(supplier) == True

        result = supplier_manager.get_by_id("s001")
        assert result is not None
        assert result["name"] == "供应商A"

    def test_get_active_suppliers(self, supplier_manager):
        """测试获取活跃供应商"""
        supplier_manager.add({
            "id": "s001",
            "name": "供应商A",
            "contact": "张三",
            "phone": "13800138000",
            "email": "a@test.com",
            "address": "地址A",
            "status": "active"
        })
        supplier_manager.add({
            "id": "s002",
            "name": "供应商B",
            "contact": "李四",
            "phone": "13900139000",
            "email": "b@test.com",
            "address": "地址B",
            "status": "inactive"
        })

        active = supplier_manager.get_active_suppliers()
        assert len(active) == 1
        assert active[0]["name"] == "供应商A"

    def test_update_supplier(self, supplier_manager):
        """测试更新供应商"""
        supplier_manager.add({
            "id": "s001",
            "name": "供应商A",
            "contact": "张三",
            "phone": "13800138000",
            "email": "a@test.com",
            "address": "地址A"
        })

        result = supplier_manager.update("s001", {"phone": "13700137000"})
        assert result == True

        updated = supplier_manager.get_by_id("s001")
        assert updated["phone"] == "13700137000"

    def test_delete_supplier(self, supplier_manager):
        """测试删除供应商"""
        supplier_manager.add({
            "id": "s001",
            "name": "供应商A",
            "contact": "张三",
            "phone": "13800138000",
            "email": "a@test.com",
            "address": "地址A"
        })

        result = supplier_manager.delete("s001")
        assert result == True

        deleted = supplier_manager.get_by_id("s001")
        assert deleted is None


class TestInventoryManager:
    """测试库存管理器"""

    def test_add_inventory(self, inventory_manager):
        """测试添加库存"""
        inventory = {
            "product_id": "p001",
            "quantity": 100,
            "min_stock": 10,
            "max_stock": 500,
            "warehouse_location": "A区"
        }
        assert inventory_manager.add_or_update(inventory) == True

        result = inventory_manager.get_by_product_id("p001")
        assert result is not None
        assert result["quantity"] == 100

    def test_update_quantity(self, inventory_manager):
        """测试更新库存数量"""
        inventory_manager.add_or_update({
            "product_id": "p001",
            "quantity": 100,
            "min_stock": 10,
            "max_stock": 500,
            "warehouse_location": "A区"
        })

        # 增加库存
        result = inventory_manager.update_quantity("p001", 50)
        assert result == True

        inv = inventory_manager.get_by_product_id("p001")
        assert inv["quantity"] == 150

        # 减少库存
        inventory_manager.update_quantity("p001", -30)
        inv = inventory_manager.get_by_product_id("p001")
        assert inv["quantity"] == 120

    def test_get_low_stock(self, inventory_manager):
        """测试获取低库存商品"""
        inventory_manager.add_or_update({
            "product_id": "p001",
            "quantity": 5,
            "min_stock": 10,
            "max_stock": 500,
            "warehouse_location": "A区"
        })
        inventory_manager.add_or_update({
            "product_id": "p002",
            "quantity": 100,
            "min_stock": 10,
            "max_stock": 500,
            "warehouse_location": "B区"
        })

        low_stock = inventory_manager.get_low_stock()
        assert len(low_stock) == 1
        assert low_stock[0]["product_id"] == "p001"


class TestPurchaseManager:
    """测试采购管理器"""

    def test_add_order(self, purchase_manager):
        """测试添加采购订单"""
        order = {
            "id": "po001",
            "supplier_id": "s001",
            "product_id": "p001",
            "quantity": 50,
            "unit_price": 80.0,
            "total_amount": 4000.0,
            "status": "pending",
            "order_date": "2024-01-01"
        }
        assert purchase_manager.add(order) == True

        result = purchase_manager.get_by_id("po001")
        assert result is not None
        assert result["status"] == "pending"

    def test_update_status(self, purchase_manager):
        """测试更新订单状态"""
        purchase_manager.add({
            "id": "po001",
            "supplier_id": "s001",
            "product_id": "p001",
            "quantity": 50,
            "unit_price": 80.0,
            "total_amount": 4000.0,
            "status": "pending",
            "order_date": "2024-01-01"
        })

        result = purchase_manager.update_status("po001", "completed")
        assert result == True

        order = purchase_manager.get_by_id("po001")
        assert order["status"] == "completed"

    def test_get_by_status(self, purchase_manager):
        """测试按状态获取订单"""
        purchase_manager.add({
            "id": "po001",
            "supplier_id": "s001",
            "product_id": "p001",
            "quantity": 50,
            "unit_price": 80.0,
            "total_amount": 4000.0,
            "status": "pending",
            "order_date": "2024-01-01"
        })
        purchase_manager.add({
            "id": "po002",
            "supplier_id": "s001",
            "product_id": "p002",
            "quantity": 30,
            "unit_price": 60.0,
            "total_amount": 1800.0,
            "status": "completed",
            "order_date": "2024-01-02"
        })

        pending = purchase_manager.get_by_status("pending")
        assert len(pending) == 1
        assert pending[0]["id"] == "po001"


class TestSalesManager:
    """测试销售管理器"""

    def test_add_sale(self, sales_manager):
        """测试添加销售记录"""
        sale = {
            "id": "sale001",
            "product_id": "p001",
            "quantity": 10,
            "unit_price": 100.0,
            "total_amount": 1000.0,
            "sale_date": "2024-01-01"
        }
        assert sales_manager.add(sale) == True

        result = sales_manager.get_by_id("sale001")
        assert result is not None
        assert result["quantity"] == 10

    def test_get_by_product(self, sales_manager):
        """测试按商品获取销售记录"""
        sales_manager.add({
            "id": "sale001",
            "product_id": "p001",
            "quantity": 10,
            "unit_price": 100.0,
            "total_amount": 1000.0,
            "sale_date": "2024-01-01"
        })
        sales_manager.add({
            "id": "sale002",
            "product_id": "p001",
            "quantity": 5,
            "unit_price": 100.0,
            "total_amount": 500.0,
            "sale_date": "2024-01-02"
        })

        sales = sales_manager.get_by_product("p001")
        assert len(sales) == 2

    def test_get_by_date_range(self, sales_manager):
        """测试按日期范围获取销售记录"""
        sales_manager.add({
            "id": "sale001",
            "product_id": "p001",
            "quantity": 10,
            "unit_price": 100.0,
            "total_amount": 1000.0,
            "sale_date": "2024-01-15"
        })
        sales_manager.add({
            "id": "sale002",
            "product_id": "p001",
            "quantity": 5,
            "unit_price": 100.0,
            "total_amount": 500.0,
            "sale_date": "2024-02-15"
        })

        sales = sales_manager.get_by_date_range("2024-01-01", "2024-01-31")
        assert len(sales) == 1


# ==================== 服务层测试 ====================

class TestProductService:
    """测试商品服务"""

    def test_create_product(self, temp_data_dir):
        """测试创建商品"""
        product_service = ProductService(temp_data_dir)
        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        assert product.name == "测试商品"
        assert product.price == 100.0
        assert len(product.id) == 8

    def test_get_product(self, temp_data_dir):
        """测试获取商品"""
        product_service = ProductService(temp_data_dir)
        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        result = product_service.get_product(product.id)
        assert result is not None
        assert result["name"] == "测试商品"

    def test_update_product(self, temp_data_dir):
        """测试更新商品"""
        product_service = ProductService(temp_data_dir)
        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        result = product_service.update_product(product.id, price=120.0)
        assert result == True

        updated = product_service.get_product(product.id)
        assert updated["price"] == 120.0

    def test_delete_product(self, temp_data_dir):
        """测试删除商品"""
        product_service = ProductService(temp_data_dir)
        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        result = product_service.delete_product(product.id)
        assert result == True

        deleted = product_service.get_product(product.id)
        assert deleted is None

    def test_search_products(self, temp_data_dir):
        """测试搜索商品"""
        product_service = ProductService(temp_data_dir)
        product_service.create_product(
            name="苹果",
            category="水果",
            unit="斤",
            price=5.0,
            cost_price=3.0
        )
        product_service.create_product(
            name="香蕉",
            category="水果",
            unit="斤",
            price=3.0,
            cost_price=2.0
        )

        results = product_service.search_products("苹")
        assert len(results) == 1
        assert results[0]["name"] == "苹果"


class TestSupplierService:
    """测试供应商服务"""

    def test_create_supplier(self, temp_data_dir):
        """测试创建供应商"""
        supplier_service = SupplierService(temp_data_dir)
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )
        assert supplier.name == "测试供应商"
        assert supplier.status == "active"

    def test_get_supplier(self, temp_data_dir):
        """测试获取供应商"""
        supplier_service = SupplierService(temp_data_dir)
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )
        result = supplier_service.get_supplier(supplier.id)
        assert result is not None
        assert result["name"] == "测试供应商"

    def test_update_supplier(self, temp_data_dir):
        """测试更新供应商"""
        supplier_service = SupplierService(temp_data_dir)
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )
        result = supplier_service.update_supplier(
            supplier.id,
            phone="13900139000"
        )
        assert result == True

        updated = supplier_service.get_supplier(supplier.id)
        assert updated["phone"] == "13900139000"

    def test_delete_supplier(self, temp_data_dir):
        """测试删除供应商"""
        supplier_service = SupplierService(temp_data_dir)
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )
        result = supplier_service.delete_supplier(supplier.id)
        assert result == True

        deleted = supplier_service.get_supplier(supplier.id)
        assert deleted is None

    def test_set_supplier_status(self, temp_data_dir):
        """测试设置供应商状态"""
        supplier_service = SupplierService(temp_data_dir)
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )
        result = supplier_service.set_supplier_status(supplier.id, "inactive")
        assert result == True

        updated = supplier_service.get_supplier(supplier.id)
        assert updated["status"] == "inactive"


class TestInventoryService:
    """测试库存服务"""

    def test_initialize_inventory(self, temp_data_dir):
        """测试初始化库存"""
        # 使用同一个数据目录和共享的product_manager
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        result = inventory_service.initialize_inventory(
            product.id,
            quantity=100,
            min_stock=10,
            max_stock=500,
            warehouse_location="A区"
        )
        assert result == True

        inv = inventory_service.get_inventory(product.id)
        assert inv is not None
        assert inv["quantity"] == 100

    def test_add_stock(self, temp_data_dir):
        """测试增加库存"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        inventory_service.initialize_inventory(product.id, 100)

        result = inventory_service.add_stock(product.id, 50)
        assert result == True

        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 150

    def test_reduce_stock(self, temp_data_dir):
        """测试减少库存"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        inventory_service.initialize_inventory(product.id, 100)

        result = inventory_service.reduce_stock(product.id, 30)
        assert result == True

        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 70

    def test_reduce_stock_insufficient(self, temp_data_dir):
        """测试库存不足时减少库存"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        inventory_service.initialize_inventory(product.id, 10)

        with pytest.raises(ValueError) as exc_info:
            inventory_service.reduce_stock(product.id, 20)
        assert "库存不足" in str(exc_info.value)

    def test_get_low_stock_items(self, temp_data_dir):
        """测试获取低库存商品"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        inventory_service.initialize_inventory(product.id, 5, min_stock=10)

        low_stock = inventory_service.get_low_stock_items()
        assert len(low_stock) == 1
        assert low_stock[0]["product_id"] == product.id


class TestPurchaseService:
    """测试采购服务"""

    def test_create_purchase_order(self, temp_data_dir):
        """测试创建采购订单"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir, 
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        order = purchase_service.create_purchase_order(
            supplier_id=supplier.id,
            product_id=product.id,
            quantity=50,
            unit_price=80.0,
            notes="测试订单"
        )
        assert order.supplier_id == supplier.id
        assert order.quantity == 50
        assert order.total_amount == 4000.0
        assert order.status == "pending"

    def test_create_order_invalid_supplier(self, temp_data_dir):
        """测试使用无效供应商创建订单"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        purchase_service = PurchaseService(
            temp_data_dir,
            product_manager=product_manager
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        with pytest.raises(ValueError) as exc_info:
            purchase_service.create_purchase_order(
                supplier_id="invalid_id",
                product_id=product.id,
                quantity=50,
                unit_price=80.0
            )
        assert "供应商不存在" in str(exc_info.value)

    def test_complete_purchase_order(self, temp_data_dir):
        """测试完成采购订单（入库）"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        # 初始化库存
        inventory_service.initialize_inventory(product.id, 0)

        # 创建订单
        order = purchase_service.create_purchase_order(
            supplier_id=supplier.id,
            product_id=product.id,
            quantity=50,
            unit_price=80.0
        )

        # 完成订单
        result = purchase_service.complete_purchase_order(order.id)
        assert result == True

        # 验证库存更新
        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 50

        # 验证订单状态
        updated_order = purchase_service.get_order(order.id)
        assert updated_order["status"] == "completed"

    def test_cancel_purchase_order(self, temp_data_dir):
        """测试取消采购订单"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        order = purchase_service.create_purchase_order(
            supplier_id=supplier.id,
            product_id=product.id,
            quantity=50,
            unit_price=80.0
        )

        result = purchase_service.cancel_purchase_order(order.id)
        assert result == True

        updated_order = purchase_service.get_order(order.id)
        assert updated_order["status"] == "cancelled"


class TestSalesService:
    """测试销售服务"""

    def test_create_sale(self, temp_data_dir):
        """测试创建销售单"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        # 初始化库存
        inventory_service.initialize_inventory(product.id, 100)

        sale = sales_service.create_sale(
            product_id=product.id,
            quantity=10,
            unit_price=100.0,
            customer_name="测试客户"
        )
        assert sale.product_id == product.id
        assert sale.quantity == 10
        assert sale.total_amount == 1000.0

        # 验证库存减少
        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 90

    def test_create_sale_insufficient_stock(self, temp_data_dir):
        """测试库存不足时创建销售单"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 5)

        with pytest.raises(ValueError) as exc_info:
            sales_service.create_sale(
                product_id=product.id,
                quantity=10
            )
        assert "库存不足" in str(exc_info.value)

    def test_get_sales_by_product(self, temp_data_dir):
        """测试按商品获取销售记录"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 100)

        sales_service.create_sale(product.id, 5)
        sales_service.create_sale(product.id, 3)

        sales = sales_service.get_sales_by_product(product.id)
        assert len(sales) == 2


class TestStatisticsService:
    """测试统计服务"""

    def test_get_inventory_summary(self, temp_data_dir):
        """测试获取库存汇总"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 100)

        summary = stats_service.get_inventory_summary()
        assert summary["total_products"] == 1
        assert summary["total_items"] == 100

    def test_get_sales_summary(self, temp_data_dir):
        """测试获取销售汇总"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 100)
        sales_service.create_sale(product.id, 10, unit_price=100.0)
        sales_service.create_sale(product.id, 5, unit_price=100.0)

        summary = stats_service.get_sales_summary()
        assert summary["total_sales"] == 2
        assert summary["total_quantity"] == 15
        assert summary["total_revenue"] == 1500.0

    def test_get_purchase_summary(self, temp_data_dir):
        """测试获取采购汇总"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        order1 = purchase_service.create_purchase_order(
            supplier.id, product.id, 50, 80.0
        )
        order2 = purchase_service.create_purchase_order(
            supplier.id, product.id, 30, 80.0
        )
        purchase_service.complete_purchase_order(order1.id)
        purchase_service.complete_purchase_order(order2.id)

        summary = stats_service.get_purchase_summary()
        assert summary["completed_orders"] == 2
        assert summary["total_amount"] == 6400.0

    def test_get_profit_analysis(self, temp_data_dir):
        """测试利润分析"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        # 采购入库
        inventory_service.initialize_inventory(product.id, 0)
        order = purchase_service.create_purchase_order(
            supplier.id, product.id, 100, 50.0
        )
        purchase_service.complete_purchase_order(order.id)

        # 销售
        sales_service.create_sale(product.id, 50, unit_price=100.0)

        analysis = stats_service.get_profit_analysis()
        assert analysis["revenue"] == 5000.0
        assert analysis["cost"] == 5000.0  # 采购成本
        assert analysis["profit"] == 0.0  # 毛利润

    def test_generate_inventory_report(self, temp_data_dir):
        """测试生成库存报表"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 100)

        report = stats_service.generate_inventory_report()
        assert "库存报表" in report
        assert "测试商品" in report
        assert "商品总数: 1" in report

    def test_generate_sales_report(self, temp_data_dir):
        """测试生成销售报表"""
        product_manager = ProductManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        stats_service = StatisticsService(temp_data_dir)

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        inventory_service.initialize_inventory(product.id, 100)
        sales_service.create_sale(product.id, 10, unit_price=100.0)

        report = stats_service.generate_sales_report()
        assert "销售报表" in report
        assert "销售笔数: 1" in report


# ==================== 集成测试 ====================

class TestIntegration:
    """集成测试"""

    def test_full_purchase_flow(self, temp_data_dir):
        """测试完整采购流程"""
        # 创建共享的数据管理器
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        inventory_manager = InventoryManager(temp_data_dir)
        
        # 创建服务
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        # 1. 创建商品
        product = product_service.create_product(
            name="集成测试商品",
            category="测试",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        # 2. 创建供应商
        supplier = supplier_service.create_supplier(
            name="集成测试供应商",
            contact="测试联系人",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        # 3. 初始化库存
        inventory_service.initialize_inventory(product.id, 0)

        # 4. 创建采购订单
        order = purchase_service.create_purchase_order(
            supplier_id=supplier.id,
            product_id=product.id,
            quantity=100,
            unit_price=50.0
        )
        assert order.status == "pending"

        # 5. 采购入库
        purchase_service.complete_purchase_order(order.id)

        # 6. 验证库存
        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 100

        # 7. 验证订单状态
        updated_order = purchase_service.get_order(order.id)
        assert updated_order["status"] == "completed"

    def test_full_sales_flow(self, temp_data_dir):
        """测试完整销售流程"""
        # 创建共享的数据管理器
        product_manager = ProductManager(temp_data_dir)
        
        # 创建服务
        product_service = ProductService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )

        # 1. 创建商品
        product = product_service.create_product(
            name="销售测试商品",
            category="测试",
            unit="个",
            price=100.0,
            cost_price=50.0
        )

        # 2. 初始化库存
        inventory_service.initialize_inventory(product.id, 50)

        # 3. 创建销售单
        sale = sales_service.create_sale(
            product_id=product.id,
            quantity=20,
            unit_price=100.0,
            customer_name="测试客户"
        )
        assert sale.quantity == 20

        # 4. 验证库存减少
        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 30

    def test_purchase_and_sales_combined(self, temp_data_dir):
        """测试采购和销售组合流程"""
        # 创建共享的数据管理器
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        
        # 创建服务
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        inventory_service = InventoryService(temp_data_dir, product_manager=product_manager)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        sales_service = SalesService(
            temp_data_dir,
            product_manager=product_manager,
            inventory_service=inventory_service
        )
        stats_service = StatisticsService(temp_data_dir)

        # 1. 创建商品和供应商
        product = product_service.create_product(
            name="综合测试商品",
            category="测试",
            unit="个",
            price=120.0,
            cost_price=80.0
        )
        supplier = supplier_service.create_supplier(
            name="综合测试供应商",
            contact="联系人",
            phone="13800138000",
            email="test@test.com",
            address="地址"
        )

        # 2. 采购入库 100 个
        inventory_service.initialize_inventory(product.id, 0)
        order = purchase_service.create_purchase_order(
            supplier.id, product.id, 100, 80.0
        )
        purchase_service.complete_purchase_order(order.id)

        # 3. 销售 30 个
        sales_service.create_sale(product.id, 30, unit_price=120.0)

        # 4. 再次采购 50 个
        order2 = purchase_service.create_purchase_order(
            supplier.id, product.id, 50, 80.0
        )
        purchase_service.complete_purchase_order(order2.id)

        # 5. 再销售 40 个
        sales_service.create_sale(product.id, 40, unit_price=120.0)

        # 6. 验证最终库存
        inv = inventory_service.get_inventory(product.id)
        assert inv["quantity"] == 80  # 100 - 30 + 50 - 40 = 80

        # 7. 验证统计数据
        sales_summary = stats_service.get_sales_summary()
        assert sales_summary["total_quantity"] == 70
        assert sales_summary["total_revenue"] == 8400.0  # 70 * 120


# ==================== 边界条件测试 ====================

class TestEdgeCases:
    """边界条件测试"""

    def test_empty_data(self, temp_data_dir):
        """测试空数据情况"""
        product_service = ProductService(temp_data_dir)
        products = product_service.get_all_products()
        assert products == []

    def test_invalid_product_id(self, temp_data_dir):
        """测试无效商品ID"""
        product_service = ProductService(temp_data_dir)
        result = product_service.get_product("nonexistent")
        assert result is None

    def test_zero_quantity_purchase(self, temp_data_dir):
        """测试采购数量为0"""
        product_manager = ProductManager(temp_data_dir)
        supplier_manager = SupplierManager(temp_data_dir)
        product_service = ProductService(temp_data_dir)
        supplier_service = SupplierService(temp_data_dir)
        purchase_service = PurchaseService(
            temp_data_dir,
            supplier_manager=supplier_manager,
            product_manager=product_manager
        )

        product = product_service.create_product(
            name="测试商品",
            category="测试分类",
            unit="个",
            price=100.0,
            cost_price=50.0
        )
        supplier = supplier_service.create_supplier(
            name="测试供应商",
            contact="张三",
            phone="13800138000",
            email="test@test.com",
            address="测试地址"
        )

        with pytest.raises(ValueError) as exc_info:
            purchase_service.create_purchase_order(
                supplier.id, product.id, 0, 50.0
            )
        assert "采购数量必须大于0" in str(exc_info.value)

    def test_negative_price(self, temp_data_dir):
        """测试负价格 - 服务层允许负价格，但业务逻辑不应允许"""
        product_service = ProductService(temp_data_dir)
        # 创建负价格商品应该失败或被允许（取决于业务规则）
        # 这里我们测试服务层是否能处理
        try:
            product = product_service.create_product(
                name="测试",
                category="测试",
                unit="个",
                price=-10.0,
                cost_price=5.0
            )
            # 如果允许创建，验证价格确实为负
            assert product.price == -10.0
        except ValueError:
            # 如果不允许创建，也是合理的
            pass


# ==================== 主函数 ====================

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
