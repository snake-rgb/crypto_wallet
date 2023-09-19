import {verify_token} from "/static/scripts/js/utils.js";
import {logout} from "/static/scripts/js/utils.js";

let profile_image
let wallets_count
$(document).ready(function () {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": false,
        "progressBar": false,
        "positionClass": "toast-top-center mt-5",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "1000",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }
    get_user()
    verify_token()
    logout()

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
            $('.btn-close').click()
            $('.import-private-key-input').val('')
            wallets_count += 1
            $('.wallets-count').text('Кошельков: ' + wallets_count)
            toastr.success('Кошелек успешно импортирован')
            let wallet = response['wallet']
            let wallet_div = $('#wallet-template').clone(true, true)
            $(wallet_div).attr('id', '')
            $(wallet_div).find('.etherscan-link').text(wallet['address'])
            $(wallet_div).find('.asset-image').attr('src', wallet['asset_image'])
            $(wallet_div).find('.etherscan-link').attr('href', 'https://sepolia.etherscan.io/address/' + wallet['address'])
            $(wallet_div).show()
            $('.wallets-list').append($(wallet_div))
        },
        error: function (response) {
            console.log(response)
            toastr.error('При импорте кошелька произошла ошибка попробуйте еще раз')
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
            console.log(response)
            toastr.success('Кошелек успешно создан')
            wallets_count += 1
            $('.wallets-count').text('Кошельков: ' + wallets_count)
            let wallet = response['wallet']
            let wallet_div = $('#wallet-template').clone(true, true)
            $(wallet_div).attr('id', '')
            $(wallet_div).find('.etherscan-link').text(wallet['address'])
            $(wallet_div).find('.asset-image').attr('src', wallet['asset_image'])
            $(wallet_div).find('.etherscan-link').attr('href', 'https://sepolia.etherscan.io/address/' + wallet['address'])
            $(wallet_div).show()
            $('.wallets-list').append($(wallet_div))
        },
        error: function (response) {
            toastr.error('При создании кошелька произошла ошибка попробуйте еще раз')
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
            profile_image = response['profile_image']
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
            wallets_count = response['wallets'].length
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
    // USER PROFILE DATA
    let username = $('#username').val()
    let password = $('#new-password').val()
    let confirm_password = $('#confirm-password').val()
    let profile_image = $('.upload-image-input').attr('src')
    if (profile_image === undefined)
        profile_image = ''


    let data = JSON.stringify({
        'username': username,
        'password': password,
        'confirm_password': confirm_password,
        'profile_image': profile_image
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
            $('.user-name-field').text(response['username'])
            $('.profile-image').attr('src', response['profile_image'])
            $('#uploadedAvatar').attr('src', response['profile_image'])
            profile_image = response['profile_image']
            toastr.success('Профиль успешно обновлен')
        },
        error: function (response) {
            console.log(response)
        }
    })

}


$('.update-profile-button').click(update_user)
$('.upload-image-button').click(function () {
    $('.upload-image-input').click()
})
$('.upload-image-input').change(function () {
    let image = $('.upload-image-input').prop('files')[0]
    if (image) {
        let reader = new FileReader();
        reader.onload = function (e) {
            $('.upload-image-input').attr('src', e.target.result);
            $('.profile-image').attr('src', e.target.result)
        };
        reader.readAsDataURL(image);

    }
})
$('.delete-image-button').click(function () {
    $('.upload-image-input').attr('src', '');
    $('.profile-image').attr('src', profile_image)
})