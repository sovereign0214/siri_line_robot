import json
import time
from src.remind_thread import myThread
class Control:
    def __init__(self):
        self.flag_todo = None
        self.flag_remind = None
        self.delete_check_todo = ""
        self.count_todo = 0
        self.count_remind = 0
        self.find_near = False
        self.find_week = False
        self.near = None
        self.week = None
        self.day = None
        self.clock = None
        self.remind_time = None
        self.seven = None
        self.today = False
        self.past = False
        self.delete_check_remind = ""
        self.insert_remind = True
        self.syntax_error = False
        self.remind_primary_key = 0

    def get_id(self):
        return self.id

    def minus_count_remind(self, minus):
        self.minus = minus
        if self.minus :
            if self.count_remind == 0:
                pass
            else:
                self.count_remind -= 1

    def to_db(self, user_id, user_text):
        self.id = user_id
        self.text = user_text
        self.text_split = self.text.split(" ", 3)
        
        if self.text_split[0] == "待辦":
            file_name = "data/to_do_list.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                data = json.load(f)
            #check if the user have previous data
            if len(data) == 0:
                self.flag_todo = 0
            else:
                for i in data:
                    if self.id == i:
                        self.flag_todo = 1
                        break
                    else:
                        self.flag_todo = 0
                    
            #write data into json file
            if self.flag_todo == 1:
                self.count_todo = self.count_todo + 1
                previous_data = data[self.id]+"\n"
                a_dict = {self.id:previous_data + self.text_split[1]}
                data.update(a_dict)
                with open(file_name, 'w') as f:
                    json.dump(data, f)

                #test what is in heroku jsons file
                # with open(file_name, 'r', encoding = 'utf8') as f:
                #     data_print = json.load(f)
                # print(json.dumps(data_print, indent=4, sort_keys=True))
        
            elif self.flag_todo == 0:
                self.count_todo = self.count_todo + 1
                a_dict = {self.id:self.text_split[1]}
                data.update(a_dict)
                with open(file_name, 'w') as f:
                    json.dump(data, f)

        elif self.text_split[0] == "提醒":
            file_name = "data/checkdate.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                check_file = json.load(f)
            
            # get time
            localtime = time.asctime(time.localtime(time.time()+8*60*60))
            time_split = str(localtime).split(" ", 4)
            get_hour_minute = time_split[3].split(":", 2)
            if get_hour_minute[0][0:1] == "0":
                hour = int(get_hour_minute[0][1:2])
            else:
                hour = int(get_hour_minute[0])
            if get_hour_minute[1][0:1] == "0":
                minute = int(get_hour_minute[1][1:2])
            else:
                minute = int(get_hour_minute[1])

            # check what day in a week
            for check in check_file["seven"][0]:
                if time_split[0] == check:
                    self.seven = check_file["seven"][0][check]
            if self.seven == None:
                self.syntax_error = True
            
            # check near or week
            for check in check_file["near"][0]:
                if self.text_split[2] == check:
                    self.find_near = True
                    self.near = check_file["near"][0][check]
                    number_means_week = int(self.seven) + int(self.near)
                    for i in check_file["change"][0]:
                        if int(i) == number_means_week:
                            self.text_split[2] = check_file["change"][0][i]
                        
            for check in check_file["week"][0]:
                if self.text_split[2] == check:
                    self.find_week = True
                    self.week = check_file["week"][0][check]
            
            if self.near == None and self.week == None:
                self.syntax_error = True
            
            # check day and clock
            s = self.text_split[3]
            s_top = s[0:2]
            s_bottom = s[2:]
            for check in check_file["day"][0]:
                if s_top == check:
                    self.day = check_file["day"][0][check]
            if self.day == None:
                self.syntax_error = True
            
            for check in check_file["clock"][0]:
                if s_bottom == check:
                    self.clock = check_file["clock"][0][check]    
            if self.clock == None:
                self.syntax_error = True
            
            # the day's start is 00:00, the week's start is Mon 00:00   
            day_first = (time.time()+8*60*60)-((60*hour+minute)*60)
            week_first = day_first - (int(self.seven)-1)*24*60*60
            
            # count the timestamp_remind
            if self.find_near:
                # check if the near is past time
                if int(self.near) == 0:
                    if self.day == "afternoon" or self.day == "night":
                        c = int(self.clock)+12
                    else:
                        c = int(self.clock)
                    if hour >= c:
                        self.past = True

                if self.day == "afternoon" or self.day == "night":
                    self.remind_time = day_first + int(self.near)*24*60*60 + (int(self.clock)+12)*60
                elif self.day == "noon":
                    self.remind_time = day_first + int(self.near)*24*60*60 + 12*60
                else:
                    self.remind_time = day_first + int(self.near)*24*60*60 + int(self.clock)*60
                
            elif self.find_week:
                # check if the week is past time
                if int(self.week) < int(self.seven) :
                    self.past = True
                elif int(self.week) == int(self.seven) :
                    if int(self.clock) > hour :
                        self.today = True
                    else:
                        self.past = True
                else:
                    if self.day == "afternoon" or self.day == "night":
                        self.remind_time = week_first + (int(self.week)-1)*24*60*60 + (int(self.clock)+12)*60
                    elif self.day == "noon":
                        self.remind_time = week_first + (int(self.week)-1)*24*60*60 + 12*60
                    else:
                        self.remind_time = week_first + (int(self.week)-1)*24*60*60 + int(self.clock)*60
                
            if self.past:
                pass
            else:
                # check if the user have previous remind list
                file_name = "data/remind_list.json"
                with open(file_name, 'r', encoding = 'utf8') as f:
                    data = json.load(f)
                if len(data) == 0:
                    self.flag_remind = 0
                else:
                    for i in data:
                        if self.id == i:
                            self.flag_remind = 1
                            break
                        else:
                            self.flag_remind = 0

                # write data into json file
                if self.flag_remind == 1:
                    self.count_remind += 1
                    self.remind_primary_key += 1
                    previous_data = data[self.id].split("\n", self.count_remind-2)
                    file_name = "data/checkdate.json"
                    with open(file_name, 'r', encoding = 'utf8') as f:
                        check_file = json.load(f)
                    
                    sorted_back_to_json = ""

                    for thing in previous_data:
                        # get every previous data
                        thing_split = thing.split(" ", 2)
                        for check in check_file["week"][0]:
                            if thing_split[1] == check:
                                thing_week = check_file["week"][0][check]

                        s = thing_split[2]
                        thing_top = s[0:2]
                        thing_bottom = s[2:]
                        for check in check_file["day"][0]:
                            if thing_top == check:
                                thing_day = check_file["day"][0][check]
                        for check in check_file["clock"][0]:
                            if thing_bottom == check:
                                thing_clock = check_file["clock"][0][check]
                        
                        #sort and check if equal
                        l_week = [int(self.week), int(thing_week)]
                        sorted_l_week = sorted(l_week)
                        if sorted_l_week == l_week:
                            if int(self.week) < int(thing_week):
                                if self.insert_remind:
                                    sorted_back_to_json += self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3] + "\n"
                                    self.insert_remind = False
                                sorted_back_to_json += thing + "\n"
                                
                            elif int(self.week) == int(thing_week):        
                                if thing_day == "afternoon" or thing_day == "night":
                                    thing_clock = str(int(thing_clock) + 12)
                                if self.day == "afternoon" or self.day == "night":
                                    self.clock = str(int(self.clock) + 12)
                                
                                l_clock = [int(self.clock), int(thing_clock)]
                                sorted_l_clock = sorted(l_clock)
                                if sorted_l_clock != l_clock:
                                    sorted_back_to_json += thing + "\n"
                                    if self.insert_remind:
                                        sorted_back_to_json += self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3] + "\n"
                                else:
                                    if self.insert_remind:
                                        sorted_back_to_json += self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3] + "\n"
                                        self.insert_remind = False
                                    sorted_back_to_json += thing + "\n"
                            else:
                                pass        
                        else:
                            sorted_back_to_json += thing + "\n"
                            if self.insert_remind:
                                sorted_back_to_json += self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3] + "\n"
                    a_dict = {self.id:sorted_back_to_json}
                    data.update(a_dict)
                    
                    file_name = "data/remind_list.json"
                    with open(file_name, 'w') as f:
                        json.dump(data, f)
                    
                    # call thread
                    locals()["thread%s"%self.remind_primary_key] = myThread(str(self.remind_primary_key), "remind", self.id, self.text_split[1], self.remind_time, self.count_remind)
                    locals()["thread%s"%self.remind_primary_key].start()
                
                elif self.flag_remind == 0:
                    self.count_remind += 1
                    self.remind_primary_key += 1
                    a_dict = {self.id:self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3]}
                    data.update(a_dict)

                    file_name = "data/remind_list.json"
                    with open(file_name, 'w') as f:
                        json.dump(data, f)
                    
                    locals()["thread%s"%self.remind_primary_key] = myThread(str(self.remind_primary_key), "remind", self.id, self.text_split[1], self.remind_time, self.count_remind)
                    locals()["thread%s"%self.remind_primary_key].start()
                
            self.remind_time = None
        
        else:
            pass

    def response(self):
        if self.text_split[0] == "待辦":
            return self.text_split[1]+"\n已被紀錄為待辦事項。"

        elif self.text_split[0] == "列出所有待辦事項":
            file_name = "data/to_do_list.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                data = json.load(f)
            if len(data) == 0 or data[self.id] == "" or data[self.id] == " " or data[self.id] == "\n" :
                return "目前尚無待辦事項"
            else:
                return data[self.id]

        elif self.text_split[0] == "刪除待辦":
            file_name = "data/to_do_list.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                data = json.load(f)
            # check if database have data
            if len(data) == 0 :
                return "無法刪除:沒有這則待辦事項。"
            else:
                for i in data:
                    # check if the user have to-do-list
                    if self.id == i:
                        self.delete_check_todo == None
                        to_do_list = data[self.id].split("\n", self.count_todo-1)
                        write_back_to_json = ""
                            
                        for thing in to_do_list :
                            clear_thing = thing.replace("\n", "")
                            if self.text_split[1] == clear_thing :
                                self.delete_check_todo = clear_thing
                                self.count_todo = self.count_todo-1 
                            else :
                                write_back_to_json += clear_thing + "\n"
                        if self.count_todo == 1 :
                            write_back_to_json = write_back_to_json.replace("\n", "")
                        
                        b_dict = {self.id:write_back_to_json}
                        data.update(b_dict)
                        with open(file_name, 'w') as f:
                            json.dump(data, f)
                        
                        # user don't have this to-do-thing
                        if self.delete_check_todo == None :
                            return "無法刪除:沒有這則待辦事項。"
                        
                        # find and delete
                        else:
                            s = self.delete_check_todo
                            self.delete_check_todo = None
                            return s+"\n此待辦事項已刪除。"
                    
                    # user don't have this to-do-list
                    else:
                        return "無法刪除:沒有這則待辦事項。"

        elif self.text_split[0] == "提醒":
            if self.syntax_error:
                return "您好，我可以幫您紀錄待辦事項與提醒，請使用如下格式:\n待辦 xxx\n刪除待辦 xxx\n列出所有待辦事項\n提醒 xxx 今天 下午三點\n提醒 xxx 明天 中午十二點\n提醒 xxx 後天 早上十點\n提醒 xxx 周六 晚上七點\n提醒 xxx 下周五 半夜兩點\n列出所有提醒事項\n刪除提醒 xxx 周六 晚上七點\n\n請打開本帳號的line通知，以利提醒。\n提醒事項在提醒後將會自動刪除。"

            if self.past :
                return "已是過去時間，無法存為提醒事項。"
            else:
                if self.today :
                    s = "今天"
                else:
                    s = self.text_split[2]

                self.near = None
                self.day = None
                self.clock = None
                self.week = None
                self.seven = None
                self.today = False
                self.past = False
                self.find_near = False
                self.find_week = False

                return self.text_split[1]+"\n已被紀錄為提醒事項，\n將在 "+s+self.text_split[3]+" 提醒。"
        
        elif self.text_split[0] == "列出所有提醒事項":
            file_name = "data/remind_list.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                data = json.load(f)
            
            if len(data) == 0 or data[self.id] == "" or data[self.id] == " " or data[self.id] == "\n" :
                return "目前尚無提醒事項"
            else:
                return data[self.id]

        elif self.text_split[0] == "刪除提醒":
            file_name = "data/remind_list.json"
            with open(file_name, 'r', encoding = 'utf8') as f:
                data = json.load(f)
            # check if database have data
            if len(data) == 0 :
                return "無法刪除:沒有這則提醒事項。"
            else:
                for i in data:
                    # check if the user have remind-list
                    if self.id == i:
                        self.delete_check_remind = None
                        remind_list = data[self.id].split("\n", self.count_remind-1)
                        write_back_to_json = ""
                            
                        for thing in remind_list :
                            clear_thing = thing.replace("\n", "")
                            if self.text_split[1]+" "+self.text_split[2]+" "+self.text_split[3] == clear_thing :
                                self.delete_check_remind = clear_thing
                                self.count_remind = self.count_remind-1 
                            else :
                                write_back_to_json += clear_thing + "\n"
                        if self.count_remind == 1 :
                            write_back_to_json = write_back_to_json.replace("\n", "")
                        
                        b_dict = {self.id:write_back_to_json}
                        data.update(b_dict)
                        with open(file_name, 'w') as f:
                            json.dump(data, f)
                        
                        # find and delete
                        if self.delete_check_remind != None :
                            s = self.delete_check_remind
                            self.delete_check_remind = None
                            return s+"\n此提醒事項已刪除。"
                        
                        # user don't have this remind-thing
                        else:
                            return "無法刪除:沒有這則提醒事項。"
                        
                    
                    # user don't have this remind-thing
                    else:
                        return "無法刪除:沒有這則提醒事項。"


        else:
            return "您好，我可以幫您紀錄待辦事項與提醒，請使用如下格式:\n待辦 xxx\n刪除待辦 xxx\n列出所有待辦事項\n提醒 xxx 今天 下午三點\n提醒 xxx 明天 中午十二點\n提醒 xxx 後天 早上十點\n提醒 xxx 周六 晚上七點\n提醒 xxx 下周五 半夜兩點\n列出所有提醒事項\n刪除提醒 xxx 周六 晚上七點\n\n請打開本帳號的line通知，以利提醒。\n提醒事項在提醒後將會自動刪除。"
