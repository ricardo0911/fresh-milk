-- 插入可兑换优惠券数据
INSERT INTO coupons (code, name, type, discount_percent, discount_amount, min_amount, max_discount, total_count, used_count, per_user_limit, start_time, end_time, is_all_products, status, description, points_required, is_exchangeable, exchange_limit, exchanged_count, created_at, updated_at)
SELECT 'EXCHANGE5', '5元优惠券', 'amount', 0, 5.00, 30.00, 0, 0, 0, 10, NOW(), DATE_ADD(NOW(), INTERVAL 365 DAY), 1, 'active', '满30元可用', 50, 1, 0, 0, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM coupons WHERE code = 'EXCHANGE5');

INSERT INTO coupons (code, name, type, discount_percent, discount_amount, min_amount, max_discount, total_count, used_count, per_user_limit, start_time, end_time, is_all_products, status, description, points_required, is_exchangeable, exchange_limit, exchanged_count, created_at, updated_at)
SELECT 'EXCHANGE10', '10元优惠券', 'amount', 0, 10.00, 50.00, 0, 0, 0, 10, NOW(), DATE_ADD(NOW(), INTERVAL 365 DAY), 1, 'active', '满50元可用', 100, 1, 0, 0, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM coupons WHERE code = 'EXCHANGE10');

INSERT INTO coupons (code, name, type, discount_percent, discount_amount, min_amount, max_discount, total_count, used_count, per_user_limit, start_time, end_time, is_all_products, status, description, points_required, is_exchangeable, exchange_limit, exchanged_count, created_at, updated_at)
SELECT 'EXCHANGE20', '20元优惠券', 'amount', 0, 20.00, 100.00, 0, 0, 0, 10, NOW(), DATE_ADD(NOW(), INTERVAL 365 DAY), 1, 'active', '满100元可用', 200, 1, 0, 0, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM coupons WHERE code = 'EXCHANGE20');

SELECT id, code, name, points_required, is_exchangeable FROM coupons WHERE is_exchangeable = 1;
