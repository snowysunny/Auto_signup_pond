# coding: utf-8

import pymysql
import math
import time
import numpy as np
import pandas as pd

company_id = "888888888$"
company_name = u'海知理财'

# 进行数据库的连接
def ConnectionDB(host="localhost", user="root", passwd="", db="user_wallet"):
    # 进行数据库的连接   112.74.134.230 | ht | wecombo | 931226
    # 内网进行连接  192.168.0.136 | ht | root | 965310
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=db, use_unicode=True, charset="utf8")
    return db

# 根据id查询某一用户的当前余额
# @param user_id 需要查询的用户的id
# @return user_balance 用户当前的余额
def check_user_balance(user_id):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "select user_balance from user_wallet where user_id = '" + user_id + "'"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        print "try:", sql
        # db.close()
        return data[0]
    except:
        print "except: ", sql
        print "search error"
        # db.close()
        return False

# 更新用户钱包信息的方法，做相应的钱包余额增减
# @param user_id 用户的id编号
# @param amount 需要增减的金额数额
# @param is_add 这笔更改是否是增加，否则为减少
# @return True/False 更新是否成功
def update_user_wallet(user_id, amount, is_add):
    db = ConnectionDB()
    cursor = db.cursor()
    if is_add:
        sql = "update user_wallet set user_balance = user_balance + " + amount + " where user_ID = '" + user_id +"'"
        try:
            print sql
            cursor.execute(sql)
            db.commit()
            # db.close()
            print "加钱成功"
            return True
        except:
            db.rollback()
            # db.close()
            print "价钱失败"
            return False
    else:
        sql = "update user_wallet set user_balance = user_balance - " + amount + " where user_ID = '" + user_id + "'"
        try:
            cursor.execute(sql)
            db.commit()
            # db.close()
            print "扣款成功"
            return True
        except:
            db.rollback()
            # db.close()
            return False

# 更新海知企业账户钱包的方法，做相应的钱包余额增减
def update_company_wallet(company_id, amount, is_add):
    db = ConnectionDB()
    cursor = db.cursor()
    if is_add:
        sql = "update user_wallet set user_balance = user_balance + " + amount + " where user_ID = '" + company_id + "'"
        try:
            print sql
            cursor.execute(sql)
            db.commit()
            # db.close()
            return True
        except:
            db.rollback()
            # db.close()
            return False
    else:
        sql = "update user_wallet set user_balance = user_balance - " + amount + " where user_ID = '" + company_id + "'"
        try:
            cursor.execute(sql)
            db.commit()
            # db.close()
            return True
        except:
            db.rollback()
            # db.close()
            return False

# 创建新的交易记录@sys_detail
# @param trade_info 交易信息数组
# @return True/False 交易激励是否创建成功
def create_sys_detail(trade_info):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "insert into sys_detail(sys_serial, sys_senderID, sys_accepterID, sys_tradeID, sys_targetID, sys_targetName, sys_type, sys_amount, sys_balance, sys_time, sys_notes) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s');"
    sql = sql %(trade_info[0], trade_info[1], trade_info[2], trade_info[3], trade_info[4], trade_info[5], trade_info[6], trade_info[7], trade_info[8], trade_info[9], trade_info[10])
    try:
        cursor.execute(sql)
        db.commit()
        # db.close()
        return True
    except:
        db.rollback()
        # db.close()
        return False


# 创建新的发奖记录@award_detail
# @param trade_info 交易信息数组
# @return True/False 交易记录是否创建成功
def create_award_detail(trade_info):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "insert into award_detail(game_number, pond_amount, pond_people_number, first_user_id, first_user_award, second_user_id, second_user_award, third_user_id, third_user_award, other_users_ids, other_users_award) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')"
    sql = sql % (
    trade_info[0], trade_info[1], trade_info[2], trade_info[3], trade_info[4], trade_info[5], trade_info[6],
    trade_info[7], trade_info[8], trade_info[9], trade_info[10])
    try:
        cursor.execute(sql)
        db.commit()
        # db.close()
        return True
    except:
        db.rollback()
        # db.close()
        return False

# 创建奖金池@pond_detail
# @param comp_id 比赛赛事的id
# @param amount 设定参赛人员的报名费用
# @param game_state 比赛类型 1:周赛，2:月赛，3:季赛，4:年赛， 5:团体大赛或者高校大赛， 默认为5，因为前面的几个都是脚本在自动进行
def create_pond_detail(comp_id, amount, game_state=5):
    db = ConnectionDB()
    cursor = db.cursor()
    pond_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "insert into pond_detail(game_number, game_state, apply_number, pond_all, pond_time) VALUES ('%s', '%s', '%s', '%s', '%s')"
    sql = sql %(comp_id, game_state, 1, amount, pond_time)
    flag = 1
    try:
        cursor.execute(sql)
        db.commit()
    except:
        flag = 0
        db.rollback()
    db.close()
    if flag:
        return True
    return False

# 根据比赛赛事的id查询该笔试是否创建了奖金池@pond_detail
# @param comp_id 比赛赛事的id
# @return data[pond_all]: 该赛事的奖金池的数额  data[apply_number]: 该赛事参赛人数
def select_pond_detail(comp_id):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "select pond_all, apply_number from pond_detail where game_number = '" + comp_id + "';"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        # db.close()
        return list(data)
    except:
        print "except: ", sql
        print "search error"
        # db.close()
        return False

# 发奖完成后，进行奖池信息的更新@pond_detail
# @param comp_id 比赛的id
# @param pond_send 这次比赛发放掉的奖金的数额
# @param pond_balance 奖池剩余的金额
# @return True/False 奖池信息更新是否成功
def update_pond_detail(comp_id, pond_send, pond_balance):
    db = ConnectionDB()
    cursor = db.cursor()
    pond_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "update pond_detail set pond_send = '" + str(pond_send) + "', pond_balance = '" + str(pond_balance) + "', pond_time = '" + str(pond_time) + "' where game_number = '" + comp_id +"'"
    try:
        cursor.execute(sql)
        db.commit()
        # db.close()
        return True
    except:
        db.rollback()
        # db.close()
        return False




# 确定好发奖金的比例情况，返回具体的发钱的列表
# @param pond_all 奖池的容量大小
# @param apply_num 报名人数，该比赛的参赛人数
# @return 返回发钱分配的列表
def determine_bonus_ratio(pond_all, apply_num):
    # 根据情况判断发钱的方案
    # 如果报名人数只有两个人是，奖金知发放给第一名
    # 报名人数<50人时，仅发前三名，奖金比例为： 6/3/1
    # 报名人数<100但>50人时，前百分之十的人均发放，奖金比例为5/2/1/2  first:0.5 second:0.2  third: 0.1 other: 0.2/(apply_num * 0.1 - 3)
    # 报名人数>100时，前百分之十的人均发放，奖金比例为:4/2/1/3  first:0.4 second:0.2 third: 0.1 other: 0.3/(apply_num * 0.1 - 3)
    award_array = []
    if apply_num <= 0:
        return []
    if apply_num <= 2 and apply_num > 0:
        award_array.append(pond_all)
    elif apply_num > 2 and apply_num <= 50:
        first_award = math.floor(pond_all * 0.6)
        second_award = math.floor(pond_all * 0.3)
        third_award = math.floor(pond_all * 0.1)
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
    elif apply_num > 50 and apply_num <= 100:
        first_award = math.floor(pond_all * 0.5)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        other_award = math.floor(pond_all * 0.2 // (apply_num * 0.1 - 3))
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
        award_array.append(other_award)
    else:
        first_award = math.floor(pond_all * 0.4)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        other_award = math.floor(pond_all * 0.3 // (apply_num * 0.1 - 3))
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
        award_array.append(other_award)
    return award_array

# 对单个获奖者进行奖金的发放
# @param comp_name 比赛赛事的name
# @param user_id 获奖者的id
# @param award_amount 获得的奖金的数目
# @param ranking 获奖者比赛排名
# @return: 0：奖金发放不成功，奖金金额不大于0  1: 发放奖金成功，企业账户更新成功，创建新的记录成功
# @return：2：用户账户更新失败，发放奖金不成功 3： 用户账户更新成功，但是企业账户更新失败，用户账户回退
# @return：4：用户账户更新成功，企业账户更新成功，但是交易记录创建失败了
def distribute_award_one(comp_name, user_id, award_amount, ranking):
    if award_amount < 0:
        return 0
    user_wallet_res = update_user_wallet(user_id, award_amount, True)
    if not user_wallet_res:
        return 2
    company_wallet_res = update_company_wallet(company_id, award_amount, False)
    if not company_wallet_res:
        update_user_wallet(user_id, award_amount, False)
        return 3
    user_balance = check_user_balance(user_id)
    trade_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    serial = str(time.time()).split('.')[0] + user_id + "16"
    trade_notes = u"您在" + comp_name + u"比赛中获得第" +  str(ranking) + u"名，获得奖金" + str(award_amount)
    trade_info = list()
    trade_info.append(serial)
    trade_info.append(company_id)
    trade_info.append(user_id)
    trade_info.append(user_id)
    trade_info.append(company_id)
    trade_info.append(company_name)
    trade_info.append("6")
    trade_info.append(award_amount)
    trade_info.append(user_balance)
    trade_info.append(trade_time)
    trade_info.append(trade_notes)
    create_sys_detail_res = create_sys_detail(trade_info)
    if not create_sys_detail_res:
        update_user_wallet(user_id, award_amount, False)
        update_company_wallet(company_id, award_amount, True)
        return 4
    return 1

# 对一场比赛中获奖的人员进行奖金的发放
# @param comp_id 比赛赛事的id
# @param comp_name 比赛赛事的name
# @param award_user_list 获奖用户user_id列表,按照获奖高低排好，比如：第一个表示此次比赛的冠军
# @return 5: 奖金池金额小于等于0   6: 参赛人数有误  7：获奖人员列表为空，或者不合法
# @return 8: 奖金发放成功，但是奖金池信息更新失败   9:该比赛没有设立奖金
# @return 0， 2-7 奖金池都未进行更新，任何表的信息都没有被改变 8是只有奖金池信息更新失败，其他操作均成功
def distribute_awards(comp_id, comp_name, award_user_list):
    pond_detail_res = select_pond_detail(comp_id)
    if pond_detail_res:
        # pond_all 奖池的容量大小
        # apply_num 报名人数，该比赛的参赛人数
        pond_all = pond_detail_res[0]
        apply_num = pond_detail_res[1]
    else:
        return 9
    if pond_all <= 0:
        return 5
    if apply_num <= 0:
        return 6
    if len(award_user_list) <= 0:
        return 7
    # award_array给获奖者发放奖金的列表
    award_array = determine_bonus_ratio(pond_all, apply_num)
    pond_send = 0
    if apply_num <= 2 and apply_num > 0:
        if len(award_user_list) >= 1:
            distribute_award_one_res = distribute_award_one(comp_name, award_user_list[0], str(award_array[0]), 1)
            pond_send = award_array[0]
    elif apply_num > 2 and apply_num <= 50:
        for i in range(min(len(award_user_list), 3)):
            distribute_award_one_res = distribute_award_one(comp_name, award_user_list[i], str(award_array[i]), i+1)
            pond_send += award_array[i]
    elif apply_num > 50 and apply_num <= 100:
        for i in range(min(len(award_user_list), int(apply_num * 0.1))):
            if i < 3:
                distribute_award_one_res = distribute_award_one(comp_name, award_user_list[i], str(award_array[i]), i+1)
                pond_send += award_array[i]
            else:
                distribute_award_one_res = distribute_award_one(comp_name, award_user_list[i], str(award_array[-1]), i + 1)
                pond_send += award_array[ -1]
    else:
        for i in range(min(len(award_user_list), int(apply_num * 0.1))):
            if i < 3:
                distribute_award_one_res = distribute_award_one(comp_name, award_user_list[i], str(award_array[i]), i+1)
                pond_send += award_array[i]
            else:
                distribute_award_one_res = distribute_award_one(comp_name, award_user_list[i], str(award_array[-1]), i + 1)
                pond_send += award_array[-1]
    if distribute_award_one_res == 1:
        pond_balance = pond_all - pond_send
        update_pond_detail_res = update_pond_detail(comp_id, pond_send, pond_balance)
        if not update_pond_detail_res:
            return 8
    return distribute_award_one_res

# 进行奖金发放
# @param comp_name 比赛赛事的name
# @param pond_all 奖池的容量大小
# @param apply_num 报名人数，该比赛的参赛人数
# @param award_user_list 获奖用户列表
def  distribute_award_test1(comp_id, comp_name, pond_all, apply_num, award_user_list):
    company_id = "888888888$"
    company_name = u"海知理财"
    if pond_all <= 0:
        return False
    # award_array: 给用户发钱，发钱列表
    award_array = determine_bonus_ratio(pond_all, apply_num)
    award_amount = 0
    # 用户账户的改变
    for i in range(len(award_user_list)):
        # 更新用户钱包
        if i < len(award_array):
            award_amount = award_array[i]
        else:
            award_amount = award_array[-1]
        # 更改用户余额
        update_user_wallet(award_user_list[i], award_amount, True)
        # 更改企业钱包
        update_company_wallet(company_id, award_amount, False)

        user_balance = check_user_balance(award_user_list[i])
        trade_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        serial = str(time.time()).split('.')[0] + award_user_list[i] + "16"
        trade_notes = u"您在"+comp_name+ u"比赛中获得第" + str(i+1) + u"名，获得奖金" + str(award_amount)
        trade_info = list()
        trade_info.append(serial)
        trade_info.append(company_id)
        trade_info.append(award_user_list[i])
        trade_info.append(award_user_list[i])
        trade_info.append(company_id)
        trade_info.append(company_name)
        trade_info.append("6")
        trade_info.append(award_amount)
        trade_info.append(user_balance)
        trade_info.append(trade_time)
        trade_info(trade_notes)
        create_sys_detail(trade_info)




