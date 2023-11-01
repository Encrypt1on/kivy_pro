from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import mainthread
from kivy.core.clipboard import Clipboard as Cb
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
import threading
import socket
import websocket
import threading
import time
import json
import ast


def decrypt(obj, i=0):
    if isinstance(obj, dict):
        decrypted_obj = {}
        if not i:
            i = obj.get("lfm5", 0)
        for key, value in obj.items():
            if not key.startswith("lfm"):
                decrypted_key = decrypt(key, i)
                decrypted_value = decrypt(value, i)
                decrypted_obj[decrypted_key] = decrypted_value
            else:
                decrypted_obj[key] = value
        return decrypted_obj
    elif isinstance(obj, list):
        return [decrypt(x, i) for x in obj]
    elif isinstance(obj, str) and i:
        res = ""
        for c in obj:
            num = ord(c)
            if (num - i) not in range(0x110000):
                res += c
            else:
                res += chr(num - i)
        if res and res[-1] == " " and res[:-1].isdigit():
            res = int(res[:-1])
        return res
    else:
        return obj


def decrypt_json(encrypted_json, offset):
    data = json.loads(encrypted_json[2:])
    decrypted_payload = decrypt(data[1], offset)
    return [data[0], decrypted_payload, *data[2:]]


def main_d(encrypted_json):
    offset = 143
    if not ('lfm1' in encrypted_json):
        offset = 0
    lines = str(decrypt_json(encrypted_json, offset))
    return (lines)


def encrypt(obj, i=0):
    if isinstance(obj, dict):
        decrypted_obj = {}
        if not i:
            i = obj.get("lfm5", 0)
        for key, value in obj.items():
            if not key.startswith("lfm"):
                decrypted_key = encrypt(key, i)
                decrypted_value = encrypt(value, i)
                decrypted_obj[decrypted_key] = decrypted_value
            else:
                decrypted_obj[key] = value
        return decrypted_obj
    elif isinstance(obj, list):
        return [encrypt(x, i) for x in obj]
    elif type(obj) == int:
        return encrypt(str(obj), i) + " "
    elif isinstance(obj, str) and i:
        res = ""
        for c in obj:
            num = ord(c)
            if (num + i) not in range(0x110000):
                res += c
            else:
                res += chr(num + i)
        return res
    else:
        return obj


def encrypt_json(decrypted_json, offset=0):
    encrypted_payload = encrypt(decrypted_json[1], offset)
    print(decrypted_json[2:])
    return "42" + json.dumps([decrypted_json[0], encrypted_payload, *decrypted_json[2:]], separators=(",", ":"),
                             ensure_ascii=False)


def main_e(decrypted_json):
    if not ('lfm1' in decrypted_json):
        offset = 0
    lines = encrypt_json(eval(decrypted_json), offset)
    return lines


ws = None
sorted_data = ''
clans_package = ''
clans_package1 = ''
clan_value = '1'
status = 'by скиллер'
info_about_acc = ''
pack_status = ''
def on_message(ws, message):
    print(message)
    global clans_package


    if "ResultTop" in message and not ("Classic" in message):
        global sorted_data
        # Decode and sort the "ResultTop" data
        dec_top = main_d(message)
        sorted_data = sort_top(dec_top)
        print(sorted_data)

    global pack_status
    if '42["NewMessageRegionChat' in message:
        a = (sort_chat(main_d(message)))
        print(a)
    if message[:22] == '42["getClansTopResult"':
        global clans_package
        global clans_package1
        clans_package = json.loads(message[23:-4])
        clans_package1 = message
        pack_status = 'ПАКЕТ ПРИШЕЛ.'
    global status
    if '42["ResultLogin",null,null' in message:
        status = "Неверные данные для входа. Войдите в аккаунт"
    global clan_value
    if '42["ResultLogin",[{"login":' in message:
        global info_about_acc
        status = ''
        data = (message[message.find(',[') + 1:message.rfind('],') + 1])
        parsed_data = json.loads(data)

        login_value = parsed_data[0]['login']
        mmr_value = parsed_data[0]['mmr']
        mmrOld_value = parsed_data[0]['mmrOld']
        Friends_value = parsed_data[0]['Friends']
        likeHave_value = parsed_data[0]['likeHave']
        countWin_value = parsed_data[0]['countWin']
        countLose_value = parsed_data[0]['countLose']
        clan_value = parsed_data[0]['clan']
        oldNick_value = parsed_data[0]['oldNick']
        money_value = parsed_data[0]['money']
        mail_value = parsed_data[0]['mail']
        mailGoogle_value = parsed_data[0]['mailGoogle']
        info_about_acc = f'Ник: {login_value}\nКлан: {clan_value}\nМонет: {money_value}\nПохвал: {likeHave_value}\nMMR: {mmr_value}\nПрошлый MMR: {mmrOld_value}\nКол-во побед: {countWin_value}\nКол-во поражений: {countLose_value}\nПрошлые ники: {oldNick_value}\nДрузья: {Friends_value}\nПочта: {mail_value}\nПочта googl: {mailGoogle_value}'
        print(info_about_acc)
    if '42["ResultGetMyClan"' in message:
        check_my_clan(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    global area, sorted_data, clans_package, clans_package1, clan_value, status, pack_status, login, password, print_clans, clan_info_str, info_about_acc
    info_about_acc = ''
    area = ''
    sorted_data = ''
    clans_package = ''
    clans_package1 = ''
    clan_value = '1'
    status = 'by скиллер'
    pack_status = ''
    print_clans = ''
    clan_info_str = ''
    print(close_msg)

def send_packet_2(ws):
    while True:
        message = "2"
        ws.send(message)
        time.sleep(5)

def on_open(ws):
    global login
    global password
    message = main_e("['Login', {'me': True, 'm1': '08:00:27:F8:24:FA', 'password': '" + str(
        password) + "', 'color': False, 'lfm5': 159, 'steamId': '', 'm2': '', 'o': '2068136186', 'p1': '21.29.5.2', 'i': '5e5988e94be148f4 ! com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME ! null ! http://www.google.com http://www.google.co.uk ! QKQ1.190825.002 ! ASUS_Z01QD ! 8e94be148f45e598', 'login': '" + str(
        login) + "', 'p2': 'FE80::A00:27FF:FE29:E349', 'version': '159.0 '}]")
    ws.send(message)

    # Start a thread to send packet "2" every 5 seconds
    packet2_thread = threading.Thread(target=send_packet_2, args=(ws,))
    packet2_thread.daemon = True
    packet2_thread.start()


def connect_websocket():
    global ws
    ws_url = "ws://mafiaonline.jcloud.kz/socket.io/?EIO=3&transport=websocket"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open

    # Create a thread for the WebSocket connection
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()


def sort_chat(message):
    packet = ast.literal_eval(message)

    mmr = packet[1]['MMR']
    clan = '(' + packet[1]['clan'] + ')'
    nickname = packet[1]['author']
    message_text = packet[1]['message']
    color_nick = packet[1]['colorNick']
    party_name = packet[1]['partyName']

    formatted_message = f"{clan} {nickname}: {message_text}"
    return formatted_message

print_clans = ''
def get_area(parsed_data, area1):
    global print_clans
    print_clans = ''
    area_lower = area1.lower()
    print(area_lower)
    try:
        for clan in parsed_data:
            registr = clan.get("RegistrateOnTerritory", "")
            if str(registr).lower() == area_lower:
                reg = str(registr)
                name = clan.get("Name", "")
                honor = clan.get("Honor", 0)
                print_clans += f"{name} | Кол-во славы: {honor}\n"

        print(print_clans)
        if print_clans == '':
            print_clans = "Ни 1 клан еще не кинул заявку на этот район"
            reg = "Ошибка"

        ch = 0

    except:
        pass
clan_info_str = ''
def check_my_clan(clan_packet):
    global clan_info_str
    clan_packet = json.loads(clan_packet[2:])
    clan_name = clan_packet[2]["Name"]
    leader_name = clan_packet[2]["Leader"]
    level = clan_packet[2]["Lvl"]
    honor = clan_packet[2]["Honor"]
    num_players = clan_packet[2]["NumberPlayers"]
    territory = clan_packet[2]["Territory"]
    registrate_on_territory = clan_packet[2]["RegistrateOnTerritory"]

    members = clan_packet[3]
    member_info = []

    for i, member in enumerate(members, 1):
        nick = member.get("Nick", "нет")
        honor_for_clan = member.get("HonorForClan", "нет")
        mmr = member.get("mmr", "нет")
        is_online = "да" if member.get("isOnline", False) else "нет"

        member_info.append(f"{i}. {nick} | Количество славы: {honor_for_clan} | ММР: {mmr} | Онлайн: {is_online}")
    clan_info_str = (
        f"Название клана: {clan_name}\n"
        f"Лидер клана: {leader_name}\n"
        f"Уровень: {level}\n"
        f"Количество славы: {honor}\n"
        f"Количество игроков: {num_players}\n"
        f"Район: {territory}\n"
        f"Заявка на: {registrate_on_territory}\n"
        "Участники клана:\n" + "\n".join(member_info)
    )
    print(clan_info_str)
def get_clan_info(parsed_data, clann):
    print(clann)
    for clan in parsed_data:
        name = clan.get("Name", "")
        try:
            if str(name) == clann:
               registr = clan.get("RegistrateOnTerritory", "")
               honor = clan.get("Honor", 0)
               honor_area = clan.get("HonorEarnedInTerritory", 0)
               max_player = clan.get("MaxPlayers", 0)
               mainer = clan.get("Leader", "")
               num_players = clan.get("NumberPlayers", "")
               clan_lvl = clan.get("Lvl", "")
               print(f"Регистрация на район: {registr} (славы у клана: {honor})")
               print("--------------")
               clan1 = f"{str(name)}\nУровень: {clan_lvl}\nГлава: {mainer}\nКол-во участников: {num_players}/{max_player}\nКол-во славы: {str(honor)}\nСлавы на районе: {str(honor_area)}\nЗаявка на: {str(registr)}"

            return clan1
        except:
            pass

def sort_top(lines):
    lines = str(lines)
    lines = lines[lines.find("[{") + 1:lines.rfind(",") - 1]
    lines = ast.literal_eval(lines)
    sorted_lines = sorted(lines, key=lambda x: x['mmr'], reverse=True)
    for item in sorted_lines:
        del item['lfm1']
        del item['lfm2']
        del item['lfm3']
        del item['lfm4']
        del item['lfm5']
    count = 0
    mes = ''
    for index, item in enumerate(sorted_lines):
        count += 1
        mes += f"{count}. {item['login']} — MMR: {item['mmr']}\n"
        if count == 20:
            return mes


login = ''
password = ''

class ZeroWindow(Screen):
    global status
    data_label = StringProperty(status)
    fl = False
    status1 = status
    def enter(self):
        global login
        global password

        print("Вход")
        if login == '' and password == '':
            login = 'trxsh29'
            password = ' '
        connect_websocket()

        global status
        global clan_value
        while  "by скиллер" in status:
            if "Неверные" in status:
                self.ids.enter.text = status
                status = 'by скиллер'
                self.fl = False
                break
            if  status == '':
                self.ids.enter.text = status
                print(clan_value)
                self.fl = True
                break

        return status
    def inputt(self):
        global login
        global password
        login = self.ids.Login.text
        password = self.ids.Pass.text
        print(login, password)

class FirstWindow(Screen):
    data_label = StringProperty("Вы не вошли в аккаунт")
    global clan_value
    clan_value1 = clan_value
    global status, info_about_acc
    status1 = status
    def enter(self):
        global login
        global password

        print("Вход")
        if login == '' and password == '':
            login = 'trxsh29'
            password = ' '
        connect_websocket()


        time.sleep(3)
        self.ids.enter.text = status
    def inputt(self):
        global login
        global password
        login = self.ids.Login.text
        password = self.ids.Pass.text
        print(login, password)

    def get_top(self):
        global ws
        ws.send('42["Top"]')
        global sorted_data
        while sorted_data == '':
            pass
        if sorted_data != '':
            # Полученные данные не пусты, обновляем свойство ta во втором окне
            self.manager.get_screen('second').ta = sorted_data
            sorted_data = ''
    def send_package(self):
        ws.send('42["getClansTop"]')
    global clan_info_str
    clan_info_str1 = clan_info_str
    def send_get_clan(self):
        global ws
        global clan_value
        if clan_value != '':
            ws.send('42["GetMyClan","' + clan_value +'"]')
            while "Название клана" not in clan_info_str:
                self.clan_info_str1 = clan_info_str
            self.clan_info_str1 = clan_info_str
    def wait(self):
        pass
    def reset_all(self):
        global area, sorted_data, clans_package, clans_package1, clan_value, status, pack_status, login, password, print_clans, clan_info_str, ws, info_about_acc
        info_about_acc = ''
        area = ''
        sorted_data = ''
        clans_package = ''
        clans_package1 = ''
        clan_value = '1'
        status = 'by скиллер'
        pack_status = ''
        print_clans = ''
        clan_info_str = ''
        ws.close()
        time.sleep(5)
class SecondWindow(Screen):
    ta = StringProperty(sorted_data)

class WindowManager(ScreenManager):
    pass

area = ''

class ThirdWindow(Screen):
    global area
    global clans_package
    global pack_status
    st = StringProperty("")
    status_pack = pack_status
    pack_status1 = StringProperty(pack_status)
    def bedn_area(self):
        area = 'Бедный район'
        get_area(clans_package, area)

    def cat_area(self):
        area = 'Кошачий район'
    def prom_area(self):
        area = 'Промышленный район'
        get_area(clans_package, area)
    def japan_area(self):
        area = 'Японский район'
        get_area(clans_package, area)
    def selsk_area(self):
        area = 'Сельский район'
        get_area(clans_package, area)
    def casino_area(self):
        area = 'Район казино'
        get_area(clans_package, area)
    def vamp_area(self):
        area = 'Район вампира'
        get_area(clans_package, area)
    def port_area(self):
        area = 'Портовый район'
        get_area(clans_package, area)
    def center_area(self):
        area = 'Центральный район'
        get_area(clans_package, area)
    def elite_area(self):
        area = 'Элитный район'
        get_area(clans_package, area)
    def voen_area(self):
        area = 'Военный район'
        get_area(clans_package, area)
    def wait(self):
        if self.status_pack == '':
            self.st = 'Пакет еще не пришел'
        while self.status_pack == '':
            self.st = 'Пакет еще не пришел'
            self.status_pack = pack_status
        else:
            self.st = 'Пакет пришел. Можете продолжать пользоваться программой'





class FourthWindow(Screen):
    global print_clans
    clans = StringProperty(print_clans)
    def set_clans(self):
        global print_clans
        while print_clans == '':
            pass
        self.manager.get_screen('result_area').clans = print_clans
        print(print_clans)


class ClanWindow(Screen):
    c = ''
    clan12 = StringProperty("")
    info = '????'
    def inputt(self):
        self.clan = self.ids.clan_name.text
    def find_clan(self):
        global clans_package1
        self.index = str(clans_package1[23:-4]).find(self.clan)
        if self.index == -1:
            self.info = "Клан не найден. Учтите, что ввод чувствителен к регистру"
        else:
            try:
                self.c = json.loads('[' + clans_package1[23:-4][self.index-9:])
            except:
                print('except')
                pass
            self.info = get_clan_info(self.c,self.clan)
        print(self.info)
        if self.info == None:
            self.info = "Клан не найден. Учтите, что ввод чувствителен к регистру"
        self.manager.get_screen('find_clan').clan12 = self.info


class InviteWindow(Screen):
    global ws
    stat1 = StringProperty("Выберите на какой район отправить заявку")
    def bedn_area(self):
        self.area = 'Бедный район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def cat_area(self):
        self.area = 'Кошачий район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def prom_area(self):
        self.area = 'Промышленный район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def japan_area(self):
        self.area = 'Японский район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def selsk_area(self):
        self.area = 'Сельский район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def casino_area(self):
        self.area = 'Район казино'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def vamp_area(self):
        self.area = 'Район вампира'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def port_area(self):
        self.area = 'Портовый район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def center_area(self):
        self.area = 'Центральный район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def elite_area(self):
        self.area = 'Элитный район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"
    def voen_area(self):
        self.area = 'Военный район'
        ws.send('42["registerClanToWar","' + self.area + '"]')
        self.manager.get_screen('invite_to_area').stat1 = f"Заявка на {self.area} отправлена"

class ClanInfoWindow(Screen):
    global clan_info_str, clan_value
    text1 = StringProperty('')
    def set_text(self):
        global clan_info_str
        print(clan_info_str)
        if clan_value == '':
            self.manager.get_screen('info_about_clan').text1 = "У вас нет клана"
        else:
            self.manager.get_screen('info_about_clan').text1 = str(clan_info_str)
class AccInfoWindow(Screen):
    global info_about_acc
    info12 = StringProperty(str(info_about_acc))
    def set_info(self):
        self.info12 = info_about_acc
class Ban1Window(Screen):
    pass
class Ban2Window(Screen):
    pass
class Ban3Window(Screen):
    def ban(self):
        global ws
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.close()
class NakrutWindow(Screen):
    s12 = StringProperty('ПЕРЕД НАЖАТИЕМ КНОПКИ УБЕДИТЕСЬ, ЧТО ВЫ ЗА НЕДЕЛЮ НЕ ВЫПОЛНИЛИ НИ 1 ЗАДАНИЯ, ИНАЧЕ АККАУНТ БУДЕТ ЗАБЛОКИРОВАН. ПОСЛЕ НАКРУТА ЗАДАНИЯ ТОЖЕ ЗАПРЕЩЕНО ВЫПОЛНЯТЬ НЕДЕЛЮ!!!!')
    def nakrut(self):
        global ws
        self.s12 = 'ВЫ НАКРУТИЛИ!!!!!'
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)
        ws.send('42["RewardTask",{"lfm5":129,"ÓæøâóåÕúñæ":"Money","ÓæøâóåÄðöïõ":"´± ","ïâîæ":"ġÂåîêï"}]')
        time.sleep(0.1)


        time.sleep(0.1)
kv = Builder.load_string('''
#:kivy 2.2.1
#:import Factory kivy.factory.Factory
<ZeroWindow>:
    orientation: "vertical"
	size_hint: (0.95, 0.95)
	pos_hint: {"center_x": 0.5, "center_y":0.5}
	BoxLayout:
	    orientation: "vertical"
        Label:
            id: enter
            halign: 'center'
            valign: 'middle'
            font_size: "15sp"
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 15
            text: root.data_label
            markup: True
            on_ref_press: root.linki()

        TextInput:
            id: Login
            multiline: False
            padding_y: (5,5)
            size_hint: (1, 0.5)
            on_text: root.inputt()

        TextInput:
            id: Pass
            multiline: False
            padding_y: (5,5)
            size_hint: (1, 0.5)
            on_text: root.inputt()
        Button:
            text: "ВХОД"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press: root.enter()
            on_release:
                if root.fl == True:app.root.current = 'first'


<FirstWindow>:
    orientation: "vertical"
	size_hint: (0.95, 0.95)
	pos_hint: {"center_x": 0.5, "center_y":0.5}
	BoxLayout:
	    orientation: "vertical"
        Label:
            id: enter
            halign: 'center'
            valign: 'middle'
            font_size: "15sp"
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 15

            markup: True
            on_ref_press: root.linki()

        Button:
            text: "ИНФОРМАЦИЯ ОБ АККАУНТЕ"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_release: app.root.current = 'info_about_account'
        Button:
            text: "ТОП"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press: root.get_top()
            on_release: app.root.current = 'second'
        Button:
            text: "ПОСМОТРЕТЬ ЗАЯВКИ"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                root.send_package()
                root.wait()

            on_release: app.root.current = 'choice_area'
        Button:
            text: "ПРОВЕРИТЬ КЛАН"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                root.send_package()
            on_release: app.root.current = 'find_clan'
        Button:
            text: "ОТПРАВИТЬ ЗАЯВКУ НА РАЙОН"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_release: app.root.current = 'invite_to_area'
        Button:
            text: "ПОСМОТРЕТЬ СВОЙ КЛАН"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                if root.clan_value1 != '':root.send_get_clan()
                if root.clan_info_str1 != '' and root.clan_value1 != '': app.root.current = 'info_about_clan'
        Button:
            text: "НАКРУТИТЬ"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                app.root.current = 'nakrut'
        Button:
            text: "ЗАБАНИТЬ АКК!!!!"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                app.root.current = 'ban1'

        Button:
            text: "ВЫХОД"
            bold: True
            background_color:'#00FFCE'
            size_hint: (1,0.5)
            on_press:
                root.reset_all()
                app.root.current = 'login'
        Label:
            halign: 'center'
            valign: 'middle'
            text: 'by скиллер'
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1]
            markup: True
            color: 1, 1, 1, 1  # Установите цвет текста на черный
            background_color: 1, 0, 0, 1


<SecondWindow>:
    orientation: "vertical"
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    ScrollView:
            Label:
                halign: 'left'
                valign: 'middle'
                text: root.ta
                multiline: True
                text_size: self.width*0.98, None
                size_hint_x: 35.0
                size_hint_y: None
                height: self.texture_size[1] + 15
                markup: True
                color: 1, 1, 1, 1  # Установите цвет текста на черный
                background_color: 1, 0, 0, 1

        Button:
            text: 'Закрыть'
            size_hint: (1, 0.3)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'

<ThirdWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
        Label:
            text: root.pack_status1
            halign: 'center'
            valign: 'middle'
            id: status
            text: root.st
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 75
            markup: True
            color: 1, 1, 1, 1  # Установите цвет текста на черный
            background_color: 1, 0, 0, 1
        Button:
            text: 'Бедный'
            on_press:
                root.bedn_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()

        Button:
            text: 'Кошачий'
            on_press:
                root.cat_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Промышленный'
            on_press:
                root.prom_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Японский'
            on_press:
                root.japan_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Сельский'
            on_press:
                root.selsk_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Казино'
            on_press:
                root.casino_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Вампира'
            on_press:
                root.vamp_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()

        Button:
            text: 'Портовый'
            on_press:
                root.port_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Центральный'
            on_press:
                root.center_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Элитный'
            on_press:
                root.elite_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()
        Button:
            text: 'Военный'
            on_press:
                root.voen_area()
                if root.status_pack != '': app.root.transition.direction = 'left'
                if root.status_pack != '': app.root.current = 'result_area'
                else: root.wait()





<FourthWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
        Label:
            text: root.clans
            halign: 'center'
            valign: 'middle'
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 15
            markup: True
            color: 1, 1, 1, 1  # Установите цвет текста на черный
            background_color: 1, 0, 0, 1
        Button:
            text: 'Получить список'
            on_press:
                root.set_clans()
        Button:
            text: 'Назад'
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'choice_area'
        Button:
            text: 'В меню'
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'



<ClanWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
        Label:
            text : root.clan12
            halign: 'center'
            valign: 'middle'
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 15
            markup: True
            color: 1, 1, 1, 1
            background_color: 1, 0, 0, 1
        TextInput:
            id: clan_name
            multiline: False
            padding_y: (5,5)
            size_hint: (1, 0.5)
            on_text: root.inputt()
        Button:
            text: 'Найти'
            on_press:
                root.find_clan()

        Button:
            text: 'В меню'
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'


<InviteWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
        Label:
            text: root.stat1
            halign: 'center'
            valign: 'middle'
            id: status
            multiline: True
            text_size: self.width*0.98, None
            size_hint_x: 1.0
            size_hint_y: None
            height: self.texture_size[1] + 75
            markup: True
            color: 1, 1, 1, 1  # Установите цвет текста на черный
            background_color: 1, 0, 0, 1
        Button:
            text: 'Бедный'
            on_press:
                root.bedn_area()
        Button:
            text: 'Кошачий'
            on_press:
                root.cat_area()
        Button:
            text: 'Промышленный'
            on_press:
                root.prom_area()
        Button:
            text: 'Японский'
            on_press:
                root.japan_area()
        Button:
            text: 'Сельский'
            on_press:
                root.selsk_area()
        Button:
            text: 'Казино'
            on_press:
                root.casino_area()
        Button:
            text: 'Вампира'
            on_press:
                root.vamp_area()
        Button:
            text: 'Портовый'
            on_press:
                root.port_area()
        Button:
            text: 'Центральный'
            on_press:
                root.center_area()
        Button:
            text: 'Элитный'
            on_press:
                root.elite_area()
        Button:
            text: 'Военный'
            on_press:
                root.voen_area()
        Button:
            text: 'В меню'
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<ClanInfoWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    ScrollView:
            Label:
                text: root.text1
                halign: 'center'
                valign: 'middle'
                font_size: "17sp"
                id: status
                multiline: True
                text_size: self.width*0.98, None
                size_hint_x: 1.0
                size_hint_y: None
                height: self.texture_size[1] + 75
                markup: True
                color: 1, 1, 1, 1  # Установите цвет текста на черный
                background_color: 1, 0, 0, 1
        Button:
            text: 'ПОЛУЧИТЬ ИНФО'
            size_hint: (1, 0.5)
            on_press:
                root.set_text()
        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<AccInfoWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    ScrollView:
            Label:
                text: root.info12
                halign: 'center'
                valign: 'middle'
                font_size: "17sp"
                id: status
                multiline: True
                text_size: self.width*0.98, None
                size_hint_x: 1.0
                size_hint_y: None
                height: self.texture_size[1] + 75
                markup: True
                color: 1, 1, 1, 1  # Установите цвет текста на черный
                background_color: 1, 0, 0, 1
        Button:
            text: 'ПОЛУЧИТЬ ИНФОРМАЦИЮ'
            size_hint: (1, 0.5)
            on_press:
                root.set_info()
        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<Ban1Window>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    
        Button:
            text: 'ЗАБАНИТЬ АКК?'
            size_hint: (1, 0.5)
            on_press:
                app.root.current = 'ban2'
        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<Ban2Window>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    
        Button:
            text: 'ЗАБАНИТЬ АКК? К АККАУНТУ БУДЕТ НЕВОЗМОЖНО ВЕРНУТЬ ДОСТУП'
            size_hint: (1, 0.5)
            on_press:
                app.root.current = 'ban3'
        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<Ban3Window>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
            
        Button:
            text: 'ЗАБАНИТЬ'
            size_hint: (1, 0.5)
            on_press:
                root.ban()
                app.root.current = 'login'
        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
<NakrutWindow>:
    BoxLayout:
        orientation: "vertical"
        size_hint: (0.95, 0.95)
	    pos_hint: {"center_x": 0.5, "center_y":0.5}
	    ScrollView:
            Label:
                text: root.s12
                halign: 'center'
                valign: 'middle'
                font_size: "17sp"
                id: status
                multiline: True
                text_size: self.width*0.98, None
                size_hint_x: 1.0
                size_hint_y: None
                height: self.texture_size[1] + 75
                markup: True
                color: 1, 1, 1, 1  # Установите цвет текста на черный
                background_color: 1, 0, 0, 1
        Button:
            text: 'НАКРУТИТЬ'
            size_hint: (1, 0.5)
            on_press:
                root.nakrut()

        Button:
            text: 'В меню'
            size_hint: (1, 0.5)
            on_press:
                app.root.transition.direction = 'right'
                app.root.current = 'first'
''')

class MyApp(App):
    running = True
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ZeroWindow(name='login'))
        sm.add_widget(FirstWindow(name='first'))
        sm.add_widget(SecondWindow(name='second'))
        sm.add_widget(ThirdWindow(name='choice_area'))
        sm.add_widget(FourthWindow(name='result_area'))
        sm.add_widget(ClanWindow(name='find_clan'))
        sm.add_widget(InviteWindow(name='invite_to_area'))
        sm.add_widget(ClanInfoWindow(name='info_about_clan'))
        sm.add_widget(AccInfoWindow(name='info_about_account'))
        sm.add_widget(Ban1Window(name='ban1'))
        sm.add_widget(Ban2Window(name='ban2'))
        sm.add_widget(Ban3Window(name='ban3'))
        sm.add_widget(NakrutWindow(name='nakrut'))
        return sm

    def on_stop(self):
        self.running = False

if __name__ == "__main__":
    MyApp().run()
