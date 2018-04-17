# coding: utf-8

import pymysql
import math
import time
import numpy as np

company_id = "888888888$"
company_name = u'海知理财'

# 进行数据库的连接
def ConnectionDB(host="192.168.0.136", user="root", passwd="965310", db="ht"):
    # 进行数据库的连接   112.74.134.230 | ht | wecombo | 931226
    # 内网进行连接  192.168.0.136 | ht | root | 965310
    # host="localhost", user="root", passwd="", db="user_wallet"
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=db, use_unicode=True, charset="utf8")
    return db

# 根据id查询某一用户name @ht_users
# @param user_id 需要查询的用户的id
# @return username
def get_user_name(user_id):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "select username from ht_users where user_id = '" + user_id + "'"
    flag = 1
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
    except:
        print "check_user_balance except:", sql
        flag = 0
    db.close()
    if flag and data:
        return data[0]
    return False


# 根据id查询某一用户的当前余额@user_wallet
# @param user_id 需要查询的用户的id
# @return user_balance 用户当前的余额
def check_user_balance(user_id):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "select user_balance from user_wallet where user_id = '" + user_id + "'"
    flag = 1
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
    except:
        print "check_user_balance except:", sql
        flag = 0
    db.close()
    if flag and data:
        return data[0]
    return False

# 更新用户钱包信息的方法，做相应的钱包余额增减@user_wallet
# @param user_id 用户的id编号
# @param amount 需要增减的金额数额
# @param is_add 这笔更改是否是增加，否则为减少
# @return True/False 更新是否成功
def update_user_wallet(user_id, amount, is_add = True):
    db = ConnectionDB()
    cursor = db.cursor()
    flag = 1
    if is_add:
        sql = "update user_wallet set user_balance = user_balance + " + str(amount) + " where user_ID = '" + user_id +"'"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            flag = 0
    else:
        sql = "update user_wallet set user_balance = user_balance - " + str(amount) + " where user_ID = '" + user_id + "'"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            flag = 0
    db.close()
    if not flag:
        return False
    return True

# 创建新的交易记录@sys_detail
# @param sys_detail数据表中的字段名
# @return True/False 交易激励是否创建成功
def create_sys_detail(trade_info):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "insert into sys_detail(sys_serial, sys_senderID, sys_accepterID, sys_tradeID, sys_targetID, sys_targetName, sys_type, sys_amount, sys_balance, sys_time, sys_notes) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s');"
    sql = sql % (
    trade_info[0], trade_info[1], trade_info[2], trade_info[3], trade_info[4], trade_info[5], trade_info[6],
    trade_info[7], trade_info[8], trade_info[9], trade_info[10])
    flag = 1
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        flag = 0
    db.close()
    if flag:
        return True
    return False

# 创建奖金池@pond_detail
# @param comp_id 比赛赛事的id
# @param apply_number 参加比赛的人数
# @param pond_all 奖池的大小
# @param pond_send 发放掉的奖金数
# @param pond_balance 剩余的奖金数
# @param game_state 比赛类型 1:周赛，2:月赛，3:季赛，4:年赛， 5:团体大赛或者高校大赛， 默认为5，因为前面的几个都是脚本在自动进行
# @return True/False
def create_pond_detail(comp_id, apply_number, pond_all, pond_send, pond_balance, game_state=5):
    db = ConnectionDB()
    cursor = db.cursor()
    pond_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "insert into pond_detail(game_number, game_state, apply_number, pond_all, pond_send, pond_balance, pond_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    sql = sql %(comp_id, game_state, apply_number, pond_all, pond_send, pond_balance, pond_time)
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

# 创建新的发奖记录@award_detail
# @param trade_info 交易信息数组
# @return True/False 交易记录是否创建成功
def create_award_detail(game_number, pound_amount, pond_people_number, first_user_id = "", first_user_award = 0, second_user_id = "", second_user_award = 0, third_user_id = "", third_user_award = 0, other_users_ids = "", other_users_award = 0):
    db = ConnectionDB()
    cursor = db.cursor()
    sql = "insert into award_detail(game_number, pond_amount, pond_people_number, first_user_id, first_user_award, second_user_id, second_user_award, third_user_id, third_user_award, other_users_ids, other_users_award) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')"
    sql = sql % (game_number, pound_amount, pond_people_number, first_user_id, first_user_award, second_user_id, second_user_award, third_user_id, third_user_award, other_users_ids, other_users_award)
    flag = 1
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        flag = 0
    db.close()
    if not flag:
        return False
    return True

# 转账（发钱）， 更新出钱方的余额@user_wallet， 更新收钱方的余额@user_wallet， 写入交易记录@sys_detail
# @param sys_serial 每一笔交易发生时系统所分配的流水号，作为每一笔交易的唯一辨识号码
# @param sender_id 交易的发起方，即出钱方
# @param accepter_id 交易的接收者，即收钱方
# @param sys_tradeID 每一笔交易主关系人的id号码；
# @param sys_targetID 每一笔交易中交易对方的id号码（相对于交易主关系人而言）；
# @param sys_type 交易类型，用于标记每一笔交易的形式及类型 (0-9， 具体请见“海知理财站点后台用户钱包及交易系统概况”文档)
# @param sys_amount 每一笔交易涉及的金额
# @param sys_balance 每一笔交易结算完成时，交易主关系人的账户余额
# @param sys_notes 每一笔交易的详情
# @return 0: 表示交易发起方的余额不足 1：表示成功 2：该次操作失败，数据库操作出现错误，进行任务回滚
def money_allocation(sys_serial, sender_id, accepter_id, sys_tradeID, sys_targetID,  sys_type, sys_amount, sys_balance, sys_notes, sys_targetName = u"海知理财"):
    db = ConnectionDB()
    cursor = db.cursor()
    # 每笔交易发生的时间
    sys_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 判断出钱方是否为系统账户，如果不为系统账户则要判断该用户的余额，余额不足不能发起交易，返回0
    if sender_id != '888888888$':
        sender_balance = check_user_balance(sender_id)
        if sender_balance < sys_amount:
            return 0
    update_sender_balance_sql = "update user_wallet set user_balance = user_balance - " + str(sys_amount) + " where user_ID = '" + sender_id + "'"

    update_accepter_balance_sql = "update user_wallet set user_balance = user_balance + " + str(sys_amount) + " where user_ID = '" + accepter_id + "'"
    sys_detail_sql = "insert into sys_detail(sys_serial, sys_senderID, sys_accepterID, sys_tradeID, sys_targetID, sys_targetName, sys_type, sys_amount, sys_balance, sys_time, sys_notes) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s');"
    create_sys_detail_sql = sys_detail_sql % (
        sys_serial, sender_id, accepter_id, sys_tradeID, sys_targetID, sys_targetName, sys_type,
        sys_amount, sys_balance, sys_time, sys_notes)
    flag = 1
    try:
        cursor.execute(update_sender_balance_sql)
        cursor.execute(update_accepter_balance_sql)
        cursor.execute(create_sys_detail_sql)
        db.commit()
    except:
        db.rollback()
        flag = 0
    db.close()
    if flag == 0:
        return 2
    return 1

# @function money_allocation的上层调用，主要用于简化参数，主要判断交易的类型，方便上层调用
# @return 0: 账户初始储备金，不能进行操作 4/5:当sys_type=4或5时， 与用户购买理财有关，此处只进行简单，未做处理，后面需要可以通过sys_detail表总结规则补充程序
# @return
def money_alliocation_trade(sys_serial, sender_id, accepter_id, sys_type, sys_amount, sys_notes, sys_targetName = u"海知理财"):
    # 0: 账户初始储备金
    # 1: 注册开户
    # 2: 注册奖金发放
    # 3: 用户报名参赛成功
    # 7：当前余额不足，自动报名失败，用户充值后手动报名
    # 8: 现金充值
    if sys_type == 0:
        return 0
    elif sys_type == 1:
        # accepter_id = "888888888$"
        sys_tradeID = sender_id
        sys_targetID = "888888888$"
        sys_amount = 0
        sys_notes = "注册开户"
    elif sys_type == 2:
        # sender_id = "888888888$"
        sys_tradeID = accepter_id
        sys_targetID = "888888888$"
        sys_amount = 50
        sys_notes = "注册奖金发放"
    elif sys_type == 3 or sys_type == 7:
        # accepter_id = "888888888$"
        sys_tradeID = sender_id
        sys_targetID = accepter_id
    # 购买理财家的会员
    elif sys_type == 4:
        return 4
        # sys_tradeID = sender_id
        # sys_targetID = accepter_id
        # accepter_id = "888888888$"
        # sys_targetName = get_user_name(sys_targetID)
    # 理财家收到其他人买自己会员的钱
    elif sys_type == 5:
        return 5
    elif sys_type == 6 or sys_type == 9:
        # sender_id = "888888888$"
        sys_tradeID = accepter_id
        sys_targetID = sender_id
    elif sys_type == 8:
        sender_id = accepter_id = sys_tradeID = sys_targetID = "888888888$"
    else:
        sender_id = accepter_id = sys_tradeID = sys_targetID = "888888888$"
    sys_balance = check_user_balance(sys_tradeID)
    money_allocation_res = money_allocation(sys_serial, sender_id, accepter_id, sys_tradeID, sys_targetID, sys_type, sys_amount, sys_balance, sys_notes, sys_targetName)
    return money_allocation_res






# 比赛模块的处理机制了

# 确定好发奖金的比例情况，返回具体的发钱的列表
# @param pond_all 奖池的容量大小
# @param apply_num 报名人数，该比赛的参赛人数
# @return 返回发钱分配的列表
def determine_bonus_ratio_old(pond_all, apply_num):
    # 根据情况判断发钱的方案
    # 如果报名人数只有两个人是，奖金知发放给第一名
    # 报名人数<50人时，仅发前三名，奖金比例为： 6/3/1
    # 报名人数<100但>50人时，前百分之十的人均发放，奖金比例为5/2/1/2  first:0.5 second:0.2  third: 0.1 other: 0.2/(apply_num * 0.1 - 3)
    # 报名人数>100时，前百分之十的人均发放，奖金比例为:4/2/1/3  first:0.4 second:0.2 third: 0.1 other: 0.3/(apply_num * 0.1 - 3)
    award_array = []
    if apply_num <= 0:
        return []
    if apply_num > 0 and apply_num < 5:
        award_array.append(pond_all)
    elif apply_num >= 5 and apply_num < 10:
        first_award = math.floor(pond_all * 0.7)
        second_award = math.floor(pond_all * 0.3)
        award_array.append(first_award)
        award_array.append(second_award)
    elif apply_num >= 10 and apply_num < 50:
        first_award = math.floor(pond_all * 0.6)
        second_award = math.floor(pond_all * 0.3)
        third_award = math.floor(pond_all * 0.1)
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
    elif apply_num >= 50 and apply_num <= 100:
        first_award = math.floor(pond_all * 0.5)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        other_award = math.floor(pond_all * 0.2)
        # other_award = math.floor(pond_all * 0.2 // (apply_num * 0.1 - 3))
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
        award_array.append(other_award)
    else:
        first_award = math.floor(pond_all * 0.4)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        other_award = math.floor(pond_all * 0.3)
        # other_award = math.floor(pond_all * 0.3 // (apply_num * 0.1 - 3))
        award_array.append(first_award)
        award_array.append(second_award)
        award_array.append(third_award)
        award_array.append(other_award)
    return award_array

# 奖金发放
# @param comp_id 比赛的id
# @param user_rank_list 比赛中用户的排名，字典格式 {1:['888000148$', '888000147$'], 2: ['888000146$'], 3...}
# @param pond_all 奖池大小
# @param sys_notes 发钱原因
# @param sys_note
# @return 0: 奖金金额不对或者参赛人数不对，或者用户排名不对  2: 错误码， 发奖时，某一名（第一名、第二名等）人数<= 0
def bonus_give_out(comp_id, user_rank_list, apply_num, pond_all, sys_notes, sys_type=6, commission_ratio = 0, company_id = "888888888$"):
    pond_send = int(pond_all - pond_all * commission_ratio)

    real_send = 0
    if apply_num <= 0 or pond_send < 0 or len(user_rank_list) <= 0:
        return 0
    elif 0 < apply_num < 5:
        if len(user_rank_list[1]) <= 0:
            return 2
        sys_amount = math.floor(pond_send // len(user_rank_list[1]))
        for user_id in user_rank_list[1]:
            sys_serial = str(time.time()).split('.')[0] + user_id + "16"
            real_send = 0
            money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            # print "sys_serial: ", sys_serial, ",  company_id: ", company_id, ",  user_id: ", user_id, "sys_type: ", sys_type, ",  sys_amount: ", sys_amount, ",  sys_notes: ", sys_notes
    elif 5 <= apply_num < 10:
        if len(user_rank_list[1]) <= 0:
            return 2
        # 第一名人数要是大于等于2人，那么和第一中情况一样，只发第一名的人
        if len(user_rank_list[1]) >= 2:
            sys_amount = math.floor(pond_send // len(user_rank_list[1]))
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                # print "sys_serial: ", sys_serial ,  ",  company_id: ", company_id, ",  user_id: ", user_id, "sys_type: ", sys_type, ",  sys_amount: ", sys_amount, ",  sys_notes: ", sys_notes
        else:
            award_array = determine_bonus_ratio(pond_send, apply_num)
            sys_serial = str(time.time()).split('.')[0] + user_rank_list[1][0] + "16"
            money_alliocation_trade(sys_serial, company_id, user_rank_list[1][0], sys_type, award_array[0], sys_notes)
            # print "sys_serial: ", sys_serial, ",  company_id: ", company_id, ",  user_id: ", user_id, "sys_type: ", sys_type, ",  sys_amount: ", sys_amount, ",  sys_notes: ", sys_notes
            if len(user_rank_list[2]) <= 0:
                return 2
            sys_amount = math.floor(award_array[1] // len(user_rank_list[2]))
            for user_id in user_rank_list[2]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                # print "sys_serial: ", sys_serial, ",  company_id: ", company_id, ",  user_id: ", user_id, "sys_type: ", sys_type, ",  sys_amount: ", sys_amount, ",  sys_notes: ", sys_notes
    elif 10 <= apply_num < 50:
        award_array = determine_bonus_ratio(pond_send, apply_num)
        if len(user_rank_list[1]) <= 0:
            return 2
        # 第一名人数要是大于等于3人，那么和第一中情况一样，只发第一名的人
        if len(user_rank_list[1]) >= 3:
            sys_amount = math.floor(pond_send // len(user_rank_list[1]))
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif len(user_rank_list[1]) == 2:
            sys_amount = math.floor((award_array[0] + award_array[1]) // 2)
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) <= 0:
                return 2
            sys_amount = math.floor(award_array[3] // len(user_rank_list[2]))
            for user_id in user_rank_list[2]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        else:
            sys_serial = str(time.time()).split('.')[0] + user_rank_list[1][0] + "16"
            money_alliocation_trade(sys_serial, company_id, user_rank_list[1][0], sys_type, award_array[0], sys_notes)
            if len(user_rank_list[2]) < 0:
                return 2
            if len(user_rank_list[2]) >= 2:
                sys_amount = math.floor((award_array[1] + award_array[2]) // len(user_rank_list[2]))
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_serial = str(time.time()).split('.')[0] + user_rank_list[2][0] + "16"
                money_alliocation_trade(sys_serial, company_id, user_rank_list[2][0], sys_type, award_array[0], sys_notes)
                if len(user_rank_list[3]) <= 0:
                    return 2
                sys_amount = math.floor(award_array[3] // len(user_rank_list[3]))
                for user_id in user_rank_list[3]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
    elif 50 <= apply_num < 100:
        award_array = determine_bonus_ratio(pond_send, apply_num)
        award_user_num = math.floor(apply_num * 0.1)
        if len(user_rank_list[1]) <= 0:
            return 2
        if len(user_rank_list[1]) >= award_user_num:
            sys_amount = math.floor(pond_send // len(user_rank_list[1]))
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif 3 < len(user_rank_list[1]) < award_user_num:
            sys_amount = (award_array[0] + award_array[1] + award_array[2] + math.floor(((len(user_rank_list[1]) - 3) * (award_array[3] // (award_user_num - 3)))) )

            remain_award_user_num = award_user_num - len(user_rank_list[1])
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= remain_award_user_num:
                sys_amount = math.floor((pond_send - sys_amount) // len(user_rank_list[2]))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_amount = math.floor((pond_send - sys_amount) // (len(user_rank_list[2]) + len(user_rank_list[3])))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif len(user_rank_list[1]) == 3:
            sys_amount = math.floor((award_array[0] + award_array[1] + award_array[2]) // 3)
            remain_award_user_num = award_user_num - len(user_rank_list[1])
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= remain_award_user_num:
                sys_amount = math.floor((pond_send - sys_amount) // len(user_rank_list[2]))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_amount = math.floor((pond_send - sys_amount) // (len(user_rank_list[2]) + len(user_rank_list[3])))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif len(user_rank_list[1]) == 2:
            sys_amount = math.floor((award_array[0] + award_array[1]) // 2)
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= 2:
                sys_amount = math.floor((award_array[2] + award_array[3]) // len(user_rank_list[2]))
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                if len(user_rank_list[3]) > 1:
                    sys_amount = math.floor(award_array[3] // len(user_rank_list[3]))
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                else:
                    sys_amount = math.floor(award_array[3] // (award_user_num - 3))
                    if sys_amount > 0:
                        for i in range(award_user_num-1, 2, -1):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        else:
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[0], sys_notes)
            if len(user_rank_list[2]) == 1:
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[1], sys_notes)
                if len(user_rank_list[3]) == 1:
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[2], sys_notes)
                    sys_amount = math.floor(award_array[3] // (award_user_num - 3))
                    if sys_amount > 0:
                        for i in range(award_user_num, 3, -1):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                else:
                    sys_amount = math.floor( (award_array[2] + award_array[3])// (award_user_num - 2))
                    if sys_amount > 0:
                        for i in range(3, award_user_num):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_amount = math.floor((award_array[1] + award_array[2]) // (len(user_rank_list[2])))
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                if award_user_num > (len(user_rank_list[2]) + 1):
                    sys_amount = math.floor((award_array[1] + award_array[2]) // (award_user_num - len(user_rank_list[2]) - 1))
                    if sys_amount > 0:
                        for i in range(4, award_user_num):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
    else:
        award_array = determine_bonus_ratio(pond_send, apply_num)
        award_user_num = math.floor(apply_num * 0.1)
        if len(user_rank_list[1]) <= 0:
            return 2
        if len(user_rank_list[1]) >= award_user_num:
            sys_amount = math.floor(pond_send // len(user_rank_list[1]))
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif 3 < len(user_rank_list[1]) < award_user_num:
            sys_amount = (award_array[0] + award_array[1] + award_array[2] + math.floor(
                ((len(user_rank_list[1]) - 3) * (award_array[3] // (award_user_num - 3)))))

            remain_award_user_num = award_user_num - len(user_rank_list[1])
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= remain_award_user_num:
                sys_amount = math.floor((pond_send - sys_amount) // len(user_rank_list[2]))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_amount = math.floor((pond_send - sys_amount) // (len(user_rank_list[2]) + len(user_rank_list[3])))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif len(user_rank_list[1]) == 3:
            sys_amount = math.floor((award_array[0] + award_array[1] + award_array[2]) // 3)
            remain_award_user_num = award_user_num - len(user_rank_list[1])
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= remain_award_user_num:
                sys_amount = math.floor((pond_send - sys_amount) // len(user_rank_list[2]))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                sys_amount = math.floor((pond_send - sys_amount) // (len(user_rank_list[2]) + len(user_rank_list[3])))
                if sys_amount > 0:
                    for user_id in user_rank_list[2]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        elif len(user_rank_list[1]) == 2:
            sys_amount = math.floor((award_array[0] + award_array[1]) // 2)
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            if len(user_rank_list[2]) >= 2:
                sys_amount = math.floor((award_array[2] + award_array[3]) // len(user_rank_list[2]))
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
            else:
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                if len(user_rank_list[3]) > 1:
                    sys_amount = math.floor(award_array[3] // len(user_rank_list[3]))
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                else:
                    sys_amount = math.floor(award_array[3] // (award_user_num - 3))
                    if sys_amount > 0:
                        for i in range(award_user_num - 1, 2, -1):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount,
                                                        sys_notes)
        else:
            for user_id in user_rank_list[1]:
                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[0], sys_notes)
            if len(user_rank_list[2]) == 1:
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[1], sys_notes)
                if len(user_rank_list[3]) == 1:
                    for user_id in user_rank_list[3]:
                        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                        money_alliocation_trade(sys_serial, company_id, user_id, sys_type, award_array[2], sys_notes)
                    sys_amount = math.floor(award_array[3] // (award_user_num - 3))
                    if sys_amount > 0:
                        for i in range(award_user_num, 3, -1):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount,
                                                        sys_notes)
                else:
                    sys_amount = math.floor((award_array[2] + award_array[3]) // (award_user_num - 2))
                    if sys_amount > 0:
                        for i in range(3, award_user_num):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount,
                                                        sys_notes)
            else:
                sys_amount = math.floor((award_array[1] + award_array[2]) // (len(user_rank_list[2])))
                for user_id in user_rank_list[2]:
                    sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                    money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
                if award_user_num > (len(user_rank_list[2]) + 1):
                    sys_amount = math.floor(
                        (award_array[1] + award_array[2]) // (award_user_num - len(user_rank_list[2]) - 1))
                    if sys_amount > 0:
                        for i in range(4, award_user_num):
                            for user_id in user_rank_list[i]:
                                sys_serial = str(time.time()).split('.')[0] + user_id + "16"
                                money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount,
                                                        sys_notes)
    return 1






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
    if apply_num <= 0:
        return []
    award_array = np.zeros(apply_num)
    award_array = list(award_array)
    if apply_num > 0 and apply_num < 5:
        award_array[0] = pond_all
    elif apply_num >= 5 and apply_num < 10:
        first_award = math.floor(pond_all * 0.7)
        second_award = math.floor(pond_all * 0.3)
        award_array[0] = first_award
        award_array[1] = second_award
    elif apply_num >= 10 and apply_num < 50:
        first_award = math.floor(pond_all * 0.6)
        second_award = math.floor(pond_all * 0.3)
        third_award = math.floor(pond_all * 0.1)
        award_array[0] = first_award
        award_array[1] = second_award
        award_array[2] = third_award
    elif apply_num >= 50 and apply_num <= 100:
        first_award = math.floor(pond_all * 0.5)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        # other_award = math.floor(pond_all * 0.2)
        other_award = math.floor(pond_all * 0.2 // (apply_num * 0.1 - 3))
        award_array[0] = first_award
        award_array[1] = second_award
        award_array[2] = third_award
        award_num = int(math.floor(apply_num * 0.1))
        for i in range(3, award_num):
            award_array[i] = other_award
    else:
        first_award = math.floor(pond_all * 0.4)
        second_award = math.floor(pond_all * 0.2)
        third_award = math.floor(pond_all * 0.1)
        other_award = math.floor(pond_all * 0.3)
        other_award = math.floor(pond_all * 0.3 // (apply_num * 0.1 - 3))
        award_array[0] = first_award
        award_array[1] = second_award
        award_array[2] = third_award
        award_num = int(math.floor(apply_num * 0.1))
        for i in range(3, award_num):
            award_array[i] = other_award
    return award_array

# 对同一个名次的人员进行奖金的发放
# @param company_id 企业的id
# @param sys_type 交易类型
# @param sys_smount 奖金发放的数量
# @param 发奖理由
# @i 本次排名的名次
def distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, i):
    for user_id in user_rank_list[i]:
        sys_serial = str(time.time()).split('.')[0] + user_id + "16"
        # money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        print "sys_serial: ", sys_serial, " company_id: ", company_id, " user_id: ", user_id, " sys_type: ", sys_type, " sys_amount: ", sys_amount, " sys_notes: ", sys_notes



# 奖金发放
# @param comp_id 比赛的id
# @param user_rank_list 比赛中用户的排名，字典格式 {1:['888000148$', '888000147$'], 2: ['888000146$'], 3...}
# @param pond_all 奖池大小
# @param sys_notes 发钱原因
# @param sys_note
# @return 0: 奖金金额不对或者参赛人数不对，或者用户排名不对  2: 错误码， 发奖时，某一名（第一名、第二名等）人数<= 0
def bonus_give_out_new(comp_id, user_rank_list, apply_num, pond_all, sys_notes, sys_type=6, commission_ratio = 0, company_id = "888888888$"):
    pond_send = int(pond_all - pond_all * commission_ratio)
    user_rank_list[0] = []
    if apply_num <= 0 or pond_send < 0 or len(user_rank_list) <= 0:
        return 0
    # 根据情况判断发钱的方案
    # 如果报名人数apply_num<5，奖金知发放给第一名
    # 报名人数apply_num<10, 奖金发给一、二名，若第一名多余一人，则只发第一名
    # 报名人数<50人时，仅发前三名，奖金比例为： 6/3/1
    # 报名人数<100但>50人时，前百分之十的人均发放，奖金比例为5/2/1/2  first:0.5 second:0.2  third: 0.1 other: 0.2/(apply_num * 0.1 - 3)
    # 报名人数>100时，前百分之十的人均发放，奖金比例为:4/2/1/3  first:0.4 second:0.2 third: 0.1 other: 0.3/(apply_num * 0.1 - 3)
    elif 0 < apply_num < 5:
        if len(user_rank_list[1]) <= 0:
            return 2
        sys_amount = math.floor(pond_send // len(user_rank_list[1]))
        distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, 1)
    elif 5 <= apply_num < 10:
        aware_array = determine_bonus_ratio(pond_send, apply_num)
        start_index = 0
        for i in range(2):
            end_index = start_index + len(user_rank_list[i+1])
            sys_amount = math.floor(sum(aware_array[start_index:end_index]) // len(user_rank_list[i+1]))
            start_index = end_index
            if sys_amount <= 0:
                break
            distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, i+1)

        # sys_amount = math.floor(sum(aware_array[:len(user_rank_list[1])]) / len(user_rank_list[1]))
        # if sys_amount > 0:
        #     for user_id in user_rank_list[1]:
        #         sys_serial = str(time.time()).split('.')[0] + user_id + "16"
        #         # money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        #         print "sys_serial: ", sys_serial, " company_id: ", company_id, " user_id: ", user_id, " sys_type: ", sys_type, " sys_amount: ", sys_amount, " sys_notes: ", sys_notes
        # # second_aware 二等奖发发金额
        # sys_amount = math.floor(sum(aware_array[len(user_rank_list[1]):len(user_rank_list[1]) + len(user_rank_list[2])]) / len(user_rank_list[2]))
        # if sys_amount > 0:
        #     for user_id in user_rank_list[2]:
        #         sys_serial = str(time.time()).split('.')[0] + user_id + "16"
        #         # money_alliocation_trade(sys_serial, company_id, user_id, sys_type, sys_amount, sys_notes)
        #         print "sys_serial: ", sys_serial, " company_id: ", company_id, " user_id: ", user_id, " sys_type: ", sys_type, " sys_amount: ", sys_amount, " sys_notes: ", sys_notes
    elif 10 <= apply_num < 50:
        aware_array = determine_bonus_ratio(pond_send, apply_num)
        start_index = 0
        for i in range(3):
            end_index = start_index + len(user_rank_list[i+1])
            sys_amount = math.floor(sum(aware_array[start_index:end_index]) // len(user_rank_list[i+1]))
            start_index = end_index
            if sys_amount <= 0:
                break
            distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, i+1)
    elif 50 <= apply_num < 100:
        aware_array = determine_bonus_ratio(pond_send, apply_num)
        award_num = int(apply_num * 0.1)
        start_index = 0
        for i in range(award_num):
            end_index = start_index + len(user_rank_list[i + 1])
            sys_amount = math.floor(sum(aware_array[start_index:end_index]) // len(user_rank_list[i + 1]))
            start_index = end_index
            if sys_amount <= 0:
                break
            distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, i + 1)
    else:
        aware_array = determine_bonus_ratio(pond_send, apply_num)
        award_num = int(apply_num * 0.1)
        start_index = 0
        for i in range(award_num):
            end_index = start_index + len(user_rank_list[i + 1])
            sys_amount = math.floor(sum(aware_array[start_index:end_index]) // len(user_rank_list[i + 1]))
            start_index = end_index
            if sys_amount <= 0:
                break
            distribute_aware_template(company_id, sys_type, sys_amount, sys_notes, i + 1)




    # return 1


comp_id = 99999
user_rank_list = {1:["888000100$"], 2:["888000200$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$"], 7:["888000700$"], 8:["888000800$"], 9:["888000900$"], 10:["888001000$"], 11: ["888001100$"]}
# user_rank_list = {1:["888000100$", "888000101$"], 2:["888000200$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$", "888000601$"], 7:["888000700$"],  8:["888000800$"], 9:["888000900$"]}
# user_rank_list = {1:["888000100$", "888000101$", "888000102$"], 2:["888000200$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$", "888000601$"], 7:["888000700$"], 8:["888000800$"]}
# user_rank_list = {1:["888000100$", "888000101$"], 2:["888000200$", "888000201$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$", "888000601$"], 7:["888000700$"],  8:["888000800$"]}
# user_rank_list = {1:["888000100$"], 2:["888000200$", "888000201$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$", "888000601$"],  7:["888000700$"], 8:["888000800$"], 9:["888000900$"]}
# user_rank_list = {1:["888000100$"], 2:["888000200$", "888000201$", "888000202$"], 3:["888000300$"], 4:["888000400$"], 5:["888000500$"], 6:["888000600$", "888000601$"],  7:["888000700$"], 8:["888000800$"], 9:["888000900$"]}
apply_num = 100
pond_all = 10000
sys_notes = "参赛获奖"
res = determine_bonus_ratio(pond_all, apply_num)
print res
bonus_give_out_new(comp_id, user_rank_list, apply_num, pond_all, sys_notes)







# award_array = [50, 20, 10, 20]
# user_rank_list = ['1', '2', '3', '4', '5']
# award_user_num = 9
# sys_amount = (award_array[0] + award_array[1] + award_array[2] + math.floor(((len(user_rank_list) - 3) * (award_array[3] // (award_user_num - 3)))) )
# print sys_amount
# print (len(user_rank_list[1]) - 3) * (award_array[3] // (award_user_num - 3))













