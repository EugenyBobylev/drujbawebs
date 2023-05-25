'use strict';

(function() {
  var checkoutBtns = document.querySelectorAll('.addBtn');
  var popupDown = document.querySelector('.popup-down');
  var overlay = document.querySelector('.overlay');
  var closeBtn = popupDown.querySelector('.close-button');
  var popupDownFooterButton = popupDown.querySelector('.popup-down__footer-button');
  var headerBasketWidget = document.querySelector('.header__basket--widget');
  var widgetCart = document.getElementById('widget-cart');

  var ADD_COUNT = 1;
  var REMOVE_COUNT = 0;

  function changeContent (el, state1, state2, state3) {
    el.value = state1;
    el.classList[state1 === ADD_COUNT ? 'add' : 'remove'](state2);
    el.textContent = state3;
  }

  function basketWidgetClick (evt) {
    evt.preventDefault();
    overlay.classList.remove('overlay--invis');
    document.body.classList.add('modal-open');
    popupDown.classList.remove('popup-down--hidden');
    popupDown.classList.add('popup-down--vis');
    closeBtn.addEventListener('click', closePopup);
    popupDownFooterButton.addEventListener('click', closePopup);
    overlay.addEventListener('click', onPopupClick);
    document.addEventListener('keydown', escPushHandler);
  }

  headerBasketWidget.addEventListener('click', basketWidgetClick);

  function closePopup () {
    overlay.classList.add('overlay--invis');
    document.body.classList.remove('modal-open');
    popupDown.classList.add('popup-down--hidden');
    popupDown.classList.remove('popup-down--vis');
    closeBtn.removeEventListener('click', closePopup);
    popupDownFooterButton.removeEventListener('click', closePopup);
    overlay.removeEventListener('click', onPopupClick);
    document.removeEventListener('keydown', escPushHandler);
  }

  function onPopupClick (event) {
    if (event.target.classList.contains('overlay')) {
      closePopup();
    }
  }

  function escPushHandler (e) {
    if (e.keyCode === 27) {
      closePopup();
    }
  }

  function openPopup (value) {
    if (value == 1) {
      overlay.classList.remove('overlay--invis');
      document.body.classList.add('modal-open');
      popupDown.classList.remove('popup-down--hidden');
      popupDown.classList.add('popup-down--vis');
      closeBtn.addEventListener('click', closePopup);
      popupDownFooterButton.addEventListener('click', closePopup);
      overlay.addEventListener('click', onPopupClick);
      document.addEventListener('keydown', escPushHandler);
    }
  }

  function changeCount (evt) {
    var target = evt.target;

    if (target.value == 0) {
      window.basket.add(target.dataset['productId'], function (response) {
        widgetCart.innerHTML = response['cart_widget'];
        window.button_cv.init();
        changeContent(target, ADD_COUNT, 'button--basket', 'Удалить');
        openPopup(target.value);
      });
    } else {
      window.basket.remove(target.dataset['productId'], function (response) {
        widgetCart.innerHTML = response['cart_widget'];
        window.button_cv.init();
        changeContent(target, REMOVE_COUNT, 'button--basket', 'Купить');
      });
    }
  }

  for (var i = 0; i < checkoutBtns.length; i++) {
    checkoutBtns[i].addEventListener('click', changeCount);
  }

})();
