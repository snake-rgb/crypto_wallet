import {logout, verify_token, get_user} from "/static/scripts/js/utils.js";

let socket
let wallets
let product_id
socket = io(`ws://${window.location.hostname}:8001/`,
    {
        transports: ["websocket", 'polling'],
        autoConnect: true,
    }
)
// socket connected event
socket.on("connect", () => {
    console.log('Socket connected')
    socket.emit('event_subscription', {'access_token': Cookies.get('access_token').replace('Bearer ', '')})
});

socket.on("disconnect", () => {
    console.log('Socket disconnected')
});
socket.on("order_status", (data) => {
    let order_id = data['order_id']
    $(`.product-div[data-order-id=${order_id}]`).find('.order-status').empty()
    $(`.product-div[data-order-id=${order_id}]`).find('.order-status').append(status_badge(data['status']))
    if (data['return_transaction_hash'])
        $(`.product-div[data-order-id=${order_id}]`).find('.order-return').text(data['return_transaction_hash'])
    $(`.product-div[data-order-id=${order_id}]`).find('.order-return')
        .attr('href', 'https://sepolia.etherscan.io/tx/' + data['return_transaction_hash'])
    console.log(data)
});
socket.on("receive_transaction", (data) => {
    let value = parseFloat(data['value']).toFixed(6)
    console.log('transaction received' + data['address'])
    let address = data['address']
    if (data['status'] === 'received') {
        toastr.info(`Получено ${value} ETH на кошелёк.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')
    } else {
        toastr.info(`Снято ${value} ETH с кошелька.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')

    }
});

socket.on("create_order", (data) => {
    //id, title, transaction_hash, price, image, return_transaction_hash, status, time
    let id = data['id']
    let title = data['title']
    let transaction_hash = data['transaction_hash']
    let price = data['price']
    let image = data['image']
    let return_transaction_hash = data['return_transaction_hash']
    let status = data['status']
    let time = data['time']
    console.log('Create order')
    console.log(data)
    add_order(id, title, transaction_hash, price, image, return_transaction_hash, status, time)
});

$(document).ready(function () {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": false,
        "progressBar": false,
        "positionClass": "toast-bottom-right",
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
    verify_token()
    logout()
    get_user()
    products_init()
    orders_init()
    get_wallets()

})

function products_init() {
    let ajax_url = 'http://' + window.location.host + '/api/v1/products/'

    $.ajax({
        url: ajax_url,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            for (let i = 0; i < response.length; i++) {
                add_product(
                    response[i]['id'],
                    response[i]['name'],
                    response[i]['wallet_address'],
                    response[i]['price'],
                    response[i]['image'])
            }
        },
        error: function (response, status, error) {
            console.log(response)

        },
    })
}

function add_product(id, title, address, price, image) {

    let product_template = $('#product-template').clone(true, true)
    $(product_template).attr('id', '')
    $(product_template).find('.buy-product-button').attr('data-id', id)
    $(product_template).find('.product-image').prop('src', image)
    $(product_template).find('.title-text').text(title)
    $(product_template).find('.address-text').text(address)
    $(product_template).find('.address-text').attr('href', 'https://sepolia.etherscan.io/address/' + address)
    $(product_template).find('.price-text').text(price + ' ETH')
    $(product_template).show()
    $('.products-list').append(product_template)
}

function orders_init() {
    let ajax_url = 'http://' + window.location.host + '/api/v1/user-orders/'

    $.ajax({
        url: ajax_url,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            for (let i = 0; i < response.length; i++) {
                console.log(response[i])
                let return_transaction_hash
                let status = response[i]['status']
                let time = response[i]['date']

                if (response[i]['return_transaction']) {
                    return_transaction_hash = response[i]['return_transaction']['hash']
                } else
                    return_transaction_hash = null


                add_order(
                    response[i]['id'],
                    response[i]['product']['title'],
                    response[i]['transaction']['hash'],
                    response[i]['product']['price'],
                    response[i]['product']['image'],
                    return_transaction_hash,
                    status,
                    time,
                )
            }
        },
        error: function (response, status, error) {
            console.log(response)

        },
    })
}

function add_order(id, title, transaction_hash, price, image, return_transaction_hash, status, time) {

    let product_template = $('#order-template').clone(true, true)
    $(product_template).attr('id', '')
    $(product_template).find('.product-div').attr('data-order-id', id)
    $(product_template).find('.order-image').prop('src', image)
    $(product_template).find('.title-text').text(title)
    $(product_template).find('.transaction-text').text(transaction_hash)
    $(product_template).find('.transaction-text').attr('href', 'https://sepolia.etherscan.io/tx/' + transaction_hash)
    $('.transaction-link').attr('href', `https://sepolia.etherscan.io/tx/${transaction_hash}`)
    $(product_template).find('.price-text').text(price + ' ETH')
    $(product_template).find('.order-status').empty()
    $(product_template).find('.order-status').append(status_badge(status))
    $(product_template).find('.order-return').text(return_transaction_hash)
    $(product_template).find('.order-time').text(moment(time).format('DD.MM.YYYY HH:mm'))
    $(product_template).find('.order-return').attr('href', 'https://sepolia.etherscan.io/tx/' + return_transaction_hash)
    $(product_template).show()
    $('.orders-list').append(product_template)
}

// clear modal inputs
$('#send-transaction-modal').on('hidden.bs.modal', function (e) {
    $(this)
        .find("input,textarea,select")
        .val('')
        .end()
        .find("input[type=checkbox], input[type=radio]")
        .prop("checked", "")
        .end();
    $(this).find('.value-error').text('').end()
    $(this).find('.address-error').text('').end()
})
$('#buy-product-modal').on('hidden.bs.modal', function (e) {
    $(this)
        .find("input,textarea,select")
        .val('')
        .end()
        .find("input[type=checkbox], input[type=radio]")
        .prop("checked", "")
        .end();
    $(this).find('.buy-product-wallet-select').empty()
})

$('.create-product-button').click(function () {
    $('#create-product-modal').modal('show')
    for (let i = 0; i < wallets.length; i++) {
        let wallet = wallets[i]
        $('.wallet-select').append(`<option value="${wallet['address']}">${wallet['address']} (${wallet['balance']} ETH)</option>`)
    }
})

function get_wallets() {
    let ajax_url = 'http://' + window.location.host + '/api/v1/wallet/get-user-wallets/'

    $.ajax({
        url: ajax_url,
        method: 'get',
        success: function (response) {
            wallets = response['wallets']
        },
        error: function (response) {
            console.log(response)
        }
    })

}

$('#create-product-modal').on('hidden.bs.modal', function (e) {
    $(this)
        .find("input,textarea,select")
        .val('')
        .end()
        .find("input[type=checkbox], input[type=radio]")
        .prop("checked", "")
        .end();
    $(this).find('.wallet-select').empty()

})
$('.create-product-submit').click(function () {
    let ajax_url = 'http://' + window.location.host + '/api/v1/create-product/'

    let data = JSON.stringify({
        'name': $('.product-name-input').val(),
        'image': $('#product-image-upload').attr('src'),
        'price': $('.product-price-input').val(),
        'wallet_address': $('.wallet-select').find('option:selected').val(),
    })


    $.ajax({
        url: ajax_url,
        method: 'post',
        data: data,
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {

            add_product(
                response['id'],
                response['name'],
                response['wallet_address'],
                response['price'],
                response['image'])
            $('#create-product-modal').modal('hide')
        },
        error: function (response) {

        }
    })
})

$('#product-image-upload').change(function () {
    let image = $('#product-image-upload').prop('files')[0]
    if (image) {
        let reader = new FileReader();
        reader.onload = function (e) {
            $('#product-image-upload').attr('src', e.target.result);
        };
        reader.readAsDataURL(image);

    }
})

$('.buy-product-button').click(function () {
    $('#buy-product-modal').modal('show')
    for (let i = 0; i < wallets.length; i++) {
        let wallet = wallets[i]
        $('.buy-product-wallet-select').append(`<option value="${wallet['address']}">${wallet['address']} (${wallet['balance']} ETH)</option>`)
    }
    product_id = $(this).attr('data-id')

})
$('.buy-product-submit').click(function () {
    let ajax_url = 'http://' + window.location.host + '/api/v1/buy-product/'
    let from_address = $('.buy-product-wallet-select').find('option:selected').val()
    let data = JSON.stringify({
        'from_address': from_address,
        'product_id': product_id,
    })


    $.ajax({
        url: ajax_url,
        method: 'post',
        dataType: "json",
        data: data,
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {
            $('#buy-product-modal').modal('hide')
            $('#transaction-link-modal').modal('show')
        },
        error: function (response, status, error) {
            console.log(response)

        },
    })
})

function status_badge(status) {
    if (status === 'REFUND')
        return `<small class="badge bg-danger">ВОЗВРАТ</small>`
    else if (status === 'DELIVERY')
        return `<small class="badge" style="background-color: #979a14">ДОСТАВКА</small>`
    else if (status === 'NEW')
        return `<small class="badge bg-warning">НОВЫЙ</small>`
    else if (status === 'SUCCESS')
        return `<small class="badge bg-success">ЗАВЕРШЕНО</small>`
    else
        return `<small class="badge" style="background-color: #3b5998">ПРОВАЛЕНО</small>`
}