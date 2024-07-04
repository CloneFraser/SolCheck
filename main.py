from typing import Final
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from telegram import Update, constants
import token_info

api_token = ''
bot_username: Final = '@SolCheckerCrypto_bot'


# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, I\'m SolCheck')


async def ca_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Enter Token Address...')


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    bot = update.message.get_bot()
    print(len(list(text)))

    if len(list(text)) >= 42 or len(list(text)) <= 45:
        token = token_info.Token(text)
        await bot.send_photo(chat_id=update.message.chat_id, photo=token.image_url)
        await update.message.reply_text(
            f"<b>Name:</b> {token.token_name}\n"
            f"<b>Symbol:</b> {token.token_symbol}\n"
            f"<b>Market Cap:</b> ${token.market_cap:,}\n"
            f"<b>Liquidity:</b> ${token.liquidity:,}\n"
            f"<b>Supply:</b> {token.token_supply:,}\n"
            f"<b>LP Burned:</b> {token.lp_burned}\n"
            f"<b>Top 10 Holders own: </b> {token.holder_percentage}%",
            parse_mode=constants.ParseMode.HTML
        )
        '''
        await update.message.reply_text(f"Name: {token.token_name}"
                                        f"\nSymbol: {token.token_symbol} \nMarket Cap: ${token.market_cap: ,}"
                                        f"\nLiquidity: ${token.liquidity: ,} \nSupply: {token.token_supply}")
        '''
    else:
        await update.message.reply_text('Invalid Token Address')

# responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hi'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print('User ' + str(update.message.chat.id) + ' in ' + message_type + ': ' + text)

    if message_type == 'group':
        if bot_username in text:
            new_text: str = text.replace(bot_username, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot: ' + response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Update ' + str(update) + ' caused error: ' + str(context.error))


if __name__ == '__main__':
    print('Starting Bot...')
    app = Application.builder().token(api_token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('enterca', ca_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, address))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Bot started...')
    app.run_polling(poll_interval=1)
