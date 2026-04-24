import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import get_connection

def run_tests():
    total_tests = 0
    passed_tests = 0
    results = []

    def assert_test(name, condition, error_msg=""):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            results.append(f"[PASS] {name}")
        else:
            results.append(f"[FAIL] {name} - {error_msg}")

    print("Starting BizMind Backend Function Tests...\n")
    
    # 1. Database Connection
    try:
        conn = get_connection()
        assert_test("Database Connection", conn is not None)
        conn.close()
    except Exception as e:
        assert_test("Database Connection", False, str(e))

    # 2. Inventory Module
    from modules.inventory import get_inventory_summary, get_all_products, add_product, update_stock, delete_product
    
    try:
        res = add_product("Test Keyboard", "Electronics", 50, 20.0, 10)
        assert_test("Add Inventory Product", res is True)
        
        df = get_all_products()
        assert_test("Fetch All Products", not df.empty and "Test Keyboard" in df['product_name'].values)
        
        test_prod_id = int(df[df['product_name'] == "Test Keyboard"]['id'].iloc[0])
        res = update_stock(test_prod_id, 45)
        assert_test("Update Stock Quantity", res is True)
        
        summ = get_inventory_summary()
        assert_test("Get Inventory Summary", 'total_products' in summ)
        
        res = delete_product(test_prod_id)
        assert_test("Delete Inventory Product", res is True)
    except Exception as e:
         results.append(f"[FAIL] Inventory Tests Encountered Error: {str(e)}")

    # 3. Accounting Module
    from modules.accounting import get_accounting_summary, get_transactions, get_monthly_data, add_transaction, get_unique_categories
    
    try:
        res = add_transaction("2026-04-20", "Income", "Sales", "Test sale", 500.0)
        assert_test("Add Accounting Transaction", res is True)
        
        df = get_transactions(type_filter="Income")
        assert_test("Fetch Transactions (Filtered)", not df.empty)
        
        cats = get_unique_categories()
        assert_test("Get Unique Categories", len(cats) > 0 and cats[0] == "All")
        
        summ = get_accounting_summary()
        assert_test("Get Accounting Summary", 'net_profit' in summ)
        
        monthly = get_monthly_data()
        assert_test("Get Monthly Trend Data", not monthly.empty)
    except Exception as e:
        results.append(f"[FAIL] Accounting Tests Encountered Error: {str(e)}")

    # 4. Analytics Module
    from modules.analytics import get_sales_data, get_analytics_summary, process_trend_data, get_top_products_data, get_category_sales
    from datetime import datetime, timedelta
    
    try:
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
        
        df_sales = get_sales_data(start_date, end_date)
        assert_test("Fetch Sales Data", not df_sales.empty)
        
        if not df_sales.empty:
            summ = get_analytics_summary(df_sales)
            assert_test("Get Analytics Summary", 'total_revenue' in summ)
            
            trend = process_trend_data(df_sales, "Monthly")
            assert_test("Process Trend Data", not trend.empty)
            
            tops = get_top_products_data(df_sales)
            assert_test("Get Top 5 Products", not tops.empty and len(tops) <= 5)
            
            cats = get_category_sales(df_sales)
            assert_test("Get Category Sales Breakdown", not cats.empty)
    except Exception as e:
        results.append(f"[FAIL] Analytics Tests Encountered Error: {str(e)}")

    # 5. Helpdesk Module (AI test)
    from modules.helpdesk import get_helpdesk_summary, get_tickets, add_ticket, update_ticket_status
    
    try:
        # Note: add_ticket will call Ollama which might take ~2-15 seconds
        print("Testing AI ticket generation (Please wait ~5s for Ollama inference)...")
        res = add_ticket("Monitor turning black", "My monitor randomly goes black after 5 minutes.", "high")
        assert_test("Add Helpdesk Ticket (Triggers AI Response)", res is True)
        
        df_t = get_tickets("Monitor turning black")
        assert_test("Fetch Tickets (Search)", not df_t.empty)
        
        if not df_t.empty:
            ticket_id = int(df_t['id'].iloc[0])
            ai_resp = str(df_t['ai_response'].iloc[0])
            assert_test("AI Auto Response Successfully Generated and Saved", "Internal system issue" not in ai_resp and len(ai_resp) > 5)
            
            res = update_ticket_status(ticket_id, "resolved")
            assert_test("Update Ticket Status", res is True)
            
        summ = get_helpdesk_summary()
        assert_test("Get Helpdesk Summary", 'open' in summ)
    except Exception as e:
        results.append(f"[FAIL] Helpdesk Tests Encountered Error: {str(e)}")

    print("\n--- TEST RESULTS ---")
    for r in results:
        print(r)
    
    print(f"\nFinal Score: {passed_tests}/{total_tests} Passed.")

if __name__ == "__main__":
    run_tests()
