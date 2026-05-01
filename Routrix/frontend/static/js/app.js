const api = {
  getOrders: () => fetch("/api/orders").then((r) => r.json()),
  createOrder: (payload) =>
    fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then((r) => r.json()),
};

const qs = (selector) => document.querySelector(selector);

function renderOrders(orders, container) {
  if (!orders || !orders.length) {
    container.textContent = "No orders found.";
    return;
  }
  container.textContent = JSON.stringify(orders, null, 2);
}

async function refreshOrders() {
  const el = qs("#ordersList");
  if (!el) return;
  const orders = await api.getOrders();
  renderOrders(orders, el);
}

async function trackOrder() {
  const id = qs("#orderId")?.value?.trim();
  const res = qs("#trackingResult");
  if (!id) {
    res.textContent = "Enter an order id to track.";
    return;
  }
  const orders = await api.getOrders();
  const order = orders.find((o) => o.id === id);
  res.textContent = order ? JSON.stringify(order, null, 2) : "Order not found.";
}

async function createOrder() {
  const customer = qs("#customer")?.value?.trim();
  const pickup = qs("#pickup")?.value?.trim();
  const dropoff = qs("#dropoff")?.value?.trim();
  const out = qs("#bookingResult");
  if (!customer || !pickup || !dropoff) {
    out.textContent = "All fields are required.";
    return;
  }

  const id = `${Date.now()}`;
  const payload = { id, customer, pickup, dropoff };
  const order = await api.createOrder(payload);
  out.textContent = `Created order:\n${JSON.stringify(order, null, 2)}`;
}

window.addEventListener("DOMContentLoaded", () => {
  qs("#refreshOrders")?.addEventListener("click", refreshOrders);
  qs("#trackBtn")?.addEventListener("click", trackOrder);
  qs("#createOrder")?.addEventListener("click", createOrder);
  refreshOrders();
});
