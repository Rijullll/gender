/**
 * app.js - Smart Inventory Management System Application Controller
 * Manages UI rendering, events, Chart.js graphs, validations, exports, and role constraints.
 */

class SmartInventoryApp {
  constructor() {
    this.currentView = "dashboard";
    this.role = "Admin";
    this.charts = {
      stockLevels: null,
      categoryValuation: null
    };

    // Product pagination state
    this.productPagination = {
      currentPage: 1,
      pageSize: 10,
      filteredProducts: []
    };

    this.initElements();
    this.bindEvents();
    this.loadState();
  }

  // Bind element selectors
  initElements() {
    // Layout Elements
    this.sidebar = document.getElementById("appSidebar");
    this.sidebarToggleBtn = document.getElementById("sidebarToggleBtn");
    this.sidebarCloseBtn = document.getElementById("sidebarCloseBtn");
    this.themeToggleBtn = document.getElementById("themeToggleBtn");
    this.notificationBtn = document.getElementById("notificationBtn");
    this.notificationDropdown = document.getElementById("notificationDropdown");
    this.notificationList = document.getElementById("notificationList");
    this.headerNotificationCount = document.getElementById("headerNotificationCount");
    this.toastContainer = document.getElementById("toastContainer");

    // Role Buttons
    this.roleBtnAdmin = document.getElementById("roleBtnAdmin");
    this.roleBtnStaff = document.getElementById("roleBtnStaff");

    // Global Search & Scan Emulator
    this.globalSearchInput = document.getElementById("globalSearchInput");
    this.globalScanSimBtn = document.getElementById("globalScanSimBtn");

    // Views
    this.menuItems = document.querySelectorAll(".menu-item");
    this.pageViews = document.querySelectorAll(".page-view");

    // Product Management Inputs & Table
    this.prodFilterSearch = document.getElementById("prodFilterSearch");
    this.prodFilterCategory = document.getElementById("prodFilterCategory");
    this.prodFilterSupplier = document.getElementById("prodFilterSupplier");
    this.prodFilterStockStatus = document.getElementById("prodFilterStockStatus");
    this.prodFilterResetBtn = document.getElementById("prodFilterResetBtn");
    this.productsTableBody = document.getElementById("productsTableBody");
    this.prodPageSizeSelect = document.getElementById("prodPageSizeSelect");
    this.prodPaginationInfo = document.getElementById("prodPaginationInfo");
    this.prodPaginationControls = document.getElementById("prodPaginationControls");

    // Category / Supplier / Transactions / Alerts Bodies
    this.categoriesTableBody = document.getElementById("categoriesTableBody");
    this.categoryStatList = document.getElementById("categoryStatList");
    this.suppliersGrid = document.getElementById("suppliersGrid");
    this.transactionsTableBody = document.getElementById("transactionsTableBody");
    this.txnFilterType = document.getElementById("txnFilterType");
    this.lowStockTableBody = document.getElementById("lowStockTableBody");
    this.alertCriticalCountText = document.getElementById("alertCriticalCountText");
    this.reorderAllBtn = document.getElementById("reorderAllBtn");

    // Reports View Bodies
    this.reportCategoryTableBody = document.getElementById("reportCategoryTableBody");
    this.reportLowStockTableBody = document.getElementById("reportLowStockTableBody");

    // Settings
    this.settingBusinessName = document.getElementById("settingBusinessName");
    this.settingCurrency = document.getElementById("settingCurrency");
    this.settingAlertMargin = document.getElementById("settingAlertMargin");
  }

  // Bind UI interactive events
  bindEvents() {
    // Responsive Sidebar Toggle
    this.sidebarToggleBtn.addEventListener("click", () => this.sidebar.classList.add("open"));
    this.sidebarCloseBtn.addEventListener("click", () => this.sidebar.classList.remove("open"));

    // Theme Switching
    this.themeToggleBtn.addEventListener("click", () => this.toggleTheme());

    // Role Switching
    this.roleBtnAdmin.addEventListener("click", () => this.setRole("Admin"));
    this.roleBtnStaff.addEventListener("click", () => this.setRole("Staff"));

    // Notification dropdown toggle
    this.notificationBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      this.notificationDropdown.classList.toggle("open");
    });
    document.addEventListener("click", () => {
      this.notificationDropdown.classList.remove("open");
    });
    this.notificationDropdown.addEventListener("click", (e) => e.stopPropagation());
    document.getElementById("notifClearBtn").addEventListener("click", () => this.dismissAllNotifications());

    // Menu Navigation Routing
    this.menuItems.forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const target = item.getAttribute("data-target");
        this.switchView(target);
        this.sidebar.classList.remove("open"); // close mobile drawer
      });
    });

    // Product search and filter bindings
    const handleProdFilter = () => {
      this.productPagination.currentPage = 1;
      this.renderProductsView();
    };
    this.prodFilterSearch.addEventListener("input", handleProdFilter);
    this.prodFilterCategory.addEventListener("change", handleProdFilter);
    this.prodFilterSupplier.addEventListener("change", handleProdFilter);
    this.prodFilterStockStatus.addEventListener("change", handleProdFilter);
    this.prodFilterResetBtn.addEventListener("click", () => {
      this.prodFilterSearch.value = "";
      this.prodFilterCategory.value = "";
      this.prodFilterSupplier.value = "";
      this.prodFilterStockStatus.value = "";
      handleProdFilter();
      this.showToast("Filters Cleared", "info");
    });

    this.prodPageSizeSelect.addEventListener("change", (e) => {
      this.productPagination.pageSize = parseInt(e.target.value) || 10;
      this.productPagination.currentPage = 1;
      this.renderProductsView();
    });

    // Stock transaction search filter binding
    this.txnFilterType.addEventListener("change", () => this.renderTransactionsView());

    // Global quick search listener
    this.globalSearchInput.addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (q && this.currentView !== "products") {
        this.switchView("products");
        this.prodFilterSearch.value = q;
        this.renderProductsView();
      } else if (this.currentView === "products") {
        this.prodFilterSearch.value = q;
        this.renderProductsView();
      }
    });

    // Scan Emulator button binding
    this.globalScanSimBtn.addEventListener("click", () => this.showScanModal());

    // Reorder critical items quick-action binding
    this.reorderAllBtn.addEventListener("click", () => this.reorderAllCriticalItems());
  }

  // Bootstraps application values
  loadState() {
    // Load local storage values or defaults
    const currentTheme = localStorage.getItem("sims_theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);
    this.updateThemeButtonIcon(currentTheme);

    const savedRole = window.inventoryDB.getCurrentRole();
    this.setRole(savedRole, true);

    const savedBizName = localStorage.getItem("sims_biz_name") || "SmartStock Inc.";
    const savedCurrency = localStorage.getItem("sims_currency") || "USD ($)";
    const savedMargin = localStorage.getItem("sims_alert_margin") || "10";

    this.settingBusinessName.value = savedBizName;
    this.settingCurrency.value = savedCurrency;
    this.settingAlertMargin.value = savedMargin;

    document.querySelectorAll(".sidebar-brand span").forEach(el => el.textContent = savedBizName);

    // Initial View Render
    this.switchView(this.currentView);
    this.updateGlobalWidgets();
  }

  // Global Widgets & Notifications update
  updateGlobalWidgets() {
    this.updateNotificationList();
    this.updateSelectDropdowns();
  }

  // Swaps Active Visible Page View
  switchView(viewName) {
    this.currentView = viewName;

    this.menuItems.forEach(item => {
      if (item.getAttribute("data-target") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    this.pageViews.forEach(view => {
      if (view.id === `page-${viewName}`) {
        view.classList.add("active");
      } else {
        view.classList.remove("active");
      }
    });

    // Run view-specific rendering
    switch (viewName) {
      case "dashboard":
        this.renderDashboardView();
        break;
      case "products":
        this.renderProductsView();
        break;
      case "categories":
        this.renderCategoriesView();
        break;
      case "suppliers":
        this.renderSuppliersView();
        break;
      case "stock":
        this.renderTransactionsView();
        break;
      case "alerts":
        this.renderAlertsView();
        break;
      case "reports":
        this.renderReportsView();
        break;
    }
  }

  // Toggles Light/Dark visual layout variables
  toggleTheme() {
    const active = document.documentElement.getAttribute("data-theme");
    const next = active === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sims_theme", next);
    this.updateThemeButtonIcon(next);
    this.showToast(`Switched to ${next} theme mode.`, "info");
    
    // Refresh graphs if on dashboard
    if (this.currentView === "dashboard") {
      this.renderDashboardCharts();
    }
  }

  updateThemeButtonIcon(theme) {
    const icon = this.themeToggleBtn.querySelector("i");
    if (theme === "dark") {
      icon.className = "fa-solid fa-sun";
    } else {
      icon.className = "fa-solid fa-moon";
    }
  }

  // Manages User Permissions Restrictions
  setRole(newRole, skipToast = false) {
    this.role = newRole;
    window.inventoryDB.setCurrentRole(newRole);

    const userNameEl = document.getElementById("sidebarUserName");
    const userSubEl = document.getElementById("sidebarUserSub");
    const avatarEl = document.getElementById("sidebarAvatar");
    const badgeEl = document.getElementById("sidebarRoleBadge");

    if (newRole === "Admin") {
      this.roleBtnAdmin.classList.add("active");
      this.roleBtnStaff.classList.remove("active");
      document.body.classList.remove("staff-role");
      document.body.classList.add("admin-role");

      userNameEl.textContent = "Administrator";
      userSubEl.textContent = "Full System Access";
      avatarEl.textContent = "A";
      badgeEl.textContent = "Admin";
      badgeEl.className = "user-role-badge";
    } else {
      this.roleBtnStaff.classList.add("active");
      this.roleBtnAdmin.classList.remove("active");
      document.body.classList.remove("admin-role");
      document.body.classList.add("staff-role");

      userNameEl.textContent = "Staff Operator";
      userSubEl.textContent = "Transaction Access Only";
      avatarEl.textContent = "S";
      badgeEl.textContent = "Staff";
      badgeEl.className = "user-role-badge staff-badge";
    }

    // Toggle display elements based on CSS classes
    this.toggleRoleBasedUI();

    if (!skipToast) {
      this.showToast(`Switched active profile mode to ${newRole}.`, "info");
    }

    // Force refresh the active panel to show/hide dynamic fields
    this.switchView(this.currentView);
  }

  toggleRoleBasedUI() {
    const isAdmin = this.role === "Admin";
    document.querySelectorAll(".admin-only").forEach(el => {
      el.style.display = isAdmin ? "" : "none";
    });
    document.querySelectorAll(".staff-only").forEach(el => {
      el.style.display = isAdmin ? "none" : "";
    });
  }

  // Triggered notifications center logic
  updateNotificationList() {
    const products = window.inventoryDB.getProducts();
    const lowStockItems = products.filter(p => p.Quantity <= p.ReorderLevel);

    this.notificationList.innerHTML = "";

    if (lowStockItems.length === 0) {
      this.headerNotificationCount.classList.add("hidden");
      this.sidebarAlertCount.style.display = "none";
      this.notificationList.innerHTML = `
        <div class="notif-empty">
          <i class="fa-solid fa-circle-check notif-empty-icon text-success"></i>
          <p>All stock levels normal</p>
        </div>
      `;
      return;
    }

    // Update notification badges
    this.headerNotificationCount.classList.remove("hidden");
    this.headerNotificationCount.textContent = lowStockItems.length;
    this.sidebarAlertCount.style.display = "inline-block";
    this.sidebarAlertCount.textContent = lowStockItems.length;

    lowStockItems.forEach(p => {
      const isOut = p.Quantity === 0;
      const notifItem = document.createElement("div");
      notifItem.className = "notif-item";
      notifItem.innerHTML = `
        <div class="notif-icon ${isOut ? 'bg-red-gradient' : 'bg-orange-gradient'}" style="color: #fff">
          <i class="fa-solid ${isOut ? 'fa-circle-xmark' : 'fa-triangle-exclamation'}"></i>
        </div>
        <div class="notif-content">
          <h4>${isOut ? 'Out of Stock' : 'Low Stock Warning'}</h4>
          <p><strong>${p.ProductName}</strong> ${isOut ? 'has depleted.' : 'has fallen below safety mark (' + p.Quantity + '/' + p.ReorderLevel + ').'}</p>
          <span class="notif-time">Requires immediate stock intake.</span>
        </div>
      `;
      notifItem.addEventListener("click", () => {
        this.switchView("alerts");
        this.notificationDropdown.classList.remove("open");
      });
      this.notificationList.appendChild(notifItem);
    });
  }

  dismissAllNotifications() {
    this.showToast("All current notifications cleared locally.", "info");
    this.headerNotificationCount.classList.add("hidden");
    this.notificationDropdown.classList.remove("open");
  }

  // Refreshes options inside standard forms selection elements
  updateSelectDropdowns() {
    const categories = window.inventoryDB.getCategories();
    const suppliers = window.inventoryDB.getSuppliers();

    // Reset filter selects
    this.prodFilterCategory.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(c => {
      this.prodFilterCategory.innerHTML += `<option value="${c.CategoryID}">${c.CategoryName}</option>`;
    });

    this.prodFilterSupplier.innerHTML = '<option value="">All Suppliers</option>';
    suppliers.forEach(s => {
      this.prodFilterSupplier.innerHTML += `<option value="${s.SupplierID}">${s.SupplierName}</option>`;
    });

    // Form inputs selects
    const formCat = document.getElementById("prodFormCategory");
    formCat.innerHTML = '<option value="" disabled selected>Select Category</option>';
    categories.forEach(c => {
      formCat.innerHTML += `<option value="${c.CategoryID}">${c.CategoryName}</option>`;
    });

    const formSup = document.getElementById("prodFormSupplier");
    formSup.innerHTML = '<option value="" disabled selected>Select Supplier</option>';
    suppliers.forEach(s => {
      formSup.innerHTML += `<option value="${s.SupplierID}">${s.SupplierName}</option>`;
    });

    // Populate transaction products list
    const stockProd = document.getElementById("stockFormProduct");
    const products = window.inventoryDB.getProducts();
    stockProd.innerHTML = '<option value="" disabled selected>Select Product SKU</option>';
    products.forEach(p => {
      stockProd.innerHTML += `<option value="${p.ProductID}">${p.ProductID} - ${p.ProductName} (${p.Quantity} in stock)</option>`;
    });
  }

  // ==========================================================================
  // MODULE 1: DASHBOARD RENDER LOGIC
  // ==========================================================================
  renderDashboardView() {
    const products = window.inventoryDB.getProducts();
    const categories = window.inventoryDB.getCategories();
    const transactions = window.inventoryDB.getTransactions();

    // 1. Calculate KPI Values
    const totalProdCount = products.length;
    const totalStockQty = products.reduce((acc, p) => acc + p.Quantity, 0);
    const lowStockCount = products.filter(p => p.Quantity > 0 && p.Quantity <= p.ReorderLevel).length;
    const outStockCount = products.filter(p => p.Quantity === 0).length;

    document.getElementById("kpi-total-products").textContent = totalProdCount;
    document.getElementById("kpi-active-categories").textContent = categories.length;
    document.getElementById("kpi-total-stock").textContent = totalStockQty;
    document.getElementById("kpi-low-stock").textContent = lowStockCount;
    document.getElementById("kpi-out-stock").textContent = outStockCount;

    // 2. Load Charts
    this.renderDashboardCharts();

    // 3. Render Recent activity logs (max 5)
    const recentActivityList = document.getElementById("recentActivityList");
    recentActivityList.innerHTML = "";

    const sortedTxns = [...transactions].sort((a, b) => new Date(b.Date) - new Date(a.Date)).slice(0, 5);

    if (sortedTxns.length === 0) {
      recentActivityList.innerHTML = '<p class="text-center text-muted">No stock actions recorded yet.</p>';
    } else {
      sortedTxns.forEach(t => {
        const prod = products.find(p => p.ProductID === t.ProductID);
        const pName = prod ? prod.ProductName : "Unknown Product";
        const isStockIn = t.TransactionType === "Stock In";
        const dateString = new Date(t.Date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + " " + new Date(t.Date).toLocaleDateString();

        const timelineItem = document.createElement("div");
        timelineItem.className = "timeline-item";
        timelineItem.innerHTML = `
          <div class="timeline-icon ${isStockIn ? 'in' : 'out'}">
            <i class="fa-solid ${isStockIn ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down'}"></i>
          </div>
          <div class="timeline-content">
            <div class="timeline-desc">
              <strong>${isStockIn ? 'Stock Added' : 'Stock Shipped'}</strong>: ${t.Quantity} units of ${pName} (${t.ProductID})
            </div>
            ${t.Remarks ? `<span class="timeline-notes">"${t.Remarks}"</span>` : ''}
            <span class="timeline-time">${dateString}</span>
          </div>
        `;
        recentActivityList.appendChild(timelineItem);
      });
    }

    // 4. Render Critical Action Items (products in alert threshold)
    const criticalActionsList = document.getElementById("criticalActionsList");
    criticalActionsList.innerHTML = "";

    const criticalItems = products.filter(p => p.Quantity <= p.ReorderLevel).slice(0, 4);

    if (criticalItems.length === 0) {
      criticalActionsList.innerHTML = `
        <div class="notif-empty" style="padding: 10px 0;">
          <i class="fa-solid fa-circle-check text-success" style="font-size: 20px; margin-bottom: 4px;"></i>
          <p style="font-size: 12px;">Warehouse stock holds healthy levels.</p>
        </div>
      `;
    } else {
      criticalItems.forEach(p => {
        const isOut = p.Quantity === 0;
        const itemCard = document.createElement("div");
        itemCard.className = `crit-item ${isOut ? 'danger-alert' : 'warning-alert'}`;
        itemCard.innerHTML = `
          <div class="crit-info">
            <h4>${p.ProductName}</h4>
            <p>${isOut ? 'Out of Stock' : 'Stock level ' + p.Quantity + ' (Safety Reorder: ' + p.ReorderLevel + ')'}</p>
          </div>
          <button class="crit-action-btn" onclick="app.quickReplenish('${p.ProductID}')">
            ${isOut ? 'Replenish' : 'Restock'}
          </button>
        `;
        criticalActionsList.appendChild(itemCard);
      });
    }
  }

  // ChartJS graphic renders
  renderDashboardCharts() {
    const products = window.inventoryDB.getProducts();
    const categories = window.inventoryDB.getCategories();
    
    // Destroy existing chart frames to prevent overlays
    if (this.charts.stockLevels) this.charts.stockLevels.destroy();
    if (this.charts.categoryValuation) this.charts.categoryValuation.destroy();

    // Chart.js Theme aware colors
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const gridColor = isDark ? "#1e293b" : "#cbd5e1";
    const textColor = isDark ? "#94a3b8" : "#475569";

    // --- CHART 1: Stock Levels vs Reorder Levels ---
    const sortedProducts = [...products].sort((a, b) => a.Quantity - b.Quantity).slice(0, 6);
    const chart1Labels = sortedProducts.map(p => p.ProductName.length > 15 ? p.ProductName.substring(0, 15) + "..." : p.ProductName);
    const chart1Stock = sortedProducts.map(p => p.Quantity);
    const chart1Reorder = sortedProducts.map(p => p.ReorderLevel);

    const ctx1 = document.getElementById("stockLevelChart").getContext("2d");
    this.charts.stockLevels = new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: chart1Labels,
        datasets: [
          {
            label: 'Current Warehouse Stock',
            data: chart1Stock,
            backgroundColor: 'rgba(37, 99, 235, 0.75)',
            borderColor: '#2563eb',
            borderWidth: 1,
            borderRadius: 6
          },
          {
            label: 'Safety Threshold Limit',
            data: chart1Reorder,
            backgroundColor: 'rgba(239, 68, 68, 0.6)',
            borderColor: '#ef4444',
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 600 } } }
        },
        scales: {
          x: { ticks: { color: textColor }, grid: { display: false } },
          y: { ticks: { color: textColor }, grid: { color: gridColor } }
        }
      }
    });

    // --- CHART 2: Value distribution by Category ---
    const categoryTotals = categories.map(cat => {
      const catProducts = products.filter(p => p.CategoryID === cat.CategoryID);
      const totalValue = catProducts.reduce((sum, p) => sum + (p.Quantity * p.PurchasePrice), 0);
      return {
        name: cat.CategoryName,
        value: totalValue
      };
    }).filter(item => item.value > 0);

    const chart2Labels = categoryTotals.map(c => c.name);
    const chart2Data = categoryTotals.map(c => c.value);

    const ctx2 = document.getElementById("categoryValueChart").getContext("2d");
    this.charts.categoryValuation = new Chart(ctx2, {
      type: 'doughnut',
      data: {
        labels: chart2Labels,
        datasets: [{
          data: chart2Data,
          backgroundColor: [
            'rgba(79, 70, 229, 0.85)',
            'rgba(37, 99, 235, 0.85)',
            'rgba(13, 148, 136, 0.85)',
            'rgba(234, 88, 12, 0.85)',
            'rgba(225, 29, 72, 0.85)',
            'rgba(100, 116, 139, 0.85)'
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 600 } }
          }
        }
      }
    });
  }

  // ==========================================================================
  // MODULE 2: PRODUCT MANAGEMENT RENDER LOGIC
  // ==========================================================================
  renderProductsView() {
    const products = window.inventoryDB.getProducts();
    const categories = window.inventoryDB.getCategories();
    const suppliers = window.inventoryDB.getSuppliers();
    
    // Apply filters
    const searchVal = this.prodFilterSearch.value.trim().toLowerCase();
    const categoryVal = this.prodFilterCategory.value;
    const supplierVal = this.prodFilterSupplier.value;
    const stockStatusVal = this.prodFilterStockStatus.value;

    let filtered = products.filter(p => {
      // 1. Search Query
      const matchSearch = p.ProductName.toLowerCase().includes(searchVal) ||
                            p.ProductID.toLowerCase().includes(searchVal) ||
                            p.Barcode.toLowerCase().includes(searchVal);

      // 2. Category
      const matchCategory = !categoryVal || p.CategoryID === categoryVal;

      // 3. Supplier
      const matchSupplier = !supplierVal || p.SupplierID === supplierVal;

      // 4. Stock status
      let matchStatus = true;
      if (stockStatusVal === "instock") {
        matchStatus = p.Quantity > p.ReorderLevel;
      } else if (stockStatusVal === "lowstock") {
        matchStatus = p.Quantity > 0 && p.Quantity <= p.ReorderLevel;
      } else if (stockStatusVal === "outofstock") {
        matchStatus = p.Quantity === 0;
      }

      return matchSearch && matchCategory && matchSupplier && matchStatus;
    });

    // Save filtered list size
    this.productPagination.filteredProducts = filtered;

    // Handle pagination limits
    const totalCount = filtered.length;
    const pageSize = this.productPagination.pageSize;
    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
    
    if (this.productPagination.currentPage > totalPages) {
      this.productPagination.currentPage = totalPages;
    }

    const startIdx = (this.productPagination.currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, totalCount);

    const paginatedProducts = filtered.slice(startIdx, endIdx);

    // Update layout indicators
    this.prodPaginationInfo.textContent = totalCount > 0 ? 
      `Showing ${startIdx + 1}-${endIdx} of ${totalCount} entries` : "Showing 0 entries";

    this.renderProductsTable(paginatedProducts, categories, suppliers);
    this.renderProductsPaginationControls(totalPages);
  }

  renderProductsTable(products, categories, suppliers) {
    this.productsTableBody.innerHTML = "";

    if (products.length === 0) {
      this.productsTableBody.innerHTML = `
        <tr>
          <td colspan="9" class="text-center text-muted" style="padding: 40px;">
            <i class="fa-solid fa-box-open mb-2" style="font-size: 32px;"></i>
            <p>No products found matching active filter options.</p>
          </td>
        </tr>
      `;
      return;
    }

    const isAdmin = this.role === "Admin";

    products.forEach(p => {
      const cat = categories.find(c => c.CategoryID === p.CategoryID);
      const catName = cat ? cat.CategoryName : "Unknown";
      
      const sup = suppliers.find(s => s.SupplierID === p.SupplierID);
      const supName = sup ? sup.SupplierName : "Unknown";

      // Status pill checks
      let statusClass = "in-stock";
      let statusLabel = "In Stock";
      if (p.Quantity === 0) {
        statusClass = "out-stock";
        statusLabel = "Out of Stock";
      } else if (p.Quantity <= p.ReorderLevel) {
        statusClass = "low-stock";
        statusLabel = "Low Stock";
      }

      // Mock Product Image theme color assignment
      const imageTheme = p.Image || "default";
      const thumbnailClass = `prod-thumbnail thumbnail-${imageTheme.split("_")[0] || 'default'}`;
      const initials = p.ProductName.substring(0, 2).toUpperCase();

      const row = document.createElement("tr");
      if (p.Quantity <= p.ReorderLevel) {
        row.className = p.Quantity === 0 ? "table-danger-alert" : "table-warning-alert";
      }
      row.innerHTML = `
        <td>
          <div class="prod-cell-details">
            <div class="${thumbnailClass}">${initials}</div>
            <div class="prod-meta">
              <h4>${p.ProductName}</h4>
              <span>Barcode: ${p.Barcode || 'N/A'}</span>
            </div>
          </div>
        </td>
        <td><code style="font-weight: 700;">${p.ProductID}</code></td>
        <td><span class="category-chip">${catName}</span></td>
        <td><span class="supplier-chip">${supName}</span></td>
        <td>
          <div style="font-size: 12px;">
            <div>Buy: <strong>$${p.PurchasePrice.toFixed(2)}</strong></div>
            <div style="color: var(--text-muted);">Sell: $${p.SellingPrice.toFixed(2)}</div>
          </div>
        </td>
        <td class="text-center"><strong style="font-size: 14px;">${p.Quantity}</strong></td>
        <td>
          <span class="status-badge ${statusClass}">
            <span class="badge-dot"></span>
            ${statusLabel}
          </span>
        </td>
        <td class="text-right">
          <div class="action-btn-group">
            <button class="action-btn stock-btn" onclick="app.showStockModal('Stock In', '${p.ProductID}')" title="Adjust Stock">
              <i class="fa-solid fa-arrow-right-arrow-left"></i>
            </button>
            <button class="action-btn edit-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.showProductModal('${p.ProductID}')` : ''}" title="${isAdmin ? 'Edit Details' : 'Admin rights required'}">
              <i class="fa-solid ${isAdmin ? 'fa-pen-to-square' : 'fa-lock'}"></i>
            </button>
            <button class="action-btn delete-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.deleteProduct('${p.ProductID}')` : ''}" title="${isAdmin ? 'Delete Product' : 'Admin rights required'}">
              <i class="fa-solid ${isAdmin ? 'fa-trash' : 'fa-lock'}"></i>
            </button>
          </div>
        </td>
      `;
      this.productsTableBody.appendChild(row);
    });

    // Make sure dynamically injected lock rules trigger visual elements properly
    this.toggleRoleBasedUI();
  }

  renderProductsPaginationControls(totalPages) {
    this.prodPaginationControls.innerHTML = "";

    // Prev Button
    const prevLink = document.createElement("a");
    prevLink.className = `page-link ${this.productPagination.currentPage === 1 ? 'disabled' : ''}`;
    prevLink.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
    prevLink.addEventListener("click", () => {
      if (this.productPagination.currentPage > 1) {
        this.productPagination.currentPage--;
        this.renderProductsView();
      }
    });
    this.prodPaginationControls.appendChild(prevLink);

    // Number Buttons
    for (let i = 1; i <= totalPages; i++) {
      const pageBtn = document.createElement("a");
      pageBtn.className = `page-link ${this.productPagination.currentPage === i ? 'active' : ''}`;
      pageBtn.textContent = i;
      pageBtn.addEventListener("click", () => {
        this.productPagination.currentPage = i;
        this.renderProductsView();
      });
      this.prodPaginationControls.appendChild(pageBtn);
    }

    // Next Button
    const nextLink = document.createElement("a");
    nextLink.className = `page-link ${this.productPagination.currentPage === totalPages ? 'disabled' : ''}`;
    nextLink.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
    nextLink.addEventListener("click", () => {
      if (this.productPagination.currentPage < totalPages) {
        this.productPagination.currentPage++;
        this.renderProductsView();
      }
    });
    this.prodPaginationControls.appendChild(nextLink);
  }

  // Handle Product CRUD Modals
  showProductModal(productId = null) {
    if (this.role !== "Admin" && productId !== null) {
      this.showToast("Admin privileges required to edit database items.", "error");
      return;
    }

    this.updateSelectDropdowns();
    const form = document.getElementById("productForm");
    form.reset();

    const titleEl = document.getElementById("productModalTitle");
    const idInput = document.getElementById("prodFormId");
    const qtyInput = document.getElementById("prodFormQuantity");

    if (productId) {
      titleEl.textContent = "Edit Product Details";
      const products = window.inventoryDB.getProducts();
      const p = products.find(prod => prod.ProductID === productId);

      if (p) {
        idInput.value = p.ProductID;
        document.getElementById("prodFormName").value = p.ProductName;
        document.getElementById("prodFormBarcode").value = p.Barcode;
        document.getElementById("prodFormCategory").value = p.CategoryID;
        document.getElementById("prodFormSupplier").value = p.SupplierID;
        document.getElementById("prodFormPurchasePrice").value = p.PurchasePrice;
        document.getElementById("prodFormSellingPrice").value = p.SellingPrice;
        
        qtyInput.value = p.Quantity;
        qtyInput.disabled = true; // restrict initial Qty edits - must use stock transactions

        document.getElementById("prodFormReorder").value = p.ReorderLevel;
        document.getElementById("prodFormImageTheme").value = p.Image ? p.Image.split("_")[0] : "electronics";

        this.calculateMarkup();
      }
    } else {
      titleEl.textContent = "Create New Product SKU";
      idInput.value = "";
      qtyInput.disabled = false;
      document.getElementById("prodFormMarkupBadge").textContent = "0% Markup";
    }

    this.openModal("productModal");
  }

  calculateMarkup() {
    const buy = parseFloat(document.getElementById("prodFormPurchasePrice").value) || 0;
    const sell = parseFloat(document.getElementById("prodFormSellingPrice").value) || 0;
    const badge = document.getElementById("prodFormMarkupBadge");

    if (buy <= 0) {
      badge.textContent = "0% Markup";
      return;
    }

    const markup = ((sell - buy) / buy) * 100;
    badge.textContent = `${markup.toFixed(0)}% Markup`;
  }

  handleProductSubmit() {
    const id = document.getElementById("prodFormId").value;
    const pData = {
      ProductName: document.getElementById("prodFormName").value.trim(),
      Barcode: document.getElementById("prodFormBarcode").value.trim(),
      CategoryID: document.getElementById("prodFormCategory").value,
      SupplierID: document.getElementById("prodFormSupplier").value,
      PurchasePrice: document.getElementById("prodFormPurchasePrice").value,
      SellingPrice: document.getElementById("prodFormSellingPrice").value,
      Quantity: document.getElementById("prodFormQuantity").value,
      ReorderLevel: document.getElementById("prodFormReorder").value,
      Image: document.getElementById("prodFormImageTheme").value + "_placeholder"
    };

    try {
      if (id) {
        // Edit flow
        window.inventoryDB.updateProduct(id, pData);
        this.showToast(`Product ${id} details updated successfully.`, "success");
      } else {
        // Create flow
        const newProduct = window.inventoryDB.addProduct(pData);
        this.showToast(`Product ${newProduct.ProductID} registered successfully.`, "success");
      }

      this.closeModal("productModal");
      this.updateGlobalWidgets();
      this.renderProductsView();
    } catch (err) {
      this.showToast(err.message, "error");
    }
  }

  deleteProduct(productId) {
    if (confirm(`Are you absolutely sure you want to delete product SKU ${productId}? This will remove all audit transaction histories.`)) {
      const success = window.inventoryDB.deleteProduct(productId);
      if (success) {
        this.showToast(`Product SKU ${productId} deleted successfully.`, "success");
        this.updateGlobalWidgets();
        this.renderProductsView();
      } else {
        this.showToast("Failed to delete product.", "error");
      }
    }
  }

  // ==========================================================================
  // MODULE 3: CATEGORY MANAGEMENT RENDER LOGIC
  // ==========================================================================
  renderCategoriesView() {
    const categories = window.inventoryDB.getCategories();
    const products = window.inventoryDB.getProducts();
    const isAdmin = this.role === "Admin";

    this.categoriesTableBody.innerHTML = "";
    this.categoryStatList.innerHTML = "";

    categories.forEach(c => {
      const count = products.filter(p => p.CategoryID === c.CategoryID).length;

      // Table Render
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code style="font-weight: 700;">#${c.CategoryID}</code></td>
        <td><strong>${c.CategoryName}</strong></td>
        <td class="text-center"><span class="badge-pill bg-gray">${count} Items</span></td>
        <td class="text-right">
          <div class="action-btn-group">
            <button class="action-btn edit-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.showCategoryModal('${c.CategoryID}')` : ''}" title="${isAdmin ? 'Edit' : 'Admin required'}">
              <i class="fa-solid ${isAdmin ? 'fa-pen-to-square' : 'fa-lock'}"></i>
            </button>
            <button class="action-btn delete-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.deleteCategory('${c.CategoryID}')` : ''}" title="${isAdmin ? 'Delete' : 'Admin required'}">
              <i class="fa-solid ${isAdmin ? 'fa-trash' : 'fa-lock'}"></i>
            </button>
          </div>
        </td>
      `;
      this.categoriesTableBody.appendChild(row);

      // Side Analytics Render
      const catValue = products.filter(p => p.CategoryID === c.CategoryID)
                              .reduce((sum, p) => sum + (p.Quantity * p.PurchasePrice), 0);

      const statItem = document.createElement("div");
      statItem.className = "stat-item";
      statItem.innerHTML = `
        <div class="stat-item-label">
          <h4>${c.CategoryName}</h4>
          <span>Asset Value: $${catValue.toFixed(2)}</span>
        </div>
        <div class="stat-item-value">${count} SKUs</div>
      `;
      this.categoryStatList.appendChild(statItem);
    });

    this.toggleRoleBasedUI();
  }

  showCategoryModal(id = null) {
    if (this.role !== "Admin") {
      this.showToast("Admin permissions required to manage settings.", "error");
      return;
    }

    const titleEl = document.getElementById("categoryModalTitle");
    const formId = document.getElementById("categoryFormId");
    const nameInput = document.getElementById("categoryFormName");

    if (id) {
      titleEl.textContent = "Edit Category Name";
      const categories = window.inventoryDB.getCategories();
      const cat = categories.find(c => c.CategoryID === id);
      if (cat) {
        formId.value = cat.CategoryID;
        nameInput.value = cat.CategoryName;
      }
    } else {
      titleEl.textContent = "Add Inventory Category";
      formId.value = "";
      nameInput.value = "";
    }

    this.openModal("categoryModal");
  }

  handleCategorySubmit() {
    const id = document.getElementById("categoryFormId").value;
    const name = document.getElementById("categoryFormName").value.trim();

    if (!name) return;

    if (id) {
      window.inventoryDB.updateCategory(id, name);
      this.showToast(`Category updated to "${name}"`, "success");
    } else {
      const newCat = window.inventoryDB.addCategory(name);
      this.showToast(`Category "${newCat.CategoryName}" added successfully.`, "success");
    }

    this.closeModal("categoryModal");
    this.updateGlobalWidgets();
    this.renderCategoriesView();
  }

  deleteCategory(id) {
    try {
      if (confirm("Are you sure you want to delete this category?")) {
        window.inventoryDB.deleteCategory(id);
        this.showToast("Category removed successfully.", "success");
        this.updateGlobalWidgets();
        this.renderCategoriesView();
      }
    } catch (err) {
      this.showToast(err.message, "error");
    }
  }

  // ==========================================================================
  // MODULE 4: SUPPLIER RENDER LOGIC
  // ==========================================================================
  renderSuppliersView() {
    const suppliers = window.inventoryDB.getSuppliers();
    const products = window.inventoryDB.getProducts();
    const isAdmin = this.role === "Admin";

    this.suppliersGrid.innerHTML = "";

    if (suppliers.length === 0) {
      this.suppliersGrid.innerHTML = `
        <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-secondary);">
          <i class="fa-solid fa-truck-ramp-box mb-2" style="font-size: 32px;"></i>
          <p>No wholesalers or suppliers registered.</p>
        </div>
      `;
      return;
    }

    suppliers.forEach(s => {
      const itemsCount = products.filter(p => p.SupplierID === s.SupplierID).length;

      const card = document.createElement("div");
      card.className = "supplier-card";
      card.innerHTML = `
        <div class="supplier-card-header">
          <h3>${s.SupplierName}</h3>
          <span class="supplier-contact-name"><i class="fa-solid fa-user-tie mr-2"></i>${s.ContactPerson}</span>
        </div>
        <div class="supplier-details-list">
          <div class="supplier-detail-row">
            <i class="fa-solid fa-phone"></i>
            <span>${s.Phone}</span>
          </div>
          <div class="supplier-detail-row">
            <i class="fa-solid fa-envelope"></i>
            <span>${s.Email}</span>
          </div>
          <div class="supplier-detail-row">
            <i class="fa-solid fa-location-dot"></i>
            <span>${s.Address || 'No Address Logged'}</span>
          </div>
          <div class="supplier-detail-row mt-2" style="font-weight: 700; color: var(--accent-blue);">
            <i class="fa-solid fa-boxes-stacked"></i>
            <span>Provides ${itemsCount} Active SKUs</span>
          </div>
        </div>
        <div class="supplier-card-actions">
          <button class="action-btn edit-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.showSupplierModal('${s.SupplierID}')` : ''}" title="${isAdmin ? 'Edit Details' : 'Admin rights required'}">
            <i class="fa-solid ${isAdmin ? 'fa-pen-to-square' : 'fa-lock'}"></i>
          </button>
          <button class="action-btn delete-btn ${isAdmin ? '' : 'disabled-lock'}" onclick="${isAdmin ? `app.deleteSupplier('${s.SupplierID}')` : ''}" title="${isAdmin ? 'Delete Supplier' : 'Admin rights required'}">
            <i class="fa-solid ${isAdmin ? 'fa-trash' : 'fa-lock'}"></i>
          </button>
        </div>
      `;
      this.suppliersGrid.appendChild(card);
    });

    this.toggleRoleBasedUI();
  }

  showSupplierModal(id = null) {
    if (this.role !== "Admin") {
      this.showToast("Admin permissions required to edit supplier directory.", "error");
      return;
    }

    const titleEl = document.getElementById("supplierModalTitle");
    const formId = document.getElementById("supplierFormId");
    const formName = document.getElementById("supplierFormName");
    const formPerson = document.getElementById("supplierFormPerson");
    const formPhone = document.getElementById("supplierFormPhone");
    const formEmail = document.getElementById("supplierFormEmail");
    const formAddress = document.getElementById("supplierFormAddress");

    if (id) {
      titleEl.textContent = "Edit Supplier Profile";
      const suppliers = window.inventoryDB.getSuppliers();
      const s = suppliers.find(sup => sup.SupplierID === id);

      if (s) {
        formId.value = s.SupplierID;
        formName.value = s.SupplierName;
        formPerson.value = s.ContactPerson;
        formPhone.value = s.Phone;
        formEmail.value = s.Email;
        formAddress.value = s.Address || "";
      }
    } else {
      titleEl.textContent = "Register Wholesale Supplier";
      formId.value = "";
      formName.value = "";
      formPerson.value = "";
      formPhone.value = "";
      formEmail.value = "";
      formAddress.value = "";
    }

    this.openModal("supplierModal");
  }

  handleSupplierSubmit() {
    const id = document.getElementById("supplierFormId").value;
    const sData = {
      SupplierName: document.getElementById("supplierFormName").value.trim(),
      ContactPerson: document.getElementById("supplierFormPerson").value.trim(),
      Phone: document.getElementById("supplierFormPhone").value.trim(),
      Email: document.getElementById("supplierFormEmail").value.trim(),
      Address: document.getElementById("supplierFormAddress").value.trim()
    };

    try {
      if (id) {
        window.inventoryDB.updateSupplier(id, sData);
        this.showToast(`Supplier profile "${sData.SupplierName}" updated.`, "success");
      } else {
        const newSup = window.inventoryDB.addSupplier(sData);
        this.showToast(`Supplier wholesaler "${newSup.SupplierName}" registered.`, "success");
      }

      this.closeModal("supplierModal");
      this.updateGlobalWidgets();
      this.renderSuppliersView();
    } catch (err) {
      this.showToast(err.message, "error");
    }
  }

  deleteSupplier(id) {
    try {
      if (confirm("Are you sure you want to delete this supplier profile?")) {
        window.inventoryDB.deleteSupplier(id);
        this.showToast("Supplier profile deleted.", "success");
        this.updateGlobalWidgets();
        this.renderSuppliersView();
      }
    } catch (err) {
      this.showToast(err.message, "error");
    }
  }

  // ==========================================================================
  // MODULE 5: STOCK FLOW TRANSACTION LOGIC
  // ==========================================================================
  renderTransactionsView() {
    const transactions = window.inventoryDB.getTransactions();
    const products = window.inventoryDB.getProducts();
    const typeFilter = this.txnFilterType.value;

    this.transactionsTableBody.innerHTML = "";

    let filtered = [...transactions].sort((a, b) => new Date(b.Date) - new Date(a.Date));

    if (typeFilter) {
      filtered = filtered.filter(t => t.TransactionType === typeFilter);
    }

    if (filtered.length === 0) {
      this.transactionsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted" style="padding: 40px;">
            <i class="fa-solid fa-clock-rotate-left mb-2" style="font-size: 32px;"></i>
            <p>No transactions registered under this filter.</p>
          </td>
        </tr>
      `;
      return;
    }

    filtered.forEach(t => {
      const prod = products.find(p => p.ProductID === t.ProductID);
      const prodName = prod ? prod.ProductName : `Unknown SKU (${t.ProductID})`;
      const isStockIn = t.TransactionType === "Stock In";
      const dateText = new Date(t.Date).toLocaleString();

      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${t.TransactionID}</code></td>
        <td>
          <div style="font-weight: 700;">${prodName}</div>
          <div class="text-muted" style="font-size: 11px;">SKU: ${t.ProductID}</div>
        </td>
        <td>
          <span class="status-badge ${isStockIn ? 'in-stock' : 'out-stock'}">
            <span class="badge-dot"></span>
            ${t.TransactionType}
          </span>
        </td>
        <td class="text-center"><strong>${t.Quantity}</strong></td>
        <td>${dateText}</td>
        <td><span class="text-secondary">${t.Remarks || '--'}</span></td>
      `;
      this.transactionsTableBody.appendChild(row);
    });
  }

  showStockModal(type = "Stock In", productId = null) {
    this.updateSelectDropdowns();

    const titleEl = document.getElementById("stockModalTitle");
    const typeValEl = document.getElementById("stockFormTypeVal");
    const currentValEl = document.getElementById("stockFormCurrentVal");
    const warningEl = document.getElementById("stockFormQtyWarning");
    const form = document.getElementById("stockForm");
    
    form.reset();
    warningEl.classList.add("hidden");

    titleEl.textContent = type === "Stock In" ? "Add Inventory Stock (Stock In)" : "Deduct Warehouse Stock (Stock Out)";
    typeValEl.textContent = type;
    typeValEl.className = `readonly-badge ${type === "Stock In" ? 'bg-blue' : 'bg-gray'}`;

    if (productId) {
      document.getElementById("stockFormProduct").value = productId;
    }

    this.updateStockFormLimit();
    this.openModal("stockModal");
  }

  updateStockFormLimit() {
    const prodId = document.getElementById("stockFormProduct").value;
    const currentValEl = document.getElementById("stockFormCurrentVal");
    const warningEl = document.getElementById("stockFormQtyWarning");

    if (!prodId) {
      currentValEl.textContent = "0 units";
      return;
    }

    const products = window.inventoryDB.getProducts();
    const p = products.find(prod => prod.ProductID === prodId);
    
    if (p) {
      currentValEl.textContent = `${p.Quantity} units in storage`;
    }

    warningEl.classList.add("hidden");
  }

  handleStockSubmit() {
    const prodId = document.getElementById("stockFormProduct").value;
    const type = document.getElementById("stockFormTypeVal").textContent;
    const qty = parseInt(document.getElementById("stockFormQty").value) || 0;
    const remarks = document.getElementById("stockFormRemarks").value.trim();

    if (!prodId || qty <= 0) return;

    const products = window.inventoryDB.getProducts();
    const pIdx = products.findIndex(p => p.ProductID === prodId);

    if (pIdx !== -1) {
      const p = products[pIdx];

      // Validation check for Stock Out exceeding current quantity
      if (type === "Stock Out" && qty > p.Quantity) {
        document.getElementById("stockFormQtyWarning").classList.remove("hidden");
        return;
      }

      window.inventoryDB.addTransaction({
        ProductID: prodId,
        TransactionType: type,
        Quantity: qty,
        Remarks: remarks
      });

      this.showToast(`Logged ${qty} units ${type === 'Stock In' ? 'Replenished' : 'Deducted'} for SKU ${prodId}.`, "success");
      this.closeModal("stockModal");
      this.updateGlobalWidgets();
      this.switchView(this.currentView); // Refresh current panel
    }
  }

  quickReplenish(productId) {
    this.showStockModal("Stock In", productId);
  }

  // ==========================================================================
  // MODULE 6: REPLENISHMENT ALERTS VIEW
  // ==========================================================================
  renderAlertsView() {
    const products = window.inventoryDB.getProducts();
    const suppliers = window.inventoryDB.getSuppliers();
    
    const lowStockItems = products.filter(p => p.Quantity <= p.ReorderLevel);

    this.lowStockTableBody.innerHTML = "";
    this.alertCriticalCountText.textContent = `${lowStockItems.length} Safety Violations`;

    if (lowStockItems.length === 0) {
      this.lowStockTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted" style="padding: 40px;">
            <i class="fa-solid fa-circle-check text-success mb-2" style="font-size: 32px;"></i>
            <p>Perfect! No inventory items currently drop below safety margins.</p>
          </td>
        </tr>
      `;
      this.reorderAllBtn.classList.add("disabled-lock");
      return;
    }

    this.reorderAllBtn.classList.remove("disabled-lock");

    lowStockItems.forEach(p => {
      const isOut = p.Quantity === 0;
      const sup = suppliers.find(s => s.SupplierID === p.SupplierID);
      const supName = sup ? sup.SupplierName : "Unknown Supplier";

      const row = document.createElement("tr");
      row.className = isOut ? "table-danger-alert" : "table-warning-alert";
      row.innerHTML = `
        <td>
          <div style="font-weight: 700;">${p.ProductName}</div>
          <span style="font-size: 11px; color: var(--text-muted);">Barcode: ${p.Barcode || 'N/A'}</span>
        </td>
        <td><code>${p.ProductID}</code></td>
        <td class="text-center"><strong style="color: var(--color-danger);">${p.Quantity}</strong></td>
        <td class="text-center">${p.ReorderLevel}</td>
        <td>
          <span class="status-badge ${isOut ? 'out-stock' : 'low-stock'}">
            <span class="badge-dot"></span>
            ${isOut ? 'Depleted' : 'Low Warning'}
          </span>
        </td>
        <td class="text-right">
          <button class="btn btn-secondary btn-sm" onclick="app.quickReplenish('${p.ProductID}')">
            <i class="fa-solid fa-truck-ramp-box"></i> Restock
          </button>
        </td>
      `;
      this.lowStockTableBody.appendChild(row);
    });
  }

  reorderAllCriticalItems() {
    const products = window.inventoryDB.getProducts();
    const lowStockItems = products.filter(p => p.Quantity <= p.ReorderLevel);

    if (lowStockItems.length === 0) return;

    if (confirm(`Are you sure you want to issue restock purchase batches (+25 units each) for all ${lowStockItems.length} warning items?`)) {
      lowStockItems.forEach(p => {
        window.inventoryDB.addTransaction({
          ProductID: p.ProductID,
          TransactionType: "Stock In",
          Quantity: 25,
          Remarks: "Bulk automated replenishment trigger"
        });
      });

      this.showToast(`Automated restock commands registered. Safety logs loaded.`, "success");
      this.updateGlobalWidgets();
      this.renderAlertsView();
    }
  }

  // ==========================================================================
  // MODULE 7: EXECUTIVE REPORTS CENTER
  // ==========================================================================
  renderReportsView() {
    const products = window.inventoryDB.getProducts();
    const categories = window.inventoryDB.getCategories();
    const suppliers = window.inventoryDB.getSuppliers();

    // 1. Calculate Aggregate Financial Statistics
    const totalAssetVal = products.reduce((acc, p) => acc + (p.Quantity * p.PurchasePrice), 0);
    const totalSellingVal = products.reduce((acc, p) => acc + (p.Quantity * p.SellingPrice), 0);
    const totalProfitMargin = totalSellingVal - totalAssetVal;

    // Average product markup percentage calculation
    let totalMarkup = 0;
    let countMarkup = 0;
    products.forEach(p => {
      if (p.PurchasePrice > 0) {
        totalMarkup += ((p.SellingPrice - p.PurchasePrice) / p.PurchasePrice) * 100;
        countMarkup++;
      }
    });
    const avgMarkup = countMarkup > 0 ? (totalMarkup / countMarkup) : 0;

    document.getElementById("rep-total-value").textContent = `$${totalAssetVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById("rep-selling-value").textContent = `$${totalSellingVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById("rep-profit-margin").textContent = `$${totalProfitMargin.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById("rep-average-markup").textContent = `${avgMarkup.toFixed(0)}% Avg`;

    // 2. Render Categories Summary table
    this.reportCategoryTableBody.innerHTML = "";
    categories.forEach(c => {
      const catProducts = products.filter(p => p.CategoryID === c.CategoryID);
      const uniqueSKUs = catProducts.length;
      const totalUnits = catProducts.reduce((sum, p) => sum + p.Quantity, 0);
      const pAsset = catProducts.reduce((sum, p) => sum + (p.Quantity * p.PurchasePrice), 0);
      const pSelling = catProducts.reduce((sum, p) => sum + (p.Quantity * p.SellingPrice), 0);

      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong>${c.CategoryName}</strong></td>
        <td class="text-center">${uniqueSKUs}</td>
        <td class="text-center">${totalUnits}</td>
        <td class="text-right">$${pAsset.toFixed(2)}</td>
        <td class="text-right">$${pSelling.toFixed(2)}</td>
      `;
      this.reportCategoryTableBody.appendChild(row);
    });

    // 3. Render Low Stock alert lines table
    this.reportLowStockTableBody.innerHTML = "";
    const lowStockItems = products.filter(p => p.Quantity <= p.ReorderLevel);

    if (lowStockItems.length === 0) {
      this.reportLowStockTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted" style="padding: 20px;">
            No items violate warehouse safety thresholds.
          </td>
        </tr>
      `;
    } else {
      lowStockItems.forEach(p => {
        const sup = suppliers.find(s => s.SupplierID === p.SupplierID);
        const supName = sup ? sup.SupplierName : "Unknown";
        const required = Math.max(5, (p.ReorderLevel * 2) - p.Quantity);

        const row = document.createElement("tr");
        row.innerHTML = `
          <td><code>${p.ProductID}</code></td>
          <td>${p.ProductName}</td>
          <td>${supName}</td>
          <td class="text-center"><span class="text-danger" style="font-weight:700;">${p.Quantity}</span></td>
          <td class="text-center">${p.ReorderLevel}</td>
          <td class="text-right"><strong style="color: var(--color-success);">+${required} units</strong></td>
        `;
        this.reportLowStockTableBody.appendChild(row);
      });
    }

    // Set printable information dates
    document.getElementById("reportPrintDate").textContent = new Date().toLocaleString();
    document.getElementById("reportPrintRole").textContent = this.role;
  }

  exportToCSV() {
    const products = window.inventoryDB.getProducts();
    const categories = window.inventoryDB.getCategories();
    const suppliers = window.inventoryDB.getSuppliers();

    // Compile columns header row
    let csv = "Product ID,Product Name,Category,Supplier,Purchase Price,Selling Price,Quantity,Reorder Level,Barcode,Created Date\n";

    products.forEach(p => {
      const c = categories.find(cat => cat.CategoryID === p.CategoryID);
      const catName = c ? c.CategoryName : "Unknown";
      const s = suppliers.find(sup => sup.SupplierID === p.SupplierID);
      const supName = s ? s.SupplierName : "Unknown";

      // Escape commas inside name strings
      const escapedName = `"${p.ProductName.replace(/"/g, '""')}"`;
      const escapedCat = `"${catName.replace(/"/g, '""')}"`;
      const escapedSup = `"${supName.replace(/"/g, '""')}"`;

      csv += `${p.ProductID},${escapedName},${escapedCat},${escapedSup},${p.PurchasePrice},${p.SellingPrice},${p.Quantity},${p.ReorderLevel},${p.Barcode},${p.CreatedDate}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `smartstock_inventory_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    this.showToast("Product data exported to CSV spreadsheet.", "success");
  }

  printReport() {
    window.print();
  }

  // ==========================================================================
  // MODULE 8: SYSTEM SETTINGS LOGIC
  // ==========================================================================
  saveSettings() {
    const name = this.settingBusinessName.value.trim();
    const curr = this.settingCurrency.value.trim();
    const margin = this.settingAlertMargin.value.trim();

    if (!name || !curr) {
      this.showToast("Required settings input fields cannot be empty.", "error");
      return;
    }

    localStorage.setItem("sims_biz_name", name);
    localStorage.setItem("sims_currency", curr);
    localStorage.setItem("sims_alert_margin", margin);

    document.querySelectorAll(".sidebar-brand span").forEach(el => el.textContent = name);
    this.showToast("System configurations saved successfully.", "success");
  }

  downloadBackupJSON() {
    const rawData = window.inventoryDB.exportData();
    const blob = new Blob([rawData], { type: 'application/json' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `smartstock_database_backup_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    this.showToast("Database file downloaded successfully.", "success");
  }

  uploadBackupJSON(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target.result;
      const success = window.inventoryDB.importData(content);
      if (success) {
        this.showToast("Database state successfully restored from JSON.", "success");
        this.loadState();
      } else {
        this.showToast("Disaster Recovery error: Invalid JSON DB schema format.", "error");
      }
    };
    reader.readAsText(file);
    e.target.value = ""; // clear selector
  }

  confirmResetDatabase() {
    if (confirm("WARNING: This will wipe out all changes you have made and restore the application data store back to its factory default sample dataset. Proceed?")) {
      window.inventoryDB.resetData();
      this.showToast("Database has been reset to defaults.", "warning");
      this.loadState();
    }
  }

  // ==========================================================================
  // BARCODE SCANNER SIMULATION MODAL
  // ==========================================================================
  showScanModal() {
    const select = document.getElementById("scanSelector");
    const products = window.inventoryDB.getProducts();

    select.innerHTML = '<option value="">-- Choose registered SKU --</option>';
    products.forEach(p => {
      if (p.Barcode) {
        select.innerHTML += `<option value="${p.Barcode}">${p.ProductID} - ${p.ProductName} (${p.Barcode})</option>`;
      }
    });

    document.getElementById("scanManualCode").value = "";
    this.openModal("scanModal");
  }

  triggerScanEmit() {
    const barcode = document.getElementById("scanManualCode").value.trim();
    if (!barcode) return;

    const products = window.inventoryDB.getProducts();
    const target = products.find(p => p.Barcode === barcode || p.ProductID === barcode);

    if (target) {
      this.closeModal("scanModal");
      this.showToast(`Laser Target: Found product ${target.ProductName} (${target.ProductID})`, "success");
      
      // Jump and highlight
      this.switchView("products");
      this.prodFilterSearch.value = target.ProductID;
      this.renderProductsView();
      
      // Highlight the matching table row
      setTimeout(() => {
        const trs = this.productsTableBody.querySelectorAll("tr");
        trs.forEach(row => {
          if (row.innerHTML.includes(target.ProductID)) {
            row.style.outline = "2px solid var(--accent-blue)";
            row.style.transition = "outline var(--transition-slow)";
            setTimeout(() => {
              row.style.outline = "none";
            }, 3000);
          }
        });
      }, 300);

    } else {
      this.showToast(`No matches found for scanned barcode: "${barcode}"`, "error");
    }
  }

  // ==========================================================================
  // MODAL CONTROLLERS (OPEN / CLOSE)
  // ==========================================================================
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("open");
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("open");
    }
  }

  // ==========================================================================
  // TOAST POPUPS (NOTIFICATIONS FEEDBACK)
  // ==========================================================================
  showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconClass = "fa-circle-check";
    if (type === "error") iconClass = "fa-triangle-exclamation";
    if (type === "warning") iconClass = "fa-circle-exclamation";
    if (type === "info") iconClass = "fa-circle-info";

    toast.innerHTML = `
      <div class="toast-icon">
        <i class="fa-solid ${iconClass}"></i>
      </div>
      <div class="toast-content">
        <h5>${type.toUpperCase()}</h5>
        <p>${message}</p>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;

    this.toastContainer.appendChild(toast);

    // Auto close
    setTimeout(() => {
      toast.classList.add("toast-closing");
      toast.addEventListener("animationend", () => {
        toast.remove();
      });
    }, 4500);
  }
}

// Instantiate App
document.addEventListener("DOMContentLoaded", () => {
  window.app = new SmartInventoryApp();
});
