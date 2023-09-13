/**
 * App Chat
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
    (function () {
        const chatContactsBody = document.querySelector('.app-chat-contacts .sidebar-body'),
            chatContactListItems = [].slice.call(
                document.querySelectorAll('.chat-contact-list-item:not(.chat-contact-list-item-title)')
            ),
            chatHistoryBody = document.querySelector('.chat-history-body'),
            chatSidebarLeftBody = document.querySelector('.app-chat-sidebar-left .sidebar-body'),
            chatSidebarRightBody = document.querySelector('.app-chat-sidebar-right .sidebar-body'),
            chatUserStatus = [].slice.call(document.querySelectorAll(".form-check-input[name='chat-user-status']")),


            userStatusObj = {
                active: 'avatar-online',
                offline: 'avatar-offline',
                away: 'avatar-away',
                busy: 'avatar-busy'
            };

        // Initialize PerfectScrollbar
        // ------------------------------

        // Chat contacts scrollbar
        if (chatContactsBody) {
            new PerfectScrollbar(chatContactsBody, {
                wheelPropagation: false,
                suppressScrollX: true
            });
        }


        // Sidebar left scrollbar
        if (chatSidebarLeftBody) {
            new PerfectScrollbar(chatSidebarLeftBody, {
                wheelPropagation: false,
                suppressScrollX: true
            });
        }

        // Sidebar right scrollbar
        if (chatSidebarRightBody) {
            new PerfectScrollbar(chatSidebarRightBody, {
                wheelPropagation: false,
                suppressScrollX: true
            });
        }

        // Scroll to bottom function
        function scrollToBottom() {
            chatHistoryBody.scrollTo(0, chatHistoryBody.scrollHeight);
        }

        scrollToBottom();


        // Update user status
        chatUserStatus.forEach(el => {
            el.addEventListener('click', e => {
                let chatLeftSidebarUserAvatar = document.querySelector('.chat-sidebar-left-user .avatar'),
                    value = e.currentTarget.value;
                //Update status in left sidebar user avatar
                chatLeftSidebarUserAvatar.removeAttribute('class');
                Helpers._addClass('avatar avatar-xl ' + userStatusObj[value] + '', chatLeftSidebarUserAvatar);
                //Update status in contacts sidebar user avatar
                let chatContactsUserAvatar = document.querySelector('.app-chat-contacts .avatar');
                chatContactsUserAvatar.removeAttribute('class');
                Helpers._addClass('flex-shrink-0 avatar ' + userStatusObj[value] + ' me-3', chatContactsUserAvatar);
            });
        });

        // Select chat or contact
        chatContactListItems.forEach(chatContactListItem => {
            // Bind click event to each chat contact list item
            chatContactListItem.addEventListener('click', e => {
                // Remove active class from chat contact list item
                chatContactListItems.forEach(chatContactListItem => {
                    chatContactListItem.classList.remove('active');
                });
                // Add active class to current chat contact list item
                e.currentTarget.classList.add('active');
            });
        });


    })();
});
