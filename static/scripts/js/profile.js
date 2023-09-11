$(document).ready(function () {
    get_user()
})
$('.import-confirm-button').click(function () {
    let private_key = $('.import-private-key-input').val()
    let params = {
        'private_key': private_key
    }
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/wallet/import/?' + $.param(params)


    $.ajax({
        url: base_url + api_endpoint,
        method: 'post',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            console.log(response)
        },
        error: function (response) {
            console.log(response)
        }
    })
})
$('#create-wallet-button').click(function () {
    // TODO: исправить id asseta при production
    let params = {
        'asset_id': 2
    }
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/wallet/create/?' + $.param(params)


    $.ajax({
        url: base_url + api_endpoint,
        method: 'post',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            let toast = $('#create-wallet-success-toast')
            let toastAnimation = new bootstrap.Toast(toast);
            toastAnimation.show();
        },
        error: function (response) {
            let toast = $('#create-wallet-error-toast')
            let toastAnimation = new bootstrap.Toast(toast);
            toastAnimation.show();
        }
    })


})

function user_messages_count(user_id) {
    let params = {
        'user_id': parseInt(user_id)
    }
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/get-user-messages-count/?' + $.param(params)
    $.ajax({
        url: base_url + api_endpoint,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            $('.messages-count').text('Сообщений в чате: ' + response['messages_count'])
        },
        error: function (response) {
            console.log(response)
        }
    })

}

function get_user() {
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/profile/'

    $.ajax({
        url: base_url + api_endpoint,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            $('.user-name-field').text(response['username'])
            $('.profile-image').attr('src', response['profile_image'])
            $('#username').val(response['username'])
            $('#email').val(response['email'])
            user_messages_count(response['id'])
            user_wallets(response['id'])
        },
        error: function (response) {
            console.log(response)
        }
    })

}

function user_wallets(user_id) {
    let params = {
        'user_id': parseInt(user_id)
    }

    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/wallet/get-user-wallets/?' + $.param(params)

    $.ajax({
        url: base_url + api_endpoint,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            let wallets_count = response['wallets'].length
            $('.wallets-count').text('Кошельков: ' + wallets_count)
            for (let i = 0; i < wallets_count; i++) {
                let wallet = response['wallets'][i]
                let wallet_div = $('#wallet-template').clone(true, true)
                $(wallet_div).attr('id', '')
                $(wallet_div).find('.etherscan-link').text(wallet['address'])
                $(wallet_div).find('.asset-image').attr('src', wallet['asset_image'])
                $(wallet_div).find('.etherscan-link').attr('href', 'https://sepolia.etherscan.io/address/' + wallet['address'])
                $(wallet_div).show()
                $('.wallets-list').append($(wallet_div))
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function update_user() {

    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/profile/edit'

    let username = $('#username').val()
    let password = $('#new-password').val()
    let confirm_password = $('#confirm-password').val()

    let data = JSON.stringify({
        'username': username,
        'password': password,
        'confirm_password': confirm_password,
        'profile_image': '',
    })
    $.ajax({
        url: base_url + api_endpoint,
        method: 'put',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        data: data,
        success: function (response) {
            console.log(response)
        },
        error: function (response) {
            console.log(response)
        }
    })
}

$('.update-profile-button').click(update_user)