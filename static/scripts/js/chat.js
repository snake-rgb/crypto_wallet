import {logout, verify_token, get_user} from "/static/scripts/js/utils.js";

let socket
let chatHistoryBody = document.querySelector('.chat-history-body')
let user_id
// socket connection to namespace chat
socket = io(`ws://${window.location.hostname}:8001/`,
    {
        transports: ["websocket", 'polling'],
        autoConnect: true,
    }
)
// socket connected event
socket.on("connect", () => {
    console.log('Socket connected sid - ' + socket.id)
    socket.emit('join_chat', {'access_token': Cookies.get('access_token').replace('Bearer ', '')})
});

socket.on("disconnect", () => {
    console.log('Socket disconnected')
    socket.emit('leave_chat', {'access_token': Cookies.get('access_token').replace('Bearer ', ''), 'sid': socket.sid})
});

socket.on("join_chat", (data) => {
    for (let i = 0; i < data.length; i++) {
        let user_template = $('#chat-user-template').clone(true, true)
        if ($('#chat-list').find(`.left-users-username[data-user-id=${data[i]['user_id']}]`).length === 0) {
            $(user_template).attr('id', '')
            $(user_template).find('.left-users-username').text(data[i]['username'])
            $(user_template).find('.left-users-username').attr('data-user-id', data[i]['user_id'])
            $(user_template).find('.left-users-profile-image>img').attr('src', data[i]['profile_image'])
            $(user_template).show()
            $('#chat-list').append(user_template)
        }

    }


})
;
socket.on("leave_chat", (data) => {
    console.log('leave chat')
    console.log(data)
});
socket.on("send_message", (data) => {
    if (data['user_id'] !== user_id) {
        let message_template = $('#chat-message-template').clone(true, true)
        let message_text = data['text']
        let messages_text = []
        let message_image = data['image']
        let date = new Date(data['date'])

        $(message_template).find('.chat-message-text').empty()
        while (message_text.length > 0) {
            messages_text.push(message_text.substring(0, 70));
            message_text = message_text.substring(70);
        }
        for (let i = 0; i < messages_text.length; i++) {
            $(message_template).find('.chat-message-text').append(`<p class="mb-0">${messages_text[i]}</p>`);
        }
        if (message_image)
            $(message_template).find('.chat-message-text').append(`<img src="${message_image}" class="chat-message-image" alt="">`)

        $(message_template).attr('id', '')
        // $(message_template).find('.chat-message-text>p').text(message_text)

        let profile_image = data['profile_image']
        $(message_template).find('.chat-message-avatar').prop('src', profile_image)
        $(message_template).find('.message-time').text(`${convert_time(date.getHours())}:` + `${convert_time(date.getMinutes())}`)
        $(message_template).show()
        $('.chat-history').append(message_template)
        scrollToBottom()
    }
});

socket.on("receive_transaction", (data) => {
    let value = parseFloat(data['value']).toFixed(6)
    let address = data['address']
    if (data['status'] === 'received') {
        toastr.info(`Получено ${value} ETH на кошелёк.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')
    } else {
        toastr.info(`Снято ${value} ETH с кошелька.\n ${address} \n<a href="https://sepolia.etherscan.io/tx/${data['hash']}">Ссылка на транзакцию</a>`, 'Новая транзакция')
    }
});

function scrollToBottom() {
    chatHistoryBody.scrollTo(0, chatHistoryBody.scrollHeight);
}

// upload image for message
$('#attach-doc').change(function () {
    let image = $('#attach-doc').prop('files')[0]
    let reader = new FileReader();
    reader.onload = function (e) {
        $('#attach-doc').attr('src', e.target.result);
    };
    reader.readAsDataURL(image);
})
$('.send-msg-btn').click(function () {

    let message_template = $('#chat-message-template-right').clone(true, true)
    let message_text = $('.message-input').val()
    let messages_text = []
    let message_text_for_db = ''
    let date = new Date()

    if (message_text && $.trim(message_text).length || $.trim(message_text).length === 0 && $('#attach-doc').prop('src')) {
        $(message_template).attr('id', '')
        $(message_template).find('.chat-message-text').empty()
        while (message_text.length > 0) {
            messages_text.push(message_text.substring(0, 70));
            message_text = message_text.substring(70);
        }

        for (let i = 0; i < messages_text.length; i++) {
            $(message_template).find('.chat-message-text').append(`<p class="mb-0">${messages_text[i]}</p>`);
            message_text_for_db += messages_text[i]
        }

        let profile_image = $('.profile-image').prop('src')
        $(message_template).find('.chat-message-avatar').prop('src', profile_image)
        if ($('#attach-doc').prop('src'))
            $(message_template).find('.chat-message-text').append(`<img src="${$('#attach-doc').prop('src')}" class="chat-message-image" alt="">`)
        $(message_template).find('.message-time').text(`${convert_time(date.getHours())}:` + `${convert_time(date.getMinutes())}`)
        send_message_ajax()
        $(message_template).show()
        $('.message-input').val('')
        $('#attach-doc').attr('src', null)
        $('.chat-history').append(message_template)

        scrollToBottom()
    } else
        $('.message-input').val('')


})

function send_message_ajax() {
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/create-message/'


    let data = JSON.stringify({
        'text': $('.message-input').val(),
        'image': $('#attach-doc').prop('src'),
    })

    $.ajax({
        url: base_url + api_endpoint,
        method: 'post',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        data: data,
        success: function (response) {
            console.log(response)
            socket.emit('send_message', response['message'])

        },
        error: function (response) {
            console.log(response)
        }
    })
}

function chat_history() {
    let base_url = 'http://' + window.location.host
    let api_endpoint = '/api/v1/get-messages/'
    $.ajax({
        url: base_url + api_endpoint,
        method: 'get',
        dataType: "json",
        headers: {
            'Content-Type': 'application/json',
        },
        success: function (response) {

            for (let i = 0; i < response['messages'].length; i++) {
                let message_template
                let profile_image
                let date = new Date(response['messages'][i]['date'])
                if (response['messages'][i]['user']['id'] === user_id) {
                    message_template = $('#chat-message-template-right').clone(true, true)
                    profile_image = $('.profile-image').prop('src')
                    $(message_template).find('.message-time').text(`${convert_time(date.getHours())}:` + `${convert_time(date.getMinutes())}`)

                } else {
                    message_template = $('#chat-message-template').clone(true, true)
                    profile_image = response['messages'][i]['user']['profile_image']

                    $(message_template).find('.message-time').text(`${convert_time(date.getHours())}:` + `${convert_time(date.getMinutes())}`)
                }

                $(message_template).find('.chat-message-avatar').prop('src', profile_image)
                let message_text = response['messages'][i]['text']
                let message_image = response['messages'][i]['image']
                let messages_text = []

                $(message_template).attr('id', '')

                $(message_template).find('.chat-message-text').empty()
                while (message_text.length > 0) {
                    messages_text.push(message_text.substring(0, 70));
                    message_text = message_text.substring(70);
                }
                for (let i = 0; i < messages_text.length; i++) {
                    $(message_template).find('.chat-message-text').append(`<p class="mb-0">${messages_text[i]}</p>`);
                }
                if (message_image)
                    $(message_template).find('.chat-message-text').append(`<img src="${message_image}" class="chat-message-image" alt="">`)
                $(message_template).show()
                $('.chat-history').append(message_template)
                scrollToBottom()
            }
        },
        error: function (response) {
            console.log(response)
        }
    })
}


$(document).ready(function () {
    verify_token()

    let profile_image
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
            user_id = response['id']
            $('.user-name-field').text(response['username'])
            $('.profile-image').attr('src', response['profile_image'])
            profile_image = response['profile_image']

            get_user()
            chat_history()
            scrollToBottom()
            logout()
        },
        error: function (response) {
            console.log(response)
        }
    })

    new PerfectScrollbar(chatHistoryBody, {
        wheelPropagation: false,
        suppressScrollX: true
    });

})
$('.message-input').keyup(function (e) {
    if (e.keyCode === 13) {  // enter, return
        $('.send-msg-btn').trigger('click')
    }
})

function convert_time(time) {
    if (time < 10) {
        return '0' + time;
    }
    return time.toString();
}