import psycopg2

# Connect to odoo_dev database
conn_odoo_dev = psycopg2.connect(
    dbname='yyy',
    host='xxx',
    port='5432',
    user='postgres',
    password='zzz'
)

# Connect to cdw_prod database
conn_cdw_prod = psycopg2.connect(
    dbname='bbb',
    host='aaa',
    port='5432',
    user='postgres',
    password='ccc'
)

# Copy the table before updating (back up to odoo_dev > datamart > ir_property_backup, overwrite)
def backup_ir_property_data():
    create_backup_table_query = """
    CREATE TABLE IF NOT EXISTS datamart.ir_property_backup AS
    TABLE ir_property WITH NO DATA
    """
    drop_backup_table_query = "DROP TABLE IF EXISTS ir_property_backup"

    insert_backup_data_query = """
    INSERT INTO datamart.ir_property_backup
    SELECT * FROM ir_property
    """
    with conn_odoo_dev.cursor() as cur:
        cur.execute(drop_backup_table_query)
        cur.execute(create_backup_table_query)
        cur.execute(insert_backup_data_query)
        conn_odoo_dev.commit()

# Get the list of products where the price is 1, 0, or null (odoo_dev connection)
def get_product_standard_price_data ():
    query = "select id, value_float, name, res_id from ir_property where name = 'standard_price'"
    with conn_odoo_dev.cursor() as cur: # Same as cur = conn_odoo_dev.cursor
        cur.execute(query)
        rows = cur.fetchall() 

        #Add product_product_id from res_id
        result = [] # result = []
        for row in rows:
            res_id = row[3]
            product_product_id = int(res_id.split(",")[1]) if res_id else None
            result.append(row + (product_product_id,))
    return result

# Get the latest price list from vendor_pricelist (cdw_prod connection)
def get_latest_pricelist_data ():
    query = """
    WITH RankedPrices AS (SELECT product_product_id, price, invoice_date, 
    ROW_NUMBER() OVER (PARTITION BY product_product_id ORDER BY invoice_date DESC) AS rn 
    FROM erp_accurate.vendor_pricelist) 
    SELECT product_product_id, price, invoice_date FROM RankedPrices WHERE rn = 1
    """
    with conn_cdw_prod.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return rows

# Fetch data
product_standard_price_data = get_product_standard_price_data()
latest_pricelist_data = get_latest_pricelist_data()

# Print fetched data for debugging
print("Product Standard Price Data:")
for row in product_standard_price_data:
    print(row)

print("\nLatest Pricelist Data:")
for row in latest_pricelist_data:
    print(row)

# Create a dictionary from latest_pricelist_data for quick lookup
pricelist_dict = {int(product_product_id): price for product_product_id, price, _ in latest_pricelist_data if product_product_id is not None}

# Print dictionary for debugging
print("\nPricelist Dictionary:")
for key, value in pricelist_dict.items():
    print(f"{key}: {value}")

# Update the ir_property table
def update_standard_price():
    update_query = """
    UPDATE ir_property
    SET value_float = %s
    WHERE id = %s
    """
    with conn_odoo_dev.cursor() as cur:
        for row in product_standard_price_data:
            product_product_id = row[4]
            # Check if the product is in the latest_pricelist_data
            if product_product_id in pricelist_dict:
                new_price = pricelist_dict[product_product_id]
                print(f"Updating id {row[0]} with new price {new_price}")
                cur.execute(update_query, (new_price, row[0]))
        conn_odoo_dev.commit() 
# Backup data before updating
#backup_ir_property_data()

# Execute the update
update_standard_price()

# Close the connections
conn_odoo_dev.close()
conn_cdw_prod.close()
