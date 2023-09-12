let socket
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
    console.log(socket.id)
});


socket.on("new_user_connected", (data) => {
    console.log(data)
    let user_template = $('#chat-user-template').clone(true, true)
    $(user_template).attr('id', '')
    $(user_template).show()
    $('#chat-list').append(user_template)

});
socket.on("chat_message", () => {
    console.log('Socket hdghdgfhdgfhdgf')
});