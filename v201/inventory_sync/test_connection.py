#!/usr/bin/env python3
"""
Test script for inventory_sync module
Run this to verify SQLite connection and basic functionality
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')
django.setup()

from inventory_sync.services import SQLiteInventoryService, InventorySyncService

def test_sqlite_connection():
    """Test SQLite database connection"""
    print("🔍 Testing SQLite connection...")
    
    sqlite_service = SQLiteInventoryService()
    
    # Check if file exists
    if not os.path.exists(sqlite_service.db_path):
        print(f"❌ SQLite file not found at: {sqlite_service.db_path}")
        print("Please place your db.sqlite3 file in the inventory_sync directory")
        return False
    
    print(f"✅ SQLite file found at: {sqlite_service.db_path}")
    
    # Test connection
    if not sqlite_service.connect():
        print("❌ Failed to connect to SQLite database")
        return False
    
    print("✅ Successfully connected to SQLite database")
    
    # Test getting products
    products = sqlite_service.get_available_products()
    print(f"✅ Found {len(products)} In-stock products in SQLite")
    
    if products:
        print("📋 Sample product:")
        sample = products[0]
        print(f"   - Reel Number: {sample.get('reel_number', 'N/A')}")
        print(f"   - Grade: {sample.get('grade', 'N/A')}")
        print(f"   - Status: {sample.get('status', 'N/A')}")
        print(f"   - Location: {sample.get('location', 'N/A')}")
    
    sqlite_service.disconnect()
    return True

def test_sync_service():
    """Test inventory sync service"""
    print("\n🔄 Testing Inventory Sync Service...")
    
    sync_service = InventorySyncService()
    
    # Test getting importable products
    importable_products = sync_service.get_importable_products()
    print(f"✅ Found {len(importable_products)} products available for import")
    
    if importable_products:
        print("📋 Sample importable product:")
        sample = importable_products[0]
        print(f"   - Reel Number: {sample['reel_number']}")
        print(f"   - External ID: {sample['external_id']}")
        print(f"   - Grade: {sample['external_data'].get('grade', 'N/A')}")
    
    return True

def test_field_mappings():
    """Test field mappings"""
    print("\n🗺️ Testing Field Mappings...")
    
    sync_service = InventorySyncService()
    
    print(f"✅ Loaded {len(sync_service.field_mappings)} field mappings")
    
    # Show some mappings
    for external_field, django_field in list(sync_service.field_mappings.items())[:5]:
        print(f"   {external_field} → {django_field}")
    
    return True

def main():
    """Main test function"""
    print("🧪 Inventory Sync Module Test")
    print("=" * 50)
    
    try:
        # Test SQLite connection
        if not test_sqlite_connection():
            return
        
        # Test sync service
        if not test_sync_service():
            return
        
        # Test field mappings
        if not test_field_mappings():
            return
        
        print("\n✅ All tests passed!")
        print("\n🎉 The inventory_sync module is ready to use!")
        print("You can now:")
        print("1. Run migrations: python manage.py migrate inventory_sync")
        print("2. Access the dashboard: /inventory-sync/dashboard/")
        print("3. Use management commands: python manage.py sync_inventory")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 