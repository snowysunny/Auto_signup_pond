# coding: utf-8

import Auto_sign_pond as sp

# user_id = "888000147$"
# print user_id
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
comp_id = 10
# amount = 2
# is_organizer = True
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "创建比赛： ", res
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# print "*********************************"
#
# user_id = "888000100$"
# print user_id
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# is_organizer = False
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "参加比赛： ", res
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# print "*********************************"
#
# user_id = "888000040$"
# print user_id
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "参加比赛： ", res
# res = sp.check_user_balance(user_id)
# print res
# print "*********************************"
#
# user_id = "888000032$"
# print user_id
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "参加比赛： ", res
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# print "*********************************"
#
# user_id = "888000046$"
# print user_id
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# res = sp.competition_signup(user_id, comp_id, amount, is_organizer)
# print user_id, "参加比赛： ", res
# res = sp.check_user_balance(user_id)
# print user_id,'余额为： ',res
# print "*********************************"
#
# print "--------------------------"


award_user_list = ["888000100$", "888000040$", "888000032$",  "888000148$"]
res = sp.competition_distribute_awards(comp_id, award_user_list)
print "发奖：", res
