/* Fashion Ecommerce Wishlist JavaScript */

odoo.define('fashion_ecommerce.wishlist', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.FashionWishlist = publicWidget.Widget.extend({
        selector: '.fashion-wishlist-toggle',
        events: {
            'click': '_onWishlistToggle',
        },

        _onWishlistToggle: function (ev) {
            ev.preventDefault();
            var $btn = $(ev.currentTarget);
            var productId = $btn.data('product-id');
            
            if (!productId) {
                return;
            }

            // Check if user is logged in
            if (!$('body').hasClass('o_portal')) {
                window.location.href = '/web/login?redirect=' + encodeURIComponent(window.location.pathname);
                return;
            }

            $btn.prop('disabled', true);
            
            ajax.jsonRpc('/shop/wishlist/toggle', 'call', {
                'product_id': productId
            }).then(function (result) {
                if (result.error) {
                    console.error('Wishlist error:', result.error);
                    return;
                }
                
                // Update button state
                if (result.in_wishlist) {
                    $btn.addClass('in-wishlist')
                        .find('i').removeClass('fa-heart-o').addClass('fa-heart');
                    $btn.find('.wishlist-text').text('Remove from Wishlist');
                } else {
                    $btn.removeClass('in-wishlist')
                        .find('i').removeClass('fa-heart').addClass('fa-heart-o');
                    $btn.find('.wishlist-text').text('Add to Wishlist');
                }
                
                // Update wishlist counter if exists
                var $counter = $('.wishlist-counter');
                if ($counter.length) {
                    var currentCount = parseInt($counter.text()) || 0;
                    var newCount = result.in_wishlist ? currentCount + 1 : currentCount - 1;
                    $counter.text(Math.max(0, newCount));
                }
                
            }).catch(function (error) {
                console.error('Wishlist toggle failed:', error);
            }).finally(function () {
                $btn.prop('disabled', false);
            });
        }
    });

    return publicWidget.registry.FashionWishlist;
});