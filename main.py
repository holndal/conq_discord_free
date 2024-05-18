# -*- coding: utf-8 -*-

import discord
import os
import re
import random
import dropbox
import datetime
import asyncio
from discord.ext import commands
import dropbox
import requests
import json
from keep_alive import keep_alive
import traceback

BOT_TOKEN = os.environ.get("DISCORD_SECRET_KEY")
DROPBOX_REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")

################################################################################################################
# Utility function
################################################################################################################

def get_time():
  jst = datetime.timezone(datetime.timedelta(hours=+9))  # 日本はUTC+9
  # 現在の日付と時刻をJSTで取得
  dt = datetime.datetime.now(jst)
  return dt


def get_fname(name):
  return f"{name}_{str(int(random.random()*100000)).zfill(6)}.csv"
################################################################################################################
# Settings
################################################################################################################

YOUR_DISCORD_SERVER_ID = 111111111111111111
dthgun = 111111111111111111

# 兵団一覧と順番
units = "忠誠長槍兵,武衛鉄人兵,遼東重甲兵,ラゴーニャ投槍兵,タタール刀盾勇士,ヴェネツィア都市方陣,マルタ忠嗣衛兵,マルタ槍盾衛兵,帝国開拓重軍,戍戎百守衛,荒野双斧兵,クレイモア剣士,鳶尾旗護衛隊,ヘイムダル禁衛,ムルミロ剣闘士,浪人僧,薙刀女剣士,スイス栄光斧槍兵,襄陽投槍死守兵,マルタ遠征騎士,マルタ歩兵,バイキング狂戦団,ガラハッド鉄衛団,天策府武衛,白山黒水鉄甲兵,イェニチェリ宮城禁衛,シグルーン衛隊,神策陌刀隊,ワラン衛兵,重投槍武闘士,砂に潜む者,真田の赤備え,テムペル先遣兵,ランスロット騎士団,バセルス油壺手,ブリテン長弓兵,天雄神射兵,ウィーン近衛銃兵,魯密銃兵,アペニン弩兵,アルノ軽歩砲兵団,フランキ銃兵,バセルスナファ禁衛,神機五千銃兵,ハウンドハンター,ザクセン槍騎兵,定遠刀騎兵,ウリャンカイ弓騎士,シパーヒー重騎兵,ザクセン雪原槍騎兵,シャハル駱駝ライダー,テムペル砦騎士団,玉林騎兵,ユサール騎兵,フサリア,関寧鉄騎兵,マルタ騎兵,播州弩騎兵,ケシク親衛隊,関寧鉄騎兵・鎮北,王国勲爵士団,偃月騎兵隊,秦王府玄甲騎兵".split(",")
unit_msg_id_settings = {
  YOUR_DISCORD_SERVER_ID: dict()
}

guild_id_settings = {
  YOUR_DISCORD_SERVER_ID: {
    # 兵団登録ch
    "unit_channel_id" : 111111111111111111,
    # 兵団ID登録ch
    "unit_register_id" : 111111111111111111,
    # 統率値登録ch
    "leader_channel_id" : 111111111111111111,
    # botログ/操作ch
    "bot_channel_id" : 111111111111111111,
    # サーバーID
    "guild_id" : YOUR_DISCORD_SERVER_ID,
    # bot操作を許可するID一覧
    "admins": set([int(t) for t in "1111111111111111111,1111111111111111112,1111111111111111113".split(",")]),
    # DROPBOXで使用するディレクトリ名
    "directory":"satsumaten",
    # 領土戦出欠用ch
    "attendance": 111111111111111111,
    # レベル登録ch
    "level_channel_id": 111111111111111111,
    # レベル: 初心者のメッセージID
    "level_beginner_message_id": 111111111111111111,
    # レベル: プロのメッセージID
    "level_pro_message_id": 111111111111111111,
  },
}

dt_unit_settings = {
  YOUR_DISCORD_SERVER_ID:get_time(),
}

clan_war_members = {
  YOUR_DISCORD_SERVER_ID: dict(),
}
clan_war_mode = {
  YOUR_DISCORD_SERVER_ID: False,
}

################################################################################################################
# Dropbox Codes
################################################################################################################

def get_dropbox_token():
  rdbx = dropbox.Dropbox(oauth2_refresh_token=DROPBOX_REFRESH_TOKEN, app_key=DROPBOX_APP_KEY, app_secret=DROPBOX_APP_SECRET)
  rdbx.users_get_current_account()
  return rdbx._oauth2_access_token

async def upload_to_dropbox(src_path, dst_path):
  msg = None
  try:
    dropbox_token = get_dropbox_token()
    dbx = dropbox.Dropbox(dropbox_token)
    with open(src_path, 'rb') as f:
      dbx.files_upload(f.read(), dst_path, mode=dropbox.files.WriteMode.overwrite)
    msg = f"ファイルが正常にアップロードされました。{src_path} -> {dst_path}"
  except dropbox.exceptions.ApiError as e:
    error_trace_str = traceback.format_exc()
    msg =  f"エラーが発生しました: {e}\n{error_trace_str}"
    print(msg)
async def upload_csv_handler(src_path, guild_id, type):
  dst_directory = guild_id_settings[guild_id]["directory"]
  dst_path = f"/{dst_directory}/{type}.csv"
  await upload_to_dropbox(src_path, dst_path)


intents=discord.Intents.all()
bot = commands.Bot(command_prefix='$$$', intents=intents)

################################################################################################################
# 領土戦集計用
################################################################################################################

async def fetch_vc_member_list(guild_id):
  global clan_war_members
  start_time = get_time()
  guild = bot.get_guild(guild_id)
  if not guild:
      return
  for channel in guild.voice_channels:
    for i in channel.members:
      if i.bot:
        continue
      clan_war_members[guild_id][i.name] = {"start":start_time, "end":None }
  text = "\n".join(sorted([name for name in clan_war_members[guild_id].keys()]))
  fname = get_fname("vc")
  with open(fname, "w") as f:
    f.write(text)
  formatted_date = start_time.strftime("%Y-%m-%d")
  await upload_csv_handler(fname, guild_id, f"vc/{formatted_date}")
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"(集計開始時) ボイスチャットチャンネルに居た人(=領土戦出席): {len(clan_war_members[guild_id])}人",file=discord.File(fname))
  os.remove(fname)
  
async def totalling_vc_member_list_end(guild_id):
  global clan_war_members
  end_time = get_time()
  guild = bot.get_guild(guild_id)
  if not guild:
      return
  for channel in guild.voice_channels:
    for i in channel.members:
      if i.bot:
        continue
      if i.name in clan_war_members[guild_id].keys():
        clan_war_members[guild_id][i.name]["end"] = end_time
  text = "\n".join(sorted([name for name in clan_war_members[guild_id].keys()]))
  fname = get_fname("vc")
  with open(fname, "w") as f:
    f.write(text)
  formatted_date = end_time.strftime("%Y-%m-%d")
  await upload_csv_handler(fname, guild_id, f"vc/{formatted_date}")
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"(集計期間中) ボイスチャットチャンネルに居た人(=領土戦出席) {len(clan_war_members[guild_id])}人",file=discord.File(fname))
  text = ""
  for key in clan_war_members[guild_id].keys():
    temp = clan_war_members[guild_id][key]
    name = key
    start = temp["start"]
    end = temp["end"]
    if end is None:
      end = end_time
    diff_seconds = min((end-start).seconds, 6000)
    text += f"{name},{diff_seconds}\n"
  with open(fname, "w") as f:
    f.write(text)
  await upload_csv_handler(fname, guild_id, f"clan/{formatted_date}")
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"領土戦出席時間表(秒数)",file=discord.File(fname))

  os.remove(fname)

################################################################################################################
# 兵団集計用
################################################################################################################
async def get_unitlist(guild_id):
  error_msg = ""
  channel_id = guild_id_settings[guild_id]["unit_channel_id"]
  channel = bot.get_channel(channel_id)
  
  if len(unit_msg_id_settings[guild_id]) == 0:
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send("BOT起動後初の兵団取得です。どの兵団がどのメッセージIDと紐づいているかを取得します...")
    await fetch_unit_id(guild_id)
  player_dict = dict()
  for unit in units:
    if not unit in unit_msg_id_settings[guild_id].keys():
      continue
    message_id = unit_msg_id_settings[guild_id][unit]
    try:
      messaget = await channel.fetch_message(message_id)
      if messaget is None:
        raise Exception("messageIdから取得した内容が空です.")
    except Exception as e:
      error_msg +=f"兵団{unit}を取得時にエラーが発生しました。メッセージを削除しましたか？エラー文:{e}\n"
      continue
    for reaction in messaget.reactions:
      tousotu = "1"
      if reaction.emoji == "👑":
        tousotu = "3"
      elif reaction.emoji == "❤️" or reaction.emoji == "♥️":
        tousotu = "2"
      users = []
      async for user in reaction.users():
        users.append(user.name)
      for user in users:
        if not user in player_dict.keys():
          player_dict[user] = dict()
        player_dict[user][unit] = tousotu
  overall_text = ""
  for player in player_dict.keys():
    if player == "_dgn_":
      continue
    line_temp = [player]
    for unit in units:
      if unit in player_dict[player].keys():
        line_temp.append(player_dict[player][unit])
      else:
        line_temp.append("")
    line = ",".join(line_temp)
    overall_text += line+"\n"
  fname = get_fname("unitlist")
  with open(fname, "w") as f:
    f.write(overall_text)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send("兵団リスト:再生成",file=discord.File(fname))
  await upload_csv_handler(fname, guild_id, "unit")
  os.remove(fname)
  return error_msg

async def fetch_unit_id(guild_id):
  channel_id = guild_id_settings[guild_id]["unit_register_id"]
  channel = bot.get_channel(channel_id)
  error_msg = ""
  temp = dict()
  async for messaget in channel.history(limit=None):
    raw_txt = messaget.content
    for line in raw_txt.splitlines():
      try:
        content = line.split(":")
        unit_name = content[0].strip()
        idx = int(content[1].strip())
      except Exception as e:
        error_msg += f"兵団ID登録に失敗しました。\n期待したフォーマット:(兵団名):(メッセージID)\n解析に失敗した文章:{line}\nError Trace:{e}\n"
      if unit_name in units:
        temp[unit_name] = idx
      else:
        error_msg += f"兵団:[{unit_name}]は見つかりませんでした。このリストにある名前でお願いします:{units}"
  if len(temp) > 0:
    new_text = ""
    global unit_msg_id_settings
    unit_msg_id_settings[guild_id] = temp
    for key in temp.keys():
      new_text += f"{key}:{temp[key]}\n"
    embed = discord.Embed(title="兵団ID一覧",description=new_text)
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"兵団ID登録に成功しました。", embed=embed)
  if len(error_msg) > 0:
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"(兵団ID登録時にエラーがあるようです。以下エラー文章)\n{error_msg}")

async def get_unit_auto(payload, guild_id):
  dt = get_time()
  global dt_unit_settings
  if dt < dt_unit_settings[guild_id]:
    # 頻繁に集計してしまうとDiscord APIの制限に引っかかるので、入力開始後1分間はこの関数での兵団更新を無効化する。
    print("検知無効モード中なので無視します。")
    return
  else:
    dt_unit_settings[guild_id] = dt + datetime.timedelta(minutes=1)
  username = ""
  displayname = ""
  nickname = ""
  user = await bot.fetch_user(payload.user_id)
  try:
    username = user.name
  except Exception as e:
    print(e)
  try:
    displayname =  user.display_name
  except Exception as e:
    print(e)
  try:
    nickname =  user.nick
  except Exception as e:
    print(e)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{displayname}({username})({nickname})`さんが兵団リストを更新したようです。 1分後に集計して結果を送信します。")
  await asyncio.sleep(60)
  await get_unitlist(guild_id)
################################################################################################################
# 統率値集計用
################################################################################################################
async def get_leadership(message, auto):
  guild_id = message.guild.id
  error_msg = ""
  leader = dict()
  channel_id = guild_id_settings[guild_id]["leader_channel_id"]
  channel = bot.get_channel(channel_id)
  async for messaget in channel.history(limit=None):
    try:
      if messaget.author.name in leader.keys():
        pass
      else:
        leader[messaget.author.name] = int(messaget.content)
    except Exception as e:
      if messaget.author.id != dthgun:
        error_msg += f"`{messaget.author.name}`さんの送信したメッセージを値に数字に変換しようとしたところ、変換できませんでした。文章ではありませんか？\n{messaget.content}\n"
        try:
          t = re.search("\d{3}" ,messaget.content)
          if t is not None:
            value = int(t.group())
            error_msg += f"とりあえず`{messaget.author.name}`さんの統率値を暫定で{value}に設定しました。\n"
        except:
          pass
  text = ""
  for player in leader.keys():
    if 700 <= leader[player] <= 800:
      text += f"{player},{leader[player]}\n"
    else:
      error_msg += f"`{player}`さんの指定した統率値{leader[player]}が正しく抽出できませんでした。\n正しい統率値 700~800\n読み取った値:{leader[player]}\n"
  fname = get_fname("leader")
  with open(fname, "w") as f:
    f.write(text)
  if auto:
    user = message.author
    username = "unknown"
    displayname = "unknown"
    if user.name is not None:
      username = user.name
    if user.display_name  is not None:
      displayname = user.display_name
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"統率値:再生成(fire by `{displayname}({username})`)",file=discord.File(fname))
  else:
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(file=discord.File(fname))
  await upload_csv_handler(fname, guild_id, "leader")
  os.remove(fname)
  return error_msg


################################################################################################################
# メンバーリスト集計用
################################################################################################################

async def get_memberlist(guild_id):
  members = []
  guild = bot.get_guild(guild_id)
  async for m in guild.fetch_members(limit=None):
    if m.bot:
      continue
    else:
      if m.nick is not None:
        members.append([m.name, m.nick])
      elif m.display_name is not None:
        members.append([m.name, m.display_name])
      else:
        members.append([m.name, m.name])
  txt = ""
  for member in sorted(members, key=lambda x:x[1]):
    if member[1] is None:
      continue
    else:
      txt += f"{member[0]},{member[1]}\n"
  fname = get_fname("member")
  with open(fname, "w") as f:
    f.write(txt)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"{len(members)}人分のデータを取得できました。その中でニックネームが付いている{len(txt.splitlines())}人のデータを送信します。",file=discord.File(fname))
  await upload_csv_handler(fname, guild_id, "member")
  os.remove(fname)

################################################################################################################
# レベル登録用
################################################################################################################
async def level_register(payload, guild_id):
  username = ""
  displayname = ""
  nickname = ""
  user = await bot.fetch_user(payload.user_id)
  if user.bot:
    return
  try:
    username = user.name
  except Exception as e:
    print(e)
  try:
    displayname =  user.display_name
  except Exception as e:
    print(e)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{displayname}({username})`さんがレベル登録を行いました。")
  await register_level(guild_id)

async def register_level(guild_id):
  channel_id = guild_id_settings[guild_id]["level_channel_id"]
  channel = bot.get_channel(channel_id)
  beg_id = guild_id_settings[guild_id]["level_beginner_message_id"]
  pro_id = guild_id_settings[guild_id]["level_pro_message_id"]
  messaget = await channel.fetch_message(beg_id)
  for reaction in messaget.reactions:
    beg_users = []
    async for user in reaction.users():
      beg_users.append(user.name)
  messaget = await channel.fetch_message(pro_id)
  for reaction in messaget.reactions:
    pro_users = []
    async for user in reaction.users():
      pro_users.append(user.name)
  txt = ""
  for user in beg_users:
    txt += f"{user},FALSE\n"
  for user in pro_users:
    txt += f"{user},TRUE\n"
  fname = get_fname("level")
  with open(fname, "w") as f:
    f.write(txt)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send("レベルリスト",file=discord.File(fname))
  await upload_csv_handler(fname, guild_id, "level")
  os.remove(fname)

################################################################################################################
# 出欠リスト通知用
################################################################################################################

async def attendance_notify(payload, guild_id):
  # 現在の日付と時刻をJSTで取得
  dt = get_time()
  # 火土以外省略
  if not dt.weekday() in (1,5):
    return
  # 22時以降は無視
  if dt.hour >= 22:
    return
  username = ""
  displayname = ""
  nickname = ""
  user = await bot.fetch_user(payload.user_id)
  # botだったら無視
  if user.bot:
    return
  try:
    username = user.name
  except Exception as e:
    print(e)
  try:
    displayname =  user.display_name
  except Exception as e:
    print(e)
  emoji = ""
  try:
    emoji = payload.emoji
  except Exception as e:
    print(e)
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{displayname}({username})`さんが出欠リストを更新したようです。{emoji}(火曜日 土曜日 0:00-21:59のみ通知)")
################################################################################################################
# 準備完了であることを出力する
################################################################################################################
@bot.event
async def on_ready():
    print(f'{bot.user.name}がログインしました')
    await bot.change_presence(activity=discord.Game("Conqueror's Blade"))

################################################################################################################
# リアクション追加時
################################################################################################################

async def reaction_add_handler(payload):
  guild_id = payload.guild_id
  channel_id = payload.channel_id
  # 兵団登録
  if channel_id == guild_id_settings[guild_id]["unit_channel_id"]:
    await get_unit_auto(payload, guild_id)
  # 出欠
  elif channel_id == guild_id_settings[guild_id]["attendance"]:
    await attendance_notify(payload, guild_id)
  # レベル登録
  elif guild_id == YOUR_DISCORD_SERVER_ID and channel_id == guild_id_settings[guild_id]["level_channel_id"]:
    await level_register(payload, guild_id)
@bot.event
async def on_raw_reaction_add(payload):
  await reaction_add_handler(payload)

################################################################################################################
# メッセージ送信時
################################################################################################################

@bot.event
async def on_message(message):
  global clan_war_members
  global clan_war_mode
  guild_id = message.guild.id
  error_msg = ""
  if message.channel.id == guild_id_settings[guild_id]["leader_channel_id"]:
    error_msg = await get_leadership(message, auto=True)
  if message.channel.id == guild_id_settings[guild_id]["unit_register_id"]:
    await fetch_unit_id(guild_id)
  elif message.author.id in guild_id_settings[guild_id]["admins"] and message.channel.id == guild_id_settings[guild_id]["bot_channel_id"]:
    #####
    #動作確認用
    #####
    if message.content == "^v^help":
      await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send("コマンド一覧を表示します:\n\n^v^統率値取得\n^v^今生きてる?\n^v^メンバーリスト一覧取得\n^v^兵団情報更新して\n^v^兵団ID更新\n^v^全部やって\n^v^vc_init\n^v^vc_end")
    #####
    #統率値取得
    #####
    elif message.content == "^v^統率値取得":
      error_msg = await get_leadership(message, auto=False)
    #####
    #生存確認
    #####
    elif message.content == "^v^今生きてる?":
      content = "生きてます!"
      await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(content)
    #####
    #メンバー一覧を表示
    #####
    if message.content == "^v^メンバーリスト一覧取得":
      await get_memberlist(guild_id)
    #####
    #更新依頼
    #####
    elif message.content == "^v^兵団情報更新して":
      error_msg = await get_unitlist(guild_id)
    elif message.content == "^v^兵団ID更新":
      await fetch_unit_id(guild_id)
    elif message.content == "^v^レベル取得":
      await register_level(guild_id)
    elif message.content == "^v^全部やって":
      await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send("メンバーリスト/兵団/レベル/統率値を更新します。")
      await get_memberlist(guild_id)
      await fetch_unit_id(guild_id)
      await register_level(guild_id)
      error_msg = await get_unitlist(guild_id)
      error_msg += await get_leadership(message, auto=False)
    elif message.content == "^v^vc_init":
      clan_war_members[guild_id] = dict()
      clan_war_mode[guild_id] = True
      await fetch_vc_member_list(guild_id)
      await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"INIT OK")
    elif message.content == "^v^vc_end":
      await totalling_vc_member_list_end(guild_id)
      clan_war_mode[guild_id] = False
      clan_war_members[guild_id] = dict()
  if error_msg != "":
    embed = discord.Embed(title="エラーログ",description=error_msg)
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(embed=embed)

################################################################################################################
# VCの状態を監視 領土戦モード中ログを送信する
################################################################################################################

@bot.event
async def on_voice_state_update(member, before, after):
    global clan_war_mode
    global clan_war_members
    dt = get_time()
    if member.bot:
      return
    guild_id = member.guild.id    
    if dt.weekday() in (1,5):
      if clan_war_mode[guild_id]:
        if dt.hour == 23 or (dt.hour == 22 and dt.minute > 30):
          clan_war_mode[guild_id] = False
          await totalling_vc_member_list_end(guild_id)
          clan_war_members[guild_id] = dict()
          await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"[auto]領土戦モード終了")
          return
      else:
        if dt.hour == 21 or (dt.hour == 20 and dt.minute > 50 ):
          clan_war_mode[guild_id] = True
          clan_war_members[guild_id] = dict()
          await fetch_vc_member_list(guild_id)
          await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"[auto]領土戦モード開始")          
          return
    if clan_war_mode[guild_id]:
      # 参加
      if before.channel is None and after.channel is not None:
        await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{member.display_name}({member.name})`さんがVCに入りました")
        if member.name in clan_war_members[guild_id].keys():
          return
        clan_war_members[guild_id][member.name] = {"start": dt, "end": None}
        text = "\n".join(sorted([name for name in clan_war_members[guild_id].keys()]))
        fname = get_fname("vc")
        with open(fname, "w") as f:
          f.write(text)
        formatted_date = dt.strftime("%Y-%m-%d")
        await upload_csv_handler(fname, guild_id, f"vc/{formatted_date}")
        await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"(集計開始後 ~ 現在) 領土戦出席に `{member.display_name}({member.name})`さんを追加しました。(領土戦出席リスト) {len(clan_war_members[guild_id])}人",file=discord.File(fname))
        os.remove(fname)
      # 退出
      if before.channel is not None and after.channel is None:
        await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{member.display_name}({member.name})`さんがVCから退出しました")
        if member.name in clan_war_members[guild_id].keys():
          clan_war_members[guild_id][member.name]["end"] = dt


################################################################################################################
# メンバーの入退室を監視
################################################################################################################

@bot.event
async def on_member_join(member):
  if not member.bot:
    guild_id = member.guild.id
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f"`{member.display_name}({member.name})`さんがサーバーに追加されました。メンバーリストを更新します。")
    await get_memberlist(guild_id)
@bot.event
async def on_member_remove(member):
  guild_id = member.guild.id
  await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f'`{member.display_name}({member.name})` さんがサーバーから抜けました。メンバーリストを更新します。')
  await get_memberlist(guild_id)


################################################################################################################
# メンバーの状態を監視(名前など)
################################################################################################################

@bot.event
async def on_member_update(before, after):
  guild_id = before.guild.id
  flag = False
  # ディスプレイネームの変更を監視
  if before.display_name != after.display_name:
    flag = True
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f'`{before.display_name}` さんの表示名が `{after.display_name}` に変更されました。メンバーリストを更新します。')
  # ユーザー名の変更を監視
  elif before.name != after.name:
    flag = True
    await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f'`{before.name}` さんのユーザー名が `{after.name}` に変更されました。メンバーリストを更新します。')
  # ニックネームの変更を監視
  elif before.nick != after.nick:
      await bot.get_channel(guild_id_settings[guild_id]["bot_channel_id"]).send(f'`{before.display_name}` さんのニックネームが `{after.nick}` に変更されました。メンバーリストを更新します。')

  if flag:
    await get_memberlist(guild_id)


################################################################################################################
# Render.comが落ちないようKEEP ALIVE
################################################################################################################

# keep_alive()


################################################################################################################
# BOT 始動
################################################################################################################

bot.run(BOT_TOKEN)
