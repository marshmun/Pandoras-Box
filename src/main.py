#!/usr/bin/env python3
"""
Inventory Tracking App - Main Application
Tracks inventory items, expenses, display items, and shrinkage
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbed_panel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from models.database import InventoryDatabase

# Set minimum window size
Window.size = (800, 600)


class InventoryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = InventoryDatabase()
        self.selected_item = None
    
    def build(self):
        """Build the main app UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(text='Inventory & Expense Tracker', size_hint_y=0.1, 
                     font_size='24sp', bold=True)
        main_layout.add_widget(title)
        
        # Tabbed interface
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Tab 1: Inventory
        inventory_tab = TabbedPanelItem(text='Inventory')
        inventory_tab.content = self.build_inventory_tab()
        tab_panel.add_widget(inventory_tab)
        
        # Tab 2: Expenses
        expenses_tab = TabbedPanelItem(text='Expenses')
        expenses_tab.content = self.build_expenses_tab()
        tab_panel.add_widget(expenses_tab)
        
        # Tab 3: Reports
        reports_tab = TabbedPanelItem(text='Reports')
        reports_tab.content = self.build_reports_tab()
        tab_panel.add_widget(reports_tab)
        
        main_layout.add_widget(tab_panel)
        
        return main_layout
    
    def build_inventory_tab(self):
        """Build inventory management tab"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add item button
        add_btn = Button(text='Add New Item', size_hint_y=0.1)
        add_btn.bind(on_press=self.show_add_item_dialog)
        layout.add_widget(add_btn)
        
        # Items list
        scroll = ScrollView()
        items_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        items_grid.bind(minimum_height=items_grid.setter('height'))
        
        items = self.db.get_all_items()
        for item in items:
            item_btn = Button(text=f"{item[1]} - Qty: {item[4]}", size_hint_y=None, height=40)
            item_btn.item_id = item[0]
            item_btn.bind(on_press=self.show_item_details)
            items_grid.add_widget(item_btn)
        
        scroll.add_widget(items_grid)
        layout.add_widget(scroll)
        
        return layout
    
    def build_expenses_tab(self):
        """Build expenses tab"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add expense button
        add_btn = Button(text='Add Expense', size_hint_y=0.1)
        add_btn.bind(on_press=self.show_add_expense_dialog)
        layout.add_widget(add_btn)
        
        # Expenses list
        scroll = ScrollView()
        expenses_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        expenses_grid.bind(minimum_height=expenses_grid.setter('height'))
        
        expenses = self.db.get_expenses(limit=20)
        for expense in expenses:
            expense_text = f"{expense[1]} - ${expense[3]:.2f} ({expense[2]})"
            expense_btn = Button(text=expense_text, size_hint_y=None, height=40)
            expenses_grid.add_widget(expense_btn)
        
        scroll.add_widget(expenses_grid)
        layout.add_widget(scroll)
        
        return layout
    
    def build_reports_tab(self):
        """Build reports tab"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Shrinkage report
        shrinkage_label = Label(text='Shrinkage Report', size_hint_y=0.1, bold=True)
        layout.add_widget(shrinkage_label)
        
        scroll = ScrollView()
        report_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        report_grid.bind(minimum_height=report_grid.setter('height'))
        
        shrinkage = self.db.get_shrinkage_report()
        if shrinkage:
            for item in shrinkage:
                item_text = f"{item[0]} - Lost: {item[1]} units (${item[2]:.2f})"
                label = Label(text=item_text, size_hint_y=None, height=40)
                report_grid.add_widget(label)
        else:
            label = Label(text='No shrinkage recorded', size_hint_y=None, height=40)
            report_grid.add_widget(label)
        
        scroll.add_widget(report_grid)
        layout.add_widget(scroll)
        
        return layout
    
    def show_add_item_dialog(self, instance):
        """Show dialog to add new item"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Item Name:', size_hint_y=0.2))
        name_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(name_input)
        
        content.add_widget(Label(text='SKU:', size_hint_y=0.2))
        sku_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(sku_input)
        
        content.add_widget(Label(text='Unit Cost:', size_hint_y=0.2))
        cost_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(cost_input)
        
        content.add_widget(Label(text='Selling Price:', size_hint_y=0.2))
        price_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(price_input)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        popup = Popup(title='Add Item', content=content, size_hint=(0.9, 0.9))
        
        def save_item():
            try:
                unit_cost = float(cost_input.text) if cost_input.text else 0
                selling_price = float(price_input.text) if price_input.text else 0
                self.db.add_item(name_input.text, sku_input.text, None, unit_cost, selling_price)
                popup.dismiss()
                self.root.clear_widgets()
                self.root.add_widget(self.build())
            except Exception as e:
                print(f"Error: {e}")
        
        save_btn = Button(text='Save', size_hint_x=0.5)
        save_btn.bind(on_press=lambda x: save_item())
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel', size_hint_x=0.5)
        cancel_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        popup.open()
    
    def show_add_expense_dialog(self, instance):
        """Show dialog to add expense"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Description:', size_hint_y=0.2))
        desc_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(desc_input)
        
        content.add_widget(Label(text='Amount:', size_hint_y=0.2))
        amount_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(amount_input)
        
        content.add_widget(Label(text='Category:', size_hint_y=0.2))
        category_input = TextInput(multiline=False, size_hint_y=0.2)
        content.add_widget(category_input)
        
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        popup = Popup(title='Add Expense', content=content, size_hint=(0.9, 0.9))
        
        def save_expense():
            try:
                amount = float(amount_input.text)
                self.db.add_expense(desc_input.text, amount, category_input.text)
                popup.dismiss()
                self.root.clear_widgets()
                self.root.add_widget(self.build())
            except Exception as e:
                print(f"Error: {e}")
        
        save_btn = Button(text='Save', size_hint_x=0.5)
        save_btn.bind(on_press=lambda x: save_expense())
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel', size_hint_x=0.5)
        cancel_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        popup.open()
    
    def show_item_details(self, instance):
        """Show item details and options"""
        item_id = instance.item_id
        item = self.db.get_item_by_id(item_id)
        
        if not item:
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Display item info
        info_text = f"Item: {item[1]}\nQuantity: {item[4]}\nSKU: {item[2]}\n"
        info_text += f"Unit Cost: ${item[5]:.2f}\nSelling Price: ${item[6]:.2f}\n"
        info_text += f"On Display: {item[7]} units"
        
        content.add_widget(Label(text=info_text, size_hint_y=0.4))
        
        # Action buttons
        btn_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.6)
        
        popup = Popup(title=item[1], content=content, size_hint=(0.8, 0.8))
        
        def update_qty():
            # Simplified quantity update
            self.db.update_quantity(item_id, 1, "stock_in")
            popup.dismiss()
            self.root.clear_widgets()
            self.root.add_widget(self.build())
        
        def record_shrinkage():
            self.db.add_shrinkage(item_id, 1, "damage", item[6])
            popup.dismiss()
            self.root.clear_widgets()
            self.root.add_widget(self.build())
        
        update_btn = Button(text='Add Stock')
        update_btn.bind(on_press=lambda x: update_qty())
        btn_layout.add_widget(update_btn)
        
        shrink_btn = Button(text='Record Loss')
        shrink_btn.bind(on_press=lambda x: record_shrinkage())
        btn_layout.add_widget(shrink_btn)
        
        close_btn = Button(text='Close')
        close_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(close_btn)
        
        content.add_widget(btn_layout)
        popup.open()


if __name__ == '__main__':
    app = InventoryApp()
    app.run()
