from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiofiles
import json

token = 'your token here'
ids = [] # ids that will have access to add/delprefix, updbd, reset commands
bot = Bot(token=token)
dp = Dispatcher(bot)

async def rdb(msg) -> dict: #i should somewhen make this bot modular
	async with aiofiles.open(f'db{msg.chat.id}.json', 'r', encoding='UTF-8') as f:
		data = await f.read(json.load(f)) 
		if data is None:
			return None
	return data
async def wdb(cid, dictionary) -> None:
	async with aiofiles.open(f'db{cid}.json', 'w', encoding='UTF-8') as f:
		await f.write(json.dumps(dictionary, ensure_ascii=False, indent=0)) 
	return None

@dp.message_handler(commands='prefix')
async def prefix_hndl(msg:types.Message):
	prfx = msg.get_args() #some basic stuff
	uid = msg.from_user.id
	un = msg.from_user.username
	cid = msg.chat.id
	db = await rdb(msg)
	await bot.delete_message(cid, msg.message_id)

	if not uid in db or not any(x in uid for x in await bot.get_chat_administrators(cid)): #checks
		await bot.send_message(cid, 'У вас нет префикса.')
		print(f'@{un}({uid}) has no prefix')
		return
	if len(prfx) > 16:
		await bot.send_message(cid, 'Префикс не должен превышать 16 символов.')
		print(f'lenght is more than 16 ({len(prfx)})')
		return
	if db is None:
		await bot.send_message(cid, 'База данных не найдена.')
		print('no db')
		return
	
	prev = db.pop(uid) #changing prefix
	db[uid] = prfx
	await bot.set_chat_administrator_custom_title(cid, uid, prfx)
	await wdb(cid, db)
	await bot.send_message(cid, f'Префикс сменен с "{prev}" на "{prfx}"')
	print(f'changed @{un}({uid}) from {prev} to {prfx}')

@dp.message_handler(commands='restore')
async def restore_hndl(msg:types.Message):
	uid = msg.from_user.id #basic stuff
	un = msg.from_user.username
	cid = msg.chat.id
	db = await rdb(msg)
	await bot.delete_message(cid, msg.message_id)

	if db is None: #checks
		await bot.send_message(cid, 'База данных не найдена.')
		print('no bd')
		return
	if not uid in db:
		await bot.send_message(cid, 'Вас нет в базе данных.')
		print(f"bd doesn't have @{un}({uid})")
		return
	
	await bot.promote_chat_member(cid, uid, can_manage_chat=True) #restoring
	await bot.set_chat_administrator_custom_title(cid, uid, db.get(uid))
	await bot.send_message(cid, f'Префикс "{db.get(uid)}" восстановлен.')
	print(f'@{un}({uid}) restored {db.get(uid)}')

@dp.message_handler(commands='addprefix')
async def addprfx_hndl(msg:types.Message):
	prfx = msg.get_args() #basic stuff
	uid = msg.reply_to_message.from_user.id
	un = msg.reply_to_message.from_user.username
	cid = msg.chat.id
	db = await rdb(msg)
	await bot.delete_message(cid, msg.message_id)

	if not msg.from_user.id in ids: #checks
		await bot.send_message(cid, 'Недостаточно прав.')
		print(f'@{msg.from_user.username}({msg.from_user.id}) has no access, but still tries')
		return
	if uid is None:
		await bot.send_message(cid, 'Ответьте на сообщение человека которому вы даете префикс.')
		print('no reply')
		return
	if db is None:
		await bot.send_message(cid, 'База данных не найдена, но теперь она создана.')
		print('created db for /addprefix')
		db = {}
	if uid in db or any(x in uid for x in await bot.get_chat_administrators(cid)):
		await bot.send_message(cid, 'У данного человека уже есть префикс, либо он находится в базе данных.') #technically i could make writing to db in case if there's no
		print(f'@{un}({uid}) already have prefix "{db.get(uid) if not db.get(uid) is None else None}"') #but it'll make possible to break the db by adding an actual admin.
		return
	if len(prfx) > 16:
		await bot.send_message(cid, 'Префикс не должен превышать 16 символов.')
		print(f'lenght is more than 16 ({len(prfx)})')
		return
	
	db[uid] = prfx #adding prefix
	await wdb(cid, db)
	await bot.promote_chat_member(cid, uid, can_manage_chat=True)
	await bot.set_chat_administrator_custom_title(cid, uid, prfx)
	print(f'@{un}({uid}) got {prfx}')

@dp.message_handler(commands='delprefix')
async def delprfx_hndl(msg:types.Message):
	uid = msg.reply_to_message.from_user.id #basic stuff
	un = msg.reply_to_message.from_user.username
	cid = msg.chat.id
	db = await rdb(msg)
	await bot.delete_message(cid, msg.message_id)

	if not msg.from_user.id in ids: #checks
		await bot.send_message(cid, 'Недостаточно прав.')
		print(f'@{msg.from_user.username}({msg.from_user.id}) has no access, but still tries')
		return
	if uid is None:
		await bot.send_message(cid, 'Ответьте на сообщение человека которому вы даете префикс.')
		print('no reply')
		return
	if db is None:
		await bot.send_message(cid, 'База данных не найдена.')
		print('no db')
		return
	if not uid in db:
		await bot.send_message(cid, 'У данного человека нет префикса, либо его нет в базе данных.') #technically i could make writing to db in case if there's no prefix
		print(f'@{un}({uid}) doesnt have prefix, but tryna to delete') #but mehh :p	
		return

	prev = db.pop(uid)
	await bot.promote_chat_member(cid, uid, can_manage_chat=False)
	print(f'{prev} deleted from @{un}({uid})')

@dp.message_handler(commands='updbd')
async def updbd_hndl(msg:types.Message):
	db = {} # basic stuff
	cid = msg.chat.id
	admins = await bot.get_chat_administrators(cid)
	await bot.delete_message(cid, msg.message_id)

	if not msg.from_user.id in ids: #checks
		await bot.send_message(cid, 'Недостаточно прав.')
		print(f'@{msg.from_user.username}({msg.from_user.id}) has no access, but still tries')
		return
	
	for admin in admins: #main stuff
		uid = admin['user']['id']
		un = admin['user']['username']
		status = admin['status']
		prfx = admin['custom_title'] if not admin['custom_title'] is None else ''
		cci = admin['can_change_info']
		cdm = admin['can_delete_messages']
		ciu = admin['can_invite_users']
		crm = admin['can_restrict_members']
		cpm = admin['can_pin_messages']
		cmt = admin['can_manage_topics'] #somewhy some users have this rights, have no clue why.
		cpms = admin['can_promote_members']
		cmv = admin['can_manage_video_chats']
		ia = admin['is_anonymous']
		cmvc = admin['can_manage_voice_chats']
		rights = [cci, cdm, ciu, crm, cpm, cpms, cmv, ia, cmvc]
		if status == 'creator' or admin['user']['is_bot'] == True:
			print(f'skipping @{un}({uid}) since bot/owner')
			continue
		if True in rights: #this check would be more easier and sexier, but im using aiogram
			print(f'skipping @{un}({uid}) since admin') #instead of pyrogram which have promoted_by
			continue
		db[uid] = prfx
		print(f'added @{un}({uid}) with "{prfx}"')

	await wdb(cid, db) #creating db itself

@dp.message_handler(commands='reset')
async def reset_hndl(msg:types.Message):
	cid = msg.chat.id
	db = await rdb(msg)

	if not msg.from_user.id in ids: #checks
		await bot.send_message(cid, 'Недостаточно прав.')
		print(f'@{msg.from_user.username}({msg.from_user.id}) has no access, but still tries')
		return
	if db is None:
		await bot.send_message(cid, 'База данных не найдена.')
		print('no db')
		return
	
	for uid in db:
		await bot.promote_chat_member(cid, uid, can_manage_chat=True)
		await bot.set_chat_administrator_custom_title(cid, uid, db.get(uid))
		print(f'restored {db.get(uid)} for {uid}')

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
