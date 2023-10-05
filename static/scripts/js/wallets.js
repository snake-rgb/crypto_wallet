import {logout, verify_token, get_user} from "/static/scripts/js/utils.js";

let socket
let from_address
let table
socket = io('ws://0.0.0.0:8001/',
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
socket.on("receive_transaction", (data) => {
    wallets_balance_update()
    let value = parseFloat(data['value']).toFixed(6)
    console.log('transaction received' + data['address'])
    let address = data['address']
    if (data['status'] === 'received') {
        toastr.info(`Получено ${value} ETH на кошелёк.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')
    } else {
        toastr.info(`Снято ${value} ETH с кошелька.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')

    }
    table.draw()

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
    wallets_init()

    $('.watch-transactions-button').click(function () {
        $('#watch-transactions-modal').modal('show')
        let wallet_div = $(this).closest('.wallet-div')
        let wallet_address = $(wallet_div).find('.wallet-address').text()
        let params = {
            'address': wallet_address,
            'limit': 100,
        }
        $('.watch-transactions-header').text(`Список транзакций  ETH кошелька ${wallet_address}`)
        $('#watch-transactions-datatable').DataTable().destroy()
        let tableData

        table = $('#watch-transactions-datatable').DataTable({
            dom: 't',
            ajax: {
                "data": function () {
                    let info = $('#watch-transactions-datatable').DataTable().page.info();
                    $('#watch-transactions-datatable').DataTable().ajax.url(
                        `/api/v1/wallet/transactions/?${$.param(params)}`,
                    );
                },

            },
            columns: [
                {
                    'data': 'hash',
                    render: function (data, type, row) {
                        if (type === 'display') {
                            if (data) {
                                return `<div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 150px;"><a href="https://sepolia.etherscan.io/tx/${data}">${data}</a></div>`
                            }
                        }
                    }
                },
                {
                    'data': 'from_address',
                    render: function (data, type, row) {
                        if (type === 'display') {
                            if (data) {
                                return `<div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 150px;"><a href="https://sepolia.etherscan.io/address/${data}">${data}</a></div>`
                            }
                        }
                    }
                },
                {
                    'data': 'to_address',
                    render: function (data, type, row) {
                        if (type === 'display') {
                            if (data) {
                                return `<div style="overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 150px;"><a href="https://sepolia.etherscan.io/address/${data}">${data}</a></div>`
                            }
                        }
                    }
                },
                {
                    'data': 'value',
                    render: function (data, type, row) {
                        if (type === 'display') {
                            if (data) {
                                let value = parseFloat(data).toFixed(5)
                                return `${value} ETH`
                            } else {
                                return `0 ETH`
                            }
                        }

                    }
                },
                {
                    'data': 'age',
                    render: function (data, type, row) {
                        if (type === 'display')
                            if (data) {
                                let date = parse_date(data)
                                return `${date}`
                            }
                    }
                },
                {
                    'data': 'fee',
                    render: function (data, type, row) {
                        if (type === 'display')
                            if (data) {
                                let value = parseFloat(data).toFixed(5)
                                return `${value} ETH`
                            } else {
                                return `0 ETH`
                            }
                    }
                },
                {
                    'data': 'status',
                    render: function (data, type, row) {
                        if (type === 'display')
                            if (data) {
                                if (data === 'SUCCESS')
                                    return `<small class="badge bg-success rounded w-100" style="font-size: 0.7rem;">УСПЕШНО</small>`
                                if (data === 'FAILED')
                                    return `<small class="badge bg-danger rounded w-100" style="font-size: 0.7rem;">ПРОВАЛЕНО</small>`
                                if (data === 'PENDING')
                                    return `<small class="badge bg-warning rounded w-100" style="font-size: 0.7rem;">В ОЖИДАНИИ</small>`
                            }
                    }
                },

            ],
            processing: true,
            serverSide: true,
            filter: false,
            ordering: false,
            initComplete: function () {
                tableData = table.ajax.json().data;

            }
        });

        table.on('init', function () {
        })
        table.on('draw', function () {

        })

    })
    $('.test-button').click(function () {
        table.draw()
    })
})

function wallets_init() {
    get_wallets()
    setInterval(wallets_balance_update, 60 * 1000)
}

function get_wallets() {
    let ajax_url = 'http://' + window.location.host + '/api/v1/wallet/get-user-wallets/'
    $.ajax({
        url: ajax_url,
        success: function (response) {
            let wallets = response['wallets']
            for (let i = 0; i < wallets.length; i++) {
                let wallet = wallets[i]
                let balance = parseFloat(wallet['balance'])
                add_wallet(wallet['id'], wallet['asset_image'], wallet['address'], balance)
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}

function add_wallet(id, asset_image, address, balance) {
    let wallet_template = $('#wallet-template').clone(true, true)
    $(wallet_template).attr('id', '')
    $(wallet_template).find('.wallet-asset-image').prop('src', asset_image)
    let wallet_href = 'https://sepolia.etherscan.io/address/'
    $(wallet_template).find('.wallet-address').text(address).attr('href', wallet_href + address)
    $(wallet_template).find('.balance-amount').text(balance)
    $(wallet_template).show()
    $('.wallets-list').append(wallet_template)
}

function parse_date(target_date) {
    let date = new Date(target_date)
    let current_date = new Date()
    let time_difference = current_date - date
    // let time_difference_milliseconds = Math.abs(time_difference)
    let days = Math.floor(time_difference / (1000 * 60 * 60 * 24));
    let hours = Math.floor((time_difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor((time_difference % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((time_difference % (1000 * 60)) / 1000);
    let result
    if (days > 0) {
        result = days + " дней назад";
    } else if (hours > 0) {
        result = hours + " часов назад";
    } else if (minutes > 0) {
        result = minutes + " минут назад";
    } else {
        result = seconds + " секунд назад";
    }
    return result
}

function wallets_balance_update() {
    let wallets_list = $('.wallets-list').find('.wallet-div')
    let ajax_url = 'http://' + window.location.host + '/api/v1/wallet/get-user-wallets/'
    $.ajax({
        url: ajax_url,
        success: function (response) {
            let wallets = response['wallets']
            for (let i = 0; i < wallets.length; i++) {
                let wallet = wallets[i]
                let wallet_div = wallets_list[i]
                let balance = parseFloat(wallet['balance'])
                $(wallet_div).find('.balance-amount').text(wallet['balance'])
            }
        },
        error: function (response) {
            console.log(response)
        }
    })

}

$('.send-transaction').click(function () {
    $('#send-transaction-modal').modal('show');
    let wallet_div = $(this).closest('.wallet-div')
    from_address = $(wallet_div).find('.wallet-address').text()


})

$('.send-transaction-button').click(function () {
    let to_address = $('#send-transaction-modal').find('.to-address-input').val()
    let ajax_url = 'http://' + window.location.host + '/api/v1/wallet/send-transaction/'
    let amount = $('#send-transaction-modal').find('.eth-amount').val()
    let data = JSON.stringify({
        'from_address': from_address,
        'to_address': to_address,
        'amount': amount,
    })
    let to_address_regex = new RegExp('^0x[a-fA-F0-9]{40}$')
    if (to_address_regex.test(to_address))
        if (amount > 0)
            $.ajax({
                url: ajax_url,
                method: 'post',
                dataType: "json",
                headers: {
                    'Content-Type': 'application/json',
                },
                data: data,
                success: function (response) {
                    console.log(response)
                    $('#send-transaction-modal').modal('hide')
                    $('#send-transaction-modal').find('input').val('')
                    $('#hash-transaction-modal').modal('show');
                    $('#hash-transaction-modal').find('.transaction-link').attr('href',
                        `https://sepolia.etherscan.io/tx/${response['transaction']['hash']}`)

                },
                error: function (response, status, error) {
                    console.log(response.responseJSON)
                    if (response.responseJSON.detail === 'not enough eth in wallet')
                        Swal.fire({
                            title: 'Недостаточно средств на кошельке',
                            customClass: {
                                confirmButton: 'btn btn-primary'
                            },
                            buttonsStyling: false
                        });
                    else if (response.responseJSON.detail === 'invalid data') {
                        console.log('invalid data')
                        Swal.fire({
                            title: 'Пожалуйста проверьте адрес',
                            customClass: {
                                confirmButton: 'btn btn-primary'
                            },
                            buttonsStyling: false
                        });
                    } else
                        Swal.fire({
                            title: 'Что-то пошло не так попробуйте позже',
                            customClass: {
                                confirmButton: 'btn btn-primary'
                            },
                            buttonsStyling: false
                        });
                },
            })
        else {
            $('.address-error').text('')
            $('.value-error').text('Пожалуйста проверьте правильность введенного количества')
        }

    else {
        $('.address-error').text('Пожалуйста проверьте правильность введенного адреса ')
        $('.value-error').text('')
    }
})
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


// $('#watch-transactions-modal').on('hidden.bs.modal', function (e) {
//     $('#watch-transactions-datatable').DataTable().destroy()
// })