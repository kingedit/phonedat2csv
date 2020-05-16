# -*- coding: utf-8 -*-

import os
import struct
import sys
import pandas as pd

__author__ = 'lovedboy'

if sys.version_info > (3, 0):
    def get_record_content(buf, start_offset):
        end_offset = buf.find(b'\x00', start_offset)
        return buf[start_offset:end_offset].decode()


class Phone(object):
    def __init__(self, dat_file=None):

        if dat_file is None:
            dat_file = os.path.join(os.path.dirname(__file__), "phone.dat")


        # 读取dat文件
        with open(dat_file, 'rb') as f:
            self.buf = f.read()

        self.head_fmt = "<4si"
        self.phone_fmt = "<iiB"
        self.head_fmt_length = struct.calcsize(self.head_fmt)
        self.phone_fmt_length = struct.calcsize(self.phone_fmt)
        self.version, self.first_phone_record_offset = struct.unpack(
            self.head_fmt, self.buf[:self.head_fmt_length])
        self.phone_record_count = (len(
            self.buf) - self.first_phone_record_offset) // self.phone_fmt_length

    # 获取版本的信息，版本号以及记录数
    def get_phone_dat_msg(self):
        print("版本号:{}".format(self.version))
        print("总记录条数:{}".format(self.phone_record_count))

    @staticmethod
    def get_phone_no_type(no):
        if no == 4:
            return "电信虚拟运营商"
        if no == 5:
            return "联通虚拟运营商"
        if no == 6:
            return "移动虚拟运营商"
        if no == 3:
            return "电信"
        if no == 2:
            return "联通"
        if no == 1:
            return "移动"

    @staticmethod
    # 格式化手机号码等其他
    def _format_phone_content(phone_num, record_content, phone_type):

        province, city, zip_code, area_code = record_content.split('|')
        return {
            "phone": phone_num,
            "province": province,
            "city": city,
            "zip_code": zip_code,
            "area_code": area_code,
            "phone_type": Phone.get_phone_no_type(phone_type)
        }

    def _lookup_phone(self,left,right):
        # 将数字转换为7位的字符串
        buflen = len(self.buf)
        listallphone = []
        while left <= right:
            current_offset = (self.first_phone_record_offset +
                left * self.phone_fmt_length)
            left=left+1
            if current_offset >= buflen:
                return

            buffer = self.buf[current_offset: current_offset + self.phone_fmt_length]
            cur_phone, record_offset, phone_type = struct.unpack(self.phone_fmt,
                                                                 buffer)

            record_content = get_record_content(self.buf, record_offset)
            phoneinfo = Phone._format_phone_content(cur_phone, record_content,
                                                   phone_type)
            
            outphoneinfo = self.human_phone_info(phoneinfo)
            listallphone.append(outphoneinfo)
            # return phoneinfo
            # return Phone._format_phone_content(cur_phone, record_content,
                                                #    phone_type)
        listallphone 
        return  listallphone

    def find(self,left,right):
        return self._lookup_phone(left,right)

    @staticmethod
    def human_phone_info(phone_info):
        if not phone_info:
            return ''

        return "{}|{}|{}|{}|{}|{}".format(phone_info['phone'],
                                          phone_info['province'],
                                          phone_info['city'],
                                          phone_info['zip_code'],
                                          phone_info['area_code'],
                                          phone_info['phone_type'])

    def test(self):
        # 分两次写入
        self.get_phone_dat_msg()
        left = 0
        right = self.phone_record_count
        mid = int(left + (right-left)/2)
        phonelist = self.find(left,mid)
        # list1=[]
        name=['phoneinfo']
        # name=['phone','province','city','zip_code','area_code','phone_type']
        # for phoneinf in phonelist:
           
        #     list1.append(phoneinf.split("|"))
        test=pd.DataFrame(columns=name,data=phonelist)
        test.to_csv('all1.csv',encoding='gbk')
        
        phonelistright = self.find(mid+1,right-1)
        test2=pd.DataFrame(columns=name,data=phonelistright)
        test2.to_csv('all2.csv',encoding='gbk')
        
        print("写入csv完成")

if __name__ == "__main__":
    phone = Phone()
    phone.test()
