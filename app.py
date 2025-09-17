from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Product, Location, ProductMovement
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # For flash messages
db.init_app(app)

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()

# Initialize database when app starts
init_db()

# Helper function to calculate balance
def calculate_balance():
    """Calculate current balance for all products in all locations"""
    balance = {}
    movements = ProductMovement.query.all()
    
    for move in movements:
        # Subtract from source location
        if move.from_location:
            key = (move.product_id, move.from_location)
            balance[key] = balance.get(key, 0) - move.qty
        
        # Add to destination location
        if move.to_location:
            key = (move.product_id, move.to_location)
            balance[key] = balance.get(key, 0) + move.qty
    
    return balance

# ---------------- ROUTES ---------------- #

@app.route("/")
@app.route("/dashboard")
def dashboard():
    # Dashboard with summary statistics
    total_products = Product.query.count()
    total_locations = Location.query.count()
    total_movements = ProductMovement.query.count()
    recent_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).limit(5).all()
    
    return render_template("dashboard.html", 
                         total_products=total_products,
                         total_locations=total_locations,
                         total_movements=total_movements,
                         recent_movements=recent_movements)

# ============ PRODUCT ROUTES ============

@app.route("/products")
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("products/list.html", products=products)

@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        try:
            quantity = int(request.form.get("quantity", 0))
            product = Product(
                product_id=request.form["product_id"].strip(),
                name=request.form["name"].strip(),
                description=request.form.get("description", "").strip(),
                quantity=quantity
            )
            db.session.add(product)
            db.session.commit()
            flash(f"Product '{product.name}' added successfully with quantity {quantity}!", "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"Error adding product: {str(e)}", "error")
    
    return render_template("products/form.html", product=None, action="Add")

@app.route("/products/<product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == "POST":
        try:
            product.name = request.form["name"].strip()
            product.description = request.form.get("description", "").strip()
            product.quantity = int(request.form.get("quantity", 0))
            db.session.commit()
            flash(f"Product '{product.name}' updated successfully!", "success")
            return redirect(url_for("products"))
        except Exception as e:
            flash(f"Error updating product: {str(e)}", "error")
    
    return render_template("products/form.html", product=product, action="Edit")

@app.route("/products/<product_id>/delete", methods=["POST"])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        # Check if product has movements
        if product.movements:
            flash(f"Cannot delete product '{product.name}' - it has movement history.", "error")
        else:
            db.session.delete(product)
            db.session.commit()
            flash(f"Product '{product.name}' deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {str(e)}", "error")
    
    return redirect(url_for("products"))

# ============ LOCATION ROUTES ============

@app.route("/locations")
def locations():
    locations = Location.query.order_by(Location.created_at.desc()).all()
    return render_template("locations/list.html", locations=locations)

@app.route("/locations/add", methods=["GET", "POST"])
def add_location():
    if request.method == "POST":
        try:
            location = Location(
                location_id=request.form["location_id"].strip(),
                name=request.form["name"].strip(),
                address=request.form.get("address", "").strip()
            )
            db.session.add(location)
            db.session.commit()
            flash(f"Location '{location.name}' added successfully!", "success")
            return redirect(url_for("locations"))
        except Exception as e:
            flash(f"Error adding location: {str(e)}", "error")
    
    return render_template("locations/form.html", location=None, action="Add")

@app.route("/locations/<location_id>/edit", methods=["GET", "POST"])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    if request.method == "POST":
        try:
            location.name = request.form["name"].strip()
            location.address = request.form.get("address", "").strip()
            db.session.commit()
            flash(f"Location '{location.name}' updated successfully!", "success")
            return redirect(url_for("locations"))
        except Exception as e:
            flash(f"Error updating location: {str(e)}", "error")
    
    return render_template("locations/form.html", location=location, action="Edit")

@app.route("/locations/<location_id>/delete", methods=["POST"])
def delete_location(location_id):
    try:
        location = Location.query.get_or_404(location_id)
        # Check if location has movements
        if location.movements_from or location.movements_to:
            flash(f"Cannot delete location '{location.name}' - it has movement history.", "error")
        else:
            db.session.delete(location)
            db.session.commit()
            flash(f"Location '{location.name}' deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting location: {str(e)}", "error")
    
    return redirect(url_for("locations"))

# ============ MOVEMENT ROUTES ============

@app.route("/movements")
def movements():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template("movements/list.html", movements=movements)

@app.route("/movements/add", methods=["GET", "POST"])
def add_movement():
    if request.method == "POST":
        try:
            product_id = request.form["product_id"].strip()
            qty = int(request.form.get("qty", 0))
            if qty <= 0:
                flash("Quantity must be greater than 0.", "error")
                return redirect(url_for("add_movement"))

            movement = ProductMovement(
                product_id=product_id,
                from_location=(request.form.get("from_location") or None),
                to_location=(request.form.get("to_location") or None),
                qty=qty,
                notes=(request.form.get("notes", "").strip())
            )

            db.session.add(movement)
            db.session.commit()
            flash("Movement saved!", "success")
            return redirect(url_for("movements"))
        except Exception as e:
            flash(f"Error: {e}", "error")

    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    return render_template("movements/form.html",
                          movement=None,
                          products=products,
                          locations=locations,
                          action="Add")

@app.route("/movements/<int:movement_id>/edit", methods=["GET", "POST"])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    
    if request.method == "POST":
        try:
            qty = int(request.form.get("qty", 0))
            if qty <= 0:
                flash("Quantity must be greater than 0.", "error")
                return redirect(url_for("edit_movement", movement_id=movement_id))

            movement.product_id = request.form["product_id"].strip()
            movement.from_location = (request.form.get("from_location") or None)
            movement.to_location = (request.form.get("to_location") or None)
            movement.qty = qty
            movement.notes = request.form.get("notes", "").strip()

            db.session.commit()
            flash("Movement updated!", "success")
            return redirect(url_for("movements"))
        except Exception as e:
            flash(f"Error updating movement: {e}", "error")
    
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    return render_template("movements/form.html", 
                         movement=movement, 
                         products=products, 
                         locations=locations, 
                         action="Edit")

@app.route("/movements/<int:movement_id>/delete", methods=["POST"])
def delete_movement(movement_id):
    try:
        movement = ProductMovement.query.get_or_404(movement_id)
        db.session.delete(movement)
        db.session.commit()
        flash("Movement deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting movement: {str(e)}", "error")
    
    return redirect(url_for("movements"))

# ============ REPORT ROUTES ============

@app.route("/report")
def report():
    balance = calculate_balance()
    
    # Organize data for the report
    report_data = []
    products = {p.product_id: p for p in Product.query.all()}
    locations = {l.location_id: l for l in Location.query.all()}
    
    for (product_id, location_id), qty in balance.items():
        if qty != 0:  # Only show non-zero balances
            report_data.append({
                'product': products.get(product_id),
                'location': locations.get(location_id),
                'qty': qty
            })
    
    # Sort by product name, then location name
    report_data.sort(key=lambda x: (x['product'].name if x['product'] else '', 
                                   x['location'].name if x['location'] else ''))
    
    return render_template("report.html", report_data=report_data, current_time=datetime.now())

# ============ API ROUTES ============

@app.route("/api/balance")
def api_balance():
    """API endpoint for balance data"""
    balance = calculate_balance()
    products = {p.product_id: p.name for p in Product.query.all()}
    locations = {l.location_id: l.name for l in Location.query.all()}
    
    result = []
    for (product_id, location_id), qty in balance.items():
        if qty != 0:
            result.append({
                'product_id': product_id,
                'product_name': products.get(product_id, 'Unknown'),
                'location_id': location_id,
                'location_name': locations.get(location_id, 'Unknown'),
                'quantity': qty
            })
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
