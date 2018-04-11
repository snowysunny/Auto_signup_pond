# coding: utf-8


import Auto_sign_pond as sp
#
#
# user_id = "888000100$"
# res = sp.check_user_balance(user_id)
# print res
# # amount = "10"
# # is_add = 0
# # res = sp.update_user_wallet(user_id, amount, is_add)
# # print(res)
# # res = sp.check_user_balance(user_id)
# # print res
#
# # company_id = "888888888$"
# # res = sp.update_company_wallet(company_id, amount, is_add)
# # print res
#
# res = sp.select_pond_detail("2017-04-2")
# print res
#
# trade_info = ['147019217188800145$', '888888888$', '888000097$', '888000097$', '888888888$', '海知理财', '2', '200', '200', '2018-04-02 10:42:51', '注册奖金发放']
# res = sp.create_sys_detail(trade_info)
# print res
#
#
# trade_info = ['11', '22', '11', '888000030$', '13', '888000028$', '6', '888000037$', '2', 'NULL', '0']
# res = sp.create_award_detail(trade_info)
# print res


# comp_id = 8
# amount = 5
# res = sp.create_pond_detail(comp_id, amount)
# print res

user_id = "888000148$"
print user_id
res = sp.check_user_balance(user_id)
print user_id,'余额为： ',res
comp_id = 10
amount = 5
is_organizer = True
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "创建比赛： ", res
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# print "*********************************"

# res = sp.update_pond_detail_siginup(comp_id, amount)
# print res
#
#
# # print "Start: "
# # comp_id = "2017-04"
# # comp_name = "2017-04"
# # award_user_list = ['888000105$','888000106$', '888000107$', '888000108$']
# # res = sp.distribute_awards(comp_id, comp_name, award_user_list)
# # print res
#
# user_id = "888000097$"
# comp_id = 2
# amount = 8
# is_organizer = False
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print res