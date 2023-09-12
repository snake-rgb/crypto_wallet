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
    $('.register-button').click(function () {
        if ($('#form-register').valid()) {
            // ajax data
            let email = $('#email').val()
            let password = $('#password').val()
            let confirm_password = $('#confirm_password').val()
            let username = $('#username').val()
            // ajax url
            let base_url = 'http://' + window.location.host
            let api_endpoint = '/api/v1/register/'

            let data = JSON.stringify({
                'email': email,
                'password': password,
                'confirm_password': confirm_password,
                'username': username,
            })
            // register ajax
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
                    console.log(response)
                }
            })

        }
    })

})
$('#form-register').validate({
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
        confirm_password: {
            required: true,
            equalTo: '#password',
        },
        username: {
            required: true,
            minlength: 6,
            maxlength: 40,
        },
        groups: {
            password: "password"
        },
    },
    messages: {
        password: {
            password_validation: 'Пароль должен содержать хотя бы 1 большую и 1 маленькую латинскую букву'
        },
        confirm_password:
            {
                equalTo: 'Пароли должны совпадать'
            },
        username: {
            minlength: 'Имя пользователя должно состоять хотя бы из 6 символов',
            maxlength: 'Имя пользователя должно состоять не более чем из 40 символов',
        }
    },
    errorPlacement: function (error, element) {
        if (element.attr("name") === "password") {
            error.insertAfter(".password-input-group");
        } else if (element.attr('name') === 'confirm_password') {
            error.insertAfter('.confirm-password-input-group');

        } else {
            error.insertAfter(element);
        }
    }
})

export function verify_token() {
    // ajax url
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/token_verify/'
    $.ajax(
        {
            url: base_url + api_endpoint,
            method: 'get',
            dataType: "json",
            headers: {
                'Content-Type': 'application/json',
            },
            success: function (response) {
                if (response === true && window.location.href !== 'http://127.0.0.1:8000/profile/')
                    window.location = base_url + '/profile/'
            },
            statusCode: {
                403: function () {
                    if (window.location.href === 'http://127.0.0.1:8000/profile/')
                        window.location = base_url + '/login/'
                }
            },
        }
    )
}