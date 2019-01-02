import threading
import time
import json

check_count_remind = False

class myThread (threading.Thread):
    def __init__(self, thread_name, method, id=None, remind_thing=None, remind_time=None, count_remind=None, linebotapi=None, textsendmessage=None):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.method = str(method)
        self.linebotapi = linebotapi
        self.textsendmessage = textsendmessage
        self.id = id
        self.remind_thing = remind_thing
        self.remind_time = remind_time
        self.count_remind = count_remind


    def run(self):
        print ("Start thread ：" + self.thread_name)
        
        global check_count_remind
        if self.method == 'remind':
           while True:
                timer = time.time()+8*60*60
                if int(timer) == int(self.remind_time):
                    
                    # delete reminded_data in json file
                    file_name = "data/remind_list.json"
                    with open(file_name, 'r', encoding = 'utf8') as f:
                        data = json.load(f)
                    
                    remind_list = data[self.id].split("\n", self.count_remind-1)
                    write_back_to_json = ""
                            
                    for thing in remind_list :
                        clear_thing = thing.replace("\n", "")
                        clear_thing_split = clear_thing.split(" ", 2)
                        if self.remind_thing == clear_thing_split[0] :
                            pass
                        else :
                            write_back_to_json += clear_thing + "\n"
                    
                    if self.count_remind == 1 :
                        write_back_to_json = write_back_to_json.replace("\n", "")
                    
                    b_dict = {self.id:write_back_to_json}
                    data.update(b_dict)
                    with open(file_name, 'w') as f:
                        json.dump(data, f)
                    
                    check_count_remind = True

                    break
                else:
                    pass

        elif self.method == "push":
            while True:
                if self.remind_thing != "":
                    p_message = self.textsendmessage(self.id)
                    self.linebotapi.push_message(p_message, self.remind_thing)
                else:
                    pass

        elif self.method == "no_idle":
            while True:
                print("fall asleep")
                time.sleep(100)

        elif self.method == "minus_count_remind":
            while True:
                if check_count_remind:
                    check_count_remind = False
                    return True
                else:
                    return False

        else :
            print("else")
        
        print ("Exit thread ：" + self.thread_name)
