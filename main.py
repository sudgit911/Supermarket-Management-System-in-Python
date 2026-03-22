"""
超市采购管理系统主程序
命令行交互界面
"""
import os
import sys
from typing import Optional

from services import (
    ProductService, SupplierService, InventoryService, 
    PurchaseService, SalesService, StatisticsService
)


class SupermarketApp:
    """超市管理系统应用"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.product_service = ProductService(data_dir)
        self.supplier_service = SupplierService(data_dir)
        self.inventory_service = InventoryService(data_dir)
        self.purchase_service = PurchaseService(data_dir)
        self.sales_service = SalesService(data_dir)
        self.stats_service = StatisticsService(data_dir)
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 80)
        print(title.center(80))
        print("=" * 80 + "\n")
    
    def print_menu(self, title: str, options: list):
        """打印菜单"""
        self.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print(f"  0. 返回上级菜单")
        print()
    
    def get_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """获取用户输入"""
        while True:
            value = input(prompt).strip()
            if value:
                return value
            if not required:
                return None
            print("  ⚠️  此项为必填项，请重新输入")
    
    def get_int_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """获取整数输入"""
        while True:
            try:
                value = int(input(prompt).strip())
                if min_val is not None and value < min_val:
                    print(f"  ⚠️  输入值不能小于 {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"  ⚠️  输入值不能大于 {max_val}")
                    continue
                return value
            except ValueError:
                print("  ⚠️  请输入有效的整数")
    
    def get_float_input(self, prompt: str, min_val: float = 0) -> float:
        """获取浮点数输入"""
        while True:
            try:
                value = float(input(prompt).strip())
                if value < min_val:
                    print(f"  ⚠️  输入值不能小于 {min_val}")
                    continue
                return value
            except ValueError:
                print("  ⚠️  请输入有效的数字")
    
    def pause(self):
        """暂停等待用户按键"""
        input("\n  按回车键继续...")
    
    # ==================== 商品管理 ====================
    def product_menu(self):
        """商品管理菜单"""
        while True:
            self.print_menu("商品管理", [
                "查看所有商品",
                "添加商品",
                "修改商品",
                "删除商品",
                "搜索商品"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 5)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_products()
            elif choice == 2:
                self.add_product()
            elif choice == 3:
                self.edit_product()
            elif choice == 4:
                self.delete_product()
            elif choice == 5:
                self.search_products()
    
    def list_products(self):
        """查看所有商品"""
        self.print_header("商品列表")
        products = self.product_service.get_all_products()
        
        if not products:
            print("  暂无商品数据")
        else:
            print(f"  {'ID':<10} {'名称':<20} {'分类':<12} {'单位':<8} {'售价':<10} {'成本':<10}")
            print("  " + "-" * 75)
            for p in products:
                print(f"  {p['id']:<10} {p['name'][:18]:<20} {p['category'][:10]:<12} "
                      f"{p['unit']:<8} ¥{p['price']:<9.2f} ¥{p['cost_price']:<9.2f}")
        self.pause()
    
    def add_product(self):
        """添加商品"""
        self.print_header("添加商品")
        try:
            name = self.get_input("  商品名称: ")
            category = self.get_input("  商品分类: ")
            unit = self.get_input("  计量单位(个/斤/箱等): ")
            price = self.get_float_input("  销售单价: ", 0)
            cost_price = self.get_float_input("  成本单价: ", 0)
            description = self.get_input("  商品描述(可选): ", required=False) or ""
            
            product = self.product_service.create_product(
                name, category, unit, price, cost_price, description
            )
            
            # 初始化库存
            self.inventory_service.initialize_inventory(product.id, 0)
            
            print(f"\n  ✅ 商品添加成功！ID: {product.id}")
        except Exception as e:
            print(f"\n  ❌ 添加失败: {e}")
        self.pause()
    
    def edit_product(self):
        """修改商品"""
        self.print_header("修改商品")
        product_id = self.get_input("  请输入商品ID: ")
        product = self.product_service.get_product(product_id)
        
        if not product:
            print(f"\n  ❌ 商品不存在: {product_id}")
            self.pause()
            return
        
        print(f"\n  当前信息: {product['name']} (分类: {product['category']})")
        print("  直接回车表示不修改该字段\n")
        
        updates = {}
        name = self.get_input(f"  商品名称 [{product['name']}]: ", required=False)
        if name:
            updates['name'] = name
        
        category = self.get_input(f"  商品分类 [{product['category']}]: ", required=False)
        if category:
            updates['category'] = category
        
        unit = self.get_input(f"  计量单位 [{product['unit']}]: ", required=False)
        if unit:
            updates['unit'] = unit
        
        price_str = input(f"  销售单价 [¥{product['price']}]: ").strip()
        if price_str:
            updates['price'] = float(price_str)
        
        cost_str = input(f"  成本单价 [¥{product['cost_price']}]: ").strip()
        if cost_str:
            updates['cost_price'] = float(cost_str)
        
        if updates:
            if self.product_service.update_product(product_id, **updates):
                print("\n  ✅ 商品修改成功！")
            else:
                print("\n  ❌ 修改失败")
        else:
            print("\n  ℹ️ 未做任何修改")
        self.pause()
    
    def delete_product(self):
        """删除商品"""
        self.print_header("删除商品")
        product_id = self.get_input("  请输入要删除的商品ID: ")
        product = self.product_service.get_product(product_id)
        
        if not product:
            print(f"\n  ❌ 商品不存在: {product_id}")
            self.pause()
            return
        
        print(f"\n  即将删除商品: {product['name']}")
        confirm = self.get_input("  确认删除？(输入 yes 确认): ", required=False)
        
        if confirm and confirm.lower() == 'yes':
            if self.product_service.delete_product(product_id):
                print("\n  ✅ 商品删除成功！")
            else:
                print("\n  ❌ 删除失败")
        else:
            print("\n  ℹ️ 已取消删除")
        self.pause()
    
    def search_products(self):
        """搜索商品"""
        self.print_header("搜索商品")
        keyword = self.get_input("  请输入搜索关键词: ")
        
        products = self.product_service.search_products(keyword)
        
        if not products:
            print(f"\n  未找到包含 '{keyword}' 的商品")
        else:
            print(f"\n  找到 {len(products)} 个商品:\n")
            print(f"  {'ID':<10} {'名称':<20} {'分类':<12} {'售价':<10}")
            print("  " + "-" * 55)
            for p in products:
                print(f"  {p['id']:<10} {p['name'][:18]:<20} {p['category'][:10]:<12} ¥{p['price']:<9.2f}")
        self.pause()
    
    # ==================== 供应商管理 ====================
    def supplier_menu(self):
        """供应商管理菜单"""
        while True:
            self.print_menu("供应商管理", [
                "查看所有供应商",
                "添加供应商",
                "修改供应商",
                "删除供应商",
                "搜索供应商"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 5)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_suppliers()
            elif choice == 2:
                self.add_supplier()
            elif choice == 3:
                self.edit_supplier()
            elif choice == 4:
                self.delete_supplier()
            elif choice == 5:
                self.search_suppliers()
    
    def list_suppliers(self):
        """查看所有供应商"""
        self.print_header("供应商列表")
        suppliers = self.supplier_service.get_all_suppliers()
        
        if not suppliers:
            print("  暂无供应商数据")
        else:
            print(f"  {'ID':<10} {'名称':<20} {'联系人':<10} {'电话':<15} {'状态':<8}")
            print("  " + "-" * 70)
            for s in suppliers:
                status = "活跃" if s['status'] == 'active' else "停用"
                print(f"  {s['id']:<10} {s['name'][:18]:<20} {s['contact'][:8]:<10} "
                      f"{s['phone']:<15} {status:<8}")
        self.pause()
    
    def add_supplier(self):
        """添加供应商"""
        self.print_header("添加供应商")
        try:
            name = self.get_input("  供应商名称: ")
            contact = self.get_input("  联系人: ")
            phone = self.get_input("  联系电话: ")
            email = self.get_input("  电子邮箱: ", required=False) or ""
            address = self.get_input("  地址: ", required=False) or ""
            
            supplier = self.supplier_service.create_supplier(
                name, contact, phone, email, address
            )
            print(f"\n  ✅ 供应商添加成功！ID: {supplier.id}")
        except Exception as e:
            print(f"\n  ❌ 添加失败: {e}")
        self.pause()
    
    def edit_supplier(self):
        """修改供应商"""
        self.print_header("修改供应商")
        supplier_id = self.get_input("  请输入供应商ID: ")
        supplier = self.supplier_service.get_supplier(supplier_id)
        
        if not supplier:
            print(f"\n  ❌ 供应商不存在: {supplier_id}")
            self.pause()
            return
        
        print(f"\n  当前信息: {supplier['name']}\n")
        
        updates = {}
        fields = [
            ('name', '供应商名称'),
            ('contact', '联系人'),
            ('phone', '联系电话'),
            ('email', '电子邮箱'),
            ('address', '地址'),
            ('status', '状态(active/inactive)')
        ]
        
        for field, label in fields:
            value = self.get_input(f"  {label} [{supplier.get(field, '')}]: ", required=False)
            if value:
                updates[field] = value
        
        if updates:
            if self.supplier_service.update_supplier(supplier_id, **updates):
                print("\n  ✅ 供应商修改成功！")
            else:
                print("\n  ❌ 修改失败")
        else:
            print("\n  ℹ️ 未做任何修改")
        self.pause()
    
    def delete_supplier(self):
        """删除供应商"""
        self.print_header("删除供应商")
        supplier_id = self.get_input("  请输入要删除的供应商ID: ")
        supplier = self.supplier_service.get_supplier(supplier_id)
        
        if not supplier:
            print(f"\n  ❌ 供应商不存在: {supplier_id}")
            self.pause()
            return
        
        print(f"\n  即将删除供应商: {supplier['name']}")
        confirm = self.get_input("  确认删除？(输入 yes 确认): ", required=False)
        
        if confirm and confirm.lower() == 'yes':
            if self.supplier_service.delete_supplier(supplier_id):
                print("\n  ✅ 供应商删除成功！")
            else:
                print("\n  ❌ 删除失败")
        else:
            print("\n  ℹ️ 已取消删除")
        self.pause()
    
    def search_suppliers(self):
        """搜索供应商"""
        self.print_header("搜索供应商")
        keyword = self.get_input("  请输入搜索关键词: ")
        
        suppliers = self.supplier_service.search_suppliers(keyword)
        
        if not suppliers:
            print(f"\n  未找到包含 '{keyword}' 的供应商")
        else:
            print(f"\n  找到 {len(suppliers)} 个供应商:\n")
            print(f"  {'ID':<10} {'名称':<20} {'联系人':<10} {'电话':<15}")
            print("  " + "-" * 60)
            for s in suppliers:
                print(f"  {s['id']:<10} {s['name'][:18]:<20} {s['contact'][:8]:<10} {s['phone']:<15}")
        self.pause()
    
    # ==================== 库存管理 ====================
    def inventory_menu(self):
        """库存管理菜单"""
        while True:
            self.print_menu("库存管理", [
                "查看所有库存",
                "查看库存详情",
                "库存预警查询",
                "修改库存设置",
                "手动入库"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 5)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_inventory()
            elif choice == 2:
                self.view_inventory_detail()
            elif choice == 3:
                self.stock_alerts()
            elif choice == 4:
                self.edit_inventory_settings()
            elif choice == 5:
                self.manual_stock_in()
    
    def list_inventory(self):
        """查看所有库存"""
        self.print_header("库存列表")
        inventory = self.inventory_service.get_all_inventory()
        
        if not inventory:
            print("  暂无库存数据")
        else:
            print(f"  {'商品名称':<20} {'分类':<12} {'库存量':<10} {'单位':<8} {'仓库位置':<15}")
            print("  " + "-" * 70)
            for inv in inventory:
                name = inv.get('product_name', '未知')[:18]
                category = inv.get('product_category', '-')[:10]
                qty = inv.get('quantity', 0)
                unit = inv.get('unit', '-')
                location = inv.get('warehouse_location', '-')[:13]
                print(f"  {name:<20} {category:<12} {qty:<10} {unit:<8} {location:<15}")
        self.pause()
    
    def view_inventory_detail(self):
        """查看库存详情"""
        self.print_header("库存详情")
        product_id = self.get_input("  请输入商品ID: ")
        inv = self.inventory_service.get_inventory(product_id)
        
        if not inv:
            print(f"\n  ❌ 库存记录不存在: {product_id}")
        else:
            print(f"\n  商品名称: {inv.get('product_name', '未知')}")
            print(f"  商品分类: {inv.get('product_category', '-')}")
            print(f"  当前库存: {inv.get('quantity', 0)} {inv.get('unit', '')}")
            print(f"  最低库存: {inv.get('min_stock', 0)}")
            print(f"  最高库存: {inv.get('max_stock', 0)}")
            print(f"  仓库位置: {inv.get('warehouse_location', '-')}")
            print(f"  最后更新: {inv.get('last_updated', '-')}")
            
            if inv.get('quantity', 0) <= inv.get('min_stock', 0):
                print("\n  ⚠️  警告：库存不足！")
        self.pause()
    
    def stock_alerts(self):
        """库存预警查询"""
        self.print_header("库存预警")
        
        low_stock = self.inventory_service.get_low_stock_items()
        if low_stock:
            print("\n  ⚠️  低库存商品:\n")
            print(f"  {'商品名称':<20} {'当前库存':<10} {'最低库存':<10} {'单位':<8}")
            print("  " + "-" * 55)
            for item in low_stock:
                print(f"  {item.get('product_name', '-')[:18]:<20} "
                      f"{item.get('quantity', 0):<10} "
                      f"{item.get('min_stock', 0):<10} "
                      f"{item.get('unit', '-'):<8}")
        else:
            print("\n  ✅ 没有低库存商品")
        self.pause()
    
    def edit_inventory_settings(self):
        """修改库存设置"""
        self.print_header("修改库存设置")
        product_id = self.get_input("  请输入商品ID: ")
        inv = self.inventory_service.get_inventory(product_id)
        
        if not inv:
            print(f"\n  ❌ 库存记录不存在: {product_id}")
            self.pause()
            return
        
        print(f"\n  当前设置:\n")
        print(f"  最低库存: {inv.get('min_stock', 0)}")
        print(f"  最高库存: {inv.get('max_stock', 0)}")
        print(f"  仓库位置: {inv.get('warehouse_location', '-')}")
        print("\n  直接回车表示不修改\n")
        
        min_stock_str = input("  最低库存: ").strip()
        max_stock_str = input("  最高库存: ").strip()
        location = self.get_input("  仓库位置: ", required=False)
        
        try:
            self.inventory_service.update_stock_settings(
                product_id,
                min_stock=int(min_stock_str) if min_stock_str else None,
                max_stock=int(max_stock_str) if max_stock_str else None,
                warehouse_location=location if location else None
            )
            print("\n  ✅ 设置更新成功！")
        except Exception as e:
            print(f"\n  ❌ 更新失败: {e}")
        self.pause()
    
    def manual_stock_in(self):
        """手动入库"""
        self.print_header("手动入库")
        product_id = self.get_input("  请输入商品ID: ")
        
        product = self.product_service.get_product(product_id)
        if not product:
            print(f"\n  ❌ 商品不存在: {product_id}")
            self.pause()
            return
        
        print(f"\n  商品: {product['name']}")
        quantity = self.get_int_input("  入库数量: ", 1)
        
        try:
            self.inventory_service.add_stock(product_id, quantity)
            print(f"\n  ✅ 入库成功！增加 {quantity} {product['unit']}")
        except Exception as e:
            print(f"\n  ❌ 入库失败: {e}")
        self.pause()
    
    # ==================== 采购管理 ====================
    def purchase_menu(self):
        """采购管理菜单"""
        while True:
            self.print_menu("采购管理", [
                "查看所有采购订单",
                "创建采购订单",
                "采购入库",
                "取消采购订单",
                "查看待处理订单"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 5)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_purchase_orders()
            elif choice == 2:
                self.create_purchase_order()
            elif choice == 3:
                self.complete_purchase()
            elif choice == 4:
                self.cancel_purchase()
            elif choice == 5:
                self.list_pending_orders()
    
    def list_purchase_orders(self):
        """查看所有采购订单"""
        self.print_header("采购订单列表")
        orders = self.purchase_service.get_all_orders()
        
        if not orders:
            print("  暂无采购订单")
        else:
            print(f"  {'订单ID':<10} {'供应商':<15} {'商品':<15} {'数量':<8} {'金额':<10} {'状态':<8}")
            print("  " + "-" * 75)
            for o in orders:
                status_map = {'pending': '待处理', 'completed': '已完成', 'cancelled': '已取消'}
                status = status_map.get(o['status'], o['status'])
                print(f"  {o['id']:<10} {o.get('supplier_name', '-')[:13]:<15} "
                      f"{o.get('product_name', '-')[:13]:<15} {o['quantity']:<8} "
                      f"¥{o['total_amount']:<9.2f} {status:<8}")
        self.pause()
    
    def create_purchase_order(self):
        """创建采购订单"""
        self.print_header("创建采购订单")
        
        # 显示可用供应商
        suppliers = self.supplier_service.get_active_suppliers()
        if not suppliers:
            print("  ❌ 没有可用的供应商，请先添加供应商")
            self.pause()
            return
        
        print("  可用供应商:")
        for s in suppliers:
            print(f"    {s['id']}: {s['name']}")
        print()
        
        supplier_id = self.get_input("  供应商ID: ")
        supplier = self.supplier_service.get_supplier(supplier_id)
        if not supplier:
            print(f"\n  ❌ 供应商不存在: {supplier_id}")
            self.pause()
            return
        
        # 显示可用商品
        products = self.product_service.get_all_products()
        if not products:
            print("  ❌ 没有商品，请先添加商品")
            self.pause()
            return
        
        print("\n  可用商品:")
        for p in products:
            print(f"    {p['id']}: {p['name']} (¥{p['cost_price']})")
        print()
        
        product_id = self.get_input("  商品ID: ")
        product = self.product_service.get_product(product_id)
        if not product:
            print(f"\n  ❌ 商品不存在: {product_id}")
            self.pause()
            return
        
        quantity = self.get_int_input("  采购数量: ", 1)
        unit_price = self.get_float_input("  采购单价: ", 0.01)
        notes = self.get_input("  备注(可选): ", required=False) or ""
        
        try:
            order = self.purchase_service.create_purchase_order(
                supplier_id, product_id, quantity, unit_price, notes
            )
            print(f"\n  ✅ 采购订单创建成功！订单ID: {order.id}")
            print(f"  订单金额: ¥{order.total_amount:.2f}")
        except Exception as e:
            print(f"\n  ❌ 创建失败: {e}")
        self.pause()
    
    def complete_purchase(self):
        """采购入库"""
        self.print_header("采购入库")
        
        pending_orders = self.purchase_service.get_pending_orders()
        if not pending_orders:
            print("  没有待处理的采购订单")
            self.pause()
            return
        
        print("  待处理订单:")
        for o in pending_orders:
            print(f"    {o['id']}: {o.get('product_name')} x {o['quantity']} from {o.get('supplier_name')}")
        print()
        
        order_id = self.get_input("  请输入要入库的订单ID: ")
        
        try:
            if self.purchase_service.complete_purchase_order(order_id):
                print("\n  ✅ 入库成功！库存已更新")
            else:
                print("\n  ❌ 入库失败")
        except Exception as e:
            print(f"\n  ❌ 入库失败: {e}")
        self.pause()
    
    def cancel_purchase(self):
        """取消采购订单"""
        self.print_header("取消采购订单")
        order_id = self.get_input("  请输入要取消的订单ID: ")
        
        order = self.purchase_service.get_order(order_id)
        if not order:
            print(f"\n  ❌ 订单不存在: {order_id}")
            self.pause()
            return
        
        if order['status'] != 'pending':
            print(f"\n  ❌ 只能取消待处理的订单，当前状态: {order['status']}")
            self.pause()
            return
        
        confirm = self.get_input("  确认取消？(输入 yes 确认): ", required=False)
        if confirm and confirm.lower() == 'yes':
            try:
                if self.purchase_service.cancel_purchase_order(order_id):
                    print("\n  ✅ 订单已取消")
                else:
                    print("\n  ❌ 取消失败")
            except Exception as e:
                print(f"\n  ❌ 取消失败: {e}")
        else:
            print("\n  ℹ️ 已取消操作")
        self.pause()
    
    def list_pending_orders(self):
        """查看待处理订单"""
        self.print_header("待处理采购订单")
        orders = self.purchase_service.get_pending_orders()
        
        if not orders:
            print("  没有待处理的采购订单")
        else:
            print(f"  {'订单ID':<10} {'供应商':<15} {'商品':<15} {'数量':<8} {'金额':<10} {'下单日期':<12}")
            print("  " + "-" * 75)
            for o in orders:
                print(f"  {o['id']:<10} {o.get('supplier_name', '-')[:13]:<15} "
                      f"{o.get('product_name', '-')[:13]:<15} {o['quantity']:<8} "
                      f"¥{o['total_amount']:<9.2f} {o['order_date']:<12}")
        self.pause()
    
    # ==================== 销售管理 ====================
    def sales_menu(self):
        """销售管理菜单"""
        while True:
            self.print_menu("销售管理", [
                "查看销售记录",
                "创建销售单",
                "按商品查询销售",
                "按日期查询销售"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 4)
            
            if choice == 0:
                break
            elif choice == 1:
                self.list_sales()
            elif choice == 2:
                self.create_sale()
            elif choice == 3:
                self.sales_by_product()
            elif choice == 4:
                self.sales_by_date()
    
    def list_sales(self):
        """查看销售记录"""
        self.print_header("销售记录列表")
        sales = self.sales_service.get_all_sales()
        
        if not sales:
            print("  暂无销售记录")
        else:
            print(f"  {'销售ID':<10} {'商品':<15} {'数量':<8} {'金额':<10} {'日期':<12} {'客户':<10}")
            print("  " + "-" * 70)
            for s in sales:
                print(f"  {s['id']:<10} {s.get('product_name', '-')[:13]:<15} "
                      f"{s['quantity']:<8} ¥{s['total_amount']:<9.2f} "
                      f"{s['sale_date']:<12} {s.get('customer_name', '-')[:8]:<10}")
        self.pause()
    
    def create_sale(self):
        """创建销售单"""
        self.print_header("创建销售单")
        
        # 显示有库存的商品
        inventory = self.inventory_service.get_all_inventory()
        available = [inv for inv in inventory if inv.get('quantity', 0) > 0]
        
        if not available:
            print("  ❌ 没有可销售的库存商品")
            self.pause()
            return
        
        print("  可销售商品:")
        for inv in available:
            print(f"    {inv.get('product_id')}: {inv.get('product_name')} "
                  f"(库存: {inv.get('quantity')} {inv.get('unit')}, "
                  f"售价: ¥{self.product_service.get_product(inv.get('product_id')).get('price', 0)})")
        print()
        
        product_id = self.get_input("  商品ID: ")
        product = self.product_service.get_product(product_id)
        if not product:
            print(f"\n  ❌ 商品不存在: {product_id}")
            self.pause()
            return
        
        inv = self.inventory_service.get_inventory(product_id)
        if not inv or inv.get('quantity', 0) <= 0:
            print(f"\n  ❌ 商品无库存")
            self.pause()
            return
        
        max_qty = inv.get('quantity', 0)
        print(f"\n  商品: {product['name']}")
        print(f"  当前库存: {max_qty} {product['unit']}")
        print(f"  销售单价: ¥{product['price']}")
        
        quantity = self.get_int_input(f"  销售数量(最大{max_qty}): ", 1, max_qty)
        
        price_str = input(f"  销售单价[¥{product['price']}]: ").strip()
        unit_price = float(price_str) if price_str else product['price']
        
        customer = self.get_input("  客户名称(可选): ", required=False) or ""
        notes = self.get_input("  备注(可选): ", required=False) or ""
        
        try:
            sale = self.sales_service.create_sale(
                product_id, quantity, unit_price, customer, notes
            )
            print(f"\n  ✅ 销售单创建成功！销售ID: {sale.id}")
            print(f"  销售金额: ¥{sale.total_amount:.2f}")
        except Exception as e:
            print(f"\n  ❌ 创建失败: {e}")
        self.pause()
    
    def sales_by_product(self):
        """按商品查询销售"""
        self.print_header("按商品查询销售")
        product_id = self.get_input("  请输入商品ID: ")
        
        sales = self.sales_service.get_sales_by_product(product_id)
        product = self.product_service.get_product(product_id)
        
        if not sales:
            print(f"\n  该商品暂无销售记录")
        else:
            print(f"\n  商品: {product['name'] if product else '未知'}\n")
            print(f"  {'销售ID':<10} {'数量':<8} {'金额':<10} {'日期':<12}")
            print("  " + "-" * 45)
            total_qty = 0
            total_amount = 0
            for s in sales:
                print(f"  {s['id']:<10} {s['quantity']:<8} ¥{s['total_amount']:<9.2f} {s['sale_date']:<12}")
                total_qty += s['quantity']
                total_amount += s['total_amount']
            print("  " + "-" * 45)
            print(f"  {'合计':<10} {total_qty:<8} ¥{total_amount:<9.2f}")
        self.pause()
    
    def sales_by_date(self):
        """按日期查询销售"""
        self.print_header("按日期查询销售")
        print("  日期格式: YYYY-MM-DD\n")
        
        start_date = self.get_input("  开始日期: ")
        end_date = self.get_input("  结束日期: ")
        
        sales = self.sales_service.get_sales_by_date_range(start_date, end_date)
        
        if not sales:
            print(f"\n  该时间段暂无销售记录")
        else:
            print(f"\n  统计期间: {start_date} 至 {end_date}\n")
            print(f"  {'销售ID':<10} {'商品':<15} {'数量':<8} {'金额':<10} {'日期':<12}")
            print("  " + "-" * 60)
            total_qty = 0
            total_amount = 0
            for s in sales:
                print(f"  {s['id']:<10} {s.get('product_name', '-')[:13]:<15} "
                      f"{s['quantity']:<8} ¥{s['total_amount']:<9.2f} {s['sale_date']:<12}")
                total_qty += s['quantity']
                total_amount += s['total_amount']
            print("  " + "-" * 60)
            print(f"  {'合计':<10} {'':<15} {total_qty:<8} ¥{total_amount:<9.2f}")
        self.pause()
    
    # ==================== 数据统计 ====================
    def statistics_menu(self):
        """数据统计菜单"""
        while True:
            self.print_menu("数据统计", [
                "库存统计",
                "销售统计",
                "采购统计",
                "利润分析",
                "库存报表",
                "销售报表"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 6)
            
            if choice == 0:
                break
            elif choice == 1:
                self.inventory_stats()
            elif choice == 2:
                self.sales_stats()
            elif choice == 3:
                self.purchase_stats()
            elif choice == 4:
                self.profit_analysis()
            elif choice == 5:
                self.inventory_report()
            elif choice == 6:
                self.sales_report()
    
    def inventory_stats(self):
        """库存统计"""
        self.print_header("库存统计")
        stats = self.stats_service.get_inventory_summary()
        
        print(f"  商品总数: {stats['total_products']}")
        print(f"  库存总件数: {stats['total_items']}")
        print(f"  库存总价值: ¥{stats['total_inventory_value']:.2f}")
        print(f"  低库存商品数: {stats['low_stock_count']}")
        self.pause()
    
    def sales_stats(self):
        """销售统计"""
        self.print_header("销售统计")
        stats = self.stats_service.get_sales_summary()
        
        print(f"  销售笔数: {stats['total_sales']}")
        print(f"  销售总量: {stats['total_quantity']}")
        print(f"  销售总额: ¥{stats['total_revenue']:.2f}")
        
        if stats['product_sales']:
            print("\n  按商品统计:")
            print(f"  {'商品名称':<20} {'销售数量':<12} {'销售额':<15}")
            print("  " + "-" * 50)
            for pid, s in stats['product_sales'].items():
                print(f"  {s['product_name'][:18]:<20} {s['quantity']:<12} ¥{s['revenue']:<14.2f}")
        self.pause()
    
    def purchase_stats(self):
        """采购统计"""
        self.print_header("采购统计")
        stats = self.stats_service.get_purchase_summary()
        
        print(f"  订单总数: {stats['total_orders']}")
        print(f"  已完成: {stats['completed_orders']}")
        print(f"  待处理: {stats['pending_orders']}")
        print(f"  采购总额: ¥{stats['total_amount']:.2f}")
        
        if stats['supplier_stats']:
            print("\n  按供应商统计:")
            print(f"  {'供应商名称':<20} {'订单数':<10} {'采购金额':<15}")
            print("  " + "-" * 50)
            for sid, s in stats['supplier_stats'].items():
                print(f"  {s['supplier_name'][:18]:<20} {s['order_count']:<10} ¥{s['total_amount']:<14.2f}")
        self.pause()
    
    def profit_analysis(self):
        """利润分析"""
        self.print_header("利润分析")
        stats = self.stats_service.get_profit_analysis()
        
        print(f"  销售收入: ¥{stats['revenue']:.2f}")
        print(f"  采购成本: ¥{stats['cost']:.2f}")
        print(f"  毛利润: ¥{stats['profit']:.2f}")
        print(f"  毛利率: {stats['profit_margin']:.2f}%")
        self.pause()
    
    def inventory_report(self):
        """库存报表"""
        self.clear_screen()
        report = self.stats_service.generate_inventory_report()
        print(report)
        self.pause()
    
    def sales_report(self):
        """销售报表"""
        self.clear_screen()
        print("\n  日期格式: YYYY-MM-DD (直接回车查询全部)\n")
        start = self.get_input("  开始日期(可选): ", required=False) or None
        end = self.get_input("  结束日期(可选): ", required=False) or None
        
        self.clear_screen()
        report = self.stats_service.generate_sales_report(start, end)
        print(report)
        self.pause()
    
    # ==================== 查询功能 ====================
    def query_menu(self):
        """查询菜单"""
        while True:
            self.print_menu("综合查询", [
                "商品查询",
                "供应商查询",
                "库存查询",
                "采购订单查询",
                "销售记录查询"
            ])
            choice = self.get_int_input("  请选择操作: ", 0, 5)
            
            if choice == 0:
                break
            elif choice == 1:
                self.search_products()
            elif choice == 2:
                self.search_suppliers()
            elif choice == 3:
                self.query_inventory()
            elif choice == 4:
                self.query_purchase()
            elif choice == 5:
                self.query_sales()
    
    def query_inventory(self):
        """库存查询"""
        self.print_header("库存查询")
        keyword = self.get_input("  请输入商品名称关键词: ")
        
        products = self.product_service.search_products(keyword)
        if not products:
            print(f"\n  未找到相关商品")
        else:
            print(f"\n  找到 {len(products)} 个商品:\n")
            print(f"  {'商品名称':<20} {'当前库存':<10} {'最低库存':<10} {'状态':<10}")
            print("  " + "-" * 55)
            for p in products:
                inv = self.inventory_service.get_inventory(p['id'])
                if inv:
                    qty = inv.get('quantity', 0)
                    min_stock = inv.get('min_stock', 0)
                    status = "⚠️ 不足" if qty <= min_stock else "✅ 正常"
                    print(f"  {p['name'][:18]:<20} {qty:<10} {min_stock:<10} {status:<10}")
                else:
                    print(f"  {p['name'][:18]:<20} {'无库存':<10} {'-':<10} {'❌ 未初始化':<10}")
        self.pause()
    
    def query_purchase(self):
        """采购订单查询"""
        self.print_header("采购订单查询")
        print("  1. 按订单ID查询")
        print("  2. 按供应商查询")
        print("  0. 返回\n")
        
        choice = self.get_int_input("  请选择: ", 0, 2)
        
        if choice == 1:
            order_id = self.get_input("  订单ID: ")
            order = self.purchase_service.get_order(order_id)
            if order:
                print(f"\n  订单详情:")
                print(f"  订单ID: {order['id']}")
                print(f"  供应商: {order.get('supplier_name', '-')}")
                print(f"  商品: {order.get('product_name', '-')}")
                print(f"  数量: {order['quantity']}")
                print(f"  单价: ¥{order['unit_price']:.2f}")
                print(f"  总金额: ¥{order['total_amount']:.2f}")
                print(f"  状态: {order['status']}")
                print(f"  下单日期: {order['order_date']}")
                if order.get('delivery_date'):
                    print(f"  入库日期: {order['delivery_date']}")
            else:
                print(f"\n  订单不存在: {order_id}")
        elif choice == 2:
            supplier_id = self.get_input("  供应商ID: ")
            orders = self.purchase_service.manager.get_by_supplier(supplier_id)
            if orders:
                supplier = self.supplier_service.get_supplier(supplier_id)
                print(f"\n  供应商: {supplier['name'] if supplier else '未知'}\n")
                for o in orders:
                    print(f"  {o['id']}: {o.get('product_id')} x {o['quantity']} - {o['status']}")
            else:
                print(f"\n  该供应商暂无采购订单")
        self.pause()
    
    def query_sales(self):
        """销售记录查询"""
        self.print_header("销售记录查询")
        sale_id = self.get_input("  销售记录ID: ")
        
        sale = self.sales_service.get_sale(sale_id)
        if sale:
            print(f"\n  销售详情:")
            print(f"  销售ID: {sale['id']}")
            print(f"  商品: {sale.get('product_name', '-')}")
            print(f"  数量: {sale['quantity']}")
            print(f"  单价: ¥{sale['unit_price']:.2f}")
            print(f"  总金额: ¥{sale['total_amount']:.2f}")
            print(f"  销售日期: {sale['sale_date']}")
            print(f"  客户: {sale.get('customer_name', '-')}")
        else:
            print(f"\n  销售记录不存在: {sale_id}")
        self.pause()
    
    # ==================== 主菜单 ====================
    def main_menu(self):
        """主菜单"""
        while True:
            self.print_menu("超市采购管理系统", [
                "商品管理",
                "供应商管理",
                "库存管理",
                "采购管理",
                "销售管理",
                "数据统计",
                "综合查询"
            ])
            choice = self.get_int_input("  请选择功能模块: ", 0, 7)
            
            if choice == 0:
                self.print_header("感谢使用")
                print("  系统已退出，再见！\n")
                break
            elif choice == 1:
                self.product_menu()
            elif choice == 2:
                self.supplier_menu()
            elif choice == 3:
                self.inventory_menu()
            elif choice == 4:
                self.purchase_menu()
            elif choice == 5:
                self.sales_menu()
            elif choice == 6:
                self.statistics_menu()
            elif choice == 7:
                self.query_menu()


def main():
    """主函数"""
    app = SupermarketApp()
    
    # 显示欢迎信息
    app.clear_screen()
    print("\n" + "=" * 80)
    print("欢迎使用超市采购管理系统".center(80))
    print("=" * 80)
    print("\n  系统功能:")
    print("  - 商品管理: 添加、修改、删除、查询商品信息")
    print("  - 供应商管理: 管理供应商信息")
    print("  - 库存管理: 实时库存监控、预警")
    print("  - 采购管理: 采购订单、入库管理")
    print("  - 销售管理: 销售记录、库存自动扣减")
    print("  - 数据统计: 报表生成、利润分析")
    print("\n" + "=" * 80)
    input("\n  按回车键开始...")
    
    # 进入主菜单
    app.main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n  程序出错: {e}")
        sys.exit(1)
