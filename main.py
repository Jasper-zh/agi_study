
from nlg_example import NLU, DST, DialogManager

def nlu_result():
    nlu = NLU()
    result = nlu.parse('推荐一个便宜的')
    print(result)

# 100G以上流量的套餐最便宜的是哪个：{"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
def dst():
    nlu = NLU()
    result = nlu.parse('有很多流量的么')
    dst = DST()
    state = {}
    result = dst.update(state, result)
    # 第二轮
    result = nlu.parse('便宜些的')
    result = dst.update(state, result)
    print(result)


def demo():
    # 创建对话管理器实例
    dialog_manager = DialogManager({
        "recommand": "根据您的需求，推荐您选择__NAME__套餐，月费为__PRICE__元，流量为__DATA__GB。",
        "not_found": "抱歉，找不到符合条件的套餐，请重新提出您的需求。您说的是__INPUT__吗？"
    })

    # 示例对话流程
    user_input = "我想找一个月费不超过200的套餐"
    response = dialog_manager.run(user_input)
    print("===系统回复===")
    print(response)

if __name__ == '__main__':
    demo()





