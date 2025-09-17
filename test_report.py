from app import app, calculate_balance
from models import db, Product, Location, ProductMovement

def test_report():
    with app.app_context():
        # Test balance calculation
        balance = calculate_balance()
        print("Balance calculation result:")
        for (product_id, location_id), qty in balance.items():
            print(f"  Product {product_id} at Location {location_id}: {qty}")
        
        # Test report data generation
        products = {p.product_id: p for p in Product.query.all()}
        locations = {l.location_id: l for l in Location.query.all()}
        
        print("\nProducts in database:")
        for pid, product in products.items():
            print(f"  {pid}: {product.name}")
            
        print("\nLocations in database:")
        for lid, location in locations.items():
            print(f"  {lid}: {location.name}")
        
        report_data = []
        for (product_id, location_id), qty in balance.items():
            if qty != 0:  # Only show non-zero balances
                report_data.append({
                    'product': products.get(product_id),
                    'location': locations.get(location_id),
                    'qty': qty
                })
        
        print(f"\nReport data entries: {len(report_data)}")
        for item in report_data:
            product_name = item['product'].name if item['product'] else 'Unknown Product'
            location_name = item['location'].name if item['location'] else 'Unknown Location'
            print(f"  {product_name} at {location_name}: {item['qty']}")

if __name__ == "__main__":
    test_report()
