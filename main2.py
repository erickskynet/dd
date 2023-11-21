import os, json, shutil, time, asyncio, aiohttp, logging
from pyrogram import Client, filters, idle
from pyromod.helpers import ikb
from doodstream import DoodStream
from pyrogram.errors.exceptions.bad_request_400 import MessageEmpty, MessageNotModified
from progress import progress_for_pyrogram, humanbytes, TimeFormatter

BOT_USERNAME = "Doodstreamingbot"
BOT_TOKEN = "2008994688:AAE-gsB-5an5oID_ZrREF1W06m7Cz_gYngY"
API_ID = 3910389
API_HASH = "86f861352f0ab76a251866059a6adbd6"
RESULTS_COUNT = 10  # NOTE Number of results to show, 4 is better
OWNER_ID = [1064471769,5958457159]
DOODSTREAM_API = "63999z3s1iui9o3tf806b"


# TODO:
# Automatic Url Detect (From stackoverflow. Can't find link lol)
DOOD_REGEX = (r"^((?:https?:)?\/\/)"
              r"?((?:www)\.)"
              r"?((?:dood\.ws))"
              r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

loop = asyncio.get_event_loop()

app = Client(
                BOT_USERNAME,
                bot_token=BOT_TOKEN,
                api_id=API_ID,
                api_hash=API_HASH,
                workers=55
            )
d = DoodStream(DOODSTREAM_API)

i = 0
ii = 0
m = None
keyboard = None
data = None
C_NAME = {"status":False,"id":"","name":""}


db_bsaec = {
    "s": False,
    "n": False
}
try:
    db_user = open("config.json", "r")
    db_user = json.load(db_user)
except:
    db_user = open("config.json", "w")
    json_object = json.dumps(db_bsaec, indent=4)
    db_user.write(json_object)
    db_user.close()

db_user = open("config.json", "r")
db_user = json.load(db_user)

silent = db_user["s"]
autorname = db_user["n"]

START_TEXT = """
👋🏻 **Hi** {user_mention},

I am a doodstream bot to maintain your [doodstream](https://doodstream.com) account.

I can upload tg files to your doodstream account too.

commands:
    - /start
    - /status
    - /myfiles
    - /silent <on/off>
    - /setrname <val> - keep empty to turn off
    
Send video to upload

**Maintained By: {bot_owner}**❤️!
"""

def convertSec(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60) 
    #return "%d:%02d:%02d" % (hour, min, sec) 
    #return "%02d minute" % min
    return "%d hours, %02d min, %02d sec" % (hour,min,sec)

@app.on_message(filters.command("silent") & filters.chat(OWNER_ID))
async def setSilent(client, message):
    if message.text.split(" ")[1] == "on":
        db_user["s"] = True
        await message.reply_text("Silent mode turned on")
    elif message.text.split(" ")[1] == "off":
        db_user["s"] = False
        await message.reply_text("Silent mode turned off")
    with open(f"config.json", "w") as fp:
        json_object = json.dumps(db_user, indent=4)
        fp.write(json_object)
        fp.close()

@app.on_message(filters.command("setrname") & filters.chat(OWNER_ID))
async def setRname(client, message):
    txt = message.text.split(" ")
    if len(txt) >= 2:
        txt = message.text.replace(txt[0] + " ","")
        db_user["n"] = txt
        await message.reply_text(f"Auto rename set to : {txt}")
    elif len(txt) == 1:
        db_user["n"] = False
        await message.reply_text("Auto rename turned off")
    with open(f"config.json", "w") as fp:
        json_object = json.dumps(db_user, indent=4)
        fp.write(json_object)
        fp.close()

# Upload video file from local storage
@app.on_message(filters.incoming & filters.video & filters.private & filters.chat(OWNER_ID))
async def localUpload(client, message):
        m = await message.reply_text("Downloading Video...", quote=True)
        dl_loc = "./Video/" + str(message.from_user.id) + "/"
        if not os.path.isdir(dl_loc):
            os.makedirs(dl_loc)
        the_media = None
        await asyncio.sleep(4)
        try:
          start_time = time.time()
          the_media = await message.download(
            file_name=dl_loc,
            progress=progress_for_pyrogram,
            progress_args=(
                "**Downloading Video...** \n",
                m,
                start_time
            )
          )
          if the_media is None:
            await m.edit_text("Unable to Download The Video!")
            return
        except Exception as err:
            await m.edit_text(f"Unable to Download The Video!\n{err}")
            return
        try:
            await m.edit_text("Uploading to Doodstream...")
            async with aiohttp.ClientSession() as session:
                m_api = "https://doodapi.com/api/upload/server?key={}"
                hit_api = await session.get(m_api.format(DOODSTREAM_API))
                json_data = await hit_api.json()
                url_for_upload = json_data['result']
                filename = the_media.split("/")[-1]
                print(filename)
                pp_data = {"api_key": DOODSTREAM_API, "file": open(the_media, "rb")}
                p_up = await session.post(url_for_upload, data=pp_data)
                u_local = await p_up.json()
                await m.delete()
                file_id = ""
                f_name = ""
                d_file = ""
                w_online = ""
                splash_img = ""
                fa_title = u_local['result'][0]
                if db_user["n"] != False:
                    fa_title = db_user["n"]
                text = f"<a href=\'{u_local['result'][0]['splash_img']}'> </a>"
                for i in u_local['result']:
                    text += f"📁 Title: {fa_title}"
                    #text += f"\n⏰ Duration: {i['length']} sec"
                    text += f"\n⏰ Duration: {convertSec(int(i['length']))}"
                    #text += f"\n📊 Size: {i['size']} KB"
                    text += f"\n📊 Size: {humanbytes(int(i['size']))}"
                    text += f"\n📆 Uploaded on: {i['uploaded']}"
                    file_id = i['filecode']
                    f_name = i['title']
                    d_file = i['download_url']
                    w_online =i['protected_embed']
                    splash_img = i['splash_img']
                #text += f"\n[]({splash_img})"
                keyboard = ikb([[("Rename",f"rename_{str(file_id)}"),("Download",str(d_file),"url")],
                                    [("Watch Online",str(w_online),"url"),("Close","close")]])
                #await message.reply_photo(
                  #photo=splash_img,
                  #caption=text,
                  #reply_markup=keyboard,
                  #quote=True,
                #)
                if not db_user["s"]:await message.reply_text(
                  text=text,
                  reply_markup=keyboard,
                  disable_web_page_preview=False,
          #        parse_mode="html",
                  quote=True,
                )
                #new feature
                if db_user["n"] != False:
                    r = d.rename_file(file_id, db_user["n"])
                    if r['status'] == 200:print("Success")
                    elif r['status'] == 403:print(f"{r['msg']}")
                    elif r['status'] == 400:print("Invalid file id")
                #if os.path.isdir(dl_loc):
                    #shutil.rmtree(dl_loc)
                if os.path.exists(the_media):
                    os.remove(the_media)
                    print("[ DoodStream-Bot ] Successfully Cleaned Temp Download Directory!")
                #await asyncio.sleep(5)
                #await m.edit(text=str(text), disable_web_page_preview=True, reply_markup=keys)
        #except TypeError:
        except Exception as e:
            print(f"Error: {e}")
            text = f"Unsopported video format for {str(the_media).split('/')[-1]}"
            text += "\nSupported video format : mkv, mp4, wmv, avi, mpeg4, mpegps, flv, 3gp, webm, mov, mpg, m4v"
            await message.reply_text(text)
        #await asyncio.sleep(5)

@app.on_message(filters.command(["start","help"]) & filters.chat(OWNER_ID))
async def startBotS(client, message):
    own = await client.get_users(message.from_user.id)
    await message.reply_text(
        text=START_TEXT.format(user_mention=message.from_user.mention, bot_owner=own.mention(style="md"))
    )

# Check doodstream account info
@app.on_message(filters.command("status") & filters.chat(OWNER_ID))
async def accountInfo(client, message):
        data = d.account_info()['result']
        msg = "#"*10+" Account Info "+"#"*10
        msg += f"\n👤 Email: {data['email']}"
        msg += f"\n💰 Balance: ${data['balance']}"
        msg += f"\n🗂️ Used Storage: {int(int(data['storage_used'])/1024)} MB"
        msg += f"\n📈 Storage Left: {data['storage_left']}"
        msg += f"\n💠 Premium Expire: {data['premim_expire']}"
        await message.reply_text(msg)

@app.on_message(~filters.command(["start", "help", "info", "myfiles", "reports", "status"]) & ~filters.regex(DOOD_REGEX) & filters.private & ~filters.media & filters.chat(OWNER_ID))
async def newName(client, message):
    if C_NAME['status']:
        C_NAME['status'] = False
        r = d.rename_file(C_NAME['id'], message.text)
        #text = "#"*10 + " Rename Video " + "#"*10
        #text = ""
        text_s = ""
        if r['status'] == 200:
            text_s += "Success"
        elif r['status'] == 403:
            text_s += f"{r['msg']}"
        elif r['status'] == 400:
            text_s += "Invalid file id"
        info = d.file_info(C_NAME['id'])
        if info['status'] == 400:
            print(info['msg'])
        d_file = ""
        w_online = ""
        splash_img = ""
        text = f"<a href=\'{info['result'][0]['splash_img']}'> </a>"
        for i in info['result']:
            if "Not found or not your file" in str(i['status']):
                text += "\nVideo Not found or not your file"
            else:
                text += f"📁 Title: {message.text}"
                #text += f"\n⏰ Duration: {i['length']} sec"
                text += f"\n⏰ Duration: {convertSec(int(i['length']))}"
                text += f"\n👁 Views: {i['views']}"
                #text += f"\n📊 Size: {i['size']} KB"
                text += f"\n📊 Size: {humanbytes(int(i['size']))}"
                text += f"\n📆 Uploaded on: {i['uploaded']}"
                splash_img = i['splash_img']
                d_file = f"https://dood.watch/d/{i['filecode']}"
                w_online = f"https://dood.watch{i['protected_embed']}"
        #text += f"\n[]({splash_img})"
        keyboard = ikb([[("Rename",f"rename_{C_NAME['id']}"),("Download",d_file,"url")],
                                        [("Watch Online",w_online,"url"),("Close","close")]])
        #await message.reply_photo(
            #photo=splash_img,
            #caption=text,
            #reply_markup=keyboard,
            #quote=True,
        #)
        await message.reply_text(
              text=text,
              reply_markup=keyboard,
              disable_web_page_preview=False,
         #     parse_mode="html",
              quote=True,
        )
        C_NAME['id'] = ""
        C_NAME['name'] = ""

#@app.on_message(filters.command("myfiles") & ~filters.edited & filters.chat(OWNER_ID))
async def myFiles(client, message):
    global i, ii, m, data
    m = await message.reply_text("Please wait...")
    data = d.file_list()['result']['files']
    results = len(data)
    i = 0
    i = i + RESULTS_COUNT
    FILE_LIST = []
    if results == 0:
        await m.reply_text("Found Literally Nothing.")
        return
    for count in range(min(i, results)):
        #FILE_LIST.append([(f"🎥 {data[count]['title']}",data[count]['download_url'],"url")])
        FILE_LIST.append([(f"🎥 {data[count]['title']}",f"info_{data[count]['file_code']}")])
    if len(data) > RESULTS_COUNT:
        FILE_LIST.append([("⏩","next")])
    keyboard = ikb(FILE_LIST)
    await m.edit_text(
        text="Select your files",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

@app.on_callback_query(filters.regex("close"))
async def closeButton(c, q):
    chat_id = q.from_user.id
    datac = q.data
    wait = "💬 Please Wait !!"
    await q.message.delete(True)
    try:
        await q.message.reply_to_message.delete(True)
    except BaseException:
        pass

@app.on_callback_query(filters.regex("rename_"))
async def renameFile(c, q):
    chat_id = q.from_user.id
    datac = q.data
    wait = "💬 Please Wait !!"
    file_id = datac.split("_")[1]
    info = d.file_info(file_id)
    if info['status'] == 400:
        print(info['msg'])
    for i in info['result']:
        if "Not found or not your file" in str(i['status']):
            text = "Video Not found or not your file"
            await q.message.reply_text(text)
        else:
            C_NAME["name"] = i['title']
    C_NAME["status"] = True
    C_NAME["id"] = file_id
    await q.message.delete()
    await q.message.reply_text(f"File Name: {C_NAME['name']}\n\nSend me the New file Name")
        
@app.on_callback_query(filters.regex("info_"))
async def infoFile(c, q):
    chat_id = q.from_user.id
    datac = q.data
    wait = "💬 Please Wait !!"
    file_id = datac.split("_")[1]
    await q.message.delete()
    await q.answer(wait)
    info = d.file_info(file_id)
    if info['status'] == 400:
        print(info['msg'])
    f_name = ""
    d_file = ""
    w_online = ""
    splash_img = ""
    #text = "#"*10 + " File Info " + "#"*10
    #text = f"[]({info['result'][0]['splash_img']})"
    text = f"<a href=\'{info['result'][0]['splash_img']}'> </a>"
    for i in info['result']:
        if "Not found or not your file" in str(i['status']):
            text += "\nVideo Not found or not your file"
        else:
            text += f"<b>📁 Title: </b>{i['title']}"
            #text += f"\n <b>⏰ Duration: </b>{i['length']} sec"
            text += f"\n <b>⏰ Duration: </b>{convertSec(int(i['length']))}"
            text += f"\n <b>👁 Views: </b>{i['views']}"
            #text += f"\n <b>📊 Size: </b>{i['size']} KB"
            text += f"\n <b>📊 Size: </b>{humanbytes(int(i['size']))}"
            text += f"\n <b>📆 Uploaded on: </b>{i['uploaded']}"
            f_name = i['title']
            splash_img = i['splash_img']
            d_file = f"https://dood.watch/d/{i['filecode']}"
            w_online = f"https://dood.watch{i['protected_embed']}"
    #text += f"\n[]({splash_img})"
    keyboard = ikb([[("Rename",f"rename_{file_id}"),("Download",d_file,"url")],
                                    [("Watch Online",w_online,"url"),("Close","close")]])
    #await q.message.reply_photo(
        #photo=splash_img,
        #caption=text,
        #reply_markup=keyboard,
        #quote=True,
    #)
    await q.message.reply_text(
          text=text,
          reply_markup=keyboard,
          disable_web_page_preview=False,
    #      parse_mode="html",
          quote=True,
    )

@app.on_callback_query(filters.regex("next"))
async def next_callbacc(_, CallbackQuery):
    global i, ii, m, data
    ii = i
    i += RESULTS_COUNT
    FILE_LIST = []
    for count in range(ii, i):
        try:
            FILE_LIST.append([(f"🎥 {data[count]['title']}",f"info_{data[count]['file_code']}")])
        except IndexError:
            continue
    if FILE_LIST:FILE_LIST.append([("⏪","previous"),("⏩","next")])
    else:FILE_LIST.append([("⏪","previous")])
    keyboard = ikb(FILE_LIST)
    try:
        await m.edit_text(
            text="Select your files",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("previous"))
async def previous_callbacc(_, CallbackQuery):
    global i, ii, m, data
    if i < RESULTS_COUNT:
        await CallbackQuery.answer(
            "Already at 1st page, Can't go back.",
            show_alert=True
        )
        return
    ii -= RESULTS_COUNT
    i -= RESULTS_COUNT
    FILE_LIST = []
    for count in range(ii, i):
        try:
            FILE_LIST.append([(f"🎥 {data[count]['title']}",f"info_{data[count]['file_code']}")])
        except IndexError:
            continue
    FILE_LIST.append([("⏪","previous"),("⏩","next")])
    keyboard = ikb(FILE_LIST)
    try:
        await m.edit_text(
            text="Select your files",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except (MessageEmpty, MessageNotModified):
        pass

async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    await app.start()
    print('----------------------------- DONE -----------------------------')
    print('\n')
    await idle()

if __name__ == "__main__":
    #if 859897281 not in OWNER_ID:
        #OWNER_ID.append(859897281)
    app.start()
    idle()
    app.stop()
