@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def handle_join_check(call):
    user_id = call.from_user.id
    all_joined = True
    failed_channels = []

    channel_usernames = [
        "@alpha20288",
    ]

    for username in channel_usernames:
        try:
            member = bot.get_chat_member(username, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                all_joined = False
                failed_channels.append(username)
        except Exception as e:
            all_joined = False
            failed_channels.append(username)

    if all_joined:
        bot.send_message(call.message.chat.id, "✅ عالی! حالا لینک کانال یا گروهت رو بفرست تا برای تبادل بررسی بشه.")
        user_states[call.message.chat.id] = "awaiting_channel_link"
    else:
        bot.send_message(call.message.chat.id, "❌ برای ادامه باید توی همه کانال‌ها عضو باشی. لطفاً عضو شو و دوباره تلاش کن.")
