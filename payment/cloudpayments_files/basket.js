'use strict';

(function () {
    var counter = document.querySelector('.basket-count'),
        emptyCart = document.querySelectorAll('.empty-cart'),
        notEmptyCart = document.querySelectorAll('.not-empty-cart');

    function changeCounter(value) {
        if (counter) {
            counter.textContent = value;
            if (value) {
                counter.classList.remove('basket-count--none');
                emptyCart.forEach(function (item) {
                    item.style.display = 'none';
                });
                notEmptyCart.forEach(function (item) {
                    item.style.display = 'block';
                });
            } else {
                counter.classList.add('basket-count--none');
                emptyCart.forEach(function (item) {
                    item.style.display = 'block';
                });
                notEmptyCart.forEach(function (item) {
                    item.style.display = 'none';
                });
            }
        }
    }

    window.basket = {
        add: function (product_id, callback, count) {
            var data = {
                action: 'addCart',
                product_id: product_id
            };
            if (typeof count !== 'undefined') {
                data['count'] = count;
            }
            $.ajax({
                url: '/order/',
                type: 'post',
                data: data,
            }).done(function (response) {
                changeCounter(response['total_count']);
                if (typeof callback == 'function') {
                    callback(response)
                }
            });
        },
        remove: function (product_id, callback, count) {
            var data = {
                action: 'removeCart',
                product_id: product_id
            };
            if (typeof count !== 'undefined') {
                data['count'] = count;
            }
            $.ajax({
                url: '/order/',
                type: 'post',
                data: data,
            }).done(function (response) {
                changeCounter(response['total_count']);
                if (typeof callback == 'function') {
                    callback(response)
                }
            });
        },
        change: function () {

        }
    }
})();
