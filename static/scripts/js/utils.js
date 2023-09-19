export function logout() {
    $('.logout-button').click(function () {
        $.ajax({
            url: 'http://' + window.location.host + '/api/v1/logout/',
            success: function () {
                window.location = 'http://' + window.location.host + '/login/'
            }
        })
    })
}

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
                if (response === true)
                    if (window.location.href === 'http://127.0.0.1:8000/login/' || window.location.href === 'http://127.0.0.1:8000/register/') {
                        window.location = base_url + '/profile/'
                    }
            },
            statusCode: {
                403: function () {
                    if (window.location.href === 'http://127.0.0.1:8000/profile/' || window.location.href === 'http://127.0.0.1:8000/chat/' || window.location.href === 'http://127.0.0.1:8000/wallets/')
                        window.location = base_url + '/login/'
                }
            },
        }
    )
}