/**
 * db.js - Smart Inventory Management System Database Layer
 * Handles schema structures, localStorage persistence, and initial seed data.
 */

const SEED_CATEGORIES = [
  { CategoryID: "1", CategoryName: "Electronics" },
  { CategoryID: "2", CategoryName: "Office Supplies" },
  { CategoryID: "3", CategoryName: "Furniture" },
  { CategoryID: "4", CategoryName: "Apparel" }
];

const SEED_SUPPLIERS = [
  { SupplierID: "1", SupplierName: "TechWorld Wholesalers", ContactPerson: "Alice Vance", Phone: "+1-555-0199", Email: "alice@techworld.com", Address: "100 Silicon Blvd, San Jose, CA" },
  { SupplierID: "2", SupplierName: "Global Office Corp", ContactPerson: "Robert Miller", Phone: "+1-555-0142", Email: "orders@globaloffice.com", Address: "450 Commerce Pkwy, Chicago, IL" },
  { SupplierID: "3", SupplierName: "Comfort Seats Ltd", ContactPerson: "Elena Rostova", Phone: "+1-555-0177", Email: "sales@comfortseats.com", Address: "78 Ergonomic Way, Grand Rapids, MI" },
  { SupplierID: "4", SupplierName: "Apex Apparel Group", ContactPerson: "Marcus Brody", Phone: "+1-555-0121", Email: "m.brody@apexapparel.com", Address: "12 Garment St, New York, NY" }
];

const SEED_PRODUCTS = [
  {
    ProductID: "PRD-1001",
    ProductName: "Logitech MX Master 3S",
    CategoryID: "1",
    SupplierID: "1",
    PurchasePrice: 75.00,
    SellingPrice: 99.99,
    Quantity: 25,
    ReorderLevel: 10,
    Barcode: "097855171734",
    Image: "electronics_mouse", // visual tag for placeholder color
    CreatedDate: "2026-07-20T10:00:00.000Z"
  },
  {
    ProductID: "PRD-1002",
    ProductName: "Dell UltraSharp 27 Monitor",
    CategoryID: "1",
    SupplierID: "1",
    PurchasePrice: 220.00,
    SellingPrice: 299.99,
    Quantity: 8,
    ReorderLevel: 12, // Quantity 8 <= ReorderLevel 12 -> Low Stock
    Barcode: "884116382905",
    Image: "electronics_monitor",
    CreatedDate: "2026-07-21T11:30:00.000Z"
  },
  {
    ProductID: "PRD-1003",
    ProductName: "Ergonomic Office Chair",
    CategoryID: "3",
    SupplierID: "3",
    PurchasePrice: 150.00,
    SellingPrice: 249.99,
    Quantity: 15,
    ReorderLevel: 5,
    Barcode: "712493018241",
    Image: "furniture_chair",
    CreatedDate: "2026-07-15T09:00:00.000Z"
  },
  {
    ProductID: "PRD-1004",
    ProductName: "Pilot G2 Gel Pens (12 Pack)",
    CategoryID: "2",
    SupplierID: "2",
    PurchasePrice: 6.50,
    SellingPrice: 12.99,
    Quantity: 45,
    ReorderLevel: 15,
    Barcode: "072838310202",
    Image: "supplies_pens",
    CreatedDate: "2026-07-18T14:15:00.000Z"
  },
  {
    ProductID: "PRD-1005",
    ProductName: "Premium Cotton Hoodie",
    CategoryID: "4",
    SupplierID: "4",
    PurchasePrice: 18.00,
    SellingPrice: 39.99,
    Quantity: 3,
    ReorderLevel: 8, // Low Stock!
    Barcode: "609214731804",
    Image: "apparel_hoodie",
    CreatedDate: "2026-07-22T16:45:00.000Z"
  },
  {
    ProductID: "PRD-1006",
    ProductName: "Standing Desk Converter",
    CategoryID: "3",
    SupplierID: "3",
    PurchasePrice: 85.00,
    SellingPrice: 149.99,
    Quantity: 0, // Out of Stock!
    ReorderLevel: 5,
    Barcode: "810056782312",
    Image: "furniture_desk",
    CreatedDate: "2026-07-23T10:00:00.000Z"
  }
];

const SEED_TRANSACTIONS = [
  { TransactionID: "TXN-1001", ProductID: "PRD-1001", TransactionType: "Stock In", Quantity: 25, Date: "2026-07-20T10:05:00.000Z", Remarks: "Initial opening stock setup" },
  { TransactionID: "TXN-1002", ProductID: "PRD-1002", TransactionType: "Stock In", Quantity: 10, Date: "2026-07-21T11:35:00.000Z", Remarks: "Initial opening stock setup" },
  { TransactionID: "TXN-1003", ProductID: "PRD-1002", TransactionType: "Stock Out", Quantity: 2, Date: "2026-07-24T15:10:00.000Z", Remarks: "Sold 2 units to corporate client" },
  { TransactionID: "TXN-1004", ProductID: "PRD-1003", TransactionType: "Stock In", Quantity: 15, Date: "2026-07-15T09:10:00.000Z", Remarks: "Direct wholesale purchase" },
  { TransactionID: "TXN-1005", ProductID: "PRD-1004", TransactionType: "Stock In", Quantity: 50, Date: "2026-07-18T14:20:00.000Z", Remarks: "Restock order #902" },
  { TransactionID: "TXN-1006", ProductID: "PRD-1004", TransactionType: "Stock Out", Quantity: 5, Date: "2026-07-25T11:00:00.000Z", Remarks: "Office floor replenishment" },
  { TransactionID: "TXN-1007", ProductID: "PRD-1005", TransactionType: "Stock In", Quantity: 3, Date: "2026-07-22T16:50:00.000Z", Remarks: "Summer apparel test batch" }
];

class InventoryDB {
  constructor() {
    this.init();
  }

  init() {
    if (!localStorage.getItem("sims_categories")) {
      localStorage.setItem("sims_categories", JSON.stringify(SEED_CATEGORIES));
    }
    if (!localStorage.getItem("sims_suppliers")) {
      localStorage.setItem("sims_suppliers", JSON.stringify(SEED_SUPPLIERS));
    }
    if (!localStorage.getItem("sims_products")) {
      localStorage.setItem("sims_products", JSON.stringify(SEED_PRODUCTS));
    }
    if (!localStorage.getItem("sims_transactions")) {
      localStorage.setItem("sims_transactions", JSON.stringify(SEED_TRANSACTIONS));
    }
    if (!localStorage.getItem("sims_role")) {
      localStorage.setItem("sims_role", "Admin");
    }
  }

  // Categories
  getCategories() {
    return JSON.parse(localStorage.getItem("sims_categories")) || [];
  }

  saveCategories(categories) {
    localStorage.setItem("sims_categories", JSON.stringify(categories));
  }

  addCategory(categoryName) {
    const categories = this.getCategories();
    const newId = (Math.max(...categories.map(c => parseInt(c.CategoryID) || 0)) + 1).toString();
    const newCategory = { CategoryID: newId, CategoryName: categoryName };
    categories.push(newCategory);
    this.saveCategories(categories);
    return newCategory;
  }

  updateCategory(id, name) {
    const categories = this.getCategories();
    const index = categories.findIndex(c => c.CategoryID === id);
    if (index !== -1) {
      categories[index].CategoryName = name;
      this.saveCategories(categories);
      return true;
    }
    return false;
  }

  deleteCategory(id) {
    // Check if category is used by any products
    const products = this.getProducts();
    if (products.some(p => p.CategoryID === id)) {
      throw new Error("Cannot delete category: It is currently assigned to active products.");
    }
    let categories = this.getCategories();
    categories = categories.filter(c => c.CategoryID !== id);
    this.saveCategories(categories);
    return true;
  }

  // Suppliers
  getSuppliers() {
    return JSON.parse(localStorage.getItem("sims_suppliers")) || [];
  }

  saveSuppliers(suppliers) {
    localStorage.setItem("sims_suppliers", JSON.stringify(suppliers));
  }

  addSupplier(supplierData) {
    const suppliers = this.getSuppliers();
    const newId = (Math.max(...suppliers.map(s => parseInt(s.SupplierID) || 0)) + 1).toString();
    const newSupplier = { SupplierID: newId, ...supplierData };
    suppliers.push(newSupplier);
    this.saveSuppliers(suppliers);
    return newSupplier;
  }

  updateSupplier(id, supplierData) {
    const suppliers = this.getSuppliers();
    const index = suppliers.findIndex(s => s.SupplierID === id);
    if (index !== -1) {
      suppliers[index] = { SupplierID: id, ...supplierData };
      this.saveSuppliers(suppliers);
      return true;
    }
    return false;
  }

  deleteSupplier(id) {
    // Check if supplier is used by any products
    const products = this.getProducts();
    if (products.some(p => p.SupplierID === id)) {
      throw new Error("Cannot delete supplier: It is currently assigned to active products.");
    }
    let suppliers = this.getSuppliers();
    suppliers = suppliers.filter(s => s.SupplierID !== id);
    this.saveSuppliers(suppliers);
    return true;
  }

  // Products
  getProducts() {
    return JSON.parse(localStorage.getItem("sims_products")) || [];
  }

  saveProducts(products) {
    localStorage.setItem("sims_products", JSON.stringify(products));
  }

  generateProductId() {
    const products = this.getProducts();
    if (products.length === 0) return "PRD-1001";
    const ids = products.map(p => {
      const parts = p.ProductID.split("-");
      return parts.length > 1 ? parseInt(parts[1]) : 1000;
    });
    const nextNum = Math.max(...ids) + 1;
    return `PRD-${nextNum}`;
  }

  addProduct(productData) {
    const products = this.getProducts();
    const newId = this.generateProductId();
    const newProduct = {
      ProductID: newId,
      ProductName: productData.ProductName,
      CategoryID: productData.CategoryID,
      SupplierID: productData.SupplierID,
      PurchasePrice: parseFloat(productData.PurchasePrice) || 0,
      SellingPrice: parseFloat(productData.SellingPrice) || 0,
      Quantity: parseInt(productData.Quantity) || 0,
      ReorderLevel: parseInt(productData.ReorderLevel) || 0,
      Barcode: productData.Barcode || "",
      Image: productData.Image || "",
      CreatedDate: new Date().toISOString()
    };
    products.push(newProduct);
    this.saveProducts(products);

    // If initial quantity > 0, log a Stock In transaction
    if (newProduct.Quantity > 0) {
      this.addTransaction({
        ProductID: newProduct.ProductID,
        TransactionType: "Stock In",
        Quantity: newProduct.Quantity,
        Remarks: "Initial quantity set upon product creation"
      });
    }

    return newProduct;
  }

  updateProduct(id, productData) {
    const products = this.getProducts();
    const index = products.findIndex(p => p.ProductID === id);
    if (index !== -1) {
      const oldQty = products[index].Quantity;
      const newQty = parseInt(productData.Quantity) || 0;

      // Update product fields
      products[index] = {
        ...products[index],
        ProductName: productData.ProductName,
        CategoryID: productData.CategoryID,
        SupplierID: productData.SupplierID,
        PurchasePrice: parseFloat(productData.PurchasePrice) || 0,
        SellingPrice: parseFloat(productData.SellingPrice) || 0,
        Quantity: newQty,
        ReorderLevel: parseInt(productData.ReorderLevel) || 0,
        Barcode: productData.Barcode || "",
        Image: productData.Image || products[index].Image
      };

      this.saveProducts(products);

      // Automatically handle transactions if stock quantity is updated directly from form
      if (newQty !== oldQty) {
        const diff = newQty - oldQty;
        this.addTransaction({
          ProductID: id,
          TransactionType: diff > 0 ? "Stock In" : "Stock Out",
          Quantity: Math.abs(diff),
          Remarks: `Manual inventory adjustment (Form Edit)`
        });
      }

      return true;
    }
    return false;
  }

  deleteProduct(id) {
    let products = this.getProducts();
    const exists = products.some(p => p.ProductID === id);
    if (!exists) return false;

    // Delete product
    products = products.filter(p => p.ProductID !== id);
    this.saveProducts(products);

    // Delete associated transactions
    let txns = this.getTransactions();
    txns = txns.filter(t => t.ProductID !== id);
    this.saveTransactions(txns);

    return true;
  }

  // Transactions
  getTransactions() {
    return JSON.parse(localStorage.getItem("sims_transactions")) || [];
  }

  saveTransactions(transactions) {
    localStorage.setItem("sims_transactions", JSON.stringify(transactions));
  }

  addTransaction(txnData) {
    const txns = this.getTransactions();
    const maxId = txns.reduce((max, t) => {
      const num = parseInt(t.TransactionID.split("-")[1]) || 1000;
      return num > max ? num : max;
    }, 1000);
    const newId = `TXN-${maxId + 1}`;

    const newTxn = {
      TransactionID: newId,
      ProductID: txnData.ProductID,
      TransactionType: txnData.TransactionType, // "Stock In" / "Stock Out"
      Quantity: parseInt(txnData.Quantity) || 0,
      Date: new Date().toISOString(),
      Remarks: txnData.Remarks || ""
    };

    txns.push(newTxn);
    this.saveTransactions(txns);

    // Adjust product quantity accordingly (unless direct edit already handled it)
    if (!txnData.skipProductUpdate) {
      const products = this.getProducts();
      const pIdx = products.findIndex(p => p.ProductID === txnData.ProductID);
      if (pIdx !== -1) {
        if (newTxn.TransactionType === "Stock In") {
          products[pIdx].Quantity += newTxn.Quantity;
        } else if (newTxn.TransactionType === "Stock Out") {
          products[pIdx].Quantity = Math.max(0, products[pIdx].Quantity - newTxn.Quantity);
        }
        this.saveProducts(products);
      }
    }

    return newTxn;
  }

  // User Role Configuration
  getCurrentRole() {
    return localStorage.getItem("sims_role") || "Admin";
  }

  setCurrentRole(role) {
    if (role === "Admin" || role === "Staff") {
      localStorage.setItem("sims_role", role);
      return true;
    }
    return false;
  }

  // Backup & Reset functions
  resetData() {
    localStorage.removeItem("sims_categories");
    localStorage.removeItem("sims_suppliers");
    localStorage.removeItem("sims_products");
    localStorage.removeItem("sims_transactions");
    this.init();
  }

  importData(jsonData) {
    try {
      const data = JSON.parse(jsonData);
      if (data.categories && data.suppliers && data.products && data.transactions) {
        localStorage.setItem("sims_categories", JSON.stringify(data.categories));
        localStorage.setItem("sims_suppliers", JSON.stringify(data.suppliers));
        localStorage.setItem("sims_products", JSON.stringify(data.products));
        localStorage.setItem("sims_transactions", JSON.stringify(data.transactions));
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  exportData() {
    return JSON.stringify({
      categories: this.getCategories(),
      suppliers: this.getSuppliers(),
      products: this.getProducts(),
      transactions: this.getTransactions()
    }, null, 2);
  }
}

const db = new InventoryDB();
window.inventoryDB = db; // expose to window for dynamic scripts
