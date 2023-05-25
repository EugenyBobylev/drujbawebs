'use strict';

(function () {
    var mail = document.getElementById('email');
    var tel = document.getElementById('tel');
    var closedBtns = document.querySelectorAll('.button--order');
    var popupBtn = document.getElementById('pay');
    var cardSection = document.querySelector('.card');

    var mailOption = {
        mask: /^\S*@?\S*$/
    };

    var telOption = {
        mask: '+{7} 000 000-00-00'
    };


/*     var telOption = {
		mask: [{
				mask: '+d 000 000-00-00',
				definitions: {
					'd': /7/
				}
			}, {
				mask: '+7 y00 000-00-00',
				definitions: {
					'y': /9/
				}
            },                     
        ]        
    }; */


    //console.log (telOption);
    var mailMask = new IMask(mail, mailOption);
    var telMask = new IMask(tel, telOption);

    function changeStateBtns(flag) {
        for (var i = 0; i < closedBtns.length; i++) {
            closedBtns[i].disabled = flag;
        }
        if (popupBtn) popupBtn.disabled = flag;
    }

    function backToBottom() {
        $('html,body').animate({scrollTop: $('.button--order').offset().top},
            'slow');
    }

    function viewCard(evt) {
        if (!evt.target.disabled) {
            cardSection.classList['remove']('card--invis');
        }
        backToBottom();
    }

    function disabledPopupBtn(check) {
        if (popupBtn && check) {
            popupBtn.disabled = true;
        } else if (popupBtn) {
            popupBtn.disabled = false;
        }
    }

    function unblockPopupBtn(e) {
        var target = e.target;

        if (target.validity.valid) {
            disabledPopupBtn(false);
        } else {
            disabledPopupBtn(true);
        }
    }

    function unblockBtn(e) {
        var target = e.target;

        if (target.validity.valid) {
            changeStateBtns(false);
            closedBtns[0].addEventListener('click', viewCard);
        } else {
            changeStateBtns(true);
            closedBtns[0].removeEventListener('click', viewCard);
        }
    }

    if (closedBtns[0]) {
        mail.addEventListener('input', unblockBtn);
        tel.addEventListener('input', unblockBtn);
    } else if (popupBtn) {
        mail.addEventListener('input', unblockPopupBtn);
        tel.addEventListener('input', unblockPopupBtn);
    }

    window.validation = {
        changeStateBtns: changeStateBtns
    }
})();
