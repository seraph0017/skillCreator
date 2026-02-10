import requests
import json
import os

# 复用 skill 中的函数
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json().get("tenant_access_token")
    except Exception as e:
        print(f"获取 Token 异常: {e}")
        return None

def get_lark_user_id(token, email=None, mobile=None):
    url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id?user_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {}
    if email:
        payload["emails"] = [email]
    if mobile:
        payload["mobiles"] = [mobile]
        
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"查询用户异常: {e}")
        return {"code": -1, "msg": str(e)}

if __name__ == "__main__":
    APP_ID = os.getenv("LARK_APP_ID")
    APP_SECRET = os.getenv("LARK_APP_SECRET")
    
    if not APP_ID or not APP_SECRET:
        print("请设置 LARK_APP_ID 和 LARK_APP_SECRET 环境变量")
        exit(1)
        
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    if not token:
        print("获取 Token 失败")
        exit(1)
        
    print("--- 飞书用户 Open ID 查询工具 ---")
    print("请输入你的飞书注册邮箱或手机号")
    user_input = input("邮箱/手机号: ").strip()
    
    result = None
    if "@" in user_input:
        result = get_lark_user_id(token, email=user_input)
    else:
        # 假设是手机号
        result = get_lark_user_id(token, mobile=user_input)
        
    if result and result.get("code") == 0:
        data = result.get("data", {})
        
        # 检查手机号结果
        if data.get("mobile_users") and data["mobile_users"].get(user_input):
             users = data["mobile_users"][user_input]
             if users:
                 print(f"\n查询成功! 你的 Open ID 是: {users[0]['user_id']}")
                 print(f"请设置环境变量: export LARK_USER_OPEN_ID='{users[0]['user_id']}'")
             else:
                 print("\n未找到对应用户，请确认手机号是否正确，或应用是否有通讯录权限。")
                 
        # 检查邮箱结果
        elif data.get("email_users") and data["email_users"].get(user_input):
             users = data["email_users"][user_input]
             if users:
                 print(f"\n查询成功! 你的 Open ID 是: {users[0]['user_id']}")
                 print(f"请设置环境变量: export LARK_USER_OPEN_ID='{users[0]['user_id']}'")
             else:
                 print("\n未找到对应用户，请确认邮箱是否正确，或应用是否有通讯录权限。")
        else:
            print(f"\n未找到用户。API 响应: {json.dumps(result, ensure_ascii=False)}")
    else:
        print(f"\n查询失败: {result}")
