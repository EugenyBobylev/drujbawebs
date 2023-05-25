'use strict';

(function () {
    var fieldMail = document.querySelector('.order__mail');
    var fieldTel = document.querySelector('.order__tel');
    var checkedMail = document.getElementById('checkMail');
    var checkedSms = document.getElementById('checkSms');

    changeFields();

    function changeField(f1, f2) {
        f1.childNodes[0].value = '';
        f1.classList.add('order__invis');
        f2.classList.remove('order__invis');
    }

    function changeFields() {
        if (checkedMail.checked) {
            changeField(fieldTel, fieldMail);
        } else if (checkedSms.checked) {
            changeField(fieldMail, fieldTel);
        }
        window.validation.changeStateBtns(true);
    }

    if (fieldMail) {
        checkedMail.addEventListener('change', changeFields);
        checkedSms.addEventListener('change', changeFields);
    }

})();
