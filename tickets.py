# coding: utf-8
"""命令行火车票查看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets 北京 上海 2016-10-10
    tickets -dg 成都 南京 2016-10-10
"""
from docopt import docopt
from stations import stations
import requests
# import PrettyTable
from prettytable import PrettyTable
from colorama import init, Fore
init()

class TrainCollection:
    header = '车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split()

    def __init__(self, available_trains, options):
        self.available_trains = available_trains
        self.options = options

    def _get_duration(self,raw_train):
        # print(raw_train)
        duration = raw_train['queryLeftNewDTO']['lishi'].replace(':' , '小时')+'分'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for raw_train in self.available_trains:
            train_no = raw_train['queryLeftNewDTO']['station_train_code']
            # print(train_no)
            initial=train_no[0].lower()
            # print(initial)
            if not self.options or initial in self.options:  #判断是否有指定了列车的类型，或者找到指定的类型的列车信息
                train = [
                    train_no,
                    '\n'.join([Fore.GREEN + raw_train['queryLeftNewDTO']['from_station_name'] + Fore.RESET,
                               Fore.RED + raw_train['queryLeftNewDTO']['to_station_name'] + Fore.RESET]),
                    '\n'.join([Fore.GREEN + raw_train['queryLeftNewDTO']['start_time'] + Fore.RESET,
                               Fore.RED + raw_train['queryLeftNewDTO']['arrive_time'] + Fore.RESET]),
                    self._get_duration(raw_train),
                    raw_train['queryLeftNewDTO']['zy_num'],
                    raw_train['queryLeftNewDTO']['ze_num'],
                    raw_train['queryLeftNewDTO']['rw_num'],
                    raw_train['queryLeftNewDTO']['yw_num'],
                    raw_train['queryLeftNewDTO']['yz_num'],
                    raw_train['queryLeftNewDTO']['wz_num'],
                ]
                # print(train)
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        # print(pt)
        for train in self.trains:
            pt.add_row(train)
            # print(pt)
        print(pt)


def cli():
    # """command-line interface"""
    arguments = docopt(__doc__)
    # print(arguments)
    from_station = stations.get(arguments['<from>'])  # arguments['<from>'] 是啥鬼？尼玛原来是arguments这个字典相应的值
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    # print('from:', from_station,date,to_station,arguments['<from>'],stations['成都'])

    url = "https://kyfw.12306.cn/otn/leftTicket/query"
    querystring = {
        "leftTicketDTO.train_date": date,
        "leftTicketDTO.from_station": from_station,
        "leftTicketDTO.to_station": to_station,
        "purpose_codes": "ADULT"
    }
    options=''.join([key for key,value in arguments.items() if value is True]) #判断获取是否选择了列车的类型

    requests.packages.urllib3.disable_warnings()  # 解决Python爬取HTTPS网页时的错误
    r = requests.get(url, params=querystring, verify=False)  # 添加verify=False参数不验证证书
    available_trains = r.json()['data']
    # print(available_trains)
    TrainCollection(available_trains,options).pretty_print()
    # print(r.json())
    # print(date)
if __name__ == '__main__':
    cli()