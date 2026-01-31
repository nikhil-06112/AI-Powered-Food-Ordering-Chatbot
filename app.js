(function () {
  'use strict';

  const MENU = [
    { id: 1, name: 'Pav Bhaji', price: 120, image: "Pav Bhaji.webp" },
    { id: 2, name: 'Chole Bhature', price: 120, image: 'Chole Bhature.webp' },
    { id: 3, name: 'Pizza', price: 100, image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&q=80' },
    { id: 4, name: 'Mango Lassi', price: 50, image: 'Mango.jpeg' },
    { id: 5, name: 'Masala Dosa', price: 120, image: 'Masala Dosa.jpeg' },
    { id: 6, name: 'Vegetable Biryani', price: 80, image: 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600&q=80' },
    { id: 7, name: 'Vada Pav', price: 50, image: 'vadaa.jpeg' },
    { id: 8, name: 'Rava Dosa', price: 100, image: 'rava.jpeg' },
    { id: 9, name: 'Samosa', price: 20, image: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&q=80' }
  ];

  let cart = [];
  const CART_KEY = 'spicebite_cart';
  function loadCart() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      cart = raw ? JSON.parse(raw) : [];
    } catch (_) {
      cart = [];
    }
    renderCart();
    updateCartCount();
  }

  function saveCart() {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    renderCart();
    updateCartCount();
  }

  function addToCart(itemId, qty) {
    const item = MENU.find(function (m) { return m.id === itemId; });
    if (!item || qty < 1) return;
    const existing = cart.find(function (c) { return c.id === itemId; });
    if (existing) {
      existing.qty += qty;
    } else {
      cart.push({ id: item.id, name: item.name, price: item.price, qty: qty });
    }
    saveCart();
  }

  function removeFromCart(itemId) {
    cart = cart.filter(function (c) { return c.id !== itemId; });
    saveCart();
  }

  function setCartQty(itemId, qty) {
    if (qty < 1) {
      removeFromCart(itemId);
      return;
    }
    const existing = cart.find(function (c) { return c.id === itemId; });
    if (existing) existing.qty = qty;
    saveCart();
  }

  function getCartTotal() {
    return cart.reduce(function (sum, c) { return sum + c.price * c.qty; }, 0);
  }

  function updateCartCount() {
    const total = cart.reduce(function (s, c) { return s + c.qty; }, 0);
    const el = document.getElementById('cartCount');
    if (el) {
      el.textContent = total;
      el.classList.toggle('has-items', total > 0);
    }
  }

  function renderMenu() {
    const grid = document.getElementById('menuGrid');
    if (!grid) return;
    grid.innerHTML = MENU.map(function (item) {
      return (
        '<article class="menu-card">' +
          '<div class="menu-card-image">' +
            '<img src="' + escapeHtml(item.image) + '" alt="' + escapeHtml(item.name) + '" loading="lazy">' +
          '</div>' +
          '<div class="menu-card-body">' +
            '<h3>' + escapeHtml(item.name) + '</h3>' +
            '<p class="menu-price">₹' + item.price + '</p>' +
            '<div class="menu-actions">' +
              '<input type="number" min="1" max="20" value="1" class="menu-qty" data-id="' + item.id + '">' +
              '<button type="button" class="btn btn-primary btn-add" data-id="' + item.id + '">Add to Cart</button>' +
            '</div>' +
          '</div>' +
        '</article>'
      );
    }).join('');

    grid.querySelectorAll('.btn-add').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const id = parseInt(btn.dataset.id, 10);
        const card = btn.closest('.menu-card');
        const qtyInput = card ? card.querySelector('.menu-qty') : null;
        const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value, 10) || 1) : 1;
        addToCart(id, qty);
        openCart();
      });
    });
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function renderCart() {
    const list = document.getElementById('cartList');
    const empty = document.getElementById('cartEmpty');
    const footer = document.getElementById('cartFooter');
    const totalEl = document.getElementById('cartTotal');
    if (!list || !empty || !footer || !totalEl) return;

    if (cart.length === 0) {
      list.innerHTML = '';
      empty.hidden = false;
      footer.hidden = true;
      return;
    }
    empty.hidden = true;
    footer.hidden = false;
    totalEl.textContent = '₹' + getCartTotal();

    list.innerHTML = cart.map(function (c) {
      return (
        '<li class="cart-item">' +
          '<div class="cart-item-info">' +
            '<span class="cart-item-name">' + escapeHtml(c.name) + '</span>' +
            '<span class="cart-item-price">₹' + c.price + ' × ' + c.qty + '</span>' +
          '</div>' +
          '<div class="cart-item-actions">' +
            '<input type="number" min="1" max="20" value="' + c.qty + '" class="cart-qty" data-id="' + c.id + '">' +
            '<button type="button" class="cart-remove" data-id="' + c.id + '" aria-label="Remove">×</button>' +
          '</div>' +
        '</li>'
      );
    }).join('');

    list.querySelectorAll('.cart-qty').forEach(function (input) {
      input.addEventListener('change', function () {
        const id = parseInt(input.dataset.id, 10);
        setCartQty(id, Math.max(1, parseInt(input.value, 10) || 1));
      });
    });
    list.querySelectorAll('.cart-remove').forEach(function (btn) {
      btn.addEventListener('click', function () {
        removeFromCart(parseInt(btn.dataset.id, 10));
      });
    });
  }

  function openCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
    if (drawer) drawer.setAttribute('aria-hidden', 'false');
    if (overlay) overlay.setAttribute('aria-hidden', 'false');
  }

  function closeCart() {
    const drawer = document.getElementById('cartDrawer');
    const overlay = document.getElementById('cartOverlay');
    if (drawer) drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
    if (drawer) drawer.setAttribute('aria-hidden', 'true');
    if (overlay) overlay.setAttribute('aria-hidden', 'true');
  }

  function init() {
    renderMenu();
    loadCart();

    document.getElementById('cartToggle').addEventListener('click', openCart);
    document.getElementById('cartClose').addEventListener('click', closeCart);
    document.getElementById('cartOverlay').addEventListener('click', closeCart);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
