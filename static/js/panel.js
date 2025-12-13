// ===== PRODUCT DETAILS PANEL =====

document.addEventListener('DOMContentLoaded', () => {
    // Initialize panel elements
    const productPanel = document.getElementById('productPanel');
    const panelContent = document.getElementById('panelContent');
    const closeBtn = document.getElementById('closePanel');
    const chatSection = document.querySelector('.chat-section');

    // Check if elements exist
    if (!productPanel || !panelContent || !closeBtn) {
        console.warn('Product panel elements not found');
        return;
    }

    // Premium product data
    const premiumProducts = {
        'iPhone 15 Pro Max': {
            name: 'iPhone 15 Pro Max',
            tagline: 'Tương lai trong tầm tay',
            price: '32.990.000₫',
            rating: '4.9',
            reviews: '2.8K',
            image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
            badges: [
                { type: 'warranty', text: 'Bảo hành 24 tháng', icon: 'fa-shield-alt' },
                { type: 'shipping', text: 'Giao hàng miễn phí', icon: 'fa-shipping-fast' },
                { type: 'discount', text: 'Giảm thêm 5%', icon: 'fa-tag' }
            ],
            highlights: [
                'Thiết kế Titan cao cấp',
                'Camera 48MP ProRAW',
                'Chip A17 Pro mạnh nhất',
                'Màn hình Always-On',
                'Chống nước IP68',
                'Sạc không dây MagSafe'
            ],
            specs: [
                { label: 'Chip xử lý', value: 'A17 Pro (3nm)', desc: '6 nhân CPU, 6 nhân GPU, 16 nhân Neural Engine' },
                { label: 'Bộ nhớ RAM', value: '8GB LPDDR5', desc: 'Tốc độ cao, tiết kiệm điện' },
                { label: 'Bộ nhớ trong', value: '256GB/512GB/1TB', desc: 'NVMe SSD, tốc độ đọc/ghi cực nhanh' },
                { label: 'Camera chính', value: '48MP + 12MP + 12MP', desc: 'Sensor lớn, khẩu độ f/1.78, ống kính Tele' },
                { label: 'Màn hình', value: '6.7" Super Retina XDR', desc: 'OLED, 120Hz ProMotion, 2000 nits' },
                { label: 'Pin & Sạc', value: '4422mAh, 20W có dây, 15W không dây', desc: 'Sử dụng cả ngày, sạc nhanh' },
                { label: 'Kết nối', value: 'USB-C 3.0, 5G, WiFi 6E', desc: 'Tốc độ truyền dữ liệu 10Gbps' },
                { label: 'Bảo mật', value: 'Face ID, iOS 17 Security', desc: 'An toàn tuyệt đối' }
            ],
            features: [
                { icon: 'fa-microchip', text: 'Chip A17 Pro 3nm' },
                { icon: 'fa-camera', text: 'Camera 48MP Pro' },
                { icon: 'fa-tint', text: 'Chống nước IP68' },
                { icon: 'fa-bolt', text: 'Sạc không dây' },
                { icon: 'fa-gamepad', text: 'Gaming AAA' },
                { icon: 'fa-video', text: 'Quay video 4K' },
                { icon: 'fa-shield-alt', text: 'Bảo mật cao' },
                { icon: 'fa-sync', text: '120Hz ProMotion' }
            ],
            delivery: 'Giao trong 2 giờ',
            support: 'Hỗ trợ 24/7'
        },
        'Samsung Galaxy S24 Ultra': {
            name: 'Samsung Galaxy S24 Ultra',
            tagline: 'Sáng tạo không giới hạn',
            price: '28.990.000₫',
            rating: '4.8',
            reviews: '1.9K',
            image: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
            badges: [
                { type: 'warranty', text: 'Bảo hành 12 tháng', icon: 'fa-shield-alt' },
                { type: 'shipping', text: 'Miễn phí vận chuyển', icon: 'fa-shipping-fast' },
                { type: 'discount', text: 'Tặng phụ kiện', icon: 'fa-gift' }
            ],
            highlights: [
                'Camera 200MP siêu nét',
                'Bút S-Pen tích hợp',
                'Màn hình Dynamic AMOLED 2X',
                'Snapdragon 8 Gen 3',
                'Pin 5000mAh, sạc 45W',
                'Thiết kế Armor Aluminum'
            ],
            specs: [
                { label: 'Chip xử lý', value: 'Snapdragon 8 Gen 3', desc: '4nm, Adreno 750 GPU' },
                { label: 'Bộ nhớ RAM', value: '12GB LPDDR5X', desc: 'Tốc độ cao, đa nhiệm mượt' },
                { label: 'Bộ nhớ trong', value: '256GB/512GB/1TB UFS 4.0', desc: 'Tốc độ đọc/ghi nhanh gấp đôi' },
                { label: 'Camera chính', value: '200MP + 50MP + 12MP + 10MP', desc: 'Zoom quang học 10x, ống kính chống rung' },
                { label: 'Màn hình', value: '6.8" Dynamic AMOLED 2X', desc: 'QHD+, 120Hz, độ sáng 2600 nits' },
                { label: 'Pin & Sạc', value: '5000mAh, sạc 45W có dây, 15W không dây', desc: 'Sạc đầy 65% trong 30 phút' },
                { label: 'Đặc biệt', value: 'Bút S-Pen tích hợp', desc: 'Độ trễ thấp 2.8ms' },
                { label: 'Kết nối', value: '5G, WiFi 7, Ultra Wideband', desc: 'Tốc độ tải xuống 10Gbps' }
            ],
            features: [
                { icon: 'fa-pen', text: 'Bút S-Pen' },
                { icon: 'fa-camera', text: 'Camera 200MP' },
                { icon: 'fa-sync', text: 'Màn hình 120Hz' },
                { icon: 'fa-bolt', text: 'Sạc nhanh 45W' },
                { icon: 'fa-satellite', text: 'GPS 2 tần số' },
                { icon: 'fa-shield-alt', text: 'Bảo mật Knox' },
                { icon: 'fa-robot', text: 'AI Features' },
                { icon: 'fa-tint', text: 'IP68' }
            ],
            delivery: 'Giao trong 24h',
            support: 'Hỗ trợ tại nhà'
        },
        'Xiaomi Poco F5': {
            name: 'Xiaomi Poco F5',
            tagline: 'Flagship Killer giá tốt',
            price: '8.490.000₫',
            rating: '4.7',
            reviews: '3.5K',
            image: 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
            badges: [
                { type: 'warranty', text: 'Bảo hành 12 tháng', icon: 'fa-shield-alt' },
                { type: 'shipping', text: 'Giao hàng nhanh', icon: 'fa-shipping-fast' },
                { type: 'discount', text: 'Trả góp 0%', icon: 'fa-percentage' }
            ],
            highlights: [
                'Snapdragon 7+ Gen 2',
                'Màn hình AMOLED 120Hz',
                'Sạc siêu nhanh 67W',
                'Thiết kế mỏng nhẹ',
                'Camera 64MP OIS',
                'Loa stereo Dolby Atmos'
            ],
            specs: [
                { label: 'Chip xử lý', value: 'Snapdragon 7+ Gen 2', desc: '4nm, hiệu năng tương đương flagship' },
                { label: 'Bộ nhớ RAM', value: '8GB/12GB LPDDR5', desc: 'Tốc độ 6400Mbps' },
                { label: 'Bộ nhớ trong', value: '256GB UFS 3.1', desc: 'Tốc độ đọc 2100MB/s' },
                { label: 'Camera chính', value: '64MP + 8MP + 2MP', desc: 'Chống rung quang học OIS' },
                { label: 'Màn hình', value: '6.67" AMOLED', desc: 'Full HD+, 120Hz, 1920Hz PWM' },
                { label: 'Pin & Sạc', value: '5000mAh, sạc 67W', desc: 'Sạc đầy 100% trong 42 phút' },
                { label: 'Âm thanh', value: 'Loa stereo Dolby Atmos', desc: 'Hi-Fi Audio, Hi-Res认证' },
                { label: 'Thiết kế', value: '181g, dày 7.9mm', desc: 'Khung nhôm, mặt kính Corning' }
            ],
            features: [
                { icon: 'fa-bolt', text: 'Sạc 67W' },
                { icon: 'fa-sync', text: '120Hz AMOLED' },
                { icon: 'fa-volume-up', text: 'Dolby Atmos' },
                { icon: 'fa-gamepad', text: 'Gaming Mode' },
                { icon: 'fa-fingerprint', text: 'Mở khoá vân tay' },
                { icon: 'fa-infinity', text: 'Pin 5000mAh' },
                { icon: 'fa-tint', text: 'IP53' },
                { icon: 'fa-gem', text: 'Giá tốt' }
            ],
            delivery: 'Giao trong 48h',
            support: 'Hỗ trợ online 24/7'
        }
    };

    // Utility function to escape HTML
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Generate star rating HTML
    function generateStarRating(rating) {
        const numRating = parseFloat(rating);
        const fullStars = Math.floor(numRating);
        const hasHalfStar = numRating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let stars = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    }

    // Show product details panel
    window.showProductDetails = function(productName) {
        const product = premiumProducts[productName] || getDefaultProduct(productName);
        
        // Generate HTML for product details
        const html = `
            <div class="product-details-card">
                <!-- Product Header -->
                <div class="product-details-header">
                    <div class="product-details-name">${escapeHtml(product.name)}</div>
                    <div class="product-details-price">${escapeHtml(product.price)}</div>
                </div>
                
                <!-- Product Image -->
                <div class="product-image-container">
                    <img src="${product.image}" alt="${escapeHtml(product.name)}" class="product-detail-image">
                    <div class="image-overlay"></div>
                </div>
                
                <!-- Tagline -->
                ${product.tagline ? `
                <div class="product-tagline">
                    <i class="fas fa-quote-left"></i>
                    ${escapeHtml(product.tagline)}
                </div>
                ` : ''}
                
                <!-- Rating -->
                <div class="product-rating">
                    <div class="rating-stars">
                        ${generateStarRating(product.rating)}
                    </div>
                    <span class="rating-value">${product.rating}/5</span>
                    <span class="rating-count">• ${product.reviews} đánh giá</span>
                    <span style="margin-left: auto; color: #10b981; font-weight: 600;">
                        <i class="fas fa-check-circle" style="margin-right: 6px;"></i>
                        Còn hàng
                    </span>
                </div>
                
                <!-- Badges -->
                <div class="product-details-badges">
                    ${product.badges.map(badge => `
                        <span class="badge badge-${badge.type}">
                            <i class="fas ${badge.icon}"></i>
                            ${escapeHtml(badge.text)}
                        </span>
                    `).join('')}
                </div>
                
                <!-- Highlights -->
                <div class="product-highlights">
                    <div class="highlights-title">
                        <i class="fas fa-fire"></i>
                        Điểm nổi bật
                    </div>
                    <div class="highlights-grid">
                        ${product.highlights.map(highlight => `
                            <div class="highlight-item">
                                ${escapeHtml(highlight)}
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Specifications -->
                <h3 class="section-title">
                    <i class="fas fa-microchip"></i>
                    Thông số kỹ thuật
                </h3>
                
                <div class="specs-grid">
                    ${product.specs.map(spec => `
                        <div class="spec-item">
                            <div class="spec-label">
                                <i class="fas fa-circle"></i>
                                ${escapeHtml(spec.label)}
                            </div>
                            <div class="spec-value">${escapeHtml(spec.value)}</div>
                            <span class="spec-desc">${escapeHtml(spec.desc)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Features -->
                <h3 class="section-title">
                    <i class="fas fa-star"></i>
                    Tính năng nổi bật
                </h3>
                
                <div class="features-grid">
                    ${product.features.map(feature => `
                        <div class="feature-item">
                            <div class="feature-icon">
                                <i class="fas ${feature.icon}"></i>
                            </div>
                            <span class="feature-text">${escapeHtml(feature.text)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Delivery Info -->
                <div class="delivery-info">
                    <div class="delivery-item">
                        <div class="delivery-icon">
                            <i class="fas fa-shipping-fast"></i>
                        </div>
                        <div class="delivery-text">
                            <div class="delivery-title">${product.delivery}</div>
                            <div class="delivery-subtitle">Miễn phí vận chuyển</div>
                        </div>
                    </div>
                    <div class="delivery-item">
                        <div class="delivery-icon">
                            <i class="fas fa-headset"></i>
                        </div>
                        <div class="delivery-text">
                            <div class="delivery-title">${product.support}</div>
                            <div class="delivery-subtitle">Tư vấn miễn phí</div>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="details-actions">
                    <button class="details-btn btn-details-primary" onclick="window.handleFindStore()">
                        <i class="fas fa-map-marker-alt"></i> Tìm cửa hàng gần nhất
                    </button>
                    <button class="details-btn btn-details-secondary" 
                        data-name="${escapeHtml(product.name)}" 
                        onclick="window.handleConsulting(this.getAttribute('data-name'), true)">
                        <i class="fas fa-comments"></i> Tư vấn & So sánh
                    </button>
                </div>
                
                <!-- Support Note -->
                <div class="support-note">
                    <div class="note-icon">
                        <i class="fas fa-phone-alt"></i>
                    </div>
                    <p>Cần hỗ trợ? Gọi ngay <strong>1900 1234</strong></p>
                    <small>Đội ngũ chuyên gia sẽ tư vấn và hỗ trợ bạn 24/7</small>
                </div>
            </div>
        `;
        
        // Set panel content
        panelContent.innerHTML = html;
        
        
        // Show panel
        productPanel.classList.add('active');
        if (chatSection) {
            chatSection.classList.add('with-panel');
        }
    };

    // Default product template
    function getDefaultProduct(productName) {
        return {
            name: productName,
            tagline: 'Sản phẩm chất lượng cao',
            price: 'Liên hệ để biết giá',
            rating: '4.5',
            reviews: '0',
            image: 'https://images.unsplash.com/photo-1546054453-4f9b6c5e4b1a?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
            badges: [
                { type: 'warranty', text: 'Bảo hành 12 tháng', icon: 'fa-shield-alt' },
                { type: 'shipping', text: 'Giao hàng toàn quốc', icon: 'fa-shipping-fast' }
            ],
            highlights: [
                'Chất lượng đảm bảo',
                'Giá cả cạnh tranh',
                'Bảo hành chính hãng',
                'Hỗ trợ tận tình'
            ],
            specs: [
                { label: 'Thông tin', value: 'Đang cập nhật', desc: 'Vui lòng liên hệ để biết thông tin chi tiết' }
            ],
            features: [
                { icon: 'fa-shield-alt', text: 'Bảo hành chính hãng' },
                { icon: 'fa-shipping-fast', text: 'Giao hàng miễn phí' },
                { icon: 'fa-headset', text: 'Hỗ trợ 24/7' },
                { icon: 'fa-exchange-alt', text: 'Đổi trả dễ dàng' }
            ],
            delivery: 'Giao hàng nhanh',
            support: 'Tư vấn miễn phí'
        };
    }

    // Close panel
    function closePanel() {
        productPanel.classList.remove('active');
        if (chatSection) {
            chatSection.classList.remove('with-panel');
        }
        
        // Clear content with fade out animation
        panelContent.style.opacity = '0';
        panelContent.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            panelContent.innerHTML = '';
            panelContent.style.opacity = '1';
            panelContent.style.transform = 'translateY(0)';
        }, 300);
    }

    // Event listeners
    closeBtn.addEventListener('click', closePanel);
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && productPanel.classList.contains('active')) {
            closePanel();
        }
    });
});