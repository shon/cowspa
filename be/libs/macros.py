import re

import be.repository.stores as stores

# 'biz:{{context:user_biz}}::approve_membership'
# 'biz:{{biz_id_from_plan_id}}::approve_plan'

def cuser_id(context, data, macro_data):
    return context.user_id

def cuser_perm_names(context, data, macro_data):
    user_id = context.user_id
    return [p.name for p in user_perms_store.get_one_by(user_id=user_id)]

def cuser_biz_ids(context, data, macro_data):
    user_id = context.user_id
    member = stores.member_store.get(user_id)
    return member.biz_memberships

def biz_id_from_plan_id(context, data, macro_data):
    plan_id = data['plan_id']
    plan = stores.plan_store.get(plan_id)
    return str(plan.bizplace_id)

def requestor_display_name(context, data, macro_data):
    user_id = data['requestor_id']
    profile = stores.profilestore.get_one_by(member=user_id, _fields=['display_name'])
    return profile.display_name or stores.userstore.get(user_id).username

def name_from_plan_id(context, data, macro_data):
    plan_id = data['plan_id']
    return stores.plan_store.get(plan_id).name

def id_by_name(context, data, macro_data):
    return stores.permission_store.get_one_by(name=macro_data).id

processors = dict(
    cuser_id = cuser_id,
    cuser_perm_names = cuser_perm_names,
    cuser_biz_ids = cuser_biz_ids,
    biz_id_from_plan_id = biz_id_from_plan_id,
    requestor_display_name = requestor_display_name,
    name_from_plan_id = name_from_plan_id,
    id_by_name = id_by_name,
    )

def process(text, context, data):
    macro_pat = '({{[^}]*}})'
    macros = re.findall(macro_pat, text)
    result = text
    for macro in macros:
        macro_name = macro[2:-2]
        if macro_name in data:
            m_result = data[macro_name]
        else:
            macro_data = None
            if ':' in macro_name:
                macro_name, macro_data = macro_name.split(':')
            f = processors[macro_name]
            m_result = f(context, data, macro_data)
        result = result.replace(macro, m_result)
    return result

if __name__ == '__main__':
    def add_a_b(context, data, macro_data):
        return str(data['a'] + data['b'])
    processors['add_a_b'] = add_a_b
    text = 'A + B = {{add_a_b}}'
    data = dict(a=1, b=2)
    print process(text, None, data, None)
