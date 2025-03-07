BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Buyer" (
	"BuyerID"	INTEGER NOT NULL,
	"BuyerName"	TEXT NOT NULL,
	"BuyerEmail"	TEXT NOT NULL UNIQUE,
	"BuyerPasscode"	TEXT NOT NULL,
	"BuyerAddress"	TEXT NOT NULL,
	"BuyerPhone"	NUMERIC NOT NULL UNIQUE,
	PRIMARY KEY("BuyerID")
);
CREATE TABLE IF NOT EXISTS "Cart" (
	"CartItemID"	INTEGER NOT NULL,
	"BuyerID"	INTEGER NOT NULL,
	"PorductID"	INTEGER NOT NULL,
	"Quantity"	INTEGER NOT NULL,
	"Price"	NUMERIC NOT NULL,
	PRIMARY KEY("CartItemID"),
	FOREIGN KEY("BuyerID") REFERENCES "Buyer"("BuyerID"),
	FOREIGN KEY("PorductID") REFERENCES "Product"("ProductID")
);
CREATE TABLE IF NOT EXISTS "HelpDesk" (
	"TicketNum"	INTEGER NOT NULL,
	"Name"	TEXT,
	"Email"	TEXT NOT NULL,
	"Description"	TEXT,
	PRIMARY KEY("TicketNum")
);
CREATE TABLE IF NOT EXISTS "Order" (
	"OrderID"	INTEGER NOT NULL,
	"BuyerID"	INTEGER NOT NULL,
	"Date"	NUMERIC NOT NULL,
	"Status"	TEXT NOT NULL,
	"Amount"	TEXT NOT NULL,
	PRIMARY KEY("OrderID"),
	FOREIGN KEY("BuyerID") REFERENCES "Buyer"("BuyerID")
);
CREATE TABLE IF NOT EXISTS "OrderItems" (
	"OrderItemID"	INTEGER NOT NULL,
	"OrderID"	INTEGER NOT NULL,
	"ProductID"	INTEGER NOT NULL,
	"Quantity"	INTEGER NOT NULL,
	"Price"	NUMERIC NOT NULL,
	PRIMARY KEY("OrderItemID"),
	FOREIGN KEY("OrderID") REFERENCES "Order"("OrderID"),
	FOREIGN KEY("ProductID") REFERENCES "Product"("ProductID")
);
CREATE TABLE IF NOT EXISTS "Product" (
	"ProductID"	INTEGER NOT NULL,
	"SupplierID"	INTEGER NOT NULL,
	"ProdName"	TEXT NOT NULL,
	"ProdPrice"	NUMERIC NOT NULL,
	"ProdQuantity"	INTEGER NOT NULL,
	"ProdDesc"	TEXT NOT NULL,
	"ProdImage"	BLOB,
	PRIMARY KEY("ProductID") ON CONFLICT ABORT,
	FOREIGN KEY("SupplierID") REFERENCES "Supplier"("SupplierID")
);
CREATE TABLE IF NOT EXISTS "Supplier" (
	"SupplierID"	INTEGER NOT NULL,
	"SupplierName"	TEXT NOT NULL,
	"SupplierEmail"	TEXT NOT NULL UNIQUE,
	"SupplierPasscode"	INTEGER NOT NULL,
	"SupplierAddress"	TEXT NOT NULL,
	"SupplierPhone"	NUMERIC NOT NULL UNIQUE,
	PRIMARY KEY("SupplierID")
);
COMMIT;
