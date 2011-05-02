import re

import be.repository.stores as stores

# 'biz:{{context:user_biz}}::approve_membership'
# 'biz:{{biz_id_from_plan_id}}::approve_plan'

def cuser_id(context, data):
    return context.user_id

def cuser_perm_names(context, data):
    user_id = context.user_id
    return [p.name for p in user_perms_store.fetch_one_by(user_id=user_id)]

def cuser_biz_ids(context, data):
    user_id = context.user_id
    member = stores.member_store.fetch_by_id(user_id)
    return member.biz_memberships

def biz_id_from_plan_id(context, data):
    plan_id = data['plan_id']
    plan = stores.plan_store.fetch_by_id(plan_id)
    return str(plan.biz_id)

def requestor_display_name(context, data):
    user_id = data['requestor_id']
    profile = stores.memberstore.fetch_by_id(user_id).profile
    return profile.display_name or stores.userstore.fetch_by_id(user_id).username

def name_from_plan_id(context, data):
    plan_id = data['plan_id']
    return stores.plan_store.fetch_by_id(plan_id).name

processors = dict(
    cuser_id = cuser_id,
    cuser_perm_names = cuser_perm_names,
    cuser_biz_ids = cuser_biz_ids,
    biz_id_from_plan_id = biz_id_from_plan_id,
    requestor_display_name = requestor_display_name,
    name_from_plan_id = name_from_plan_id,
    )

def process(text, context, data):
    macro_pat = '({{[^}]*}})'
    macros = re.findall(macro_pat, text)
    result = text
    for macro in macros:
        f = processors[macro[2:-2]]
        m_result = f(context, data)
        result = result.replace(macro, m_result)
    return result

if __name__ == '__main__':
    def add_a_b(context, data):
        return str(data['a'] + data['b'])
    processors['add_a_b'] = add_a_b
    text = 'A + B = {{add_a_b}}'
    data = dict(a=1, b=2)
    print process(text, None, data)
