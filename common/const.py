# -*- coding: utf-8 -*-
SUB_CLASSIFIER_xiaoshou = 0#销售相关咨询
SUB_CLASSIFIER_guihua = 1#学习规划
SUB_CLASSIFIER_shijian = 2#课程时间安排
SUB_CLASSIFIER_gongju = 3#上课工具
SUB_CLASSIFIER_jiaoshi = 4#教师问题
SUB_CLASSIFIER_huoli = 5#客户获利咨询
SUB_CLASSIFIER_shouhou = 6#售后相关咨询
SUB_CLASSIFIER_dizhi = 7#地址信息反馈
SUB_CLASSIFIER_geren = 8#个人信息反馈
SUB_CLASSIFIER_zixun = 9#其他咨询
SUB_CLASSIFIER_dazhaohu = 10#打招呼
SUB_CLASSIFIER_jujue = 11#拒绝结束
SUB_CLASSIFIER_kaolv = 12#考虑结束
SUB_CLASSIFIER_zantongke = 13#赞同结束-可跟进
SUB_CLASSIFIER_zantongbu = 14#赞同结束-不需跟进
SUB_CLASSIFIER_bangmang = 15#找帮忙
SUB_CLASSIFIER_jitang = 16#祝福鸡汤
SUB_CLASSIFIER_ad = 17#纯广告
SUB_CLASSIFIER_xianliao = 18#闲聊
SUB_CLASSIFIER_qita = 19#其他（）
SUB_CLASSIFIER_re_lahei= 101#正则拉黑
SUB_CLASSIFIER_re_zhaohu = 102#正则打招呼
SUB_CLASSIFIER_re_wuyi = 103#正则无意义
SUB_CLASSIFIER_re_tonghua = 104#正则通话
SUB_CLASSIFIER_re_hongbao = 106#正则红包
SUB_CLASSIFIER_re_jujie = 107#正则拒接
SUB_CLASSIFIER_re_TBD = 201#未知
SUB_CLASSIFIER_re_wuwenben = 202#无可用文本
SUB_CLASSIFIER_re_qiye = 108#正则企业转好友


sub_classifier_set = set([
SUB_CLASSIFIER_xiaoshou,
SUB_CLASSIFIER_guihua,
SUB_CLASSIFIER_shijian ,
SUB_CLASSIFIER_gongju,
SUB_CLASSIFIER_jiaoshi ,
SUB_CLASSIFIER_huoli,
SUB_CLASSIFIER_shouhou,
SUB_CLASSIFIER_dizhi,
SUB_CLASSIFIER_geren ,
SUB_CLASSIFIER_zixun,
SUB_CLASSIFIER_dazhaohu ,
SUB_CLASSIFIER_jujue,
SUB_CLASSIFIER_kaolv,
SUB_CLASSIFIER_zantongke,
SUB_CLASSIFIER_zantongbu,
SUB_CLASSIFIER_bangmang,
SUB_CLASSIFIER_jitang,
SUB_CLASSIFIER_ad,
SUB_CLASSIFIER_xianliao ,
SUB_CLASSIFIER_qita,
SUB_CLASSIFIER_re_lahei ,
SUB_CLASSIFIER_re_zhaohu,
SUB_CLASSIFIER_re_wuyi,
SUB_CLASSIFIER_re_tonghua,
SUB_CLASSIFIER_re_hongbao,
SUB_CLASSIFIER_re_jujie,
SUB_CLASSIFIER_re_TBD,
SUB_CLASSIFIER_re_wuwenben,
SUB_CLASSIFIER_re_qiye,
])

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2