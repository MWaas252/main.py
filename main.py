import argparse
import csv
import os
from datetime import date, datetime, timedelta
import tabulate
import subprocess

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.
BOUGHT_CSV_PATH = 'boughtcsv.csv'
SOLD_CSV_PATH = 'soldcsv.csv'
PLANTUML_PATH_DEFAULT = "C:/Users/Administrator/plantuml-1.2023.12.jar"  # Specify the actual path to your PlantUML JAR file

# Load CSV function
def load_csv(filename):
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Strip leading and trailing spaces from the fields
            row = {key: value.strip() if isinstance(value, str) else value for key, value in row.items()}
            data.append(row)
    return data

# Get current day function
def get_current_day():
    try:
        with open('current_day.txt', 'r') as file:
            current_date = file.read().strip()
            return datetime.strptime(current_date, '%Y-%m-%d').date()
    except FileNotFoundError:
        return date.today()

# Set current day function
def set_current_day(day, days_to_advance):
    new_day = day + timedelta(days=days_to_advance)
    with open('current_day.txt', 'w') as file:
        file.write(new_day.strftime('%Y-%m-%d'))

# Action functions
def perform_products_action(args, bought_data, plantuml_path):
    products = set(entry['product_name'] for entry in bought_data)
    print("Products offered by the supermarket:")
    if args.product_list:
        selected_products = set(args.product_list)
        products = products.intersection(selected_products)

    table = [["Product"]]    
    for product in products:
        table.append([product])

        table_format = args.format if args.format else "grid"
        print(tabulate.tabulate(table, headers="firstrow", tablefmt=table_format))

        # PlantUML class diagram example
        uml_code = """
        @startuml
        class Product {
            - product_name: str
            - purchase_price: float
            - expiry_date: str
        }
        @enduml
        """
        generate_uml(uml_code, "product_class_diagram", plantuml_path)

def perform_count_action(bought_data):
    product_counts = {}
    for entry in bought_data:
        product_name = entry['product_name']
        product_counts[product_name] = product_counts.get(product_name, 0) + 1

    table = [["Product", "Count"]]
    for product, count in product_counts.items():
        table.append([product, count])

    table_format = args.format if args.format else "grid"
    print("Current product counts:")
    print(tabulate.tabulate(table, headers="firstrow", tablefmt="grid"))

def perform_details_action(bought_data):
    product_details = {}
    for entry in bought_data:
        product_name = entry['product_name']
        purchase_price = entry.get('purchase_price', 'N/A')
        expiry_date = entry.get('expiry_date', 'N/A')

        if product_name not in product_details:
            product_details[product_name] = {'purchase_price': purchase_price, 'expiry_date': expiry_date}
    
    print("Product details:")
    for product, details in product_details.items():
        print(f"Product: {product}")
        print(f"Purchase Price: {details['purchase_price']}")
        print(f"Expiry Date: {details['expiry_date']}")

def perform_buy_action(args, bought_data):
    if not args.product_name:
        print("Please specify a product name using --product_name")
        return

    if not args.price:
        print("Please specify a price using --price")
        return

    if not args.quantity:
        print("Please specify a quantity using --quantity")
        return
    if not args.expiry_date:
        print("Please specify an expiration date using --expiration_date")
        return

    new_entry = {
        'id': len(bought_data) + 1,
        'product_name': args.product_name,
        'buy_date': date.today().strftime('%d-%m-%Y'),
        'purchase_price': args.price,
        'expiry_date': args.expiration_date
    }
    bought_data.append(new_entry)
    print(f"Bought {args.quantity} {args.product_name}(s) for ${args.price} each.")

def perform_sell_action(args, sold_data):
    if not args.product_name:
        print("Please specify a product name using --product_name")
        return

    if not args.price:
        print("Please specify a price using --price")
        return

    if not args.expiration_date:
        print("Please specify an expiration date using --expiration_date")
        return

    new_entry = {
        'product_name': args.product_name,
        'sale_price': args.price,
        'expiry_date': args.expiration_date
    }
    sold_data.append(new_entry)
    print(f"Sold {args.product_name} for ${args.price}. Expiry date: {args.expiration_date}")

def perform_sold_action(sold_data, current_date, product_to_check, date_to_check):
    sold_info = {}
    for entry in sold_data:
        product_name = entry['product_name']
        if product_name not in sold_info:
            sold_info[product_name] = {'sale_price': entry['sale_price'], 'expired': False}

        if entry['expiry_date']:
            expiry_date = datetime.strptime(entry['expiry_date'], '%Y-%m-%d').date() 
    
            if expiry_date < date_to_check:
                sold_info[product_name]['expired'] = True

    print("Product sale info:")
    for product, info in sold_info.items():
        print(f"Product: {product}")
        print(f"Sale Price: {info['sale_price']}")
        if info['expired']:
            print("Status: Expired")
        else:
            print("Status: Not Expired")


def generate_uml(uml_code, output_path, plantuml_path):
    try:
        subprocess.run(["java", "-jar", plantuml_path, "-tsvg", "-o", output_path], input=uml_code.encode(), check=True)
    except Exception as e:
        print("Error generating PlantUML diagram: {}".format(e))

def main():
    parser = argparse.ArgumentParser(description="Superpy - Inventory Tracking Tool")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands')


    parser_action = subparsers.add_parser('action', help='Perform actions')
    parser_action.add_argument('action', choices=['products', 'count', 'details', 'sold', 'buy', 'sell'], help='Action to perform')
    parser_action.add_argument('--format', help='Table format (e.g., "grid", "html", "latex")')
    parser_action.add_argument('--product_list', nargs='+', help='List of product names to filter')
    parser_action.add_argument('--sold_product', help='Product name')
    parser_action.add_argument('--price', type=float, help='Price')
    parser_action.add_argument('--quantity', type=int, help='Quantity')
    parser_action.add_argument('--expiry_date', help='Expiration date (YYYY-MM-DD')
    parser_action.add_argument('--plantuml_path', default=PLANTUML_PATH_DEFAULT, help='Path to the PlantUML JAR file')

    # Define arguments specific to the 'buy' action
    parser_buy = subparsers.add_parser('buy', help='Buy a product')
    parser_buy.add_argument('--product_name', required=True, help='Name of the product to buy')
    parser_buy.add_argument('--price', type=float, required=True, help='Price')
    parser_buy.add_argument('--quantity', type=int, required=True, help='Quantity')
    parser_buy.add_argument('--expiry_date', required=True, help='Expiration date (YYYY-MM-DD)')

    # Define arguments specific to the 'sell' action
    parser_sell = subparsers.add_parser('sell', help='Sell a product')
    parser_sell.add_argument('--product_name', required=True, help='Name of the product to sell')
    parser_sell.add_argument('--price', type=float, required=True, help='Price')
    parser_sell.add_argument('--quantity', type=int, required=True, help='Quantity')
    parser_sell.add_argument('--expiry_date', required=True, help='Expiration date (YYYY-MM-DD)')
    parser.add_argument('--set_date', help='Set the current date (YYYY-MM-DD)')

    parser_advance = subparsers.add_parser('advance-time', help='Advance time by specified number of days')
    parser_advance.add_argument('days', type=int, help='Number of days to advance')

    args = parser.parse_args()

    script_directory = os.path.dirname(os.path.abspath(__file__))
    bought_csv_path = os.path.join(script_directory, 'boughtcsv.csv')
    sold_csv_path = os.path.join(script_directory, 'soldcsv.csv')

    bought_data = load_csv(bought_csv_path)
    sold_data = load_csv(sold_csv_path)

    if args.subcommand == 'action':
        current_day = get_current_day()

        if args.action == 'products':
            perform_products_action(args, bought_data, args.plantuml_path)
        elif args.action == 'count':
            perform_count_action(bought_data)
        elif args.action == 'details':
            perform_details_action(bought_data)
        elif args.action == 'sold':
            if args.sold_product and args.expiry_date:
                product_to_check = args.sold_product
                date_to_check = datetime.strptime(args.expiry_date, '%Y-%m-%d').date()
                perform_sold_action(sold_data, current_day, product_to_check, date_to_check)
        elif args.action == 'buy':
            perform_buy_action(args, bought_data)
        elif args.action == 'sell':
            perform_sell_action(args, sold_data)
            if args.set_date:
                new_date = datetime.strptime(args.set_date, '%Y-%m-%d').date()
                set_current_day(new_date, 0)  # 0 days to advance
                print(f"Setting the current date to {new_date.strftime('%Y-%m-%d')}.")

    elif args.subcommand == 'advance-time':
        current_day = get_current_day()
        set_current_day(current_day, args.days)
        print(f"Advancing time by {args.days} day(s)...")

if __name__ == "__main__":
    main()

