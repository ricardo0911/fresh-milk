/**
 * 主入口文件
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initSearch();
    initCategories();
    initHotProducts();
    initNewProducts();
    initScrollAnimations();
    utils.updateCartBadge();
});

// 初始化导航栏
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.querySelector('.nav-menu');

    // 滚动时改变导航栏样式
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    });

    // 移动端菜单
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }
}

// 初始化搜索
function initSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const searchModal = document.getElementById('searchModal');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');

    if (searchBtn && searchModal) {
        searchBtn.addEventListener('click', () => {
            searchModal.classList.add('active');
            searchInput.focus();
        });

        searchClose.addEventListener('click', () => {
            searchModal.classList.remove('active');
        });

        // ESC关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                searchModal.classList.remove('active');
            }
        });

        // 搜索
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && searchInput.value.trim()) {
                window.location.href = `products.html?search=${encodeURIComponent(searchInput.value.trim())}`;
            }
        });
    }
}

// 初始化分类
async function initCategories() {
    const categoryGrid = document.getElementById('categoryGrid');
    if (!categoryGrid) return;

    // 显示骨架屏
    const skeletons = utils.createSkeleton('category-card', 6);
    skeletons.forEach(s => categoryGrid.appendChild(s));

    // 模拟分类数据 (实际项目中从API获取)
    const categories = [
        { id: 1, name: '鲜牛奶', icon: '🥛' },
        { id: 2, name: '酸奶', icon: '🍶' },
        { id: 3, name: '奶酪', icon: '🧀' },
        { id: 4, name: '有机奶', icon: '🌿' },
        { id: 5, name: '儿童奶', icon: '👶' },
        { id: 6, name: '周期购', icon: '📅' },
    ];

    // 清除骨架屏并渲染分类
    setTimeout(() => {
        categoryGrid.innerHTML = '';
        categories.forEach((category, index) => {
            const card = createCategoryCard(category);
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-slide-up');
            categoryGrid.appendChild(card);
        });
    }, 500);
}

// 创建分类卡片
function createCategoryCard(category) {
    const card = document.createElement('a');
    card.href = `products.html?category=${category.id}`;
    card.className = 'category-card';
    card.innerHTML = `
        <div class="category-icon">${category.icon}</div>
        <span class="category-name">${category.name}</span>
    `;
    return card;
}

// 初始化热门产品
async function initHotProducts() {
    const productGrid = document.getElementById('hotProductGrid');
    if (!productGrid) return;

    // 显示骨架屏
    const skeletons = utils.createSkeleton('product-card', 4);
    skeletons.forEach(s => productGrid.appendChild(s));

    // 模拟产品数据
    const products = [
        {
            id: 1,
            name: '每日鲜牛奶',
            specification: '250ml × 10瓶',
            price: 39.90,
            original_price: 49.90,
            cover_image: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&q=80',
            is_hot: true,
            is_new: false
        },
        {
            id: 2,
            name: '有机纯牛奶',
            specification: '1L × 6盒',
            price: 89.00,
            original_price: 108.00,
            cover_image: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80',
            is_hot: true,
            is_new: true
        },
        {
            id: 3,
            name: '低脂鲜牛奶',
            specification: '500ml × 8瓶',
            price: 56.80,
            original_price: 68.00,
            cover_image: 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&q=80',
            is_hot: true,
            is_new: false
        },
        {
            id: 4,
            name: '儿童成长奶',
            specification: '200ml × 12瓶',
            price: 68.00,
            original_price: 79.00,
            cover_image: 'https://images.unsplash.com/photo-1572443490709-e57652c96a1b?w=400&q=80',
            is_hot: true,
            is_subscription: true
        },
    ];

    // 渲染产品
    setTimeout(() => {
        productGrid.innerHTML = '';
        products.forEach((product, index) => {
            const card = createProductCard(product);
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-slide-up');
            productGrid.appendChild(card);
        });
    }, 800);
}

// 初始化新品
async function initNewProducts() {
    const productScroll = document.getElementById('newProductScroll');
    if (!productScroll) return;

    // 模拟新品数据
    const products = [
        {
            id: 5,
            name: 'A2蛋白鲜牛奶',
            specification: '950ml × 2瓶',
            price: 45.00,
            original_price: 52.00,
            cover_image: 'https://images.unsplash.com/photo-1600788907416-456578634209?w=400&q=80',
            is_new: true
        },
        {
            id: 6,
            name: '草莓味酸奶',
            specification: '100g × 12杯',
            price: 38.00,
            original_price: 45.00,
            cover_image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&q=80',
            is_new: true
        },
        {
            id: 7,
            name: '原味希腊酸奶',
            specification: '400g × 4盒',
            price: 59.00,
            original_price: 72.00,
            cover_image: 'https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&q=80',
            is_new: true
        },
        {
            id: 8,
            name: '高钙牛奶',
            specification: '250ml × 16盒',
            price: 65.00,
            original_price: 78.00,
            cover_image: 'https://images.unsplash.com/photo-1634141510639-d691d8092a14?w=400&q=80',
            is_new: true
        },
    ];

    // 渲染产品
    setTimeout(() => {
        productScroll.innerHTML = '';
        products.forEach((product) => {
            const card = createProductCard(product);
            productScroll.appendChild(card);
        });
    }, 1000);
}

// 创建产品卡片
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    // 标签
    let tagsHtml = '';
    if (product.is_hot) {
        tagsHtml += '<span class="product-tag hot">热门</span>';
    }
    if (product.is_new) {
        tagsHtml += '<span class="product-tag new">新品</span>';
    }
    if (product.is_subscription) {
        tagsHtml += '<span class="product-tag subscription">周期购</span>';
    }

    card.innerHTML = `
        <div class="product-image">
            <img src="${product.cover_image}" alt="${product.name}">
            <div class="product-tags">${tagsHtml}</div>
        </div>
        <div class="product-info">
            <h3 class="product-name">${product.name}</h3>
            <p class="product-spec">${product.specification || ''}</p>
            <div class="product-footer">
                <div class="product-price">
                    <span class="price-current">${utils.formatPrice(product.price)}</span>
                    ${product.original_price ? `<span class="price-original">¥${utils.formatPrice(product.original_price)}</span>` : ''}
                </div>
                <button class="product-cart-btn" onclick="addToCart(${product.id}, event)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 5v14M5 12h14"/>
                    </svg>
                </button>
            </div>
        </div>
    `;

    // 点击跳转详情页
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.product-cart-btn')) {
            window.location.href = `product-detail.html?id=${product.id}`;
        }
    });

    card.style.cursor = 'pointer';

    return card;
}

// 添加到购物车
function addToCart(productId, event) {
    event.stopPropagation();

    // 模拟产品数据(实际应从状态或API获取)
    const product = {
        id: productId,
        name: '产品' + productId,
        price: 39.90
    };

    utils.localCart.addItem(product, 1);
    utils.showToast('已加入购物车', 'success');

    // 按钮动画
    const btn = event.target.closest('.product-cart-btn');
    btn.style.transform = 'scale(1.2)';
    setTimeout(() => {
        btn.style.transform = 'scale(1)';
    }, 200);
}

// 滚动动画
function initScrollAnimations() {
    const revealElements = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        revealElements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (elementTop < windowHeight - 100) {
                el.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', utils.throttle(revealOnScroll, 100));
    revealOnScroll(); // 初始检查
}

// 全局暴露
window.addToCart = addToCart;
