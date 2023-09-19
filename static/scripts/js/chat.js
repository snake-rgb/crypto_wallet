import {verify_token} from "/static/scripts/js/register.js";
import {logout} from "/static/scripts/js/profile.js";

let socket
let chatHistoryBody = document.querySelector('.chat-history-body')
let user_id
// socket connection to namespace chat
socket = io('ws://localhost:8001/',
    {
        transports: ["websocket", 'polling'],
        autoConnect: true,
    }
)
// socket connected event
socket.on("connect", () => {
    console.log('Socket connected')
    socket.emit('join_chat', {'access_token': Cookies.get('access_token').replace('Bearer ', '')})
});

socket.on("disconnect", () => {
    console.log('Socket disconnected')
    // socket.emit('leave_chat', {'access_token': Cookies.get('access_token').replace('Bearer ', '')})
});

socket.on("join_chat", (data) => {
    $.ajax(
        {
            url: 'http://' + window.location.host + '/api/v1/users/online',
            method: 'get',
            dataType: "json",
            headers: {
                'Content-Type': 'application/json',
            },
            success: function (response) {
                console.log(response)
                $('#chat-list').empty()
                for (let i = 0; i < response['users'].length; i++) {
                    let user_template = $('#chat-user-template').clone(true, true)
                    $(user_template).attr('id', '')
                    $(user_template).find('.left-users-username').text(response['users'][i]['username'])
                    $(user_template).find('.left-users-profile-image>img').attr('src', response['users'][i]['profile_image'])
                    $(user_template).show()
                    $('#chat-list').append(user_template)
                }
            }
        }
    )


});
socket.on("leave_chat", (data) => {
    $.ajax(
        {
            url: 'http://' + window.location.host + '/api/v1/users/online',
            method: 'get',
            dataType: "json",
            headers: {
                'Content-Type': 'application/json',
            },
            success: function (response) {
                console.log(response)
                $('#chat-list').empty()
                for (let i = 0; i < response['users'].length; i++) {
                    let user_template = $('#chat-user-template').clone(true, true)
                    $(user_template).attr('id', '')
                    $(user_template).find('.left-users-username').text(response['users'][i]['username'])
                    $(user_template).find('.left-users-profile-image>img').attr('src', response['users'][i]['profile_image'])
                    $(user_template).show()
                    $('#chat-list').append(user_template)
                }
            }
        }
    )


});
socket.on("send_message", (data) => {
    if (data['user_id'] !== user_id) {
        let message_template = $('#chat-message-template').clone(true, true)
        let message_text = data['text']
        $(message_template).attr('id', '')
        $(message_template).find('.chat-message-text>p').text(message_text)

        let profile_image = data['profile_image']
        $(message_template).find('.chat-message-avatar').prop('src', profile_image)
        $(message_template).show()
        $('.chat-history').append(message_template)
        scrollToBottom()
    }
});

function scrollToBottom() {
    chatHistoryBody.scrollTo(0, chatHistoryBody.scrollHeight);
}

// upload image for message
$('#attach-doc').change(function () {
    let image = $('#attach-doc').prop('files')[0]
    if (image) {
        let reader = new FileReader();
        reader.onload = function (e) {
            $('#attach-doc').attr('src', e.target.result);
        };
        reader.readAsDataURL(image);
    }
})
$('.send-msg-btn').click(function () {
    let message_template = $('#chat-message-template-right').clone(true, true)
    let message_text = $('.message-input').val()

    $(message_template).attr('id', '')
    $(message_template).find('.chat-message-text>p').text(message_text)

    let profile_image = $('.profile-image').prop('src')
    $(message_template).find('.chat-message-avatar').prop('src', profile_image)
    $(message_template).show()

    $('.chat-history').append(message_template)

    socket.emit('send_message', {
        'user_id': user_id,
        'text': message_text,
        'profile_image': profile_image,
    })
    send_message_ajax()
    scrollToBottom()
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
                if (response['messages'][i]['user']['id'] === user_id) {
                    message_template = $('#chat-message-template-right').clone(true, true)
                    profile_image = $('.profile-image').prop('src')

                } else {
                    message_template = $('#chat-message-template').clone(true, true)
                    profile_image = response['messages'][i]['user']['profile_image']
                }

                $(message_template).find('.chat-message-avatar').prop('src', profile_image)
                let message_text = response['messages'][i]['text']
                let message_image = response['messages'][i]['image']
                if (message_image)
                    $(message_template).find('.chat-message-image').prop('src', message_image)
                $(message_template).attr('id', '')
                $(message_template).find('.chat-message-text>p').text(message_text)


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
        },
        error: function (response) {
            console.log(response)
        }
    })

    new PerfectScrollbar(chatHistoryBody, {
        wheelPropagation: false,
        suppressScrollX: true
    });
    chat_history()
    scrollToBottom()
    logout()
})