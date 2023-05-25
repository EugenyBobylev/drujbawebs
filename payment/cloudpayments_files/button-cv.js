'use strict';

(function () {
    window.button_cv = {
        init: function () {
            var buttons = document.querySelectorAll('.button-cv');
            var sumFields = document.getElementById('sumFields');
            var textBtn = document.querySelector('.card__sum-pay');

            if (buttons) {
                for (var i = 0; i < buttons.length; i++) {
                    buttons[i].addEventListener('click', changeValue);
                }
            }

            function changeValue(evt) {
                var target = evt.target,
                    productId = target.dataset['productId'],
                    goodsValue = document.getElementById('goodsValue-' + productId),
                    goodsCost = document.getElementById('goodsCost-' + productId);

                if (target.value == 1) {
                    window.basket.add(productId, function(response) {
                        goodsValue.value = response['item_count'];
                        goodsCost.textContent = response['item_cost'];
                        updateState(response['total_cost']);
                    }, 1);
                } else if (target.value == 0) {
                    window.basket.remove(productId, function(response) {
                        goodsValue.value = response['item_count'];
                        goodsCost.textContent = response['item_cost'];
                        updateState(response['total_cost']);
                    }, 1);
                }
            }

            function updateState(value) {
                sumFields.textContent = value + ' ';
                if (textBtn) {
                    textBtn.textContent = value;
                }
                window.order_cost = value;
            }
        }
    };

    window.button_cv.init();
})();
