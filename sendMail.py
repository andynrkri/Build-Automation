# coding=utf-8
# Don't delele the report.pkl file found in the directory where HSAN_build_automation and this script is executing.
# It uses that to get the report faster than File I/O operations.
import sys
import smtplib
import pickle

with open('report.pkl', 'rb') as input:
    report = pickle.load(input)
sender = 'abc@xyz.in'  # put the senders email id
receivers = 'def@xyz.in'  # put the recievers id's in a list

message = "Dear All Concerned, \n"+report

try:
    smtpobj = smtplib.SMTP('10.0.0.46')
    smtpobj.sendmail(sender, receivers, message)
    print('MAIL SENT!')
except Exception as ex:
    print(ex)
