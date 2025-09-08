/* Fashion Ecommerce Search JavaScript */

odoo.define('fashion_ecommerce.search', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.FashionSearch = publicWidget.Widget.extend({
        selector: '.fashion-search-form',
        events: {
            'input .search-input': '_onSearchInput',
            'click .search-suggestion': '_onSuggestionClick',
            'submit': '_onSearchSubmit',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.searchTimeout = null;
        },

        _onSearchInput: function (ev) {
            var self = this;
            var $input = $(ev.currentTarget);
            var term = $input.val().trim();
            
            clearTimeout(this.searchTimeout);
            
            if (term.length < 2) {
                this._hideSuggestions();
                return;
            }
            
            this.searchTimeout = setTimeout(function () {
                self._fetchSuggestions(term);
            }, 300);
        },

        _fetchSuggestions: function (term) {
            var self = this;
            
            ajax.jsonRpc('/shop/autocomplete', 'call', {
                'term': term
            }).then(function (suggestions) {
                self._showSuggestions(suggestions);
            }).catch(function (error) {
                console.error('Autocomplete error:', error);
                self._hideSuggestions();
            });
        },

        _showSuggestions: function (suggestions) {
            var $container = this.$('.search-suggestions');
            
            if (!$container.length) {
                $container = $('<div class="search-suggestions"></div>');
                this.$('.search-input').after($container);
            }
            
            $container.empty();
            
            if (suggestions.length === 0) {
                $container.hide();
                return;
            }
            
            suggestions.forEach(function (suggestion) {
                var $item = $('<div class="search-suggestion" data-product-id="' + suggestion.id + '">' +
                    '<img src="' + suggestion.image + '" alt="' + suggestion.name + '" class="suggestion-image">' +
                    '<div class="suggestion-content">' +
                        '<div class="suggestion-name">' + suggestion.name + '</div>' +
                        '<div class="suggestion-brand">' + suggestion.brand + '</div>' +
                        '<div class="suggestion-price">$' + suggestion.price.toFixed(2) + '</div>' +
                    '</div>' +
                '</div>');
                
                $container.append($item);
            });
            
            $container.show();
        },

        _hideSuggestions: function () {
            this.$('.search-suggestions').hide();
        },

        _onSuggestionClick: function (ev) {
            var $suggestion = $(ev.currentTarget);
            var productId = $suggestion.data('product-id');
            
            if (productId) {
                window.location.href = '/shop/product/' + productId;
            }
        },

        _onSearchSubmit: function (ev) {
            var $form = $(ev.currentTarget);
            var searchTerm = $form.find('.search-input').val().trim();
            
            if (!searchTerm) {
                ev.preventDefault();
                return;
            }
            
            this._hideSuggestions();
        }
    });

    // Price range slider
    publicWidget.registry.PriceRangeSlider = publicWidget.Widget.extend({
        selector: '.price-range-slider',
        
        start: function () {
            var self = this;
            var $slider = this.$el;
            var minPrice = parseFloat($slider.data('min-price')) || 0;
            var maxPrice = parseFloat($slider.data('max-price')) || 1000;
            var currentMin = parseFloat($slider.data('current-min')) || minPrice;
            var currentMax = parseFloat($slider.data('current-max')) || maxPrice;
            
            // Initialize range slider (requires external library like noUiSlider)
            if (typeof noUiSlider !== 'undefined') {
                noUiSlider.create($slider[0], {
                    start: [currentMin, currentMax],
                    connect: true,
                    range: {
                        'min': minPrice,
                        'max': maxPrice
                    },
                    format: {
                        to: function (value) {
                            return Math.round(value);
                        },
                        from: function (value) {
                            return Number(value);
                        }
                    }
                });
                
                $slider[0].noUiSlider.on('update', function (values) {
                    self.$('.min-price-display').text('$' + values[0]);
                    self.$('.max-price-display').text('$' + values[1]);
                    self.$('input[name="min_price"]').val(values[0]);
                    self.$('input[name="max_price"]').val(values[1]);
                });
            }
        }
    });

    return {
        FashionSearch: publicWidget.registry.FashionSearch,
        PriceRangeSlider: publicWidget.registry.PriceRangeSlider
    };
});