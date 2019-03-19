LANGUAGES_DICTIONARY = {
    'ru': {
        'start_message_1': 'Привет, {0} !\n'
                           '📱 Ниже находится клавиатура для управления ботом.\n'
                           'Приятного пользования!',

        'menu_get_eth': '💎 Получить Эфириум',
        'menu_news': '📰 Новости',
        'menu_wallet': '💼 Кошелек',
        'menu_friends': '🤝 Друзья',
        'menu_statistics': '📊 Статистика',
        'menu_about': 'ℹ️ О сервисе',
        'menu_luck': '🎲 Лотерея Luck',

        'get_eth_message_1': '💎 *Получить Эфириум*\n\n'
                           '⏳ Следующий бонус будет доступен через {0}ч.\n'
                           '👣 Заходите каждый день и получайте от 15 до 50 сабо.\n'
                           '✉️ Приглашайте друзей и зарабатывайте дополнительные сатоши!\n\n',
        'get_eth_message_2': '💎 *Получить Эфириум*\n\n'
                             '💸 Вам начислен ежедневый бонус в размере 25 сабо.\n'
                             '👣 Заходите через 24 часа и получайте еще бонусы!\n'
                             '✉️ Пока ждете приглашайте друзей и зарабатывайте дополнительные сабо',

        'invite_friends_button': '📢 Пригласить друзей',
        'invite_friends_message_1': '✉️ Отправьте сообщение Вашим друзьям '
                                    'и знакомым и получайте дополнительные сабо! ⤵️',
        'invite_friends_message_2': '⚡️ Присоединяйтесь к GetFreeETH и получайте бесплатные криптоденьги, '
                                    'а так же будьте в курсе актуальных новостей из мира криптовалют и блокчейна.\n'
                                    '{0}',

        'news_message': '📰 *Новости*\n\n'
                        '{0}',
        'no_news_message': 'Нет новостей.\n'
                           'Повторите запрос позже!',

        'wallet_message': '💼 *Кошелек*\n\n'
                          '💰 Баланс: *{0} сабо*\n'
                          '📢 Вы пригласили: *{1} человек.*\n'
                          '📣 Ваши рефералы пригласили: *{2} человек.*\n\n'
                          '📝 _Минимальная сумма вывода: 0.025 ETH (25000 сабо)_',
        'withdrawal_button': '📥 Вывести ETH',
        'withdrawal_message': '📤 *Вывести ETH*\n\n'
                              '❗️ Недостаточно средств для вывода.\n'
                              'Вывод накопленных средств осуществляется на кошелек в бот обменник '
                              '[http://t.me/ETH_CHANGE_BOT](@ETH banker)!\n'
                              '📝 Минимальная сумма вывода: 0.025 ETH (25000 сабо).\n\n'
                              '✉️ Приглашайте друзей и зарабатывайте дополнительные сабо!',

        'friends_message': '🤝 *Друзья*\n\n'
                           '☝️ Приглашайте новых пользователей и получайте за это дополнительные сабо!\n'
                           '✔️ *10 сабо* за каждого приглашенного Вами друга (реферал 1-ого уровня).\n'
                           '✔️ *5 сабо* за каждого приглашенного друга Вашим рефералом (реферал 2-ого уровня).\n'
                           '✔️ *50 сабо* за 5 приглашенных друзей.\n'
                           '✔️ *100 сабо* за 15 приглашенных друзей.\n'
                           '✔️ *200 сабо* за 30 приглашенных друзей.\n'
                           '✔️ *300 сабо* за 50 приглашенных друзей.\n'
                           '✔️ *500 сабо* за 100 приглашенных друзей.\n\n'
                           '✉️ Отправьте сообщение Вашим друзьям и знакомым и получайте дополнительные сабо! ⤵️',

        'statistics_message': '📊 *Статистика GetFreeETH*\n\n'
                              '👤 Пользователей: *{0}.*\n'
                              '💰 Всего начислено: *14.845774 ETH.*\n'
                              '📆 Дней онлайн: *{1}.*',

        'about_message': 'ℹ️ *О сервисе*\n\n'
                         '⚠️ Факт использования бота GetFreeETH подразумевает, что Вы согласны и принимаете правила.\n'
                         '☝️ Если Вы с этими правилами не согласны, пожалуйста, не пользуйтесь ботом GetFreeETH.\n\n'
                         '    *ПОРЯДОК СОЗДАНИЯ АККАУНТА*\n'
                         '▪️ Аккаунт пользователя в боте GetFreeETH создается после выполнения им команды /start.\n'
                         '▪️ Нажимая /start, пользователь дает свое согласие c правилами установленными '
                         'в боте GetFreeETH и согласен следовать им.\n\n'
                         '    *ПОРЯДОК ИСПОЛЬЗОВАНИЯ БОТА*\n'
                         '▪️ Баланс пользователя в Аккаунте GetFreeETH привязан к его Телеграм Аккаунту (его id). '
                         'Накопленные средства не могут быть перенесены с одного на другой Аккаунт GetFreeETH, '
                         'в случае потери пользователем своего Телеграм Аккаунта или потери доступа к нему.\n'
                         '▪️ В случае удаления пользователем бота, баланс пользователя обнуляется, '
                         'а также прекращается начисление бонусных сабо за привлеченных им рефералов, '
                         'до момента повторной регистрации пользователя в боте (выполнении команды /start).\n'
                         '▪️ Запрещается спамить бота повторяющимися командами!\n'
                         '❗️ В случае обнаружения данного факта, баланс пользователя обнуляется, '
                         'а сам пользователь заносится в черный список.\n'
                         '▪️ Запрещается накручивать рефералов фейковыми и неактивными аккаунтами!\n'
                         '❗️ В случае обнаружения данного факта, баланс пользователя обнуляется, '
                         'а сам пользователь заносится в черный список.\n'
                         '▪️ Запрещается присылать администрации бота GetFreeETH сообщения, '
                         'содержащие негативный характер (оскорбления, ругательства и т.д.)!\n'
                         '❗️ В случае обнаружения данного факта, баланс пользователя обнуляется, '
                         'а сам пользователь заносится в черный список.\n\n'
                         '    *ВЫВОД СРЕДСТВ*\n'
                         '▪️ Вывод средств осуществляется при достижении баланса пользователя минимальной суммы '
                         '(0.025 ETH - 25000 сабо) переводом на ETH кошелек в бот '
                         '[http://t.me/ETH_CHANGE_BOT](@ETH banker).\n'
                         'Перевод осуществляется с помощью ETH чека (ссылка, перейдя по которой, '
                         'человек получает сумму, заложенную в этом чеке на свой кошелек в боте '
                         '[http://t.me/ETH_CHANGE_BOT](@ETH banker)❗️ '
                         'Запрещается запрашивать вывод средств с другого Телеграм Аккаунта '
                         '(Телеграм Аккаунта не привязанного к системе GetFreeETH), '
                         'в случае обнаружения данного факта, аккаунт с которого был сделан запрос добавляется '
                         'в черный список!\n'
                         '❗️ При заказе вывода средств, осуществляется проверка начисленных сабо пользователя. '
                         'В случае обнаружения факта неправомерных начислений сатоши таких как: '
                         'получение сатоши за счет привлечения неактивных участников - '
                         'участников которые заходят в бота и сразу удаляют его (более 80%), '
                         'получение  сабо за счет привлечения участников путем размещенния обманных '
                         'объявлений в разных информационных ресурсах и социальных сетях и т.д. '
                         'такие начисленные сабо не будут учитываться при выплате!\n\n'
                         '*Бот GetFreeETH предоставляет массу возможностей получения сабо легальным путем, '
                         'чтобы не получить обнуление баланса и не попасть в черный список - '
                         'не нарушайте установленные правила!*',
        'luck_message': '🎲 *Лотерея Luck*\n\n'
                        '✌️ При поддержке '
                        '[http://t.me/ETH_CHANGE_BOT](@ETH banker) '
                        'проходит розыгрыш лотереи с удвоенными бонусами!\n\n'
                        '🕘 Розыгрыш лотереи: 03.06.18 в 22:22.\n'
                        '🎯 Вы делаете ставку и получаете персональный номер.\n'
                        '   Система GetFreeETH из всех номеров в день розыгрыша '
                        'случайным образом выбирает 5 номеров победителей.\n'
                        '🔸 1-й номер: выигрыш 9000 х 2 = 18000 сабо!\n'
                        '🔹 2-й номер: выигрыш 6000 х 2 = 12000 сабо!\n'
                        '🔸 3-й номер: выигрыш 3000 х 2 = 6000 сабо!\n'
                        '🔹 4-й номер: выигрыш 1500 х 2 = 3000 сабо!\n'
                        '🔸 5-й номер: выигрыш 1000 х 2 = 2000 сабо!\n\n'
                        '💲 Стоимость ставки: 50 сабо.\n'
                        '💰 Ваш баланс: 102 сабо.\n'
                        '⚡️ Текущий розыгрыш: № 16.\n'
                        '🏇 Вы можете сделать неограниченное количество ставок за один розыгрыш.\n'
                        'Текущее количество ставок: 1363.\n'
                        '📝 Результаты розыгрышей. [http://t.me/GetFreeETH_Game] \n\n'
                        '☝️ Все выигрыши зачисляются напрямую на Ваш адрес в боте: '
                        '[http://t.me/ETH_CHANGE_BOT](@ETH banker).\b'
                        '💸 Выигрыши зачисляются с помощью ETH чеков (ссылка, перейдя по которой, '
                        'человек получает сумму, заложенную в этом чеке на свой кошелек в боте '
                        '[http://t.me/ETH_CHANGE_BOT](@ETH banker))',
        'make_deal_button': '🎯 Сделать ставку',
        'back_button': '🔙 Назад',
        'my_deals': '📕 Мои ставки',

        'make_deal_message': '🎯 *Сделать ставку*\n\n'
                             '☑️ Подтвердите Вашу ставку!\n'
                             'С Вашего баланса будут списаны 50 сабо.',
        'make_deal_apply_button': '🎯 Подтвердить',
        'make_deal_loosen_button': '🚫 Отменить',
        'make_deal_apply_message': '🎯 Сделать ставку\n\n'
                                   '🎲 Ваша ставка принята!\n'
                                   'Что бы узнать номера Ваших активных ставок нажмите кнопку:\n'
                                   '📕 Мои ставки\n\n'
                                   '⏳ Ожидайте результата розыгрыша!',
        'make_deal_loosen_message': '🎯 Сделать ставку\n\n'
                                    '🚫 Ставка отменена!',

        'my_deals_message': '📕 Мои ставки\n\n'
                            '📒 У Вас {0} активных ставок.\n'
                            '📋 Ваши номера:\n'
                            '{1}',
    },

    'ww': {
        'choose_language_message': 'Choose language please\nВыберите язык пожалуйста',
        'ru_button': '🇷🇺 Русский',
    }
}
