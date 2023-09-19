import {verify_token} from '/static/scripts/js/utils.js';
// email validation pattern
$.validator.methods.email = function (value, element) {
    return this.optional(element) || new RegExp("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\\.[A-Z|a-z]{2,})+").test(value);
}
$.validator.addMethod("password_validation", function (value, element, param) {
    if (this.optional(element)) {
        return true;
    }
    param = new RegExp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$");
    return param.test(value);
});
$(document).ready(function () {

    verify_token()

})
$('#form-authentication').validate({
    debug: true,
    rules: {
        email: {
            required: true,
            email: true,
        },
        password: {
            required: true,
            minlength: 8,
            maxlength: 20,
            password_validation: "(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,20}$/",
        },
        groups: {
            password: "password"
        },
    },
    messages: {
        password: {
            password_validation: 'Пароль должен содержать хотя бы 1 большую и 1 маленькую латинскую букву'
        }
    },
    errorPlacement: function (error, element) {
        if (element.attr("name") === "password") {
            error.insertAfter(".password-input-group");
        } else {
            error.insertAfter(element);
        }
    }
})
$('.login-button').click(function () {
    if ($('#form-authentication').valid()) {
        // ajax data
        let email = $('#email').val()
        let password = $('#password').val()
        let remember_me = $('#remember_me').prop('checked')
        // ajax url
        let base_url = 'http://' + window.location.host
        let api_endpoint = '/api/v1/login/'

        let data = JSON.stringify({
            'email': email,
            'password': password,
            'remember_me': remember_me
        })
        // login ajax
        $.ajax({
            url: base_url + api_endpoint,
            method: 'post',
            dataType: "json",
            headers: {
                'Content-Type': 'application/json',
            },
            data: data,
            success: function (response) {
                window.location.href = base_url + '/profile/'
            },
            error: function (response) {
                $('.invalid-login').remove()
                let error = `<span class="error invalid-login">Неверный логин или пароль</span>`
                $(error).insertAfter(".password-input-group");
            },
        })

    }
})

